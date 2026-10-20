# Replication archive: security skills for AI coding agents

Materials for the AGENT 2027 workshop short paper on whether security guidance
(one-line reminder, checklist, a security skill file, a public skill, a length-matched
placebo) helps an AI coding agent (Codex CLI, gpt-5.6-luna) write safer code without
losing the feature.

## Layout
| folder | contents |
|---|---|
| `skills/` | the three versions of our skill: v0.3, v0.4 draft 1, v0.4 draft 2 (frozen, the one tested in Phase 6) |
| `fixtures/` | starter projects the agents modified |
| `prompts/` | task prompts (`suite.json`) and arm texts |
| `criteria/` | per-prompt security and fidelity criteria used by graders |
| `preregistrations/` | pre-registrations written before each phase's results |
| `protocol/` | PROTOCOL.md (running log), ROADMAP.md, skill freeze records |
| `manifests/` | run manifests (arm, prompt, run id) |
| `tools/` | run harness, blinding, grading, analysis and adjudication scripts |
| `results/` | graded data and reports per phase (`results/phase6/` is the final phase) |
| `human-sample/` | 20-run human-reviewed (AI-assisted) check of Phase 6 |

## Skill hashes (`python3 tools/run_study.py hash <skill folder>`)
- v0.3: `414759660eb6`
- v0.4 draft 1: `4fdaaa2f8e44`
- v0.4 draft 2 (frozen): `43abd693e0bf`
- Public comparison skill: `raroque/vibe-security-skill`, commit `850938f20f6915e7c3688d85c0a838f7909c87bb`, hash `3408bccfe0e5`. **Not redistributed here**; fetch that commit from its own repository.

## Reproducing the Phase 6 numbers
`python3 tools/final_phase6.py <runs dir> <out dir>` regenerates `final-p6.csv` and
`phase6-results.md` from the graded runs. `results/phase6/final-p6.csv` is the published output. The raw run
folders (full agent workspaces and logs) are large and are not in this repository.

## Caveats stated in the paper
- All grading is by LLM graders (blind to arm), with a 20-run human-reviewed sample that was AI-assisted (see `human-sample/HUMAN-SAMPLE-REPORT.md`).
- `fake` credentials (e.g. `sk-proj-ABCDEF...`) in prompts and tools are deliberate test strings, not real keys.
- `C:\w` paths are the throwaway work root used for runs.

## Licenses
Code: MIT (`LICENSE`). Data and documentation: CC BY 4.0 (`LICENSE-DATA`).
