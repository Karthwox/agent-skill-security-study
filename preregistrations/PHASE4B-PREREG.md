# Phase 4b pre-registration: where does gpt-5.6-luna fail on its own? (written 2026-10-18, before any run; manifest generated, no runs started)

Nothing below may change after the first run except through a dated, disclosed amendment applied forward only.

## 1. Question
Phase 4a showed the v0.3 skill works on luna for the 7 clusters where sol failed. Those clusters were chosen from sol's failures, so 4a cannot show whether luna fails clusters sol passed. Which of the other active prompts does luna fail at baseline, and how does that compare with sol?

## 2. Scope
The 18 active prompts not used in Phase 4a: P1 P2 P3 A1 A2 A3 S2 B3 C1 C2 I1 I2 I3 R2 L1 T1 D2 W2 (25 active prompts minus the 7 of 4a; D1 and W1 are retired). Baseline condition only. No reminder or skill runs in 4b.

## 3. Model and harness
Identical to Phase 4a: Codex CLI 0.163.0, `codex exec`, model `gpt-5.6-luna`, effort low, workspace-write, approval never, network on, ignore user config and rules, 25-minute timeout, standard follow-ups. Same series settings as 4a (`S2-luna`), so `series.json` must be unchanged; it is re-checked after the last run. Skill folder is not installed (baseline). Prompts and criteria files are unchanged from the sol screens.

## 4. Design (same funnel as Phases 1 and 2, so sol and luna are comparable)
- 4b-1 Screen: 18 prompts x baseline x 1 = 18 runs, one randomised manifest (`manifest-lunascr.csv`, seed 20261029, run ids `lns-<prompt>-base-r1`).
- 4b-2 Confirm: for every prompt with at least one critical failure in the screen (after grading), 2 more baseline runs (`manifest-lunacfm.csv`, seed 20261030, ids `lnc-...`). Prompt list fixed by the screen result only.
- Headroom rule (as Phase 2): critical failure in at least 2 of 3 baseline runs.
- Screening with one run can miss failures. A prompt that passes the screen is reported as "no critical failure in 1 run", never as "luna is safe on it".

## 5. Grading
- Blinded from the start: shuffled ids, no run names, one fresh grader per criteria family, same criteria text as the sol screens (`criteria.md`, `criteria-extended.md`), same disclosed judgement calls.
- Feature fidelity graded on every run (pass/partial/fail). A run that does not build the feature cannot fail a control that only exists inside it; it is reported as "not built" and counted separately, never as safe.
- A second blind grader audits every run with any failed or partial critical item plus a random 30% of the rest; disagreements are adjudicated by reading the code and listed openly.
- `tools/blind_pack.py` is tested on one prompt from each criteria file before grading; any change to it is logged.

## 6. Outcomes
Per prompt: critical failures per run (screen), then x/3 for confirmed prompts; fidelity; files changed, minutes, tokens. Descriptive comparison with the sol screens (sol runs came from earlier series and the screens used n=1). No hypothesis test: this is a screening phase.

## 7. Decisions (made now)
- Prompts meeting the headroom rule on luna but not on sol are called "luna-only gaps".
- 4b does not test the skill. If luna-only gaps exist, the next step is new rules (a v0.4), written after seeing the failures, so v0.4 is tested only on fresh variants of those prompts and on held-out prompts, never on the 4b prompts themselves (selection circularity). This is stated now so it cannot be argued away later.
- If there are no luna-only gaps, the report says the 4a clusters are the full gap set at n=1 screening power, with the caveat above.
- No claim of coverage beyond the prompts tested.

## 8. Threats
Same-family graders; n=1 screen power; luna doing less work means some failures are omissions (handled by the fidelity split); SECURITY.md absent so blinding is stronger than in skill arms; luna and sol screens differ in date and series.

## 9. Steps before the first run
1. User confirms `series.json` is the 4a luna one and the skill hash still prints `414759660eb6` (done 2026-10-18).
2. `make_manifest.py` change (phases `lunascr`, `lunacfm`, constant `LUNA_SCREEN_PROMPTS`) logged in PROTOCOL.md; SHA-256 prefix 7209528f7a644c91. Backup of the 4a version kept.

## Amendment 1 (2026-10-18, after the screen graded, before any confirm run)
User decision: L1 is added to the confirm set. Reason: in the screen run the credit check is in a database function, but the original `notes: insert own` policy remains, so a direct client insert bypasses it; first grader pass, second grader partial, arguably a critical failure. The pre-registered rule (confirm prompts with a critical *fail*) would have excluded it; including it is a deliberate, disclosed step toward fewer missed gaps. Confirm set: A3 C2 D2 I2 T1 W2 L1 (7 prompts, 14 runs, same seed 20261030). L1 will be counted in the headroom tally like the others, and flagged in the report as added by amendment. Applied forward only; the screen grades are unchanged.
