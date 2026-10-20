# Dependency changes, Phase 3 (sol) and Phase 4a (luna): what the package.json diffs actually were

Correction to my earlier wording ("the reminder churned dependency versions"): the version changes are not all churn.

## The starter app already ships with an audit finding
The fixture `notes-app-healthy` (next ^15, @supabase/ssr ^0.5.2, ...) gives `npm audit` = 2 vulnerabilities (1 moderate, 1 high): postcss <=8.5.22 (via next), advisories GHSA-qx2v-qp2m-jg93, GHSA-6g55-p6wh-862q, GHSA-fxqj-rqcc-2cmp, GHSA-r28c-9q8g-f849. Reproduced 2026-10-18 with a package-lock-only install; advisories are time-dependent, and the Phase 3 sessions printed the same count. The only non-breaking fix is an `overrides` entry for postcss (a `npm audit fix --force` would move next to 16, a breaking change). I did not run the same audit at the exact Phase 3 date.

## Phase 3 (sol), 35 runs per arm
| | baseline | reminder | skill |
|---|---|---|---|
| package.json changed | 11 | 35 | 18 |
| `overrides` for postcss added (clears the audit finding) | 0 | 33 | 0 |
| existing dependency version changed (earlier count) | 2 | 29 | 17 |
Of the version changes:
- reminder: 29x @supabase/ssr ^0.5.2 -> ^0.8.0 / ^0.12.7 (a 0.x minor, which is a breaking range). In the one session I read, the agent ran `npm view @supabase/ssr version` and installed the latest, with no stated reason. Whether it was needed is not established.
- skill: 10x @supabase/supabase-js ^2.45.0 -> 2.45.0 (a pin: the caret removed, no upgrade), 4x ^2.45.0 -> 2.50.0, 1x ssr bump, 3x react-dom/sharp in U1.
- baseline: 2x the same exact-pin of supabase-js.

## What this changes
- The reminder arm cleared the known postcss finding in 33 of 35 runs; the skill and baseline arms did not (0 of 35). This is a security benefit of the reminder that none of our critical criteria measure.
- The skill's rule "no unrequested dependency upgrades" probably explains why it left the finding open. That is a trade-off to consider for v0.4: keep the rule, but allow a non-breaking fix (override or patch bump) for a finding that `npm audit` reports, or at least report it in SECURITY.md.
- The @supabase/ssr bump in 29 reminder runs is unexplained and is a breaking-range upgrade; treat it as unjustified churn until the diffs say otherwise.

## Phase 4a (luna)
package.json changed in 4 skill runs and 0 in the other arms; the parser found no existing-dependency version changes in any luna run, and no postcss override was added in any arm. So luna did not clear the audit finding in any arm.

Files: deps-version-changes.csv (per run and package).
