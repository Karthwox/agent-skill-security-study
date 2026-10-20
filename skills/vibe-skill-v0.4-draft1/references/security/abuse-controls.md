# Abuse controls: rate limits, resource caps, spend limits

*Last checked against vendor docs: October 2026. Vendor details (platform firewall features, managed-auth limits, limiter libraries, proxy settings) change; confirm against current docs before relying on them.*

## Short version (read this even if you read nothing else)

For every route or server action that costs money, sends a message, takes a public form, issues a code, or returns lists or exports:

1. Authenticate first (anonymous: per-IP limit plus a challenge such as Turnstile).
2. Per-user limit, applied after auth. Per-target limit if it contacts someone else (email, SMS, one account).
3. Global daily ceiling so a loop or attack cannot exceed what you will pay.
4. Caps: input length, page size, `max_tokens` or output limit, timeout, steps in any tool loop.
5. Keep the counters where every instance can see them (database table or shared store), never in a per-process variable on serverless.
6. Respond 429 with `Retry-After`. Never let a caller choose who an email goes to.
7. Write the route in the abuse table in `SECURITY.md`, and add a test that exceeds the limit.

The rest of this file explains how, and what to verify.

## When to read this

Read before creating or changing any of: an endpoint or server action that sends email, SMS, or notifications; calls a paid API (LLM, maps, payments); handles signup, login, password reset, one-time codes, or verification; accepts a public form; returns lists, search results, or exports; or runs an expensive query or job. Also read when choosing how to deploy (serverless and multi-instance setups change how limits must be stored). Upload size limits are covered in `uploads.md`.

## Why this happens

Rate limiting is a requirement that nobody sees when it is missing. The feature works in a demo, nothing breaks in development, and no prompt mentions abuse, so happy-path code never includes it. It also needs shared state, which is more setup than "make it work" invites. The costs show up later: an anonymous endpoint that calls an LLM lets strangers spend your money, a signup form becomes an email-bombing tool, and a bug that loops can do the same damage as an attacker. Being logged in does not fix this, because one valid account can still drive unbounded usage.

## Workflow

1. **List the abuse surface** in `SECURITY.md` before writing any endpoint that costs money, sends messages, or handles auth.
2. **Implement layered limits and caps** through one central helper.
3. **Prove it** with tests that exceed each limit.
4. **Run the ship check** and report what was and wasn't verified.

## Step 1: Abuse surface list

