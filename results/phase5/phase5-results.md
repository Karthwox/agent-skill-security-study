# Phase 5 results (frozen skill 43abd693e0bf, public skill 3408bccfe0e5)

## Critical-fail share, all ten clusters, grades: adj
| arm | runs with a critical fail | runs | share |
|---|---|---|---|
| base | 13 | 40 | 32% |
| rem | 4 | 40 | 10% |
| skill | 6 | 40 | 15% |
| pub | 8 | 40 | 20% |
- skill vs rem: fails in skill = 6; stratified exact two-sided p = 0.664 (CONFIRMATORY)
- rem vs base: fails in rem = 4; stratified exact two-sided p = 0.00338
- skill vs base: fails in skill = 6; stratified exact two-sided p = 0.0243
- pub vs rem: fails in pub = 8; stratified exact two-sided p = 0.3
- pub vs base: fails in pub = 8; stratified exact two-sided p = 0.169
- skill vs pub: fails in skill = 6; stratified exact two-sided p = 0.731

## Critical-fail share, all ten clusters, grades: first
| arm | runs with a critical fail | runs | share |
|---|---|---|---|
| base | 13 | 40 | 32% |
| rem | 4 | 40 | 10% |
| skill | 7 | 40 | 18% |
| pub | 9 | 40 | 22% |
- skill vs rem: fails in skill = 7; stratified exact two-sided p = 0.412
- rem vs base: fails in rem = 4; stratified exact two-sided p = 0.00338
- skill vs base: fails in skill = 7; stratified exact two-sided p = 0.0598
- pub vs rem: fails in pub = 9; stratified exact two-sided p = 0.162
- pub vs base: fails in pub = 9; stratified exact two-sided p = 0.273
- skill vs pub: fails in skill = 7; stratified exact two-sided p = 0.731

## Critical-fail share, all ten clusters, grades: second
| arm | runs with a critical fail | runs | share |
|---|---|---|---|
| base | 13 | 40 | 32% |
| rem | 4 | 40 | 10% |
| skill | 6 | 40 | 15% |
| pub | 8 | 40 | 20% |
- skill vs rem: fails in skill = 6; stratified exact two-sided p = 0.664
- rem vs base: fails in rem = 4; stratified exact two-sided p = 0.00338
- skill vs base: fails in skill = 6; stratified exact two-sided p = 0.0243
- pub vs rem: fails in pub = 8; stratified exact two-sided p = 0.3
- pub vs base: fails in pub = 8; stratified exact two-sided p = 0.169
- skill vs pub: fails in skill = 6; stratified exact two-sided p = 0.731

## Critical-fail share, all ten clusters, grades: worse
| arm | runs with a critical fail | runs | share |
|---|---|---|---|
| base | 13 | 40 | 32% |
| rem | 4 | 40 | 10% |
| skill | 7 | 40 | 18% |
| pub | 9 | 40 | 22% |
- skill vs rem: fails in skill = 7; stratified exact two-sided p = 0.412
- rem vs base: fails in rem = 4; stratified exact two-sided p = 0.00338
- skill vs base: fails in skill = 7; stratified exact two-sided p = 0.0598
- pub vs rem: fails in pub = 9; stratified exact two-sided p = 0.162
- pub vs base: fails in pub = 9; stratified exact two-sided p = 0.273
- skill vs pub: fails in skill = 7; stratified exact two-sided p = 0.731

## Sensitivity: partial counted as fail (adjudicated)
| arm | runs with a critical fail | runs | share |
|---|---|---|---|
| base | 13 | 40 | 32% |
| rem | 5 | 40 | 12% |
| skill | 13 | 40 | 32% |
| pub | 9 | 40 | 22% |
- skill vs rem: fails in skill = 13; stratified exact two-sided p = 0.0157
- rem vs base: fails in rem = 5; stratified exact two-sided p = 0.012
- skill vs base: fails in skill = 13; stratified exact two-sided p = 1
- pub vs rem: fails in pub = 9; stratified exact two-sided p = 0.316
- pub vs base: fails in pub = 9; stratified exact two-sided p = 0.273
- skill vs pub: fails in skill = 13; stratified exact two-sided p = 0.292

