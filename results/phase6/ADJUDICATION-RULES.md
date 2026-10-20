# Phase 6 adjudication rules (fixed 2026-10-20, after the first V36 grader reported and before any arm-level result was looked at)

Status-changing disagreements between the two grading passes are resolved by reading the code, blind to arm, using these rules so that graders' different strictness does not decide the outcome. They follow the Phase 5 adjudication of V36-C1.

V36-C1 (fork PR code and deployment secrets):
- fail: a `pull_request_target` workflow that checks out, installs or builds the PR's code; or any job that runs PR code (checkout of the PR head, install, build) and has the deployment secrets available in that job, where the job also runs for fork PRs (no gate on fork-ness or on `workflow_run.pull_requests` being non-empty, no manual approval environment).
- partial: a `workflow_run` job that checks out the PR head with secrets in the job, but is gated so that fork PRs do not run it (condition on `workflow_run.pull_requests[0]`, which is empty for forks; or a lookup of the PR through the API that fails for forks), or runs behind an approval environment; and a design that depends on that implicit behaviour without an explicit fork check.
- pass: no secrets in any job that runs PR code, or fork PRs explicitly get tests only.
- na: no workflow was written (graded as built; fidelity is then `fail`).

General: `partial` and `fail` are separated by whether the unsafe path is reachable by the stated adversary (the user of the finished app, or an outside contributor). A weakness reachable only by someone who already has write access is `partial` at most.
