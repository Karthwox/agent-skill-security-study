# Phase 5a pre-registration: second harness (Antigravity CLI, Gemini model)

**STATUS: ABANDONED 2026-10-19.** Only 6 of 72 runs completed before the account's weekly agent quota ran out (reset too late for the paper deadline). The series was not completed, graded or analysed; see PROTOCOL.md. This file is kept as the record of what was planned.

Written 2026-10-19, before any Antigravity study run. Descriptive replication; no decision rules.

## Purpose
The Codex series uses one harness and one model family. This series asks whether the direction of the Codex result (skill and reminder versus baseline, skill versus reminder) shows up in a second harness with a different model. It is **descriptive, not confirmatory**: 72 runs cannot support a second hypothesis test, and the skill was frozen after Codex round 2.

## Design
- Harness: Antigravity CLI `agy` 1.4.2, headless: `agy -p <prompt> --output-format stream-json --dangerously-skip-permissions --model <model> --print-timeout 25m --new-project`, run folder as cwd. `--disable-slash-commands` is not passed (it disables skills in print mode).
- Model: `gemini-3.8-flash-low` (pinned in `series-agy.json`; if the account cannot use it the series is not started until the model is changed and this file is amended before the first run). `--effort` is not passed, because the model name already carries the level.
- Prompts: the 12 round-2 variants V22 to V33 (same text, same fixtures, same criteria as Codex round 2). They were not edited after seeing any Codex round-2 result.
- Conditions: baseline, reminder (same sentence as Codex), skill (frozen draft 2, folder hash `43abd693e0bf`, installed at `.agents/skills/vibe-skill-v0.4d2/`).
- Replicates: 2 per cell, 72 runs. Order is blocked by replicate (all r1 first, then all r2), shuffled within a block, seed in `make_manifest.py` (`agy1`). If a usage limit stops the series, the completed runs are analysed as they are and the shortfall is reported; no run is dropped or replaced because of its content.
- Follow-ups: at most 2, same scripted replies as Codex, only if the reply ends with a question and no files changed.
- Retries: a turn that produced no tool call and no file change (dropped connection, quota blip) is retried up to 3 times in the same folder and logged in `retries.log`. Any other failure stays as recorded.

## Isolation
- `~/.gemini/GEMINI.md` is empty (checked by the user on 2026-10-19). `run_agy.py` preflight refuses to start if it has content, or if any user skills or global AGENTS.md exist.
- Built-in Antigravity skills (`run-workflow`, `permissioned-github`, ...) are present in every run and are recorded per run.
- Shared state (`history.jsonl`, `conversation_summaries.db`) cannot be switched off. Each run uses `--new-project`. Each run's tool calls are scanned for paths outside its own folder and flagged (`+outside`); flagged runs are inspected by hand and reported.
- Skill loading is measured from the event stream (views of files under `.agents/skills/` and of `references/security`), as for Codex.

## Measures (same definitions as Codex)
1. Share of runs with at least one critical criterion graded `fail` (partial only in a sensitivity analysis); stratified exact permutation test over prompts, reported with the exact p but labelled descriptive.
2. Fidelity (pass, partial, fail; `refusal` tallied separately), under the three treatments (first grader, second grader, worse of both).
3. Tokens: `total_tokens` from the CLI's `usage` block (input + output + thinking), summed over turns. Input counts are summed over steps, as for Codex; the CLI reported no cached input in the probes, so token ratios are not comparable across harnesses, only across conditions within the harness.

## Grading
Same as Codex round 2: blinded packets (`tools/blind_pack.py`, which also strips `.agents/` and `.codex/`), first blind grader on all runs, second blind grader on every run with a non-pass critical or fidelity item plus a random quarter of the rest, status-changing disagreements adjudicated by reading the code and listed. Graders are Claude models, so the Codex outputs are graded by a different model family than produced them, and the Gemini outputs likewise.

## What the paper may say
- That the direction did or did not hold in a second harness, with counts and intervals.
- Not: that the result is general across models or harnesses; that the effect is due to the skill's specific content (the length-matched control was dropped); anything from a comparison of absolute rates between the two harnesses (different models, sandboxes, tools).

## Known threats, stated in advance
Single model per harness; 2 runs per cell; one prompt set; permissions skipped in the Antigravity run (`--dangerously-skip-permissions`, with `--sandbox` added if the two-run trial shows it works; the setting used is recorded in `series-agy.json`), whereas Codex used workspace-write with no approvals; the Antigravity tool set (browser, web search) is wider than Codex's; shared CLI state.
