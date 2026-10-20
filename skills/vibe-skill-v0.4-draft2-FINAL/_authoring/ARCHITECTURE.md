# Architecture: vibe-skill (draft)

Authoring document. Not loaded by the skill. Decisions only; each has a status, a reason, and what we are assuming or will test.

**Status key:** Settled = agreed. Proposed = my recommendation, not yet confirmed. Open = needs a decision.

## Purpose

One skill that makes AI-agent vibecoding produce better results: distinctive UI, secure code, and tests that can fail. The reader is a coding agent. Every file must justify its context cost.

## Principles

1. **Progressive disclosure.** `SKILL.md` stays short and routes. Detail loads only when the task needs it.
2. **Decide before coding.** Each cluster starts by recording a decision artifact (matrix, inventory, brief) so omissions can't hide.
3. **Deterministic where possible.** Checks that a script can do shouldn't depend on the model remembering.
4. **Fail safe.** When unsure, apply the stricter rule.
5. **Honest reporting.** The agent states what it checked, how, and what it could not verify.

## Decisions

### D1. File structure. *Settled*
```
vibe-skill/
├── SKILL.md                    router, non-negotiables, gate triggers
├── references/
│   ├── design.md               Impeccable integration + our additions
│   ├── testing.md
│   ├── gate.md                 exposure gate procedure
│   ├── audit.md                audit mode: verify and fix an existing project
│   └── security/<cluster>.md   one file per cluster
├── scripts/                    deterministic checks and enumerators
├── assets/SECURITY.template.md
└── _authoring/                 not shipped: templates, this document
```
Install location differs per tool (see D9).
*Why:* a mixed file loads rules the task doesn't need. Per-cluster files keep context small and let vendor-specific facts change independently.
*Risk:* the agent may not load a file it needs. Mitigated by D2 and tested in D11.

### D2. `SKILL.md` contents. *Proposed*
Under ~100 lines: (a) a description that triggers on building or changing apps, (b) 6 to 10 non-negotiables that apply regardless of routing, (c) a task-to-file routing table keyed by what the agent is doing, (d) the short list of gate triggers pointing to `gate.md`, (e) the reporting rule.
*Why:* if routing fails, the non-negotiables still prevent the worst outcomes.
*Assumes:* routing by activity ("adding a table", "calling a paid API") works better than routing by cluster name.

### D3. Cluster file template. *Settled*
See `cluster-template.md`. Same section order in every file so the agent knows where to look. Each file ends with a Verify section and a Related files list. Each carries a "last checked" line.

### D4. Shared project state: `SECURITY.md`. *Settled*
Created in the user's project from `assets/SECURITY.template.md`. Holds the decision artifacts: access matrix, secrets inventory, abuse surface and budgets, authentication decisions, and the status fields from D5.
*Why:* decisions survive across sessions and across agents, and the user can read and edit them.

### D5. Strictness model. *Settled: strict by default with a deferral register*
Options:
1. Three modes (prototype, shared, production) with by-mode tables in every file.
2. No modes, one strict standard.
3. **Strict by default.** An explicit deferral register lists controls postponed for local-only work, each with the condition that ends it. An exposure flag takes yes, no, or unknown, and unknown counts as yes. Exposed means no deferrals.

*Why option 3:* undeclared projects land on the strict side, a missed gate stays survivable, and there is one yes/no question instead of a mode system.
*Cheap, always on:* secrets handling, server-side authorization and ownership scoping, input validation, package verification, never disabling a protection to fix an error, a spend cap on any paid key.
*Deferrable for local-only work:* login UI and provider setup (use the dev stub), rate limits and challenges, MFA, security headers, CORS tightening, monitoring.
*Assumes:* the deferrable list is where prototyping friction actually comes from. *Test:* compare extra turns and rule violations on the same prototyping prompts under option 2 and option 3.

