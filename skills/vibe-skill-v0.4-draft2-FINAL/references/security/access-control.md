# Access control: data access and authorization

*Last checked against vendor docs: October 2026. Vendor details (Supabase keys and policies, Firebase rules syntax) change; confirm against current docs before relying on them.*

## When to read this

Read before creating or changing any of: database tables or policies, API routes, server actions, auth-gated pages, storage buckets, roles, payments or entitlements. Skip for pure static or visual work.

## Why this happens

Access control is code someone has to write on purpose. A feature works fine without it, so when the goal is "make it work," the check is simply never written. Scanners struggle to flag it because nothing wrong is present, only something absent. And when a protection blocks a query, the fastest-looking fix is to switch the protection off. Everything below is built around those three facts: decide access before writing data code, enforce it in one place, and prove it holds.

## Workflow

1. **Write the access matrix** (`SECURITY.md`) before any data code.
2. **Implement deny-by-default** from the matrix.
3. **Prove it with negative tests.**
4. **Run the ship check** and report what was and wasn't verified.

## Step 1: Access matrix

Use `SECURITY.md` in the project root, creating it from `assets/SECURITY.template.md` if it doesn't exist, and fill in the roles, access matrix, identity rules, and server-only operations. Draft it yourself from the app description, then ask the user only about rows marked `?` or rows touching personal data, money, or health. Anything not listed means no access.

Example of the format:

```markdown
## Access matrix
| Resource      | Anonymous | Owner | Other user | Admin | Notes                         |
|---------------|-----------|-------|------------|-------|-------------------------------|
| profiles      | none      | RU    | none       | R     | owner = profiles.id           |
| notes         | none      | CRUD  | none       | R     | owner = notes.user_id         |
| public_posts  | R         | CRUD  | R          | CRUD  | intentionally public          |

## Identity rules
- User id and tenant id come from the session, never from the request.
```

Keep it short. A resource that is public on purpose must say so in the Notes column, because the ship check treats everything else as private.

## Step 2: Implementation principles

**1. Enforce where the data lives.** The database or server decides. A hidden button, a disabled menu item, or a client-side role check is cosmetic, never a control.

**2. Identity comes from the session.** Derive user and tenant ids on the server. Never accept `user_id`, `tenant_id`, `role`, `price`, or `isAdmin` from a request body, URL, or hidden form field and use it to authorize or to write.

```js
// Bad: the URL alone decides who sees the order
db.query("select * from orders where id = $1", [req.params.id]);

// Good: the id AND the session owner must both match
db.query("select * from orders where id = $1 and user_id = $2",
         [req.params.id, session.userId]);
```

**3. Allowlist fields in both directions.** Parse input with a strict schema that rejects unknown keys, so `role: "admin"` in a request is an error instead of a silent write. Select explicit columns on output instead of returning whole rows.

```ts
const UpdateNote = z.object({
  title: z.string().max(200),
  body: z.string().max(10_000),
}).strict();                       // unknown keys are rejected
const data = UpdateNote.parse(req.body);

db.from("users").select("id, display_name, avatar_url");   // not select("*")
```

**4. One central place for checks.** Put authorization in database policies, one middleware or guard, or a single data-access layer. Scattered inline checks get skipped by later edits. Every route or handler either goes through the guard or is listed as public in the matrix.

**5. Privileged credentials stay on the server.** See `secrets.md` for full handling. For this section: any key that bypasses access policies must never appear in client code, a public-prefixed env var (`NEXT_PUBLIC_`, `VITE_`, and similar), or a built bundle.

**6. Never fix an error by removing protection.** If a policy blocks a query, debug the policy: check which role is calling, whether the user is signed in, and whether the policy matches the column. If a feature genuinely needs elevated access, build it as a server-only function that explicitly checks who is calling. If you are stuck, stop and tell the user. Do not disable row-level security, remove an auth check, set CORS to `*`, or "make it public for now," even temporarily, because temporary shortcuts are the ones that ship.

**7. Money and entitlements are server-derived.**
- Look up prices and discounts from a server-side catalog. Never trust an amount sent by the client.
- Verify payment webhooks with the provider's signature check. Treat a "success" redirect as unconfirmed until the webhook or a server-side lookup confirms it.
- Check premium or role-gated features on the server for every request, not only in the UI.
- Make state changes that move money or stock atomic and idempotent, so double clicks and replays do nothing.


### Sharing, teams, invitations and roles

Read this when users can share data with other users, belong to teams or organisations, or hold roles.

1. **Put it in the matrix.** Add the roles and what each can read, write, invite and remove. Anything not listed means no access.
2. **Membership is data, protect it.** Only an owner or admin can add or remove members. A user must not be able to add themselves, change their own role, or send a role in a request. Writes to the membership table go through a function that checks the caller, not through a bare insert policy.
3. **Avoid recursive policies.** A policy on the membership table that queries the membership table, or two tables whose policies read each other, fails or loops. Put the membership test in a `SECURITY DEFINER` helper with a fixed `search_path` and call it from the policies.

```sql
create function public.is_team_member(t uuid) returns boolean
language sql stable security definer set search_path = '' as $$
  select exists (select 1 from public.team_members m
                 where m.team_id = t and m.user_id = (select auth.uid()));
$$;
-- policies use: using (public.is_team_member(team_id))
```
   In any policy subquery, qualify every column with its table alias (`i.team_id = team_id` is wrong: the right-hand name binds to `i` too, so the check is always true and any row passes). Write `i.team_id = team_members.team_id` or pass the value into a function.

