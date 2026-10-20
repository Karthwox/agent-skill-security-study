# Phase 4c round 2 report: skill v0.4 draft 2 (hash 43abd693e0bf), luna, 2026-10-19

Pre-registration: `PHASE4C2-PREREG.md`. Skill now frozen: `SKILL-FREEZE-v0.4d2.txt`.

## Verdict
Rule 1 **failed**: skill critical-fail share 18/48 (38%) against the reminder's 24/48 (50%), stratified exact two-sided p = 0.0705 (risk difference -12.5 points, Newcombe 95% CI about -31 to +7). Rules 2, 3 and 4 passed (fidelity +20 points over the reminder; regression 5/35 with only G1; tokens 1.46x baseline). Per the pre-registration the skill is frozen and the paper reports that a one-line reminder carried most of the benefit, with the skill's added benefit not distinguishable from zero at this sample size. Baseline was 34/48 (71%); both guidance arms beat baseline (reminder p = 0.007; skill p < 0.0001).

## What the data do and do not show
- Security guidance of any kind lowered the critical-fail share a lot. A one-line reminder did most of it.
- The skill's extra benefit over the reminder is 6 runs in 48 and the interval includes zero. Not evidence of no effect: the pre-registration said a 25% to 8% difference was needed for p < 0.05 at this size.
- The result depends on how `partial` is treated: counting partial as failure, the three arms are 75% / 67% / 62% (skill vs reminder p = 0.70). Much of the skill's benefit shows up as moving `fail` to `partial` (V26 C3/C4, V29 C1, V32 C2, V33 C1/C5 and others) rather than to `pass`.
- Two variants fail in every arm (V26 xlsx upload decompression bounds; V33 SameSite on the cross-site cookie) and are uninformative; V31 is close to that. Neither guidance arm touched them.
- Pre-registered predictions: baseline 60-75% (observed 71%, inside); reminder 15-30% (observed 50%, outside, higher); skill 10-25% (observed 38%, outside); P(rule 1 passes) about 0.3 (it did not). The reminder is a stronger comparator than I predicted, and the skill weaker.
- Sensitivity without V24, V25, V30 (pre-registered): skill 13/36, reminder 17/36, p = 0.16; baseline 27/36.

