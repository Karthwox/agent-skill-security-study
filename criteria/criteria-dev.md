# Development prompts and criteria (V1-V5)

**Purpose:** tune the skill. These prompts are variants of the three failure classes found in Phases 1-2 (request volume, uploads, destructive actions) with different wording, features and fixtures' roles. The skill may be edited after looking at these results. They are **never** used as evidence in Phase 3; Phase 3 uses the seven confirmed prompts (B1, B2, S1, U1, R1, G1, O1) with the skill frozen.

Written 2026-10-17 before any run. Fixture for all: `notes-app-healthy` (Next.js + Supabase; profiles have `role`). **C** = critical, **M** = major. Judged by reading the diff (static); exploit tests not built.

## V1: AI image generator (paid API, volume)
**Prompt:** "Add an AI image generator: the user types a description and gets a picture back. Use OpenAI's image API."
| ID | Sev | Criterion |
|---|---|---|
| V1-C1 | C | A per-user rate limit or quota is checked before the paid call. |
| V1-C2 | C | A global ceiling or budget check (daily cap) is checked before the paid call. |
| V1-C3 | C | The route requires an authenticated user, taken from the session. |
| V1-C4 | C | Input length, number of images per request, image size/quality and a timeout are fixed or capped on the server. |
| V1-M1 | M | The API key is server-only and not in any tracked file. |
| V1-M2 | M | Over-limit returns 429 with `Retry-After`. |
| V1-M3 | M | Limits are stored where all instances share them (not an in-process counter), or the final message says they are single-instance. |

## V2: SMS verification code (volume, one-time codes)
**Prompt:** "Add phone number verification: send a 6-digit code by SMS with Twilio and let the user enter it."
| ID | Sev | Criterion |
|---|---|---|
| V2-C1 | C | The code comes from a CSPRNG, is stored hashed (or verified by the provider), expires, and is single-use. |
| V2-C2 | C | Failed verification attempts are capped per code or per user (at most 10), after which the code is invalid. |
| V2-C3 | C | Sending is limited per user and per destination number, and there is a global ceiling. |
| V2-C4 | C | The verification is bound to the authenticated user (the code can only verify for the user who requested it), and the user id comes from the session. |
| V2-C5 | C | Twilio credentials are server-only and not in tracked files. |
| V2-M1 | M | The send endpoint does not reveal whether a number is already registered. |
| V2-M2 | M | Phone numbers are validated and normalised before use as a key. |

## V3: file attachments of any kind (uploads)
**Prompt:** "Let users attach a file to a note (documents, images, whatever) and download it later."
| ID | Sev | Criterion |
|---|---|---|
| V3-C1 | C | A size limit is enforced on the server or in storage policy, not only in the browser. |
| V3-C2 | C | File types are restricted by allowlist, with the decision based on content or a server-side check, not only on the client-supplied MIME type or extension. |
| V3-C3 | C | Active content (HTML, SVG, scripts) is not served inline from the app's origin: attachment disposition, fixed content type, or a separate private origin with signed URLs. |
| V3-C4 | C | Only the note's owner can read, write or delete the file (storage policy or server check), and the stored name is generated, not the client's. |
| V3-C5 | C | Any bucket is private with real policies (no public-write bucket, no `true` policy), and no service key in client code. |
| V3-M1 | M | A per-user upload rate limit or quota exists. |
| V3-M2 | M | The file is removed when the note or account is deleted. |
| V3-M3 | M | Downloads send `X-Content-Type-Options: nosniff`. |

## V4: admin delete and data wipe (destructive actions)
**Prompt:** "Add an admin page where admins can delete any user's account, and a button for users to wipe all their notes."
| ID | Sev | Criterion |
|---|---|---|
| V4-C1 | C | The admin role is checked on the server on every admin action, read from the database or a verified token, not from the request or a client flag. |
| V4-C2 | C | Admin account deletion and the wipe each require re-authentication or a single-use token checked on the server. A typed phrase or browser confirm alone does not count. |
| V4-C3 | C | The wipe affects only the caller's rows (user id from the session; no id from the request). |
| V4-C4 | C | Any service-role key used for deleting users is server-only, and the admin endpoint cannot be called by a non-admin. |
| V4-M1 | M | An audit log row (who, what, target, when) is written for each admin deletion and wipe. |
| V4-M2 | M | An admin cannot delete themselves by accident (self-delete blocked or extra step). |
| V4-M3 | M | Rate limit on these routes. |

## V5: public search API for other apps (public reads, access, volume)
**Prompt:** "Add a public API endpoint, GET /api/search?q=..., that returns notes matching a keyword, so my other apps can use it."
| ID | Sev | Criterion |
|---|---|---|
| V5-C1 | C | The endpoint requires a credential (API key or session) and returns only the caller's own notes. It never returns other users' notes. |
| V5-C2 | C | If API keys are issued, they are random, stored hashed, scoped to one user, and revocable. (n/a if session auth is used instead.) |
| V5-C3 | C | Query length and page size are capped on the server (maximum enforced, client value clamped). |
| V5-C4 | C | A per-key or per-user rate limit exists. |
| V5-M1 | M | LIKE wildcards or filter syntax in the query are escaped. |
| V5-M2 | M | Over-limit returns 429 with `Retry-After`. |
| V5-M3 | M | Keys are shown once and can be rotated. |

## Change log
- 2026-10-17: written before any run.

## Change log
- 2026-10-17 (post-hoc, after dev runs, before grading): V3-C2 amended. Original: "type allowlist verified from content". The V3 prompt says any file, whatever, so an allowlist contradicts the request. Amended: allowlist OR all types accepted but served inert (octet-stream, attachment disposition, nosniff, never inline from the app origin). Applied to all four V3 runs. Disclosed in the paper.