4. **Invitations are a complete flow, not a row.** Build the whole path: create (owner or admin only), deliver or display, accept, expire, revoke. The token is unguessable, expires, works once, and accepting it binds to the signed-in user whose verified email matches the invite. If email delivery needs a provider key you cannot invent, make the invitation usable in-app (the invitee sees pending invitations when they sign in and can accept) and list the email step as the missing piece.
5. **Sharing stays owner-controlled.** Only the owner can share or unshare a note. Recipients get the access level they were given and cannot raise it. Existing owner-only write policies stay owner-bound; add member access as separate, narrower policies. Revoking a share or removing a member removes access.
6. **Limits:** cap and rate-limit invitations per team and per user (see `abuse-controls.md`).
7. **Verify with two or three seeded users:** a non-member cannot read team data or the member list; a member cannot add themselves to another team, invite, or edit what they only share-read; an invitation cannot be accepted twice, by another user, or after expiry; removing a member ends access.

## Stack notes

### Supabase / Postgres with row-level security (RLS)

- Enable RLS on every table in an exposed schema. Without it, the public client key can read and write the table. With RLS enabled and no policies, access is denied, which is the safe default.
- Bind policies to the row owner. An `INSERT` policy takes only a `with check`, and it must tie the new row to the caller, or users can create rows in someone else's name. An `UPDATE` policy with only `using` reuses it as the `with check` (Postgres does this for `UPDATE` and `ALL` policies), which is safe, but write both so the check can't silently differ from the filter. A `with check` that is looser than `using` lets users rewrite rows into someone else's name.

```sql
alter table public.notes enable row level security;

create policy "read own" on public.notes for select to authenticated
  using ((select auth.uid()) = user_id);

create policy "insert own" on public.notes for insert to authenticated
  with check ((select auth.uid()) = user_id);

create policy "update own" on public.notes for update to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

create policy "delete own" on public.notes for delete to authenticated
  using ((select auth.uid()) = user_id);
```

- **Signed in is not the same as allowed.** A policy that only checks that the caller is authenticated, or is `using (true)`, lets any user read everyone's rows. Allow this only for data the matrix marks public.
- **Do not base policies on `user_metadata`.** Users can edit it themselves. Use server-controlled `app_metadata` or a roles table.
- **Views bypass RLS by default** because they run with the owner's privileges. Create them with `security_invoker = true` (Postgres 15+) or avoid exposing them.
- **`SECURITY DEFINER` functions bypass RLS.** Set a fixed `search_path`, validate the caller inside the function, and expose them only to roles that need them.
- **Storage has separate policies** on `storage.objects`. Table policies do not cover files.
- **Keys.** Supabase is moving from the legacy `anon` and `service_role` keys to publishable (`sb_publishable_...`) and secret (`sb_secret_...`) keys. The publishable key is subject to RLS. The secret key always bypasses RLS. Use the publishable key in the browser and the secret key only in server code. Confirm the current naming and deprecation dates in the docs.

### Firebase

- Start from deny-all (`allow read, write: if false;`) and open specific paths.
- Tie access to the owner: `request.auth != null && request.auth.uid == resource.data.userId`.
- Never ship `allow read, write: if true;` or time-limited open rules.
- Validate written fields in the rules, not only in the client.

### Plain Postgres or MongoDB with an ORM

- Put ownership scoping in repository or service functions, so no handler builds an unscoped query.
- Use the session's user id in every `where` clause for user-owned data.

## Step 3: Negative tests

Test that the wrong people are refused, not only that the right people succeed. Use two seeded users, A and B.

- Anonymous request to each protected route and table: denied.
- A reads, updates, and deletes B's record by id: denied or not found.
- A creates a record with B's `user_id`: denied or overwritten with A's id.
- Non-admin calls each admin route: denied.
- Request body includes `role`, `isAdmin`, `user_id`, or `price`: ignored or rejected.
- List endpoints return only the caller's rows and only allowed fields.

Assert the denial explicitly (status 401/403/404, or an empty result), not just the absence of an error. For each test, confirm it would fail if the check were removed: briefly disable the policy or guard in a scratch copy, or at least assert on a value that only the correct behavior produces.

## Step 4: Ship check

Run what the environment allows. If you have no database access, run the static checks against migration files and state that live checks were not done.

**Database (Postgres/Supabase):**

```sql
-- Tables without RLS in the exposed schema
select schemaname, tablename from pg_tables
where schemaname = 'public' and not rowsecurity;

-- Policies that allow everything; review each against the matrix
select tablename, policyname, cmd, roles, qual, with_check
from pg_policies
where schemaname = 'public' and (qual = 'true' or with_check = 'true');

-- Views: reloptions should include security_invoker=true
select c.relname, c.reloptions from pg_class c
join pg_namespace n on n.oid = c.relnamespace
where n.nspname = 'public' and c.relkind = 'v';
```

Also read every remaining policy and confirm it references a user or tenant column.

**Code and build output:**

- Search client code and the built bundle for `service_role`, `sb_secret_`, and other privileged keys.
- Search env files and config for public-prefixed variables that hold secrets (`NEXT_PUBLIC_.*(SECRET|SERVICE|PRIVATE)`, `VITE_.*(SECRET|SERVICE|PRIVATE)`).
- Search for leftovers: `skipAuth`, `bypass`, `DISABLE ROW LEVEL SECURITY`, `TODO.*auth`, `FIXME.*auth`, test or debug routes, default credentials such as `admin/admin`.
- List every route, handler, and server action. Confirm each calls the central guard or is marked public in `SECURITY.md`.
- Search write paths for client-supplied `price`, `amount`, `role`, `isAdmin`, `user_id`, `tenant_id`.

**Report.** End the task with a short summary: what was checked and how (live or static), what failed and was fixed, and what could not be verified. Do not report a check you did not run.

## Related files

- `secrets.md`: privileged keys and how they reach the server.
- `abuse-controls.md`: rate limits and abuse protection for payment, webhook, and write endpoints.