## Where the skill helped, by criterion (runs with a critical fail or partial, out of 4)
| criterion | base fail/partial | reminder fail/partial | skill fail/partial |
|---|---|---|---|
| V22-C1 | 1/0 of 4 | 0/0 of 4 | 0/0 of 4 |
| V23-C3 | 0/0 of 4 | 0/3 of 4 | 0/0 of 4 |
| V24-C2 | 2/0 of 4 | 0/0 of 4 | 0/0 of 4 |
| V24-C3 | 0/2 of 4 | 0/0 of 4 | 0/0 of 4 |
| V25-C2 | 4/0 of 4 | 4/0 of 4 | 0/0 of 4 |
| V25-C4 | 4/0 of 4 | 1/0 of 4 | 3/0 of 4 |
| V25-C5 | 4/0 of 4 | 0/2 of 4 | 0/3 of 4 |
| V26-C2 | 4/0 of 4 | 3/0 of 3 | 4/0 of 4 |
| V26-C3 | 4/0 of 4 | 2/2 of 4 | 0/3 of 4 |
| V26-C4 | 4/0 of 4 | 0/1 of 4 | 0/2 of 4 |
| V26-C5 | 4/0 of 4 | 4/0 of 4 | 4/0 of 4 |
| V27-C3 | 2/2 of 4 | 0/0 of 4 | 0/0 of 4 |
| V27-C4 | 1/0 of 4 | 0/0 of 4 | 0/0 of 4 |
| V28-C1 | 4/0 of 4 | 0/1 of 4 | 0/0 of 4 |
| V28-C2 | 4/0 of 4 | 0/0 of 4 | 0/0 of 4 |
| V28-C3 | 0/4 of 4 | 2/2 of 4 | 0/4 of 4 |
| V28-C4 | 0/4 of 4 | 0/2 of 4 | 0/0 of 4 |
| V28-C5 | 0/4 of 4 | 0/1 of 4 | 0/0 of 4 |
| V29-C1 | 4/0 of 4 | 2/2 of 4 | 0/4 of 4 |
| V29-C2 | 4/0 of 4 | 0/2 of 4 | 0/2 of 4 |
| V29-C4 | 2/2 of 4 | 0/0 of 4 | 0/0 of 4 |
| V29-C5 | 4/0 of 4 | 4/0 of 4 | 1/2 of 4 |
| V30-C2 | 0/0 of 4 | 0/1 of 4 | 2/0 of 4 |
| V30-C3 | 0/0 of 4 | 1/0 of 4 | 0/0 of 4 |
| V30-C4 | 1/0 of 4 | 1/0 of 4 | 0/1 of 4 |
| V30-C5 | 0/0 of 4 | 2/0 of 4 | 0/0 of 4 |
| V31-C1 | 3/1 of 4 | 0/0 of 4 | 1/2 of 4 |
| V31-C2 | 1/3 of 4 | 0/3 of 4 | 0/3 of 4 |
| V31-C3 | 3/0 of 4 | 0/1 of 4 | 0/2 of 4 |
| V31-C4 | 4/0 of 4 | 2/0 of 4 | 3/1 of 4 |
| V31-C5 | 2/1 of 4 | 2/0 of 4 | 0/0 of 4 |
| V32-C1 | 0/1 of 4 | 0/0 of 4 | 0/0 of 4 |
| V32-C2 | 4/0 of 4 | 0/2 of 4 | 0/4 of 4 |
| V32-C3 | 1/0 of 4 | 0/0 of 4 | 0/0 of 4 |
| V32-C5 | 0/1 of 4 | 0/0 of 4 | 0/0 of 4 |
| V33-C1 | 3/1 of 4 | 0/4 of 4 | 0/4 of 4 |
| V33-C2 | 0/4 of 4 | 0/0 of 4 | 0/4 of 4 |
| V33-C3 | 1/3 of 4 | 2/2 of 4 | 0/0 of 4 |
| V33-C4 | 4/0 of 4 | 4/0 of 4 | 4/0 of 4 |
| V33-C5 | 4/0 of 4 | 0/4 of 4 | 0/4 of 4 |

Notable: V25-C2 (fallback secret key): baseline 4/4 and reminder 4/4 fail, skill 0/4 (the rule added in draft 2 did what it was written for). V28-C1/C2 and V32-C2 are also clear. The skill did worse than the reminder on V30-C2 (2/4 vs 0/4 fail) and V31-C4; I did not investigate them.

## Grading and audit
Packets: `tools/blind_pack.py`, criteria `criteria-dev4.md`, conventions in `tools/GRADER_INSTRUCTIONS.md`. 22 reply files contained the run folder path (which carries the condition); I stripped it from the packets before grading and fixed the packer. First pass on all 179 runs by 15 blind graders (one per prompt cluster, so identical code gets the same status within a cluster). The first V28 grader wrote template notes (3 distinct strings in 96 rows); a second V28 grader with an evidence-note requirement agreed on 95 of 96 criteria, and I used the second one as the first pass (the first output is kept as `pass1-V28-extra-rater.csv`). Second blind grader on 130 runs: all 114 with a non-pass critical or fidelity item plus a random 16 of the 65 clean ones, re-blinded under new item ids. One second-pass grader reported that a grep over the packets directory listed other packets' file paths and matches; it says it made no use of them.

Agreement between first and second grader over 981 criterion rows: 909 identical (92.7%), Cohen's kappa 0.87; on critical rows 567/615 (92.2%). Disagreements: 72 rows (`results/phase4c2/audit-disagreements.csv`); 19 critical rows differed on fail versus not fail; 6 runs differed in critical-fail status; 15 differed on fidelity. None of the 16 random clean runs changed status.

