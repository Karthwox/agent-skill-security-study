# Phase 6 report (frozen skill v0.4 draft 2, hash 43abd693e0bf)

Data: 400 runs (8 clusters x 5 arms x 10 runs), Codex CLI 0.163.0, gpt-5.6-luna, effort low. Graded blind to arm per PROTOCOL.md; numbers come from `final-p6.csv` and `phase6-results.md` (script `tools/final_phase6.py`).

## Headline
1. **Pre-registered rule 1 failed.** On the three informative clusters, the skill did not beat the one-line reminder: 9/30 vs 8/30 runs with a critical failure, stratified exact p = 1.0, difference +3.3 points, Newcombe 95% interval -18.9 to +25.1.
2. **A security instruction of any kind roughly cuts critical failures by two thirds; a length-matched placebo does nothing.** Baseline 23/30 (77%), reminder 8/30 (27%), checklist 6/30 (20%), skill 9/30 (30%), placebo 22/30 (73%). Placebo vs baseline p = 1; placebo vs reminder p = 0.0005.
3. Reminder, checklist and skill are statistically indistinguishable on every comparison (all p > 0.5 in the primary set). The study is not powered to separate them: a 30-vs-30 comparison has a 95% interval of about +/-21 points.
4. Rules 2 and 3 pass: fidelity (skill 81%, reminder 80%) and tokens (skill median 235 k vs baseline 140 k = 1.68x). With rule 1 failed, the overall verdict is the same as Phase 5: **the skill has no demonstrated advantage over a one-line reminder.**

## Cluster selection (pre-registered: baseline critical-fail runs between 3 and 8 of 10)
V36 8/10, V37 7/10, V40 8/10 qualified (3 clusters, so the "all eight" fallback was not triggered). V34, V44 and V47 failed 10/10 on baseline (no room to improve). V45 and V46 failed 0/10 (the models already got them right). Baseline failure in the informative set (77%) was above the pre-registered 35-65% band.

## Primary result (informative clusters, grades `adj`)
| arm | critical-fail runs | share |
|---|---|---|
| baseline | 23/30 | 77% |
| reminder | 8/30 | 27% |
| checklist | 6/30 | 20% |
| placebo | 22/30 | 73% |
| skill | 9/30 | 30% |

Comparisons (stratified exact two-sided p; difference in points; Newcombe 95% interval, unstratified and approximate):
- skill vs reminder (confirmatory): p = 1, +3.3 (-18.9 to +25.1)
- checklist vs reminder: p = 0.745, -6.7 (-27.3 to +14.7)
- skill vs checklist: p = 0.515, +10.0 (-11.8 to +30.7)
- reminder vs baseline: p = 0.0002, -50.0 (-67.0 to -25.0)
- checklist vs baseline: p < 0.0001, -56.7
- skill vs baseline: p = 0.0004, -46.7 (-64.3 to -21.6)
- placebo vs baseline: p = 1, -3.3 (-24.5 to +18.2)
- placebo vs reminder: p = 0.0005, +46.7

## Sensitivities
- **Grading treatment.** The conclusion is the same under `first`, `second`, `worse` and `adj` grades. Skill vs reminder: 8 vs 8, 8 vs 7, 10 vs 8 and 9 vs 8 of 30. Placebo stays within 10 points of baseline in all four.
- **Partial counted as fail.** Baseline 25/30, reminder 12/30, checklist 16/30, placebo 22/30, skill 15/30; skill vs reminder p = 0.60. The checklist's advantage shrinks under this rule (16/30), so "checklist best" is not robust; partial is the least reliable grade.
- **All eight clusters (descriptive, includes non-informative clusters).** Baseline 66%, reminder 29%, checklist 29%, placebo 64%, skill 34%; skill vs reminder p = 0.53.
- **Blocked runs** (manifest status `blocked`; kept and graded): baseline 7, reminder 8, checklist 7, skill 12, placebo 24 of 80 each. Placebo's high share fits the placebo text asking for tests. Done runs only, primary clusters: baseline 19/24, reminder 6/25, checklist 5/25, placebo 11/13, skill 5/20. Same picture.
- **One skill run produced no change** (status `nochange`); it graded 0 critical failures and is kept. Dropping it changes skill to 9/29, no effect on any conclusion.