Use `SECURITY.md` in the project root (create it from `assets/SECURITY.template.md` if it doesn't exist) and fill in the abuse surface and budgets. Draft it from the app description. Ask the user only about spending limits and anything unclear.

```markdown
## Abuse surface
| Endpoint            | Caller    | Cost / risk                 | Limit                                  | Keyed by      | On exceed        |
|---------------------|-----------|-----------------------------|----------------------------------------|---------------|------------------|
| POST /api/chat      | user      | LLM tokens                  | 20/hour per user, 1,000/day global     | user id       | 429              |
| POST /api/signup    | anonymous | verification email, spam    | 5/hour per IP, 3/day per email address | IP, email     | 429 + challenge  |
| POST /api/contact   | anonymous | email to owner              | 3/hour per IP                          | IP            | 429 + challenge  |

## Budgets
- Global daily ceilings: chat 1,000 requests, outbound email 200
- Provider spend caps and alerts set by the user: <yes/no, which providers>
```

Tier the work so simple projects stay simple:

- **Tier 1, always:** anything that costs money, sends a message, or handles auth and one-time codes. Per-caller limits, per-target limits, a global budget, and a challenge if anonymous.
- **Tier 2:** endpoints that write data. Per-user limits and size caps.
- **Tier 3:** public reads. Size and pagination caps only.

Starting points, to tune against real use: login 5 to 10 attempts per 15 minutes per account and IP; signup 3 to 5 per hour per IP; password reset or one-time code 3 per hour per account and per IP; email or SMS sends 3 to 5 per hour per recipient; LLM chat 20 to 60 requests per hour per user. Do not offer anonymous access to paid APIs unless the product needs it, and if it does, use a very tight limit plus a challenge.

## Step 2: Implementation rules

**1. One central helper.** Put limiting in a single helper or middleware that every listed route calls, so a later edit can't quietly skip one route. Server actions and route handlers are both public HTTP endpoints and both need it.

**2. Layer the limits.**

- *Per IP* for anonymous traffic, applied early so floods are stopped before expensive work.
- *Per user*, applied after authentication, so unauthenticated requests don't consume a user's quota.
- *Per target* for actions that affect other people: emails to one address, codes to one number, attempts on one account. This stops distributed abuse that per-IP limits miss.
- *Global budget* as a circuit breaker, so a runaway loop or distributed attack can't exceed what you are willing to spend.
- *Provider caps and alerts* at the LLM, email, SMS, and maps providers. You can't set or verify these, so ask the user to set them and record the answer.

```ts
export async function POST(req: Request) {
  const session = await requireUser(req);                       // auth first (see access-control.md)
  if (!(await limit(`chat:user:${session.userId}`, 20, 3600)))  return tooMany(3600);
  if (!(await limit(`chat:global:${today()}`, 1000, 86400)))    return tooMany(600);   // budget breaker
  const input = ChatInput.parse(await req.json());              // schema caps input length
  return callModel(input, { maxTokens: 800, timeoutMs: 20_000 });
}
```

**3. Store limits where the deployment can share them.** An in-memory counter is per process. On serverless or any multi-instance deployment, each instance counts separately, so a limit of 10 per minute across ten warm instances allows 100. Use:

- a shared store (Redis, for example Upstash), or
- a database table (works with no new service, but must be server-only: enable RLS with no policies, see `access-control.md`), or
- the platform's own edge or firewall rate limiting, which also stops floods before app code runs.

In-memory limiting is fine only for a single long-lived process, and it needs eviction so old keys don't pile up. A minimal cross-instance fixed-window counter in Postgres:

```sql
create table if not exists rate_limits (
  key          text primary key,
  window_start timestamptz not null,
  count        integer not null
);
alter table rate_limits enable row level security;   -- no policies: clients get nothing

-- $1 = key, $2 = window length such as '1 hour'; allowed when returned count <= limit
insert into rate_limits as r (key, window_start, count)
values ($1, now(), 1)
on conflict (key) do update set
  count        = case when r.window_start < now() - $2::interval then 1 else r.count + 1 end,
  window_start = case when r.window_start < now() - $2::interval then now() else r.window_start end
returning count;
```

Delete old rows on a schedule (for example, `window_start` older than a day). Fixed windows allow a short burst at each boundary, which is acceptable for abuse control. Use a sliding-window library if you need strictness.

**4. Choose keys the client can't forge.**

- Do not read `x-forwarded-for` straight from the request. A client can send any value, which lets it reset its own counter and fill your store with junk keys. Use the client address that your platform or proxy sets itself, and configure how many proxy hops to trust (for example Express's `trust proxy`).
- Bound the key space with expiry or eviction.
- Normalize per-target keys (lowercase email addresses) so variations don't dodge the limit.

**5. Decide what happens when the limiter fails.** For Tier 1 routes, fail closed: if the store is unreachable, refuse the request instead of skipping the limit. For low-risk reads, fail open and log. A switch to disable limits for tests is fine if it defaults to on and production configuration never sets it.

**6. Respond properly.** Return 429 with a `Retry-After` header and a generic message. Avoid hard account lockouts, which let an attacker lock out a victim. Throttle with backoff per account and IP, and use a challenge after repeated failures. Login and reset specifics are in `authentication.md`.

**7. Cap resource use everywhere.**

- **Pagination:** the server enforces a default and a maximum page size and ignores or clamps the client's value. Prefer cursors over deep offsets.
- **Request size:** set a body size limit at the framework or platform, and `.max()` on strings, arrays, and nesting in input schemas.
- **Time:** set timeouts on outbound HTTP calls, database statements, and function duration.
- **Work driven by user input:** bound loops and recursion, avoid regexes with nested quantifiers, never compile user-supplied patterns, cap export size, and move large exports to a background job.
- **Concurrency:** limit simultaneous expensive jobs per user and queue the rest.
- **GraphQL:** enforce depth and complexity limits.
- **LLM calls:** set `max_tokens`, cap input length, enforce a per-user request or token budget, set a timeout, and cap the number of steps in any tool-calling loop.
- **Caching:** cache expensive public reads.

**8. Protect public forms from bots and spam.**

- Add a challenge (Turnstile, hCaptcha, or similar) to signup and to public forms that cause email or other side effects. Verify the token on the server. A client-only check is cosmetic.
- A honeypot field is a cheap extra, never the only defense.
- Never let an unauthenticated request choose the recipient of an email or message. A contact form always sends to the owner. An endpoint that emails an address supplied by the caller is an open relay.
- Limit per recipient as well as per IP, so signup and reset flows can't be used to email-bomb a victim.
- Scraping can't be eliminated. Keep bulk data behind authentication, cap page sizes, and avoid sequential full dumps.

**9. Make abuse visible.** Log limiter hits (route, key type, counts) without logging secrets or unnecessary personal data, and alert when the global budget breaker trips. Without this, abuse is discovered on the bill.

## Stack notes

Version-sensitive; confirm in current docs.

- **Managed auth providers** (Supabase Auth, Firebase Auth, Auth0, Clerk, and similar) have built-in limits for sign-in, signup, one-time codes, and email sending. Find those settings and check they are configured. Your own endpoints around them (contact forms, custom code routes) still need limits.
- **Next.js and similar serverless frameworks:** middleware does not share state across instances. Use a shared store or the platform's firewall rules. Server actions are reachable by direct POST.
- **Express, Fastify, and similar servers:** use a maintained limiter with a shared store. Some default to an in-memory store, which is wrong for multiple instances. Set the proxy trust setting to the exact number of hops.
- **Edge and CDN rate limiting rules** (Cloudflare and similar) are the best first layer for anonymous floods.

## Step 3: Verify

Write tests that exceed each limit. Use low limits through test configuration.

- Each Tier 1 route returns 429 on request max + 1, with `Retry-After`.
- User A hitting a limit does not block user B. Many IPs targeting one email address are still limited by the per-target key.
- Changing `x-forwarded-for` does not reset the counter.
- When the global budget is exhausted, the route refuses without calling the provider (mock the provider and assert it was not called).
- Oversized bodies are rejected (413 or 400), page sizes above the maximum are clamped, and over-long input is rejected.
- With the limiter store unavailable, Tier 1 routes refuse requests.

**Ship check:**

- List every route handler, server action, and edge function. Each Tier 1 route appears in the abuse surface list, and its code calls the limiter before the costly call or send (and after authentication for user-keyed limits).
- Search for in-memory limiter patterns in serverless projects (`new Map()` near `rate` or `limit`, `rateLimitMap`, default in-memory store options).
- Search for raw `x-forwarded-for` or `x-real-ip` reads used as limiter keys.
- Search unauthenticated routes that call LLM, email, or SMS code. Each must be in the list with a challenge and tight limits.
- Search LLM calls for a missing output token cap, and check input length caps.
- Check that the recipient of every email or SMS send comes from server configuration or verified user data, never the request body.
- Check production configuration for any variable that disables limiting.
- Ask the user to confirm provider spend caps and alerts, and record the answer. If you could not verify them, say so.

**Report.** End with a short summary: which routes are covered and by what, what was tested, anything not verified (especially provider caps and multi-instance behavior).

## Step 4: If abuse is happening

1. **Stop the spend first:** disable or tighten the affected route (a feature flag is ideal), and rotate any key the abuse could have used.
2. **Find the pattern** in logs: route, key, volume, timing.
3. **Add or tighten limits and a challenge,** using temporary edge blocks if needed.
4. **Check provider usage and bills,** and contact the provider about credits if appropriate.
5. **Add detection** (the budget alert) so the next incident is noticed early.

## Related files

- `access-control.md`: limiter tables need RLS, and authenticate before applying user-keyed limits.
- `secrets.md`: a server route that holds a key must also be rate-limited and authenticated.
- `authentication.md`: login brute force, lockout policy, reset and verification flows.
- `uploads.md`: upload size and type limits.