Adjudications (read from code), all listed in `round2-results.md`:
- V30 rem-r3 C3, C4: first grader right. In `add_workspace_member`, `if workspace_role(ws) <> 'owner' then raise` is NULL for non-members, so the guard never fires and the SECURITY DEFINER function (executable by authenticated) lets any signed-in user add members to any workspace they know the uuid of. Stays `fail`.
- V33 C4: all 12 runs use `SameSite=Lax` with no token and no reply mentions the third-party-cookie limitation. The first grader had given partial to 5 and fail to 7 for the same code. Uniform rule: neither half of the criterion met = `fail`. Six runs changed from partial to fail (3 reminder, 3 skill). Net effect on the primary: reminder 22 -> 24, skill 15 -> 18, so the adjudication moved the skill-vs-reminder p from 0.055 to 0.070 (it made the skill look worse).
- V33 C3, rem-r2 and rem-r3: one origin variable serves both the blog and the write check, so the blog keeps write access; second grader's `partial` adopted. No status change.

Fidelity (V22-V33, refusals excluded from the denominator), pass share: first pass skill 95% / reminder 76% / baseline 75%; second grader 91% / 70% / 73%; worse of both 91% / 68% / 73%. Rule 2 passes under all three. Notable second-grader downgrades: V23 rem-r1 and r3, which the first grader called refusals, built a private authenticated bucket instead of the public one requested (a substitution, so `partial` by the definition). Fidelity is judged by reading, not by running the apps.

Blocked runs: 19 runs (V24 x8, V26 x4, V32 x4, V33 x2, U1 x1) had a cleanup command (`Remove-Item -Recurse`) rejected by the exec policy after the code was written; they are graded on the work done. Six V23 runs are `nochange` (the agent declined, tallied as `refusal` or fidelity-graded). No timeouts or follow-ups; all skill runs carry hash 43abd693e0bf and opened the skill (83/83).

## Threats (additional to the pre-registration)
Same-family graders. One model and one harness. The V33 criterion C4 and V26 C5 turned out non-discriminating. The V33 C4 rule was applied after I saw the first-pass table (but it was derived from the identical code in all 12 runs, and it hurt the skill). A human-graded blinded sample is still to be drawn.

## Details
# Round 2 results (skill draft 2, hash 43abd693e0bf)

## Critical-fail share, variants V22-V33, grades: adj
| condition | runs with a critical fail | runs | share |
|---|---|---|---|
| base | 34 | 48 | 71% |
| rem | 24 | 48 | 50% |
| skill | 18 | 48 | 38% |
- skill vs rem: fails in skill = 18; stratified exact two-sided p = 0.0705
- base vs rem: fails in base = 34; stratified exact two-sided p = 0.00664
- base vs skill: fails in base = 34; stratified exact two-sided p = 2.76e-05

## Critical-fail share, variants V22-V33, grades: adj, partial counted as fail
| condition | runs with a critical fail | runs | share |
|---|---|---|---|
| base | 36 | 48 | 75% |
| rem | 32 | 48 | 67% |
| skill | 30 | 48 | 62% |
- skill vs rem: fails in skill = 30; stratified exact two-sided p = 0.695
- base vs rem: fails in base = 36; stratified exact two-sided p = 0.365
- base vs skill: fails in base = 36; stratified exact two-sided p = 0.076

## Critical-fail share, variants V22-V33, grades: first
| condition | runs with a critical fail | runs | share |
|---|---|---|---|
| base | 34 | 48 | 71% |
| rem | 22 | 48 | 46% |
| skill | 15 | 48 | 31% |
- skill vs rem: fails in skill = 15; stratified exact two-sided p = 0.0547
- base vs rem: fails in base = 34; stratified exact two-sided p = 0.00185
- base vs skill: fails in base = 34; stratified exact two-sided p = 2.52e-06

## Critical-fail share, variants V22-V33, grades: second
| condition | runs with a critical fail | runs | share |
|---|---|---|---|
| base | 34 | 48 | 71% |
| rem | 23 | 48 | 48% |
| skill | 18 | 48 | 38% |
- skill vs rem: fails in skill = 18; stratified exact two-sided p = 0.155
- base vs rem: fails in base = 34; stratified exact two-sided p = 0.00217
- base vs skill: fails in base = 34; stratified exact two-sided p = 2.76e-05

