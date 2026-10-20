# Human-reviewed sample, Phase 6 (20 runs, 137 rows)

Sample drawn by the rule in `PHASE6-HUMAN-SAMPLE-PREREG.md` (5 arms x 2 critical-fail + 2 non-fail runs). Sheet returned 2026-10-20 (`human-sample-returned.csv`), compared with the adjudicated LLM grades (`human-sample-key.csv`).

**Label.** The pre-registration said no AI help. The author reports using ChatGPT while checking the code by hand, so these are human-reviewed, AI-assisted grades, not an independent human grading. The paper says so and does not call them human grades without that qualifier.

## Agreement
- All 137 rows: 119 agree (86.9%). Critical and fidelity rows (89): 79 agree (88.8%).
- Run level (at least one critical `fail`): 7 both fail, 8 both pass, 2 reviewer fail / LLM pass, 3 LLM fail / reviewer pass. Cohen's kappa 0.50 (n = 20; wide uncertainty).
- Disagreements are not concentrated in one arm (critical and fidelity rows: baseline 3, reminder 3, skill 2, placebo 2, checklist 0).

## The ten critical/fidelity disagreements, checked against the criteria text
1. V40-C3 (3 rows, two skill runs and one placebo run; reviewer partial, LLM fail). Key management accepts API keys. The criterion says "creating, listing and revoking keys require the user's login token, so a key cannot mint more keys". A key that can mint keys breaks that clause, so the LLM grade (fail) stands. The reviewer was more lenient. These three account for all of the LLM-fail / reviewer-pass runs.
2. V37-C1 and V37-C3 (4 rows, one reminder and one baseline run; reviewer fail, LLM pass or na). Both runs never store the token (one-shot use). The criteria concern a stored token's encryption, so "not stored in plaintext" is met. The reviewer's fail describes missing reusable storage, which is a fidelity reduction (graded partial) and is not counted twice. LLM grades stand.
3. V37-C4 (2 rows, a baseline and a placebo run; reviewer partial, LLM pass). The saved token is also readable by the browser through a whole-row owner SELECT. The LLM graders already failed those runs on C2 (browser-readable), so the run-level result is unchanged. Not changed.
4. V47-FIDELITY (1 row, reminder run; reviewer fail, LLM pass). Real finding. The only SELECT policy on `profiles` is `username is not null`, so a new profile with a null username is invisible to its owner and the update that sets the username changes zero rows. I scanned all 50 V47 packets for this pattern: one more run (skill arm, `item-8cdeac`) has the same defect and was graded pass. Both set to fidelity fail (`tools/final_phase6.py` OV). This rests on reading the SQL, not running it.

## Effect on the results
- Critical-fail counts are unchanged. Fidelity pass share becomes baseline 82%, reminder 80%, checklist 80%, placebo 78%, skill 81% (rule 2 holds).
- If the reviewer's grades replace the LLM grades for the 20 sampled runs, the primary set reads baseline 24/30, reminder 9/30, checklist 6/30, placebo 21/30, skill 7/30 (skill against reminder 7 vs 9). Same conclusion, and it favours the skill slightly.
- V40-C3 is a standing sensitivity: it is the only critical failure in 5 of 8 baseline, 3 of 3 reminder, 6 of 6 checklist, 10 of 10 placebo and 3 of 3 skill V40 runs. If a key able to mint keys were counted as partial, V40 would drop to 3, 0, 0, 0, 0. Without V40 the primary set (V36, V37) is baseline 15/20, reminder 5/20, checklist 0/20, placebo 12/20, skill 6/20: the same ordering, skill against reminder 6 vs 5.

## Limits
20 runs; reviewer used an AI assistant; the sample was drawn on LLM outcomes and cannot establish absence of bias; the V47 policy finding is from reading SQL.
