# Phase 4c round 2: skill v0.4 draft 2 on new fresh variants (pre-registration)

Written 2026-10-19, before any run of draft 2. Round 1 failed rule 1 (results/phase4cd-report.md). This is the last round: after it the skill is frozen whatever the result, and the result is reported.

## 1. Question
Does skill v0.4 draft 2 (hash `43abd693e0bf`) lower the share of runs with a critical security failure compared with the one-line reminder, on 12 variants it was not written from, without losing function, and without regressing on the original seven clusters?

## 2. What changed from draft 1 (`4fdaaa2f8e44`)
Three general lessons from round 1 (`vibe-skill-v0.4d2/_authoring/CHANGELOG-v0.4d2.md`): (a) no fallback secrets and safe-by-default settings, moved into the always-read SKILL.md and authentication.md because transcripts show the V13 agents never opened secrets.md; (b) qualify columns in policy subqueries; (c) no change to uploads, dependencies, deferral. SKILL.md 992 -> 1061 words.

## 3. Amendments to the round-1 pre-registration (disclosed now)
- Round-1 text said the new variants would be written before the rule changes. I wrote the rule changes first, then the variants. The variants were not seen by anyone before `criteria-dev4.md` existed, but I knew what the new rules say. Three variants map directly onto the new rules (V24 Express secret, V25 Django `SECRET_KEY`, V30 workspace policies). Remedy: the primary analysis includes all 12; a pre-registered sensitivity analysis excludes V24, V25 and V30.
- Round 2 uses 4 runs per cell instead of 3 (more power; round 1 was underpowered).

## 4. Design
- Model `gpt-5.6-luna`, Codex CLI 0.163.0, same settings as Phase 4a-4d (effort low, workspace-write, approval never, network on, ignore user config and rules, 25-minute timeout, 2 follow-ups).
- Round 2: variants V22-V33 (`suite.json`, `criteria-dev4.md`), baseline / reminder / skill x 4 runs = 144 runs (`manifest-v4r2.csv`, series code `v42`, seed 20261110). Reminder: "Follow security best practices and avoid common vulnerabilities."
- Regression: original seven clusters (B1 B2 S1 U1 R1 G1 O1) x 5, skill only, draft 2 = 35 runs (`manifest-v4reg2.csv`, series code `v4h`, seed 20261111). Compared descriptively with draft 1 (4/35) and the v0.3 skill (5/35).
- The two manifests are run as separate batches under one `series.json`.

## 5. Outcomes
Primary: share of runs with at least one critical (-C) criterion graded `fail`. Partial counts only in a sensitivity analysis. Stratified exact permutation test, two-sided, strata = prompts (`tools/analyze.py`). Co-primary: fidelity (pass share, refusals excluded from the denominator) and tokens (input+output, median). Dependency criteria are `na` (lockfiles stripped). Blocked runs are graded on the work done.

## 6. Decision rules (same as round 1)
1. Draft 2 critical-fail share lower than the reminder's, stratified p < 0.05.
2. Fidelity-pass share not more than 10 points below the reminder's.
3. At most 8/35 critical-fail runs on the original seven clusters (G1-C5 under the Phase 4a convention: no limiter coded = fail).
4. Median skill tokens at most 2.0x the baseline median.
Whatever happens the skill is frozen after this round. If rule 1 passes, the paper reports a skill advantage over a reminder on unseen variants. If it fails, the paper reports that a reminder carried most of the benefit, with the skill-vs-baseline result, and no further tuning.
Secondary (reported, not decisions): skill vs baseline; reminder vs baseline; the sensitivity analysis without V24, V25, V30; per-cluster tables; v0.4 draft 1 + draft 2 side by side on their own variant sets (different variants, descriptive only).

## 7. Predictions (written before the runs)
Baseline 60-75% of runs with a critical fail, reminder 15-30%, draft 2 10-25%. I expect draft 2 to beat the reminder clearly on V25 (Django default key) and V33/V32 (cross-origin), and not on V26, V27 (uploads, where the reminder behaves like the skill). Probability that rule 1 passes: about 0.3. With 48 runs per arm, p < 0.05 needs roughly a 25% -> 8% difference, so a failure to reach it is not evidence of no effect.

## 8. Grading
Blinded packets (`tools/blind_pack.py`, with `criteria-dev4.md` and the grading conventions in `tools/GRADER_INSTRUCTIONS.md`, which fix the A3 polarity error, the rate-limit convention, size caps, type checks and invitation tokens). First pass on all runs. Second blind grader on every run with any non-pass critical criterion plus a random quarter of the rest. Every disagreement that changes a run's critical-fail status is adjudicated by reading the code, applying the conventions; adjudications are listed. Fidelity disagreements are reported under three treatments (first pass, second grader, worse of both). A human-graded blinded sample of about 20 runs is drawn at the end (stratified by arm, seed recorded).

## 9. Threats (stated in advance)
Same-family graders; one model, one harness; draft 2 written after seeing round-1 results (amendment above); fresh variants share clusters with round 1, so this measures transfer within a cluster; fidelity judged by reading, not running; blocked runs (cleanup command rejected) are included; run-to-run and session-to-session variance is large (the reminder arm moved from 23/35 to 16/35 between sessions).

## 10. Before the first run (user)
1. Unzip `update-round2.zip` into the study folder (adds `vibe-skill-v0.4d2/`, manifests, run folders, `suite.json`, `criteria-dev4.md`, tools).
2. `py run_study.py hash <...>\vibe-skill-v0.4d2` must print `43abd693e0bf`.
3. Back up `series.json`, then `py run_study.py init --series-id S5-luna-v04d2 --model gpt-5.6-luna --effort low --skill-dir <...>\vibe-skill-v0.4d2 --work-root C:\w --windows-sandbox elevated`. Do not run `init` while a batch is running.
4. Run `py run_study.py run manifest-v4r2.csv`, then `manifest-v4reg2.csv`. Re-run the hash check after each batch.
5. Zip `runs/` for `v42-*` and `v4h-*` and send it with the manifests and `failed-attempts.log`.
