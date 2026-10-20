# Phase 4a pre-registration (model and scope confirmed by the user 2026-10-18; manifest generated; no runs started)

Written 2026-10-18 before any run on the new model. Nothing below may change after the first run except through a dated, disclosed amendment applied forward only.

## 1. Question
Phase 3 (gpt-6.1-sol) found baseline 35/35 runs with a critical failure, reminder 0/35, skill 0/35. Does the skill beat the one-line reminder on a weaker model, where the reminder may not be enough?

## 2. Model and harness
- Harness: Codex CLI 0.163.0 (same as Phase 3), `codex exec`, sandbox workspace-write, approval never, network on, `--ignore-user-config`, `--ignore-rules`, effort low.
- Model: **`gpt-5.6-luna`** (string supplied by the user). Series id `S2-luna`. The first run doubles as a check that `codex exec -m gpt-5.6-luna` works; if it errors, nothing is recorded as a result.
- Everything else identical to Phase 3 (prompts, criteria, reminder wording, stop rule, follow-up rule, fresh folder per run).

## 3. Skill
v0.3, frozen, hash `414759660eb6`. Hash checked before the first run and after the last. Any mismatch voids the series. No skill edits in response to these results.

## 4. Design
7 prompts (B1, B2, S1, U1, R1, G1, O1) x 3 conditions (baseline, reminder, skill) x 5 runs = 105 runs, run as ONE interleaved randomised manifest (`manifest-luna.csv`, seed 20261025, run ids `lun-<prompt>-<cond>-r<n>`), same circuit-breaker settings. Unlike Phase 3 there is no part A / part B split, so conditions share sessions and drift cannot masquerade as an arm effect. The only code change is adding phase `luna` to `make_manifest.py` (logged in PROTOCOL.md).
Baseline is rerun on this model: Phase 3 baselines say nothing about luna.

## 5. Outcomes (fixed now)
Primary: share of runs with at least one critical failure, per condition, pooled and stratified by prompt.
Primary comparison: **skill vs reminder** (this is the question Phase 3 left open). Secondary: baseline vs reminder, baseline vs skill.
Test: stratified exact permutation test, two-sided, strata = prompts. Report exact p, per-prompt tables and the raw counts.
Secondary outcomes: major-criteria pass rates; **feature fidelity** (does the requested feature work, pass/partial/fail, graded for every run); files changed, minutes, tokens, package.json changes, SECURITY.md written, new required secrets, features shipped disabled.
Because a weaker model may fail to build the feature, critical-fail rates are also reported **conditional on feature fidelity not being fail**. A run that builds nothing is not counted as a safe run in the headline.
Descriptive only: comparison of sol (Phase 3) and luna (Phase 4a). The models differ in more than strength and runs are separate series, so no pooled test.

## 6. Grading (changed from Phase 3, fixed now)
- Primary grading is **blinded**: shuffled item ids, no condition, no run names, skill folder and lockfiles stripped, one fresh grader per prompt, same criteria text and the same disclosed judgement calls as Phase 3 (R1-C3, R1-C4, B1-M3).
- Known leak: SECURITY.md identifies most skill-arm runs. Disclosed in the report.
- A second grader (me, unblinded after the blind pass) audits a random 30% plus every run where any critical criterion is partial or the two disagree. Disagreements are listed and adjudicated openly; blind grades are never overwritten silently.
- Majors G1-M1/M2, O1-M1..M3 and U1-M3 are graded this time.

## 7. Decision rules (what each outcome means; the report is written whatever happens)
- Skill critical-fail share lower than reminder (clear gap, p < 0.05): the skill adds value where the model is weaker.
- No difference again: the skill's measured value is limited to majors and process; report as such, and test harder prompts next.
- Reminder lower than skill: report it, and examine whether the skill's costs (disabled features, extra secrets, feature substitution) drive it.
- No claim of generality from one extra model.

## 8. Threats (stated in advance)
One extra model, n=5 per cell; skill written from sol failures, so luna runs are still in-sample on prompts; same model family may grade (shared blind spots); no exploit tests yet; ceiling or floor effects are possible in either direction.

## 9. Before the first run
1. Back up the Phase 3 `series.json` on the runner machine (it is overwritten by `init`), e.g. copy to `results/series-S1-default.json`.
2. `py run_study.py hash <vibe-skill>` must print 414759660eb6.
3. `py run_study.py init --series-id S2-luna --model gpt-5.6-luna --effort low --skill-dir <vibe-skill> --work-root <short path>` plus the same Windows options as Phase 3.
4. `py run_study.py run manifest-luna.csv --stop-after 2 --wait-minutes 30 --max-waits 10`.
5. Re-run the hash after the last run.
