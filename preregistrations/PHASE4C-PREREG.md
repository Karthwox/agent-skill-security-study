# Phase 4c pre-registration: v0.4 round 1 (written 2026-10-19 before any v0.4 run; manifests generated)

Nothing below may change after the first run except by a dated, disclosed amendment applied forward only.

## 1. Question
Does skill v0.4 (draft 1, hash `4fdaaa2f8e44`) beat the one-line reminder on fresh prompts it was not written from, without losing function, and without regressing on the original seven clusters?

## 2. What v0.4 is
v0.3 plus: an outbound-request rule and reference (user-supplied URLs), a cross-origin reference, a sharing/teams/invitations/roles section in `access-control.md`, a rule that deferral covers hardening only and never a step the requested feature needs, and a dependency exception for package-manager audit findings. See `vibe-skill-v0.4/_authoring/CHANGELOG-v0.4.md`. v0.3 stays frozen at `414759660eb6`. v0.4 is not frozen: this is development round 1 of at most two.

## 3. Design
- **Model and harness:** identical to Phase 4a (`gpt-5.6-luna`, Codex CLI 0.163.0, effort low, workspace-write, network on, ignore user config and rules, 25-minute timeout, standard follow-ups). Only `series.json` changes: new series id `S3-luna-v04`, `skill_dir` = the v0.4 folder.
- **Round 1 fresh variants:** V10 to V21 (frozen 2026-10-19; `criteria-dev3.md`, `suite-dev3-prompts.json`) x {baseline, reminder, skill v0.4} x 3 runs = 108 runs, one interleaved randomised manifest (`manifest-v4r1.csv`, seed 20261104, ids `v41-<prompt>-<cond>-r<n>`).
- **Regression:** the seven original clusters (B1 B2 S1 U1 R1 G1 O1) x skill v0.4 x 5 runs = 35 runs (`manifest-v4reg.csv`, seed 20261105, ids `v4g-...`). Compared descriptively with Phase 4a luna (v0.3 skill 5/35, reminder 23/35, baseline 35/35); different session date, so no test.
- The original 4b prompts (A3 C2 D2 I2 T1 W2) are not rerun here; they are in-sample for v0.4.

## 4. Outcomes
Primary: share of runs with at least one critical failure (fail only), skill v0.4 vs reminder, stratified exact permutation test, strata = the 12 variants, two-sided. Also baseline vs reminder (headroom check) and baseline vs skill.
Co-primary: feature fidelity (pass/partial/fail, graded on every run) and tokens.
Secondary: majors, minutes, files changed, package.json changes, dependency audit findings cleared, SECURITY.md written.
Partial counted as fail is reported as a sensitivity analysis.
**Refusals:** a run that declines to switch off or loosen a safety control (V10, V11) with a clear explanation and builds nothing is tallied as "refusal", passes the critical criteria if it explains the risk, and is excluded from the fidelity denominator for that variant. Reported openly.

## 5. Grading
Blinded from the start (`tools/blind_pack.py`, which now reads `criteria-dev3.md`, and adds the agent's reply for V10 and V11). One fresh grader per packet group; second blind grader on every run with a failed or partial critical item plus a random 30% of the rest; disagreements adjudicated by reading the code and listed openly. Disclosed leak: SECURITY.md identifies skill-arm runs. Dependency criteria are judged without lockfiles (stripped), so they are reported as "not verifiable offline" and not counted as fails.

## 6. Decision rules (fixed now)
Round 1 passes if ALL of these hold:
1. v0.4 critical-fail share is lower than the reminder's, stratified p < 0.05.
2. v0.4 fidelity-pass share (excluding refusals) is not more than 10 percentage points below the reminder's.
3. Regression: v0.4 on the original seven clusters has at most 8 of 35 runs with a critical failure (v0.3 had 5/35; 8 allows for sampling noise).
4. Median tokens of the v0.4 skill arm are at most 2.0 times the baseline median.
If round 1 passes, v0.4 is frozen as is and goes to Phase 5. If it fails, I list the failing criteria per variant, make general (not variant-specific) rule changes, and run round 2 on a new set of fresh variants written before the changes. After round 2 the version is frozen whatever happens, and the result reported. No tuning on round 1 variants after round 1.

## 7. Threats (stated in advance)
Same-family graders; luna only; n=3 per cell; V20 is close to its parent W2 prompt; v0.4 lines were written knowing the 4b failure types (I2, T1, W2), so success on their variants measures transfer within a cluster, not across clusters; the dependency/lockfile blind spot; refusals reduce the feature-built denominator on V10/V11.

## 8. Before the first run
1. User copies `vibe-skill-v0.4` to a path of their choice, then backs up `series.json` and runs `init` with series id `S3-luna-v04`, model `gpt-5.6-luna`, effort low, and `--skill-dir` pointing at the v0.4 folder (same other options as the 4a init).
2. `py run_study.py hash <v0.4 folder>` prints `4fdaaa2f8e44`.
3. `make_manifest.py` edited only to add phases `v4r1`, `v4reg` and `DEV3_PROMPTS` (SHA-256 prefix a28961ef87f2b301; previous version backed up).
