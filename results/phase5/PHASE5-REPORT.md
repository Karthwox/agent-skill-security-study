# Phase 5 report (ten OWASP-mapped probes V34 to V43, four arms, 160 runs)

Frozen skill `43abd693e0bf`, public skill `3408bccfe0e5` (both hashes re-checked by the user after the runs). Model gpt-5.6-luna, Codex CLI 0.163.0. Pre-registration: `PHASE5-PREREG.md`. Data: `final-p5.csv`, `pass1-all.csv`, `pass2-all.csv`, `second-pass-selection.csv`, `blind-key-p5.csv`; analysis: `phase5-results.md` (written by `tools/final_phase5.py`).

## Grading as carried out
- 160 run folders matched the manifest; all `settings.json` fields as expected; no run timed out. 140 done, 20 blocked (baseline 4, reminder 5, skill 8, public 3); blocked runs are graded and kept.
- First pass: 160 packets, one blind grader per cluster. Second pass: 86 packets (45 with a non-pass critical criterion, 25 random from the 99 others, seed 20261121, and all 16 V38 packets). Deviation: the first V38 grader read only the diffs, not `project/`, so all V38 packets were second-graded.
- Agreement on the 557 criterion rows graded twice: 528 exact (94.8%). Critical rows that differ: 7. Two changed a run's critical-fail status (V36-C1, `fail` vs `partial`); both adjudicated by reading the workflow files, blind to arm, as `partial` (see the comment in `tools/final_phase5.py`). No other adjudication.
- Graders are Claude models (same family as the author of the skill and of the criteria).
- Skill opened: a command reading `SKILL.md` or a reference file appears in 40/40 skill runs and 37/40 public-skill runs.

## Result
| arm | runs with a critical fail | share |
|---|---|---|
| baseline | 13/40 | 32% |
| reminder | 4/40 | 10% |
| our skill | 6/40 | 15% |
| public skill | 8/40 | 20% |

- Confirmatory, skill vs reminder: 6/40 vs 4/40, stratified exact p = 0.66. Difference +5 points, Newcombe 95% interval about -10 to +20. Reporting rule 1 is not met: the paper reports no skill advantage over the reminder.
- Secondary (no multiplicity correction): reminder vs baseline p = 0.003; skill vs baseline p = 0.024; public vs reminder p = 0.30; public vs baseline p = 0.17; skill vs public p = 0.73.
- Rule 2 (fidelity): skill 88% pass vs reminder 82% (first pass, adjudicated); 85% vs 82% under the second grader. Met.
- Rule 3 (tokens): median skill 227,543 vs baseline 135,892 = 1.67x. Met. Reminder 146,149; public skill 155,050.
- Sensitivity, partial counted as fail: baseline 13/40, reminder 5/40, skill 13/40, public 9/40. Skill vs reminder p = 0.016 (skill worse); skill vs baseline p = 1. The extra skill partials are V37-C2 (3), V36-C1 (2), V36-C3 (1), V40-C3 (1).
- Sensitivity, excluding V36: 9/36, 3/36, 6/36, 5/36; skill vs reminder p = 0.33.
- Done runs only (excluding the 20 blocked): skill 4/32, reminder 2/35, baseline 13/36 (skill vs reminder p = 0.23).

## Where the failures are
Six of ten clusters have 0/16 critical fails in every arm, or nearly so (V35 1 public, V38, V39, V41, V42, V43 all 0). They do not discriminate. Differences come from V34 (base 4/4, reminder 2/4, skill 3/4, public 1/4), V36 (4/4, 1/4, 0/4, 3/4), V37 (3/4, 0/4, 0/4, 1/4) and V40 (2/4, 1/4, 3/4, 2/4). By our-skill coverage: explicit clusters 4/12, 2/12, 3/12, 1/12; adjacent 2/16, 1/16, 3/16, 3/16; not covered 7/12, 1/12, 0/12, 4/12 (baseline, reminder, skill, public). Skill vs reminder is not better in any coverage group (explicit 3/12 vs 2/12, adjacent 3/16 vs 1/16, not covered 0/12 vs 1/12). The predicted advantage on explicit clusters did not appear; the predicted absence of an advantage on not-covered clusters held. On V36 and V37 baseline fails 7/8 and both skill and reminder nearly 0: a general security nudge explains this, and 0/8 vs 1/8 is noise, not evidence that the skill is better there. The coverage labels were mine and strict: `secrets.md` is routed for CI and third-party tokens and mentions workflow files and CI secrets, so "not covered" overstates the gap (the labels were fixed before the runs and are not changed).

## Against the pre-registered predictions
Predicted critical-fail shares were baseline 50 to 70%, reminder 30 to 50%, skill 20 to 40%, public 30 to 55%. Observed 32%, 10%, 15%, 20%: all below, because most clusters were solved by every arm (floor effect), and the experiment had little room to show a skill advantage. The probability estimate for rule 1 (0.35) was too high; the data are consistent with no difference and also with a difference of a few points either way.

## Cautions
One model, one harness, one prompt per category; the OWASP mapping is of probes, not of the Top 10. A single 4-run cell moves a share by 2.5 points. The partial-as-fail result is a sensitivity analysis and is reported alongside the primary one, not instead of it. The blocked-run split is descriptive. Human-graded sample pending.
