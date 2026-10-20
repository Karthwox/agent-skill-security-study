# Authentication and sessions

*Last checked against vendor docs: October 2026. Vendor details (auth provider settings and names, framework session APIs, hashing library options) change; confirm against current docs before relying on them.*

## When to read this

Read before: adding login, signup, sessions, password handling, password reset or email verification, OAuth or SSO, JWTs, API tokens for users, or MFA; protecting a route with a login check; configuring an auth provider; or when a project that deferred authentication is about to be exposed (see "Deferrals for local-only work" below).

## Why this happens

Authentication code has many small details (expiry, rotation, invalidation, enumeration, redirect validation), and a login that omits all of them still logs people in. Nothing visibly breaks, so each omission is silent. Tutorial-style examples with hardcoded secrets, fast hashes, and tokens that never expire are common, and generated auth code tends to mirror them. Hand-rolling auth also multiplies the places to make a mistake, which is why the first decision below is to avoid building it. Finally, "temporary" shortcuts (a fake login, a hardcoded password) have a way of shipping.

## Workflow

1. **Design the identity model first,** even if login comes later: who the users are, what each owns, which roles exist.
2. **Choose the approach** (managed provider by default) and record it in `SECURITY.md`.
3. **Implement and configure** everything that isn't deferred.
4. **Verify,** and report what was and wasn't checked.

## Deferrals for local-only work