### D6. Exposure gate. *Proposed*
- Triggers listed in `SKILL.md`: deploy or publish commands, tunnels or public host flags, public repo or link sharing, non-local database or backend, live payment keys, real or user-supplied data, hosted agent environments, and user phrases such as "launch", "customers", "demo link".
- Procedure in `gate.md`: stop before the action, tell the user in one message what it exposes, run the exposed-standard checks (the audit procedure, D13), record any accepted risks, update the flag. Later gates in the same state run a delta check only.
- Optional script outputs yes/no/unknown plus reasons and never prints secret values. Optional pre-push hook and CI step call the same script. The user installs them.
- Enforcement hooks key on `PreToolUse` because it is common to all three target tools (see D9).
*Assumes:* instruction-only triggers will miss cases, so layers outside the model matter. *Test:* gate-evasion prompts (D11), where a missed gate is a blocking failure.

### D7. Design layer. *Settled in principle*
Delegate to Impeccable: `init`, `shape`, `craft`, `harden`, `onboard`, and its detector. Depend on it, don't copy it. If it isn't installed, tell the user the install command and use a minimal inline fallback.
Our additions in `design.md`: an imagery sourcing ladder for harnesses without image generation, a rule that the user's chosen style overrides default bans, and a calibration pass for Claude-based agents.
*Open question:* verify how Impeccable's shape step handles the style question before writing the additions. Also confirm that Impeccable installs and runs in all three target tools.

### D8. Scripts. *Proposed, after cluster tests*
The grep, SQL, and git commands now inline in cluster files move to `scripts/`. Cluster files keep only interpretation. Scripts output findings, never secret values.
*Why later:* we don't know the full set of checks until the clusters are tested.
Scripts include enumerators (routes, tables, env vars, secrets, dependencies) that audit mode depends on (D13).
*Open sub-question:* script runtime. It must work in all three tools without installs, so one language with only its standard library. Candidates: Python 3 or Node. Decide before writing scripts.

### D9. Environment assumptions. *Settled*
**Targets:** Claude Code, Antigravity, Codex. We assume an agent with a shell and filesystem, so scripts, hooks, and live checks are available, and cluster files don't need a no-shell fallback for each check. "Not verified" reporting still applies to anything the agent can't reach (databases, provider dashboards, deployed environments).

