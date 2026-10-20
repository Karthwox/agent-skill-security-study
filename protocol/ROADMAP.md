# Roadmap after Phase 4b (agreed with the user 2026-10-18)

Skill v0.3 stays frozen (hash 414759660eb6) until the 4b confirm result is read. Phase 3 and 4a numbers are v0.3 results.

1. Finish the 4b confirm runs (`manifest-lunacfm.csv`, 14 runs incl. L1 by amendment) and grade them blind.
2. Draft fresh variants (2 to 3 per confirmed new cluster) with criteria, and freeze them BEFORE the v0.4 text is written, so the variants are not shaped by the new rules. Then write v0.4.
3. Test v0.4 on the fresh variants (baseline, reminder, skill), plus a regression run of v0.4 on the original 7 clusters. The 4b prompts are only a smoke check, never evidence.
4. At most 2 tuning rounds. Each round uses a fresh variant set (V1 to V9 are spent). Stop rule and fidelity/tokens as co-primary outcomes are fixed in the round's pre-registration.
5. Freeze v0.4 (new hash) and run Phase 5 held-out prompts on sol and luna. v0.3 is reported as development history; the final numbers belong to the frozen v0.4.
6. In parallel from now on: exploit-style proof of concept on existing generated apps; housekeeping (8 Phase 3 grader disagreements, package.json diff classification, skill-loading tally).
7. Check how Antigravity and Gemini load skills, then run a Gemini series.
8. Audit mode as a separate piece with its own evaluation (seeded vulnerable repos). The first paper covers generation mode.

Each step gets a pre-registration and, for the skill, a hash freeze before its first run. The paper (Results, Discussion, Abstract) is written last.

## Revision 2026-10-19: goal is now a workshop paper (agreed with the user)
The primary goal is a workshop paper documenting the findings (target: AGENT 2027 at ICSE, short paper, 5 pages incl. references, deadline 13 Nov 2026, IEEE template, single-anonymous). The skill is one of the things measured, not the product.
- Keep: finish v0.4 round 1 (pre-registered test of whether targeted rules transfer to fresh prompts) and grade it.
- Add: Phase 4d, an existing public skill as a fourth arm (`PHASE4D-PREREG.md`, 106 runs on luna: reminder and public skill on the original 7 clusters x5 and the 6 luna-only clusters x3; baselines reused). The length-matched control arm was considered and dropped by the user: the question is whether advice helps at all versus nothing and a generic reminder, not why. Consequence for claims: the paper may say that a skill of this kind and size helped, and must not attribute the effect to its specific content.
- Add: human-graded sample at the end (the user grades about 20 blinded runs), to answer the same-family-grader objection.
- Deprioritised until after the workshop deadline: a second tuning round (unless round 1 fails and time allows), full Phase 5 on sol and luna (a reduced luna-only held-out run only if round 1 passes quickly), Gemini series, audit mode, exploit proof of concept (one small one if time allows).
- Paper uses Phases 3, 4a, 4c and 4d. v0.3 results are reported with the disclosure that v0.3 was tuned on variants of the same clusters.
