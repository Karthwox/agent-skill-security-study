# SECURITY.md

Project security decisions. Keep this short and current. Anything not listed means no access.

Exposed: unknown   <!-- yes | no | unknown. Unknown counts as yes. -->

## Roles
<!-- e.g. anonymous, user, admin -->

## Access matrix
| Resource | Anonymous | Owner | Other user | Admin | Notes |
|----------|-----------|-------|------------|-------|-------|

## Identity rules
- User id and tenant id come from the session, never from the request.

## Server-only operations
<!-- Operations that need elevated credentials, e.g. payment webhooks. -->

## Secrets inventory
| Name | Can do | Lives in | Read by | Rotate |
|------|--------|----------|---------|--------|

## Abuse surface
| Endpoint | Caller | Cost / risk | Limit | Keyed by | On exceed |
|----------|--------|-------------|-------|----------|-----------|

## Budgets
- Global daily ceilings:
- Provider spend caps and alerts set by the user: <yes/no, which providers>

## Authentication decisions
- Approach: <managed provider | vetted library | custom (user required)>: <name>
- Session mechanism:
- Lifetimes: access / refresh / idle / absolute
- Password policy:
- MFA:
- Redirect allowlist:

## Assumptions
<!-- Security choices taken by default without asking the user. One line each. -->

## Deferrals
<!-- Controls postponed for local-only work. One line each: what, and the condition that ends it (default: before the project is exposed). Empty means nothing is deferred. -->

## Accepted risks
<!-- Gaps knowingly accepted after the user was told. Date each. -->
