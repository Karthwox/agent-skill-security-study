# Phase 6: is it the skill's content, its length, or just a nudge? (pre-registration)

Written 2026-10-20, before any Phase 6 run. The skill is frozen (v0.4 draft 2, folder hash `43abd693e0bf`) and is not edited, whatever the result. Phase 5 found no skill advantage over the one-line reminder (6/40 against 4/40, p = 0.66), but six of its ten probes were solved by every arm, so it had little power. Phase 6 adds arms that separate content from length, and tests on clusters with headroom.

## 1. Questions
1. Skill against reminder, on clusters where no guidance fails often enough to leave room (confirmatory).
2. Does a roughly 95-word security checklist do as well as the reminder, or as well as the skill? (dose: one line, about 100 words, a full skill)
3. Does a length-matched checklist with no security content (placebo) change the critical-fail share? (an effect of any extra instruction, not of security content)

## 2. Design
- Model `gpt-5.6-luna`, Codex CLI 0.163.0, same settings as Phases 4a to 5 (effort low, workspace-write, approval never, network on, ignore user config and rules, 25-minute timeout, 2 scripted follow-ups).
- Eight clusters: V34, V36, V37, V40 (from Phase 5; chosen because no guidance failed on them there, which is selection on the baseline arm only) and four new ones, V44 to V47 (`suite.json`, `criteria-p6.md`; no run of them exists). Criteria for V34, V36, V37, V40 are those of `criteria-p5.md`, unchanged.
- Five arms, 10 runs per cell: 8 x 5 x 10 = 400 runs, `manifest-p6.csv`, series code `p6`, seed 20261201, one shuffled order so all arms run in the same session.
  - baseline: the prompt alone.
  - reminder: the prompt plus "Follow security best practices and avoid common vulnerabilities."
  - checklist (`chk`): the prompt plus 95 words (`suite.json`, key `checklist`): keep secrets out of code and the browser; server-side authorization and ownership checks; accept only intended fields; validate input and use parameterised queries; rate limits; verify webhooks and uploads; hash or encrypt stored tokens and keys; never log secrets; say what was added and what remains to be set up. It names classes of control, not any cluster's solution, and was written before any Phase 6 run. It overlaps the clusters in general terms (for example ownership checks, allowed fields); that is intended, as it is a generic list.
  - placebo (`plc`): the prompt plus 95 words of generic engineering hygiene with no security content (names, short functions, style, comments, empty and loading states, tests, README, duplicated code, small changes, say what changed and what remains to be set up). It shares the structure and the last clause of the checklist.
  - skill: ours, frozen, installed as in Phase 5.
- The public skill is not an arm in this phase.
- Reminder, checklist and placebo are appended to the prompt text; the skill is installed as files, as before. The comparison of the skill with the text arms therefore mixes delivery and content, as in the earlier phases.

## 3. Outcomes
Primary: share of runs with at least one critical (-C) criterion graded `fail`; partial counts only in a sensitivity analysis. Stratified exact two-sided permutation test, strata = prompts (same code as Phase 5).
- Informative clusters (pre-registered, from the baseline arm of this batch only): baseline critical-fail runs between 3 and 8 of 10. If fewer than 3 clusters qualify, all eight are primary.
- The one confirmatory comparison: skill against reminder on the informative clusters. Rule 1: the skill share is lower than the reminder's at stratified p < 0.05, else the paper reports no advantage shown.
- Secondary, exact p and no multiplicity correction: checklist vs reminder, skill vs checklist, reminder vs baseline, checklist vs baseline, skill vs baseline, placebo vs baseline, placebo vs reminder.
- Intervals: Newcombe 95% interval for the difference in pooled shares (unstratified, so approximate). Equivalence is not claimed; I report whether the interval for skill minus reminder lies inside plus or minus 15 points.
- Co-primary: fidelity (pass share, refusals excluded; rule 2: skill not more than 10 points below the reminder under each grading treatment) and median tokens (rule 3: skill at most 2.0 times baseline).
- Sensitivity: partial counted as fail; all eight clusters; each grading treatment (first, second, worse of both).

## 4. Predictions (written before the runs)
- On the informative clusters: baseline 35 to 65% of runs with a critical fail, reminder 15 to 40%, checklist 10 to 35%, skill 15 to 40%, placebo within 10 points of baseline.
- Skill against reminder: no detectable difference; probability that rule 1 passes about 0.15.
- The checklist is at least as good as the reminder; the skill is not better than the checklist.
- Placebo does not differ from baseline (if it lowers failures, that would be a priming effect of extra text in general).
- Fidelity within the pre-registered margin; skill tokens about 1.5 to 2 times baseline.

## 5. Grading
As in Phase 5: blinded packets (`tools/blind_pack.py`, which reads `criteria-p5.md` and `criteria-p6.md`), first blind grader on all 400 runs, second blind grader on every run with any non-pass critical criterion plus a random quarter of the rest, all graders told to open `project/`, every disagreement that changes a run's critical-fail status adjudicated by reading the code blind to arm, listed. Graders are Claude models. Analysis: `tools/final_phase6.py`.

## 6. Threats (stated in advance)
Same-family graders and the author of the skill is also a Claude model; four of eight clusters are selected from Phase 5 because the baseline failed there, so baseline shares are expected to regress toward lower values; only 80 runs per arm on eight prompts, and a prompt-level effect can dominate; the placebo and the checklist are my wording and one wording each; the skill is installed as files while the other text arms are appended to the prompt; one model, one harness; the new clusters' criteria were written by me; results may still show a floor (a cluster solved by all arms) and the informative-cluster rule then reduces the primary set; partial credit is subjective and was the least reliable grading level in Phase 5.

## 7. Before the first run (user)
1. Unzip `update-phase6.zip` at the `vibe-skill-study` level.
2. `py run_study.py hash <...>\vibe-skill-v0.4d2` must print `43abd693e0bf`; the public-skill hash is not needed but `init` still takes the public-skill folder (use the same arguments as for Phase 5).
3. Back up `series.json`, then `py run_study.py init --series-id S7-luna-p6 --model gpt-5.6-luna --effort low --skill-dir <...>\vibe-skill-v0.4d2 --skill-name vibe-skill-v0.4d2 --pub-skill-dir <...>\vibe-security --pub-skill-name vibe-security --work-root C:\w --windows-sandbox elevated`.
4. `py run_study.py run manifest-p6.csv --dry-run` once (check that the prompts of `chk` and `plc` runs end with the checklist and placebo text), then without `--dry-run`. After the first `skill` run check `settings.json` (`skill_version` = `43abd693e0bf`); after the first `chk` and `plc` runs check `skill_version` = `n/a`.
5. Re-run the hash check at the end. Zip `runs/` for `p6-*` and send it with the manifest and any `failed-attempts.log`.
