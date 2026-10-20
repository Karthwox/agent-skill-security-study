# Reconciliation of the user's All_docs.zip with the working copy (2026-10-20)

92 files received. 65 byte-identical to the working copy. 22 differ, 5 had no copy.

## Differences, all explained
- 19 manifests: same run ids, order, prompts, conditions and replicate numbers as the working copy in every case. Only the status and date columns differ (the user's carry the real run outcomes; the working copy's were all `todo`). The user's versions replace the working copies. Status counts across the 18 study manifests (excluding screen and agy1): 689 done, 68 blocked (cleanup command rejected), 13 nochange, plus the Phase 5 batch in progress (142 todo at the time of upload).
- `criteria.md` (user): the early DRAFT of the unified suite ("freeze when you sign off"), with inverted wording on S1-C1, S1-C2, S1-M1 and no S1-C4. Not the frozen file. The frozen versions are `screening/criteria.md` (Phase 1, frozen 2026-10-16) and `study/criteria.md` (Phase 2 onward, with S1-C4 added 2026-10-17). Archive both frozen files, not the draft.
- `screening-report.md` (user): older than the working copy, which has the §8 Phase 2 addendum (B1, B2 and S1 confirm runs).
- `dev2-report.md` (user): names `dv2-grades.csv`; the file is `dev2-grades.csv`. Working copy corrected.
- 5 series files (`s1-default.json` ... `s5-luna-v04d2-series.json`) had no copy: saved to `results/series/`. They record the settings of each series: S1 model `gpt-6.1-sol`; S2 to S5 model `gpt-5.6-luna`; all effort low, workspace-write, approval never, elevated Windows sandbox, user config and rules ignored, network on, 25 minutes, 2 follow-ups, work root C:\w. S2 installs skill v0.3 (`vibe-skill`), S3 v0.4 (`vibe-skill-v0.4`), S4 the public skill (`vibe-security`), S5 draft 2 (`vibe-skill-v0.4d2`).

## Numbers recomputed from the user's grade files (all match the paper)
- Phase 3 (sol): 35/35, 0/35, 0/35; partial counted as fail, same. Phase 4a (luna): 35/35, 23/35, 5/35; partial = fail 35/35, 29/35, 11/35.
- Round 1: 27/36, 7/36, 5/36. Phase 4d: reminder 22/53, public 29/53 (original seven 16/35 vs 23/35; six more 6/18 vs 6/18). v0.4 draft 1 regression 4/35.
- Audit: 194 of 249 runs, 1,482 criteria, 1,330 agree (4c round 1 and 4d); round 2: 130 runs, 981 criteria, 909 identical; Cohen's kappa over all 2,463 criteria = 0.839.
- Scratchpad grade files `final-v41.csv`, `final-pub.csv`, `final-v4g.csv` are identical, status for status, to the subsets of `final-grades.csv`.

## Found and fixed in the paper
1. The grading section described blinded grading for every phase. Phase 3 had a single unblinded grader (condition visible in the folder name) plus a blind re-grade of 42 of 105 runs; Phase 4a had a blinded first pass on 105 runs and a second grader on 72 (502 of 537 criteria agree, 93.5 %, 7 adjudications). Both now stated, and the unblinded Phase 3 grader added to the threats.
2. The models were not named: gpt-6.1-sol (Phase 3) and gpt-5.6-luna (Phase 4a on), and the Codex CLI version 0.163.0, are now in the study design.
3. Blocked runs (cleanup command rejected) and no-change runs were not disclosed. Round 1: 17 of 108 blocked; round 2: 18 of 144 blocked and 6 no-change. Sensitivity excluding them: round 2 skill 17/41 vs reminder 21/41, p = 0.071 (unchanged); round 1 5/28 vs 7/30, p = 0.48. Now in the threats.
4. The reference list had every entry numbered twice. Fixed.

## Not verifiable from the received files
- The run folders themselves (events, patches, project zips): not part of this archive. The `51 of 53 runs opened the public skill` figure comes from `phase4cd-report.md`, whose source was the run logs; the underlying `settings.json` files were not in this archive.
- Phase 5: batch in progress (manifest shows 16 done, 2 blocked, 142 todo at upload time).