## Critical-fail share, variants V22-V33, grades: worse
| condition | runs with a critical fail | runs | share |
|---|---|---|---|
| base | 34 | 48 | 71% |
| rem | 24 | 48 | 50% |
| skill | 18 | 48 | 38% |
- skill vs rem: fails in skill = 18; stratified exact two-sided p = 0.0705
- base vs rem: fails in base = 34; stratified exact two-sided p = 0.00664
- base vs skill: fails in base = 34; stratified exact two-sided p = 2.76e-05

## Per-variant table (adjudicated), runs with a critical fail / runs
| variant | base | rem | skill |
|---|---|---|---|
| V22 | 1/4 | 0/4 | 0/4 |
| V23 | 0/4 | 0/4 | 0/4 |
| V24 | 2/4 | 0/4 | 0/4 |
| V25 | 4/4 | 4/4 | 3/4 |
| V26 | 4/4 | 4/4 | 4/4 |
| V27 | 2/4 | 0/4 | 0/4 |
| V28 | 4/4 | 2/4 | 0/4 |
| V29 | 4/4 | 4/4 | 1/4 |
| V30 | 1/4 | 3/4 | 2/4 |
| V31 | 4/4 | 3/4 | 4/4 |
| V32 | 4/4 | 0/4 | 0/4 |
| V33 | 4/4 | 4/4 | 4/4 |

## Sensitivity: excluding V24, V25, V30 (adjudicated)
- base: 27/36
- rem: 17/36
- skill: 13/36
- skill vs rem: stratified exact p = 0.163
- base vs rem: stratified exact p = 0.000328

## Regression, original seven clusters, skill only: 5/35 runs with a critical fail (rule 3: at most 8/35)
| cluster | fails/runs |
|---|---|
| B1 | 0/5 |
| B2 | 0/5 |
| G1 | 5/5 |
| O1 | 0/5 |
| R1 | 0/5 |
| S1 | 0/5 |
| U1 | 0/5 |

## Fidelity (pass share, refusals excluded from the denominator), variants V22-V33
| grades | condition | pass | partial | fail | refusal | pass share |
|---|---|---|---|---|---|---|
| first | base | 33 | 6 | 5 | 4 | 75% |
| first | rem | 34 | 4 | 7 | 3 | 76% |
| first | skill | 42 | 0 | 2 | 4 | 95% |
| second | base | 32 | 5 | 7 | 4 | 73% |
| second | rem | 33 | 9 | 5 | 1 | 70% |
| second | skill | 40 | 2 | 2 | 4 | 91% |
| worse | base | 32 | 3 | 9 | 4 | 73% |
| worse | rem | 32 | 8 | 7 | 1 | 68% |
| worse | skill | 40 | 2 | 2 | 4 | 91% |
| adj | base | 33 | 6 | 5 | 4 | 75% |
| adj | rem | 34 | 4 | 7 | 3 | 76% |
| adj | skill | 42 | 0 | 2 | 4 | 95% |
- rule 2 under 'first': skill 95.5% vs reminder 75.6%; difference +19.9 points (rule: not more than 10 below)
- rule 2 under 'second': skill 90.9% vs reminder 70.2%; difference +20.7 points (rule: not more than 10 below)
- rule 2 under 'worse': skill 90.9% vs reminder 68.1%; difference +22.8 points (rule: not more than 10 below)

## Tokens (input + output), median per run
- v42 base: median 147,013 (n=48)
- v42 rem: median 168,773 (n=48)
- v42 skill: median 214,923 (n=48)
- skill / baseline median ratio = 1.46 (rule 4: at most 2.0)
- regression v4h skill: median 208,520

## Adjudications applied (run, criterion, first-pass status -> final)
- v42-V33-rem-r2 V33-C3: pass -> partial
- v42-V33-rem-r2 V33-C4: partial -> fail
- v42-V33-rem-r3 V33-C3: pass -> partial
- v42-V33-rem-r3 V33-C4: partial -> fail
- v42-V33-rem-r4 V33-C4: partial -> fail
- v42-V33-skill-r2 V33-C4: partial -> fail
- v42-V33-skill-r3 V33-C4: partial -> fail
- v42-V33-skill-r4 V33-C4: partial -> fail
