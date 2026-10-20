# Human-graded sample for Phase 6: pre-registration

Written 2026-10-20 13:56 IST (08:26 UTC), before the sample was drawn and before any human grade exists. Phase 6 grades (adjudicated, `results/phase6/final-p6.csv`) are frozen.

## Purpose
Check the LLM graders against a human on a small blinded sample, so the paper can report agreement and where they differ. It cannot establish absence of bias; 20 runs are too few. It is descriptive.

## Sampling rule (fixed here)
- Pool: Phase 6 runs in clusters V34, V36, V37, V40, V44, V47 (300 runs). V45 and V46 are excluded because no run in any arm had a critical failure.
- Strata: arm (baseline, reminder, checklist, placebo, skill) x final adjudicated critical-fail status (at least one critical criterion `fail` in `final-p6.csv`, or none). Two runs per stratum, 20 in total. Every stratum has at least 7 runs.
- Draw: `random.Random(20261021)`; for each arm in the order base, rem, chk, plc, skill, and each status in the order fail, pass, sort the stratum's run ids, shuffle them, and take the first two, skipping a run if its cluster already has 5 sampled packets.
- Packets: the same blind packets used for the LLM graders (item ids are random hex, no arm, run number or condition in the name). The human receives PROMPT.txt, CRITERIA.md, changes.patch, project/ and REPLY.txt where present, and a blank grading sheet. The sample key (item -> run id, arm, LLM grades) is kept separately and not shown to the human until the sheet is returned.
- The human does not see any LLM grades, notes, or the key. SECURITY.md in skill-arm projects can reveal the arm; this is a known limit.

## What the human grades
Every row of CRITERIA.md using the same statuses as the LLM graders (pass, partial, fail, na; refusal for the fidelity row), judging from the code only. Critical (C) and fidelity (F) rows are analysed; major (M) rows are recorded but not analysed.

## Analysis (fixed here)
1. Run-level: human critical-fail yes/no against the adjudicated LLM grade; counts of agreement and disagreement, Cohen's kappa, and the direction of each disagreement by arm.
2. Criterion-level: exact agreement on critical and fidelity rows, with partial/fail and pass/partial disagreements reported separately.
3. Sensitivity: re-run the primary comparison with the human's grade in place of the LLM grade for these 20 runs; report the changed counts. The primary analysis stays as published.
4. If the human and the LLM disagree on a run, both grades are reported; no further adjudication changes the main result.
5. Extra graders (ChatGPT, Gemini, or others) are LLM graders and are reported separately from the human, with the same tables.