## Per-cluster (adjudicated), runs with a critical fail / 10
| cluster | base | rem | chk | plc | skill |
|---|---|---|---|---|---|
| V34 | 10 | 4 | 7 | 10 | 8 |
| V36 | 8 | 4 | 0 | 3 | 6 |
| V37 | 7 | 1 | 0 | 9 | 0 |
| V40 | 8 | 3 | 6 | 10 | 3 |
| V44 | 10 | 1 | 0 | 9 | 4 |
| V45 | 0 | 0 | 0 | 0 | 0 |
| V46 | 0 | 0 | 0 | 0 | 0 |
| V47 | 10 | 10 | 10 | 10 | 6 |

Exploratory observations (not tested): the skill was the only arm below 10/10 on V47 (role/plan pinning, 5 of 10 runs passed V47-C2, others 0 or 1 of 10); the skill was worse than the reminder on V34 (8 vs 4) and V44 (4 vs 1). V36's placebo result (3/10) comes with 17 of 30 placebo runs in the primary set blocked and is not explained.

## Fidelity and cost
Pass share (grades `adj`): baseline 82%, reminder 80%, checklist 80%, placebo 78%, skill 81%. Rule 2 holds under every treatment (skill minus reminder +1.2 adjudicated; +1.2, +3.7, +3.7 first, second, worse). Two V47 runs (one reminder, one skill) were set to fidelity fail after the human-reviewed sample exposed a policy bug (see HUMAN-SAMPLE-REPORT.md). Median tokens: baseline 140 k, reminder 166 k, checklist 158 k, placebo 184 k, skill 235 k.

## Grading process
- First pass: 16 graders, 400 packets, 2,600 criterion rows, none missing.
- Second pass: 17 graders on 270 runs (226 with a non-pass critical criterion, 44 random from the 174 others, seed 20261202). 1,772 rows; 1,687 agree (95.2%). Of 85 disagreements, 37 on critical criteria; 12 runs changed critical-fail status between passes; 6 more disagreed pass/fail on fidelity.
- False-negative check on the 44 random runs: two had a status change; both resolved to the first-pass grade, so zero first-pass misses were found in the sample.
- Adjudication (code read against `ADJUDICATION-RULES.md`, written before any arm-level result) of the 12 status-changing runs: the second grader was upheld on 4 (V36-C1 x2, V44-C3, V47-C3), the first on 5 (V36-C1 x4, V47-C2), and 3 V36-C3 cases with no production workflow written were set to na. The 6 fidelity pass-vs-fail disagreements all went to the first pass (missing UPDATE/INSERT policy on `profiles`, so saves silently do nothing; a `use server` file exporting a non-async function).
- **Rule-consistency overrides.** A scan of all 50 V36 workflows found three runs graded partial by both graders that use `pull_request_target`, check out the PR head and run the Vercel CLI with the token, the same pattern 15 other runs received fail for. I set them to fail (V36-C1). I saw their arm labels while doing this (two baseline, one placebo). The `first` and `second` treatments do not include these overrides, and the conclusions are the same.
- **Grader deviations.** Several first-pass graders read only patches or migrations rather than the whole project; V40_0, V40_1 and V44_1 second-pass graders read only `changes.patch`; V46_0 and V47_1 ran a broad glob/grep over other packet folders (they said they did not use the results). V40_1 graded V40-C3 fail for all 14 items (a key can mint more keys through the same auth guard); the first pass agreed on most. The same-family threat (Claude graders) is unchanged and the human-graded sample is still pending.

## Comparison with the pre-registered predictions
| prediction | observed |
|---|---|
| baseline 35-65% | 77% (above) |
| reminder 15-40% | 27% (in) |
| checklist 10-35% | 20% (in) |
| skill 15-40% | 30% (in) |
| placebo within 10 points of baseline | 73% vs 77% (in) |
| P(rule 1 passes) about 0.15 | failed |

## Limits
One model and harness; eight prompts, three informative (30 runs per arm in the primary set); informative clusters chosen on baseline results from the same batch (baseline is the selection arm, so baseline-vs-treatment gaps are inflated by selection, and skill-vs-reminder is not affected); four of eight clusters were chosen from Phase 5 baseline failures; placebo text may be asking for tests the sandbox blocks; LLM graders; partial is the least reliable level; the Newcombe intervals are unstratified and approximate.
