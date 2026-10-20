# Cluster file template (authoring notes, not loaded by the skill)

Every file in `references/security/` follows this structure so the agent knows where to look.

```markdown
# <Cluster name>

*Last checked against vendor docs: <month year>. <What tends to change>; confirm against current docs.*

## When to read this
Concrete triggers: what the agent is doing when this file applies. One short paragraph.

## Why this happens
The root cause in a few sentences, so the agent understands the reasoning and can handle cases the rules don't list.

## Workflow
Numbered, 3-5 steps. Decide, implement, verify, handle failure.

## Step 1: <the decision artifact>
What to record in `SECURITY.md` before writing code (matrix, inventory, etc.), with a compact example.

## Step 2: Implementation rules
Numbered rules, each with the reason. Short code examples only where they remove ambiguity.

## Stack notes (optional)
Per-stack details, flagged as version-sensitive.

## Step 3: Verify
Negative tests and/or ship-check commands. Say which checks need live access and what to do without it.
End with the reporting rule: state what was checked, how, and what was not verified.

## Step 4: If it goes wrong (optional)
Incident steps, in order.

## Related files
Pointers to other cluster files that commonly apply together.
```

Style: imperative voice, explain why instead of stacking MUSTs, keep under ~300 lines, add a table of contents above that.
