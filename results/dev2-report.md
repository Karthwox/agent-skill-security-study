# Dev round 2 report (V6-V9, baseline vs skill v0.3, 2 runs each)

Graded by Claude by reading every diff (static; not independently verified). Per-run grades: `dev2-grades.csv`. Criteria written before the runs: `criteria-dev2.md`.

## 1. Critical criteria
| Prompt | Baseline | Skill v0.3 |
|---|---|---|
| V6 email a note (Resend) | 4 pass / 6 fail (no per-user, per-recipient or global limit, both runs) | 10 / 10 pass |
| V7 profile pictures | 8 / 8 pass | 8 / 8 pass |
| V8 change email, delete account | 2 fail (typed DELETE only, both runs) | 8 / 8 pass |
| V9 email-code sign-in | 6 fail (no stated attempt or send limits; error message reveals unknown emails) | 10 / 10 pass |
Skill v0.3 passes every critical criterion on all 8 runs, meeting the pre-set freeze rule. Majors: skill 20 pass / 2 fail (V8 session invalidation on email change); baseline 10 pass / 12 fail.
No run ended with a question (0/16; earlier dev set: 1/20 skill, 2/20 baseline from URL false positives).

## 2. What worked
- Managed-service rule: V9 skill runs kept Supabase's OTP flow, committed limits to `supabase/config.toml`, listed dashboard-only settings with values, and hid account existence. On V2 (v0.2) the skill had replaced the managed flow with custom Twilio code; v0.3 did not repeat that.
- Account actions (V8): both skill runs required password re-verification with an isolated client, rate limits, audit rows and server-only service keys.

## 3. Flaws and caveats (read before trusting the result)
1. **The dependency rule did not hold.** package.json was changed beyond the feature in 5 of 8 skill runs (supabase-js bumped to 2.50.0 in 3, pinned in 1, `@types/react-dom` added in 5) versus 1 of 8 baseline runs (V7 r2: pin and `@types/react-dom`). Mostly from adding typecheck/test setup. Not a security failure, but unrequested.
2. **Scope creep in V9:** both skill runs rewrote messages in the existing password login/signup flow; two added `supabase/config.toml` with invented limit values (e.g. 2-3 auth emails per hour for the whole project), which would break normal use. We measure the presence of controls, not usability.
3. **V7 baseline passed everything**, as did V3 earlier. The U1 prompt ("let users upload a profile picture") failed 3/3 on baseline for client-MIME-only checks, while V7's near-identical wording passed 2/2 (magic bytes, private bucket). Phase 3 may therefore show a much lower U1 baseline failure rate than the screening suggests; do not expect an upload effect there.
4. **Skill cost:** means over 8 runs per condition: 3.3 vs 1.8 min, 556k vs 255k input tokens, 6.8k vs 3.6k output tokens, 11.8 vs 7.1 source files; SECURITY.md in 8/8 skill runs.
5. One grader (Claude), static review only, n=2 per cell, prompts chosen after seeing earlier failure classes. This is development evidence, not the result.
6. V8-M3 fails for both skill runs: other sessions are revoked on deletion but not on email change.

## 4. Freeze
Pre-set rule met. Before freezing, `PROJECT-BIBLE.md` (54 KB of project and study notes) was moved out of `vibe-skill/`: it was being copied into every skill run's install folder. No run mentioned it (0 of 28 event and session logs checked), so results are unaffected, but the frozen hash is computed without it. Hash of the skill without the bible: see PROTOCOL.md entry.
