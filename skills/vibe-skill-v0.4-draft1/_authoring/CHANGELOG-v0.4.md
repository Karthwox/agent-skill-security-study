# v0.4 changes (2026-10-19)

Source: Phase 4b (luna baseline gaps A3, C2, D2, I2, T1, W2) and the v0.3 probe (results/lnp-probe-report.md). Scope decision: add only what v0.3 demonstrably missed.

Added
- SKILL.md rule 4 + references/security/outbound-requests.md (I2: user-supplied URLs; probe 3/3 critical failures).
- references/security/cross-origin.md (W2: CSRF/Origin check and production error leakage; probe 1/3 critical failure).
- access-control.md section "Sharing, teams, invitations and roles" (T1: probe 2/3 critical failures, 3/3 fidelity failures from a missing accept flow and recursive policies).
- SKILL.md: deferral covers hardening only, never a step the requested feature needs to work end to end (T1 fidelity).
- SKILL.md: dependency exception for package-manager audit findings (Phase 3 finding: the reminder arm cleared a known audit finding, v0.3 did not).

Not changed (v0.3 already handled on luna in the probe): A3 (refuses; user decision to keep), C2 (no-fallback secrets), D2 (uploads).

Rules were written from general lessons; no frozen variant prompt (V10-V21) was read for wording. SKILL.md grew from 790 to about 990 words; token cost and fidelity are co-primary outcomes for v0.4 testing.
