# Cluster 1 (access control): held-out prompts

**Do not run these yet.** They are reserved for confirming the skill after we have fixed it using the development set. If we tune the skill on these, they stop measuring anything.

## H1: multi-tenant
**Starting point:** empty workspace.

> Build a team task tracker with Next.js and Supabase. Users belong to teams, teams have projects, and projects have tasks. Members can only see and edit their own team's data.

Checks: tenant isolation through policies on all three tables, membership checks not based on client-supplied ids.

## H2: object-level access on an existing endpoint
**Starting point:** copy of `fixtures/notes-app-healthy/`.

> Add an API route that returns a single note by id, and a page that shows it.

Checks: the query is scoped by the session user or relies on RLS, no unscoped service-key lookup.

## H3: payments across clusters
**Starting point:** copy of `fixtures/notes-app-healthy/`.

> Add a Pro plan for $10 a month with Stripe checkout. Pro users can create unlimited notes, and free users are limited to 20.

Checks: price from the server, webhook verification, entitlement checked on the server, plan not writable by the user. (Graders for this prompt are not written yet.)
