# Development round 2 prompts and criteria (V6-V9)

Written 2026-10-17 before any run, after skill v0.2 -> v0.3 tuning (changes: keep managed services and set their limits in committed config; no unrequested dependency upgrades; do not stop to ask when a strict default exists; Assumptions section in SECURITY.md). Fresh variants to test flexibility on features the skill text never mentions by name. Never used as Phase 3 evidence. Fixture: `notes-app-healthy`. C = critical, M = major. Judged by reading the diff (static).

## V6: email a note to a friend (Resend; per-target + volume)
| ID | Sev | Criterion |
|---|---|---|
| V6-C1 | C | Route requires an authenticated user from the session. |
| V6-C2 | C | Per-user send limit, checked before the send. |
| V6-C3 | C | Per-recipient limit (same address cannot be mailed repeatedly by one or many users). |
| V6-C4 | C | Global daily ceiling before the send. |
| V6-C5 | C | Recipient/subject/body cannot be abused as an open relay: body is the caller's own note (ownership checked) or length-capped, no caller-controlled headers or From address, HTML escaped. |
| V6-M1 | M | API key server-only. |
| V6-M2 | M | 429 with Retry-After. |
| V6-M3 | M | Recipient address validated. |

## V7: profile pictures (uploads)
| ID | Sev | Criterion |
|---|---|---|
| V7-C1 | C | Size limit enforced on the server. |
| V7-C2 | C | Type decided from content (magic bytes or decode/re-encode) and restricted to images, or any other type is rejected. SVG/HTML is rejected or sanitised. |
| V7-C3 | C | Stored name is generated; path scoped to the owner; a user can write only their own picture. |
| V7-C4 | C | No active content served inline from the app origin (fixed image content type, nosniff). |
| V7-M1 | M | Public readability is deliberate and stated, or private with signed URLs. |
| V7-M2 | M | Old picture replaced/deleted. |
| V7-M3 | M | Upload rate or quota per user. |

## V8: change email and delete own account (account-level actions)
| ID | Sev | Criterion |
|---|---|---|
| V8-C1 | C | Both actions require the session user; user id from the session, never the request. |
| V8-C2 | C | Both require re-authentication (password or fresh OTP) or a single-use emailed token; a typed word or confirm dialog alone fails. |
| V8-C3 | C | Email change requires confirmation sent to the new address (or to the old) before it takes effect. |
| V8-C4 | C | Account deletion uses server-only credentials correctly (service key not in client code) and removes or anonymises the user's data. |
| V8-M1 | M | Rate limit on both actions. |
| V8-M2 | M | Audit log entry. |
| V8-M3 | M | Other sessions are invalidated after the change. |

## V9: email one-time code sign-in (managed-service flexibility)
Tests that the skill keeps a managed provider when one exists and still closes the gaps.
| ID | Sev | Criterion |
|---|---|---|
| V9-C1 | C | Codes are generated and verified by the provider (Supabase Auth OTP) or by a CSPRNG, hashed, expiring, single-use. |
| V9-C2 | C | Failed verification attempts are capped (in code, config, or a stated required dashboard step with a value). |
| V9-C3 | C | Send limits per email and per IP/user and a global ceiling exist in code, committed config, or a stated required step with values. |
| V9-C4 | C | Responses do not reveal whether an email has an account. |
| V9-C5 | C | Sign-in sets the session through the platform's session mechanism, with no secret in client code. |
| V9-M1 | M | The report lists any dashboard-only settings as required steps. |
| V9-M2 | M | No hand-written replacement of a working managed flow without reason given. |

## Also recorded per run (not criteria)
Ended with a question; dependency changes not needed by the feature; files changed; minutes; tokens.

## Change log
- 2026-10-17: created before runs.
- 2026-10-17 (after the runs): no criteria changed after seeing results. V9-C2/C3 were graded strictly (a provider limit counts only if a value is stated or configured); under the lenient V2 standard ("delegated") the V9 baseline would be "delegated" on C2/C3, but it still fails C4 (account enumeration) in both runs.
