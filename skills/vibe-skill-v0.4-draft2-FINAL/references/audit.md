# Audit mode

Verify and fix an existing project against the same rules as build mode. Prefer a fresh session and, if possible, a different model from the one that built it.

## Procedure
1. **Enumerate, do not skim.** List every route and server action, table, env var, secret-like string (including git history), external call that costs or sends, and dependency. Use scripts in `scripts/` when present; otherwise grep and report that the list is hand-built.
2. **Treat `SECURITY.md` as claims.** Check each claim against code. Missing controls are invisible when reading code, so go item by item through the inventory.
3. **Check each item against the cluster Verify sections** for the clusters that apply.
4. **Fix in tiers:**
   - Tier 1: safe mechanical fixes, apply directly.
   - Tier 2: needs a decision (RLS policies need a confirmed access matrix); propose, ask.
   - Tier 3: user actions (rotate keys, provider spend caps, dashboard settings); list with exact steps.
   - Tier 4: refactors that need tests first; write tests, then change.
   Never fix by weakening a protection.
5. **Report coverage:** items enumerated, items checked, items not verifiable and why. No "no issues found" without this.
