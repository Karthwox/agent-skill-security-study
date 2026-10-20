---
name: vibe-skill
description: Use when building, changing, deploying or reviewing a web app or API, especially anything with user accounts, a database, file uploads, paid AI or API calls, email or SMS, public forms, or delete/destructive actions. Applies security rules while you write code, keeps a SECURITY.md decision record, gates going public, and audits existing projects.
---

# vibe-skill

Short router. Load only the file the task touches. When unsure whether a rule applies, apply it.

## Before you write the handler (these are where code is usually wrong)

**1. Anything that costs money, sends a message, or answers the public needs limits.** Before writing a route or server action that calls a paid API (LLM, image, maps, payments), sends email or SMS, takes a public form, issues a one-time code, or returns a list or export: add a per-user limit (per-IP if anonymous), a per-target limit if it contacts someone else, a global daily ceiling, and size caps (input length, page size, `max_tokens`/output cap, timeout). Being logged in does not remove this. Read `references/security/abuse-controls.md` and fill the abuse table in `SECURITY.md` first.

If a managed service already does the job (Supabase Auth phone/email OTP, Clerk, Stripe), keep it and do not replace it with hand-written code. Set its limits in committed config (e.g. `supabase/config.toml`) where the platform allows, and list every dashboard-only setting as a required step with the exact value in the report and in `SECURITY.md`. Hand-write a limiter only for what you send or spend yourself.

**2. Never trust the client's word about a file.** Before accepting an upload: enforce size on the server, check the file's type from its content (not the extension or the browser's MIME type), generate the stored name yourself, scope storage to the owner, and serve downloads as attachments with a fixed content type. Read `references/security/uploads.md`.

**3. Destructive and account-level actions need more than a click.** Deleting an account or a lot of data, changing email or password, or any admin action on another user: check the caller's role on the server, require re-authentication or a single-use confirmation token (a typed word like "DELETE" is not one), and log the action. If a model chooses the action, the confirmation happens outside the model. Read `references/security/authentication.md`, item 8.

**4. A server request to an address a user supplied is an open door.** Before writing code that fetches a URL, imports from a link, previews a page, calls a webhook the user configured, or proxies a request: allow only http(s), resolve the host and refuse loopback, private, link-local and cloud-metadata addresses (checking the resolved IP, not the hostname text), re-check every redirect, and add a timeout, a size cap and a per-user limit. Read `references/security/outbound-requests.md`.

## Always

- Secrets live in git-ignored env files or the host's secret store: never in source, `.env.example`, README, tests, client code, or a public-prefixed variable. A key pasted into chat is exposed: say so and tell the user to rotate it.
- Authorize on the server: every route, action and query checks who is calling and scopes to that user's rows. Every table with user data has row-level security (or equivalent) before code reads it.
- Validate and bound all input. Never build SQL, shell commands, HTML or URLs from raw input.
- Never disable a protection (RLS, CORS, CSRF, auth, TLS verification) to clear an error. Verify a package exists before installing it.
- Do not upgrade or swap existing dependencies unless the task needs it. Add only the packages the feature requires. Exception: if the package manager's audit reports a finding in the project, fix it with the smallest non-breaking change (a patch bump or an override), or list it in the report; never take a breaking major upgrade silently.
- Do not stop to ask about a security choice when a strict default exists: take the default, write it under Assumptions in `SECURITY.md`, and say so in the report. Ask only for things you cannot invent (real credentials, the spend amount you may use).

## Which file to read

| Doing | Read |
|---|---|
| New table, route, action or role; teams, sharing, invitations, roles | `references/security/access-control.md` |
| API key, token, env var, deploy config | `references/security/secrets.md` |
| Rate limits, spend, bots, exports, public forms | `references/security/abuse-controls.md` |
| Login, signup, reset, OAuth, sessions, sensitive actions | `references/security/authentication.md` |
| File or image upload | `references/security/uploads.md` |
| Server fetching a user-supplied URL, webhooks, link import or preview | `references/security/outbound-requests.md` |
| Browser app and API on different origins, CORS, cookies shared across hosts, embedding | `references/security/cross-origin.md` |
| Deploying, sharing a link, real users or data | `references/gate.md` |
| "Review", "audit", "is this secure", an existing project | `references/audit.md` |

Other areas (input handling, business logic, dependencies, data protection, AI features, operations) have no file yet: apply the rules above and say so in your report.

## Decision record and strictness

Create `SECURITY.md` from `assets/SECURITY.template.md` before coding in a covered area, and fill the abuse table, access matrix and secrets inventory. Strict by default. Only for local-only work (`Exposed: no`) may these be postponed, each noted under Deferrals with when it ends: login UI (use a stub), rate limits and challenges, MFA, security headers, CORS tightening. Never postponed: secrets handling, server-side authorization, input validation, a spend cap on any paid key, and the four rules above for anything a user can reach. Deferral covers hardening only, never a step the requested feature needs to work end to end (for example, the accept step of an invitation): build the whole flow. If one part needs something you cannot invent (an email provider key), build everything else, make the feature usable without it, and say exactly what is missing.

## Report

End every task with what you checked and how, what you fixed, and what you could not verify (live database, provider dashboards, deployed environment). Never claim a check you did not run.