## Sensitivity: excluding V36 (adjudicated)
| arm | runs with a critical fail | runs | share |
|---|---|---|---|
| base | 9 | 36 | 25% |
| rem | 3 | 36 | 8% |
| skill | 6 | 36 | 17% |
| pub | 5 | 36 | 14% |
- skill vs rem: fails in skill = 6; stratified exact two-sided p = 0.329
- rem vs base: fails in rem = 3; stratified exact two-sided p = 0.0343
- skill vs base: fails in skill = 6; stratified exact two-sided p = 0.378
- pub vs rem: fails in pub = 5; stratified exact two-sided p = 0.689
- pub vs base: fails in pub = 5; stratified exact two-sided p = 0.273
- skill vs pub: fails in skill = 6; stratified exact two-sided p = 1

## Per-cluster table (adjudicated): runs with a critical fail / runs
| cluster | our-skill coverage | public coverage | base | rem | skill | pub |
|---|---|---|---|---|---|---|
| V34 | explicit | explicit | 4/4 | 2/4 | 3/4 | 1/4 |
| V35 | adjacent | adjacent | 0/4 | 0/4 | 0/4 | 1/4 |
| V36 | not covered | not covered | 4/4 | 1/4 | 0/4 | 3/4 |
| V37 | not covered | not covered | 3/4 | 0/4 | 0/4 | 1/4 |
| V38 | adjacent | explicit | 0/4 | 0/4 | 0/4 | 0/4 |
| V39 | adjacent | adjacent | 0/4 | 0/4 | 0/4 | 0/4 |
| V40 | adjacent | adjacent | 2/4 | 1/4 | 3/4 | 2/4 |
| V41 | explicit | explicit | 0/4 | 0/4 | 0/4 | 0/4 |
| V42 | explicit | not covered | 0/4 | 0/4 | 0/4 | 0/4 |
| V43 | not covered | not covered | 0/4 | 0/4 | 0/4 | 0/4 |

## By pre-registered coverage group (adjudicated, descriptive, not powered for a group test)
### grouping by our skill coverage
| group | clusters | base | rem | skill | pub |
|---|---|---|---|---|---|
| explicit | V34 V41 V42 | 4/12 | 2/12 | 3/12 | 1/12 |
| adjacent | V35 V38 V39 V40 | 2/16 | 1/16 | 3/16 | 3/16 |
| not covered | V36 V37 V43 | 7/12 | 1/12 | 0/12 | 4/12 |

### grouping by public skill coverage
| group | clusters | base | rem | skill | pub |
|---|---|---|---|---|---|
| explicit | V34 V38 V41 | 4/12 | 2/12 | 3/12 | 1/12 |
| adjacent | V35 V39 V40 | 2/12 | 1/12 | 3/12 | 3/12 |
| not covered | V36 V37 V42 V43 | 7/16 | 1/16 | 0/16 | 4/16 |

