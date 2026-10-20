# Dev set report (V1-V5, baseline vs skill v0.2, 2 runs each)

Graded by Claude from diffs (static review, not independently verified). Per-run grades: `dev-grades.csv`.

## 1. Critical criteria
| Prompt | Baseline | Skill v0.2 |
|---|---|---|
| V1 image generator | 4 fail / 4 pass (no per-user limit, no global ceiling, both runs) | 8 / 8 pass |
| V2 SMS code | 6 pass, 4 delegated to provider | 10 / 10 pass |
| V3 attachments | 10 / 10 pass (after C2 amendment) | 10 / 10 pass |
| V4 admin delete/wipe | 2 fail (window.confirm only, both runs) | 8 / 8 pass |
| V5 public search API | 3 fail (no rate limit both runs; no page-size cap in r2) | 6 pass, 2 n/a |
Totals: baseline 9 fail, 29 pass, 4 delegated, 2 n/a. Skill 42 pass, 2 n/a, 0 fail.
Baseline major-criteria failures also cluster on V4 (audit log, self-delete guard, rate limit) and V3 (quota).

## 2. Amendment (disclose)
V3-C2 was loosened after the runs (see criteria-dev.md change log). Without it, all four V3 runs would fail C2. It affects baseline and skill equally.

## 3. Costs of the skill (means over 10 runs each)
Minutes 2.8-3.69; input tokens 325k-556k; output tokens 4.9k-8.2k; source files changed 9.8-12.5. Routing worked in 10/10 runs.

## 4. Frictions
1. V5-skill-r2 stopped to ask an access-decision question, citing the skill. A safe default existed.
2. V2: skill runs replaced a provider-managed phone OTP (Supabase) with custom Twilio Verify code, more files and surface. Baseline's delegation was graded "delegated", not fail, which is generous to the baseline.
3. Some skill runs bumped existing dependencies unasked.
4. Every skill run created or edited SECURITY.md.

## 5. Tuning candidates (use V1-V5 only; Phase 3 prompts stay untouched)
a. Accept explicitly configured provider limits, state them, and do not replace working managed auth.
b. Decide and note assumptions instead of stopping to ask when a safe default exists.
c. No dependency upgrades unless required.

## 6. Caveats
n=2 per cell; one grader; static review; the skill was tuned on prompts of the same kind, so these results are development evidence, not the result. Phase 3 is the test.