Everything in this file applies by default. The one exception: while a project is local-only (it runs only on the developer's machine, with fake data, and nobody else can reach it), the user may defer the costly parts of authentication. A deferral is a deliberate choice recorded in `SECURITY.md`, never an assumption. If the user doesn't ask to defer, nothing is deferred.

**May be deferred:** login UI and provider setup (use the dev stub below), MFA, reset and verification flows, session hardening and timeouts, password policy polish.

**May not be deferred, even locally:**
- The identity model: ownership columns, role names, and per-user scoping in every query. Real auth can be added late only if adding it changes nothing else. Retrofitting ownership into a finished app is where missing RLS and IDOR come from.
- Real passwords and personal data stay out of any project that uses deferrals.
- The dev stub's production guard.

**Recording a deferral.** Add one line to the deferral register in `SECURITY.md`: what is deferred and the condition that ends it. The default condition is "before the project is exposed."

**Exposure.** A project is exposed if anyone else can, or might be able to, reach it, or if it holds real data. If you aren't sure, treat it as exposed. Stop before any action that likely exposes it: deploy or publish commands, tunnels or public host flags, sharing a link, a non-local database or backend, live payment keys, real or user-supplied data, a hosted agent environment, or the user mentioning launch, customers, or a demo link. Tell the user in one message what the action exposes and which deferrals are open, then clear each one or record it as an accepted risk with the date. The full procedure is in `gate.md` (not yet written).

**The dev-only login stub.** Use it so prototyping isn't slowed by login screens. It must return an identity shaped like the real session, so the access-control code is exercised, and it must be impossible to run in production.

```ts
// dev-auth.ts: local prototyping only
if (process.env.NODE_ENV === "production") {
  throw new Error("dev auth stub must not run in production");
}
export const devUser = { id: "dev-user-1", role: "user" };
```

List the stub in the deferral register in `SECURITY.md`, ending when the project is exposed. The ship check searches for it. A hand-written fake login with a hardcoded password is worse than this stub, because nothing stops it from shipping.

## Step 1: Authentication decisions

Use `SECURITY.md` in the project root (create it from `assets/SECURITY.template.md` if it doesn't exist) and fill in the authentication decisions.

```markdown
## Authentication decisions
- Approach: managed provider | vetted library | custom (user required): <name>
- Session mechanism: provider session cookie | server session in HttpOnly cookie | JWT + refresh
- Lifetimes: access <minutes>, refresh <days>, idle timeout <>, absolute timeout <>
- Password policy: min <15 without MFA, 8 with MFA>, max >= 64, no composition rules, breached-password check <yes/no>
- MFA: offered | required for admin | not yet
- Redirect allowlist: <exact URLs>

## Deferrals
- <dev auth stub, login UI, MFA: until the project is exposed>
```

**Decision order for the approach:**

1. **Managed provider** (Supabase Auth, Auth.js, Clerk, Auth0, Firebase Auth, or similar) by default. Most of the rules below are then handled for you, leaving configuration and correct integration.
2. **Vetted library** for self-hosted needs.
3. **Custom** only if the user explicitly requires it. Then every rule below applies without exception.

## Step 2: Implementation rules

**1. Every protected route and action checks identity on the server.** Call the central guard (see `access-control.md`). Client-side route guards and hidden pages are UX, not controls. Don't rely only on framework middleware, since middleware bypass bugs have existed (a 2025 Next.js flaw let a crafted header skip it). Check again at the route or data layer.

**2. Passwords, if you store them.** Use Argon2id with at least OWASP's minimum (19 MiB memory, 2 iterations, 1 degree of parallelism), or scrypt or bcrypt if Argon2id is unavailable. Never MD5, SHA-1, or plain SHA-256. Use the library's compare function, not `===`.

```ts
const hash = await argon2.hash(password, {
  type: argon2.argon2id,
  memoryCost: 19456,   // KiB, OWASP minimum; raise if the hardware allows
  timeCost: 2,
  parallelism: 1,
});
```

Policy: OWASP's authentication guidance, aligned with NIST, treats passwords under 15 characters as weak when there is no MFA and under 8 with MFA. Allow at least 64 characters, impose no composition rules, don't force periodic rotation, and check new passwords against a breached-password list.

**3. Sessions.**

- Keep session identifiers or tokens in `HttpOnly`, `Secure`, `SameSite` cookies, not in localStorage or sessionStorage, where any XSS can read them.
- Rotate the session identifier on login and on privilege change.
- Invalidate sessions on logout and on password change.
- Enforce idle and absolute timeouts on the server.

```ts
res.cookie("session", sessionId, {
  httpOnly: true,
  secure: true,          // needs HTTPS; relax only for local development
  sameSite: "lax",
  path: "/",
  maxAge: 7 * 24 * 60 * 60 * 1000,
});
```

**4. JWTs, only when needed** (stateless APIs, third-party consumers). A token that is decoded but not verified proves nothing.

```ts
const claims = jwt.verify(token, KEY, {
  algorithms: ["RS256"],         // fixed allowlist; never take the algorithm from the token header
  issuer: ISSUER,
  audience: AUDIENCE,
});                              // expiry is checked by default
```

Keep access tokens short-lived (minutes), rotate refresh tokens and support revocation, and load signing keys from the environment (see `secrets.md`). Never use a guessable signing secret.

**5. Reset, verification, and magic-link flows.**

```ts
const token = crypto.randomBytes(32).toString("base64url");     // CSPRNG, never Math.random
await saveResetToken({ hash: sha256(token), userId, expiresAt: now + 30 * 60_000 });  // store only a hash
// Always answer: "If that address has an account, we sent a link."
```

Tokens are single-use, short-lived, and invalidated on use and on password change. Build links from a configured base URL, not the request's Host header. Respond identically whether or not the account exists. Rate limit by account, IP, and recipient (see `abuse-controls.md`). Treat an email as verified only after a confirmation link is used.

**6. Brute force and credential stuffing.** Throttle per account and per IP with backoff, add a challenge after repeated failures, use uniform error messages, and avoid hard lockouts (they let an attacker lock out a victim). Offer MFA and require it for admins. Don't build SMS code delivery yourself.

**7. OAuth and SSO.** Use the provider's library. Register exact-match redirect URIs, with no wildcards and no leftover localhost or tunnel URLs in production. Use `state` and PKCE, validate `iss`, `aud`, and nonce for OIDC, and link accounts only by verified email. Validate any post-login `next` or `redirect` parameter against an allowlist, otherwise it is an open redirect.

**8. Sensitive and destructive actions need re-authentication or a single-use token, checked on the server.** This covers changing password or email, deleting an account, deleting or wiping large amounts of data, changing payment details, and any admin action on another user.

- Require the user's password (or a fresh sign-in within the last few minutes), or send a single-use confirmation link or code that expires quickly and is bound to this user and this action.
- A typed phrase such as "DELETE" or a browser confirm dialog is a guard against slips, not security: it adds nothing against a hijacked session or a forged request. Use it in addition, never instead.
- Admin actions on someone else's account: check the caller's role on the server on every call (never from a client flag), refuse self-escalation, and write an audit log row (who, what, target, when).
- If an AI model proposes the action, the user confirms it through a separate request the model cannot make, and the server re-checks ownership and a row cap at that point.
- Rate limit these routes (`abuse-controls.md`) and invalidate other sessions after a password change or account deletion.

Verify: try the action with a valid session but without the second factor (it must fail); call it as a non-admin (it must fail); confirm an audit row exists.

## Stack notes

Version-sensitive; confirm in current docs.

- **Managed providers: settings to find and check** (names and locations vary): email confirmation required (not switched off for convenience and forgotten), breached-password protection if offered, minimum password length, MFA enabled or offered, exact-match redirect and callback URLs, session and token lifetimes, refresh token rotation, rate limits for sign-in, one-time codes, and email sending, unused sign-in methods and anonymous sign-in disabled, and the admin or secret key kept server-only.
- **Framework middleware** is a convenience layer. Always verify the session again where data is read or written.
- **Custom auth** also needs CSRF protection for cookie sessions (see the web hardening file, not yet written).
- **Platform-verified tokens:** when a provider's JWT is verified by the platform for database policies, your own server code must still verify tokens it relies on.

## Step 3: Verify

Tests, run against the real auth path where possible:

- Protected routes and actions return 401 without a session, and 403 or 404 for the wrong user.
- Tampered, expired, and `alg: none` tokens are rejected.
- A session is invalid after logout and after password change.
- A reset token works once, expires, and is rejected after use.
- Reset and login responses don't reveal whether an email has an account.
- Post-login redirects accept only allowlisted targets.
- Repeated failed logins are throttled.
- Login responses set cookies with `HttpOnly`, `Secure`, and `SameSite` (check with `curl -i`).

**Ship check:**

```bash
# Weak hashing: review each hit, flag any used on passwords
git grep -nEi "createHash\(['\"](md5|sha1|sha256)['\"]\)|hashlib\.(md5|sha1|sha256)"

# JWTs decoded without verification, or unsafe algorithm settings
git grep -nE "jwt\.decode\(|jwtDecode\(|alg['\"]? *[:=] *['\"]none|ignoreExpiration"

# Tokens in browser storage
git grep -nE "(localStorage|sessionStorage)\.(setItem|getItem)\(['\"][^'\"]*(token|jwt|session|auth)"

# Weak randomness near tokens or codes
git grep -n "Math.random"

# Possible open redirects, review each hit
git grep -nE "redirect\(.*(req\.(query|body)|searchParams)"
```

- Search provider and environment config for `*` in redirect or callback URL lists and for leftover localhost or tunnel URLs.
- Confirm every entry in the deferral register is still valid. If the project is exposed or exposure is unknown, the register must be empty or each remaining entry must be a dated, accepted risk, and the dev auth stub must not exist.
- Check provider dashboard settings from the checklist above. If you can't access them, ask the user to confirm and record the answer, or report them as not verified.

**Report.** End with a short summary: exposure status and open deferrals, what was tested and how, what was found, and what could not be verified (especially provider settings).

## Step 4: If an account or token is compromised

1. **Revoke** sessions and refresh tokens for affected users. If tokens may have been forged, rotate the signing key, and tell the user that this signs everyone out.
2. **Force a password reset** for affected accounts.
3. **Find the cause.** If a secret leaked, follow the incident steps in `secrets.md`.
4. **Check notification obligations** for affected users, which depend on local rules, and tell the user to check them.
5. **Add detection,** such as alerts on unusual login patterns.

## Related files

- `access-control.md`: authorization after authentication, and identity taken from the session.
- `secrets.md`: signing keys and OAuth client secrets.
- `abuse-controls.md`: throttling, challenges, and per-target limits on login, reset, and code endpoints.
- Web hardening (not yet written): CSRF, CORS, and security headers.