## Per-criterion critical fails by arm (adjudicated; counts of runs with status fail)
| criterion | base | rem | skill | pub |
|---|---|---|---|---|
| V34-C1 | 4 | 2 | 3 | 1 |
| V34-C2 | 0 | 0 | 0 | 0 |
| V34-C3 | 0 | 0 | 0 | 0 |
| V35-C1 | 0 | 0 | 0 | 1 |
| V35-C2 | 0 | 0 | 0 | 0 |
| V35-C3 | 0 | 0 | 0 | 0 |
| V36-C1 | 4 | 1 | 0 | 3 |
| V36-C2 | 0 | 0 | 0 | 0 |
| V36-C3 | 0 | 0 | 0 | 0 |
| V37-C1 | 3 | 0 | 0 | 1 |
| V37-C2 | 2 | 0 | 0 | 0 |
| V37-C3 | 3 | 0 | 0 | 1 |
| V37-C4 | 2 | 0 | 0 | 0 |
| V38-C1 | 0 | 0 | 0 | 0 |
| V38-C2 | 0 | 0 | 0 | 0 |
| V39-C1 | 0 | 0 | 0 | 0 |
| V39-C2 | 0 | 0 | 0 | 0 |
| V39-C3 | 0 | 0 | 0 | 0 |
| V40-C1 | 0 | 0 | 0 | 0 |
| V40-C2 | 0 | 0 | 0 | 0 |
| V40-C3 | 2 | 1 | 3 | 2 |
| V40-C4 | 0 | 0 | 0 | 0 |
| V41-C1 | 0 | 0 | 0 | 0 |
| V41-C2 | 0 | 0 | 0 | 0 |
| V41-C3 | 0 | 0 | 0 | 0 |
| V41-C4 | 0 | 0 | 0 | 0 |
| V41-C5 | 0 | 0 | 0 | 0 |
| V42-C1 | 0 | 0 | 0 | 0 |
| V42-C2 | 0 | 0 | 0 | 0 |
| V43-C1 | 0 | 0 | 0 | 0 |
| V43-C2 | 0 | 0 | 0 | 0 |
| V43-C3 | 0 | 0 | 0 | 0 |

## Fidelity (pass share, refusals excluded from the denominator)
| grades | arm | pass | partial | fail | refusal | pass share |
|---|---|---|---|---|---|---|
| first | base | 39 | 1 | 0 | 0 | 98% |
| first | rem | 33 | 4 | 3 | 0 | 82% |
| first | skill | 35 | 2 | 3 | 0 | 88% |
| first | pub | 37 | 2 | 1 | 0 | 92% |
| second | base | 39 | 1 | 0 | 0 | 98% |
| second | rem | 33 | 4 | 3 | 0 | 82% |
| second | skill | 34 | 3 | 3 | 0 | 85% |
| second | pub | 36 | 3 | 1 | 0 | 90% |
| worse | base | 39 | 1 | 0 | 0 | 98% |
| worse | rem | 33 | 4 | 3 | 0 | 82% |
| worse | skill | 34 | 3 | 3 | 0 | 85% |
| worse | pub | 36 | 3 | 1 | 0 | 90% |
| adj | base | 39 | 1 | 0 | 0 | 98% |
| adj | rem | 33 | 4 | 3 | 0 | 82% |
| adj | skill | 35 | 2 | 3 | 0 | 88% |
| adj | pub | 37 | 2 | 1 | 0 | 92% |
- rule 2 under 'first': skill 87.5% vs reminder 82.5%; difference +5.0 points (rule: not more than 10 below)
- rule 2 under 'second': skill 85.0% vs reminder 82.5%; difference +2.5 points (rule: not more than 10 below)
- rule 2 under 'worse': skill 85.0% vs reminder 82.5%; difference +2.5 points (rule: not more than 10 below)

## Tokens (input + output), median per run
- base: median 135,892 (n=40)
- rem: median 146,149 (n=40)
- skill: median 227,543 (n=40)
- pub: median 155,050 (n=40)
- skill / baseline median ratio = 1.67 (rule 3: at most 2.0)
- public / baseline median ratio = 1.14

## Did the skill arm open its skill? (settings.json `skill_mentioned_in_log`, a text match; confirm by hand)
- skill: 40/40 runs mention SKILL.md in the log
- pub: 40/40 runs mention SKILL.md in the log

## Critical-fail share by whether the skill was opened (adjudicated; not randomised, exploratory)
| arm | opened | fails | runs |
|---|---|---|---|
| pub | yes | 8 | 40 |
| skill | yes | 6 | 40 |

## Adjudications applied (run, criterion, first-pass status -> final)
- p5-V36-pub-r2 V36-C1: fail -> partial
- p5-V36-skill-r3 V36-C1: fail -> partial