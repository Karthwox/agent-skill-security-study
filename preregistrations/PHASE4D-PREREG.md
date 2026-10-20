# Phase 4d pre-registration: an existing public skill as a fourth arm (written 2026-10-19, before any run)

Nothing below may change after the first run except by a dated, disclosed amendment applied forward only.

Revisions before any run (same day, user decisions): (1) the fresh baseline arm was dropped, because baseline is at ceiling on the original seven clusters (35/35 in Phase 4a); (2) the six luna-only clusters from Phase 4b were added. Final design: reminder and public skill only, 106 runs, luna only.

## 1. Question
Does an existing, popular, unmodified public security skill reduce critical failures in generated code on the clusters where luna's baseline showed gaps, compared with a one-line reminder, and what does it cost in fidelity and tokens?

This phase measures the public skill. It does not tune anything, and it has no pass or fail gate.

## 2. The public skill (arm "public")
- Repository: `raroque/vibe-security-skill` (MIT), commit `850938f20f6915e7c3688d85c0a838f7909c87bb` (2026-03-15). Skill folder: `vibe-security/` (SKILL.md about 920 words, nine reference files about 3,700 words, `agents/openai.yaml`).
- Folder hash by our method (`py run_study.py hash <folder>`): `3408bccfe0e5`. It must print this before the first run and again after the last.
- Installed unmodified at `.codex/skills/vibe-security` (its own name; `--skill-name vibe-security`), with implicit invocation only (no `$vibe-security`). Its description asks the agent to use it when writing or reviewing code that handles authentication, payments, database access, secrets or user data, and says to "consult the relevant reference files proactively" when generating code.
- Disclosure: I read the skill's files before writing this pre-registration. Skill v0.4 round 1 had already been written and was running; v0.4 was not informed by this skill. The predictions below are informed by my reading of it.

## 3. Design
- Model and harness: identical to Phase 4a and 4c (`gpt-5.6-luna`, Codex CLI 0.163.0, effort low, workspace-write, network on, ignore user config and rules, 25-minute timeout, standard follow-ups). Only `series.json` changes: series id `S4-luna-pub`, `skill_dir` = the public skill folder, `skill_install_name` = `vibe-security`.
- Two prompt groups, with their frozen criteria:
  - Group A, the original seven clusters (B1 B2 S1 U1 R1 G1 O1): reminder and public skill x 5 runs = 70 runs.
  - Group B, the six luna-only clusters from Phase 4b (A3 C2 D2 I2 T1 W2): reminder and public skill x 3 runs = 36 runs.
  - All 106 runs in one interleaved random manifest (`manifest-pub.csv`, phase `pub`, seed 20261107, ids `pub-<prompt>-<cond>-r<n>`).
- The reminder is re-run in this session as the same-session comparison. Group A's Phase 4a reminder (23/35) gives a repeatability check.
- Baseline is not re-run. Group A uses the Phase 4a baseline (35/35). Group B uses the three Phase 4b baseline runs per prompt (A3 3/3, C2 2/3, D2 2/3, I2 3/3, T1 3/3, W2 3/3 critical failures). Both are different sessions and descriptive only. **Group B's baseline is biased upward:** these prompts were selected because the screening baseline failed, so the baseline rate there overstates the true rate (regression to the mean). It must not be used for a test; only the same-session reminder is.
- Comparison with our own skill is descriptive only: v0.3 and v0.4 were tuned on these clusters; the public skill was not.
- Not run here: the fresh variants V10 to V21 (a later untuned public-skill comparison under its own amendment) and any sol run (sol's reminder and v0.3 skill were both 0/35, so a public skill cannot be separated from the reminder there).

## 4. Outcomes
Primary: share of runs with at least one critical failure (fail only), public skill vs reminder, same session, stratified exact permutation test (strata = the 13 prompts), two-sided.
Pre-specified subgroup views (reported, not corrected for multiple comparison, exploratory): Group A alone and Group B alone, and per prompt as k/n.
Co-primary: feature fidelity (pass/partial/fail, all runs; A3 as in 4b, where a refusal is tallied separately) and tokens.
Secondary: major failures, minutes, files changed, whether the agent opened the skill (session log mentions `vibe-security/SKILL.md` or its reference files) and which references, SECURITY.md written, partial-counted-as-fail sensitivity, descriptive comparisons with the baselines above and with our skill, reminder re-run vs Phase 4a reminder.

## 5. Predictions (stated in advance, so they can be wrong; low confidence)
1. Public skill has fewer critical-fail runs than the old baselines.
2. Group A: largest effect where the skill has a reference: abuse controls and AI integration (B1, B2, G1 partly) and secrets (S1); little or no effect on uploads (U1), password reset (R1), and account export and deletion (O1), where it has no reference.
3. Group B: little or no effect on I2 (no outbound-request or SSRF reference), D2 (dependencies) and T1 (no teams or invitations reference); a possible effect on A3 (database security reference), C2 (authentication reference) and W2 (deployment reference covers headers).
4. It is often not opened at all on generation prompts, because it is framed as an audit tool; the loaded-versus-not split will matter.
5. No prediction on public skill vs reminder overall; either direction is a result.

## 6. Grading
Same procedure as 4a, 4b and 4c: blinded packets (`tools/blind_pack.py`, which strips `.codex/`, so the installed skill folder is not in the packet; A3 is graded with its reply text as in 4b), a fresh grader per group, second blind grader on every run with a failed or partial critical item plus a random 30%, disagreements adjudicated by reading the code and listed. This arm leaves no SECURITY.md, so it leaks less than ours. Dependency criteria are not verifiable offline (lockfiles stripped).

## 7. Threats (stated in advance)
Our skill was tuned on these clusters and the public skill was not, so a gap in our favour is partly tuning and must not be reported as a clean win. The public skill is audit-oriented, so non-activation is likely and is part of the result. Same-family graders; luna only; n=5 (Group A) and n=3 (Group B) per cell, so Group B cells are small; baselines are cross-session, and Group B's is selection-biased. A human-graded sample is planned at the end for the whole paper.

## 8. Before the first run (user)
1. Wait until the v0.4 batch (`manifest-v4r1.csv`) has finished and its hash re-check printed `4fdaaa2f8e44`. Do not run `init` before then: it overwrites `series.json`, which the running batch reads.
2. Back up `series.json` (for the v0.4 series).
3. Unzip `public-skill-vibe-security.zip` (byte-exact copy of the pinned commit's `vibe-security/` folder, with LICENSE and a source note outside it). `py run_study.py hash <...>\vibe-security` must print `3408bccfe0e5`.
4. `py run_study.py init --series-id S4-luna-pub --model gpt-5.6-luna --effort low --skill-dir <...>\vibe-security --skill-name vibe-security --work-root C:\w --windows-sandbox elevated` (same other options as the earlier luna inits).
5. Replace `run_study.py` and `make_manifest.py` with the new versions, copy `manifest-pub.csv`, then `py run_study.py run manifest-pub.csv` (106 runs, about 1.5 hours).
6. Upload the `pub-*` runs, the manifest and `failed-attempts.log`; re-check the public skill hash afterwards.
