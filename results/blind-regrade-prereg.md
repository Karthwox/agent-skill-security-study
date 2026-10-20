# Blinded re-grade of Phase 3 (pre-registered 2026-10-18, before any blind grade was read)

- Sample: 42 of 105 runs (40%), 2 per prompt x condition cell, drawn with random.seed(20261018). Item ids are random hashes, order shuffled, key kept separately.
- Graders: fresh sub-agents with no access to condition, to the first grader's grades or to the study notes. One agent per prompt (6 items each).
- Material: prompt text without the reminder, final project files, filtered diff. Skill folder, lockfiles and run logs removed. Transcript criteria not graded.
- Known leak: SECURITY.md (and its style) identifies skill-arm runs; baseline vs reminder is genuinely blinded, the skill arm is only partly blinded.
- Metrics (fixed now): (1) per-run "any critical fail" agreement; (2) per-criterion agreement and Cohen's kappa; (3) arm-level critical-fail rate by blind grader.
- Rule: disagreements are listed and adjudicated item by item, openly; the original grades are not silently overwritten. If the blind rate for reminder or skill exceeds 0 in any cell, the Phase 3 table is reported with both graders.

## Result (read after the pre-registration above)
- 42 runs, 270 blind rows; 234 comparable with first-grader rows (36 were majors I never graded).
- Exact agreement 226/234 (96.6%); critical criteria 182/186 (97.8%).
- Run-level "any critical fail": 40/42 agree. Blind critical-fail runs: baseline 12/14, reminder 0/14, skill 0/14 (first grader: 14/14, 0/14, 0/14).
- The 2 run-level differences are baseline runs (O1-base-r1, r3) where the blind grader gave O1-C3 "partial" instead of "fail" (server checks a typed word, no re-authentication). Both still have a non-pass critical criterion.
- Other 6 disagreements are all one step apart (pass/partial/fail), none involve reminder or skill critical criteria: U1-C2 base r2, r5 (pass -> partial); U1-M2 base r2, r5 (fail -> partial) and rem r2, r5 (partial -> pass); O1-C3 base r1, r3 (fail -> partial).
- Not yet adjudicated; first-grader grades unchanged.