**Portability constraints.** These come from a first look at the three tools. The sources were mostly third-party repos and guides, so confirm against each tool's official docs before writing any config.
- All three read the standard `SKILL.md` directory format. Discovery paths differ: Claude Code uses `.claude/skills/`, Codex and Antigravity use `.agents/skills/` in the repo plus user-level directories. Ship one skill folder and document the install path for each tool.
- Keep `SKILL.md` frontmatter to the standard `name` and `description` fields. Tool-specific metadata (for example Codex's `agents/openai.yaml`) goes in separate files.
- **Hooks:** all three appear to support `PreToolUse`, `PostToolUse`, and `Stop`. `UserPromptSubmit` and `SessionStart` are not common to all (Antigravity appears to lack a prompt-submit hook). So gate enforcement relies on `PreToolUse`, which can intercept shell commands. Config formats differ (`.claude/settings.json`, `.codex/hooks.json`, `.agents/hooks.json`), so we ship one script plus three thin config snippets, installed by the user.
- **Models differ across these tools.** Instructions must not rely on one model family's habits, and tests should cover at least two.

### D10. Reporting rule. *Settled*
Every task ends with a short summary of what was checked and how, what failed and was fixed, and what could not be verified. The agent never reports a check it didn't run.

### D11. Testing. *Proposed*
- **Cluster by cluster,** starting with the first cluster written, then the next. A small smoke test of the router and gate comes before more content.
- **Method:** same prompts, run with and without the skill, scored against a written rubric per cluster.
- **Measures:** (a) the right files were loaded, (b) the listed vulnerabilities were avoided, (c) gate misses, which are blocking, (d) friction (extra turns and questions), (e) honest reporting (no claimed checks that weren't run).
- **Prompt types:** realistic vibecoding requests, prompts that tempt shortcuts ("just make it work"), gate-evasion prompts ("just push it", slow drift, stale `SECURITY.md`), cross-cluster tasks ("add Stripe payments").
- **Who runs them:** tests have to run in the real target agent. I prepare prompts, rubrics, and scoring sheets, and the results come back for analysis.
- **Harness matrix:** cluster content tests run in one primary harness. The router and gate smoke test runs in all three, since skill discovery and hooks differ. Models differ too, so content tests should cover at least two model families.
- **Method details:**
  - Fresh project folder per run. Several runs per prompt and condition, because outputs vary.
  - Graders are scripts plus a binary rubric. They stay outside the skill folder and prompts stay unseen by the agent, so the skill can't be tuned to the test.
  - Prompts are split into a development set (used to fix the skill) and a held-out set (used only to confirm).
  - Success thresholds are agreed before running. Gate misses must be zero on the adversarial set.
  - Start with a small pilot per cluster, then scale if the signal justifies it.
- **Automation:** Claude Code (`claude -p`) and Codex (`codex exec`) have headless modes. Antigravity's CLI (`agy -p`) has one too, but earlier versions had non-TTY output problems and headless runs soft-deny shell tools until granted. Verify on the installed version before relying on it.
- **Audit tests (D13):** seeded-vulnerability repos, scored on vulnerabilities found, correctly fixed, regressions introduced, and false assurance. Run in a fresh session.

### D12. Maintenance. *Settled*
Each file has a "last checked" line. Vendor-specific facts live in stack notes, flagged as version-sensitive. Facts are checked against current docs when files are written or revised.

### D13. Two ways to use the skill: build and audit. *Settled*
**Build** (preventive) applies the cluster rules while the agent creates or changes code. **Audit** (remedy) checks an existing project against the same rules, reports, and fixes in tiers. Typical flow: build with the skill during development, then audit the same project before it is exposed, and again afterwards.
- **One rule set.** Audit reuses the clusters' Verify sections. There is no separate standard to maintain.
- **Inventory-driven.** Audit enumerates every route, table, env var, secret, and dependency with scripts, then checks each against the rules. It treats `SECURITY.md` as claims to verify against the code, not as truth. Missing controls are invisible when reading code, so free-form review is not enough.
- **Independent.** Run in a fresh session, ideally with a different model, so the agent isn't marking its own work.
- **Tiered fixes.** (1) Safe mechanical fixes applied directly. (2) Fixes that need a user decision (for example, RLS policies need a confirmed access matrix). (3) User actions the agent can't do (rotate keys, provider settings, spend caps). (4) Refactors that need tests first. Never fix by weakening a protection.
- **Coverage statement.** Every audit reports what was checked and what could not be, and never says "no issues found" without coverage.
- **Gate.** The exposure gate (D6) runs audit checks for the exposed standard.
*Why:* it covers the large stock of existing vibe-coded apps, is invoked explicitly (so activation is more reliable than for build mode), and is easier to measure than prevention.
*Assumes:* the enumerators are reliable enough that "checked every route" is true. *Test:* see D11.

## Roadmap

1. Done: D5 resolved; `authentication.md` and `SECURITY.template.md` revised to match.
2. Minimal router and gate, smoke tested against the existing four cluster files.
3. Test clusters one at a time, fixing each before the next.
4. Remaining clusters: input handling and web hardening, dependencies and supply chain, uploads, AI features.
5. `testing.md`, `design.md`, `audit.md` with enumerator scripts (D8, D13), full router.

## Open decisions

1. **D11:** test method above. The first series runs in Codex (Antigravity usage ran out); Antigravity and other harnesses come later as separate series.
2. **D8:** script runtime (Python 3 or Node, standard library only).
