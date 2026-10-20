# v0.4 draft 2 changes (2026-10-19)

Source: Phase 4c round 1 results (results/phase4cd-report.md). Rule 1 failed (v0.4 5/36 vs reminder 7/36). Changes are general lessons, not variant text.

- SKILL.md "Always": no fallback secrets (even labelled dev), safe settings by default. Cause: in V13 skill runs 3/3 shipped `dev-only-change-me`; transcripts show secrets.md (which already forbids fallbacks) was never opened, the agents read authentication.md. The rule now sits in the always-read file and in authentication.md.
- authentication.md: same rule for session/signing secrets; Secure/debug must not depend on a variable production may not set (V13 partial: FLASK_ENV).
- access-control.md section on teams: qualify columns in policy subqueries (V19 skill r3: unqualified column made an invite check always true).
Not changed: upload rule (already in v0.4; the public skill's U1 failures do not apply to us), dependency exception, deferral clause.
Round 1 variants V10-V21 were read for these lessons, so round 2 must use new variants.
