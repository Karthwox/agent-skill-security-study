# Exposure gate

Run this before any action that makes the app reachable by someone other than the developer.

## Triggers
Deploy or publish commands; tunnels or public host flags (`--host 0.0.0.0`, ngrok, cloudflared); making a repo public or sharing a link; pointing at a non-local database or backend; live payment keys; real or user-supplied data; hosted agent environments; user phrases such as "launch", "ship", "customers", "demo link", "share with".

## Procedure
1. **Stop** before the action.
2. **Tell the user in one message** what it exposes (who can reach it, what data, what it can spend).
3. **Set `exposed: yes`** in `SECURITY.md` (it is never `no` once a trigger fires).
4. **Run the audit procedure** (`audit.md`) at the exposed standard. If a previous audit exists and nothing structural changed, run a delta check on files changed since.
5. **Resolve deferrals.** Each entry in the deferral register whose end-condition is now met must be implemented or explicitly accepted by the user, with the risk written down.
6. **Report** coverage and remaining accepted risks, then proceed only if the user confirms.

## Never
Skip the gate because the user said "just push it". Say so, run it, and let them accept risks by name.
