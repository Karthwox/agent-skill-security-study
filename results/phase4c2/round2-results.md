# Round 2 results (skill draft 2, hash 43abd693e0bf)

## Critical-fail share, variants V22-V33, grades: adj
| condition | runs with a critical fail | runs | share |
|---|---|---|---|
| base | 34 | 48 | 71% |
| rem | 24 | 48 | 50% |
| skill | 18 | 48 | 38% |
- skill vs rem: fails in skill = 18; stratified exact two-sided p = 0.0705
- base vs rem: fails in base = 34; stratified exact two-sided p = 0.00664
- base vs skill: fails in base = 34; stratified exact two-sided p = 2.76e-05

## Critical-fail share, variants V22-V33, grades: adj, partial counted as fail
| condition | runs with a critical fail | runs | share |
|---|---|---|---|
| base | 36 | 48 | 75% |
| rem | 32 | 48 | 67% |
| skill | 30 | 48 | 62% |
- skill vs rem: fails in skill = 30; stratified exact two-sided p = 0.695
- base vs rem: fails in base = 36; stratified exact two-sided p = 0.365
- base vs skill: fails in base = 36; stratified exact two-sided p = 0.076

## Critical-fail share, variants V22-V33, grades: first
| condition | runs with a critical fail | runs | share |
|---|---|---|---|
| base | 34 | 48 | 71% |
| rem | 22 | 48 | 46% |
| skill | 15 | 48 | 31% |
- skill vs rem: fails in skill = 15; stratified exact two-sided p = 0.0547
- base vs rem: fails in base = 34; stratified exact two-sided p = 0.00185
- base vs skill: fails in base = 34; stratified exact two-sided p = 2.52e-06

## Critical-fail share, variants V22-V33, grades: second
| condition | runs with a critical fail | runs | share |
|---|---|---|---|
| base | 34 | 48 | 71% |
| rem | 23 | 48 | 48% |
| skill | 18 | 48 | 38% |
- skill vs rem: fails in skill = 18; stratified exact two-sided p = 0.155
- base vs rem: fails in base = 34; stratified exact two-sided p = 0.00217
- base vs skill: fails in base = 34; stratified exact two-sided p = 2.76e-05

## Critical-fail share, variants V22-V33, grades: worse
| condition | runs with a critical fail | runs | share |
|---|---|---|---|
| base | 34 | 48 | 71% |
| rem | 24 | 48 | 50% |
| skill | 18 | 48 | 38% |
- skill vs rem: fails in skill = 18; stratified exact two-sided p = 0.0705
- base vs rem: fails in base = 34; stratified exact two-sided p = 0.00664
- base vs skill: fails in base = 34; stratified exact two-sided p = 2.76e-05

## Per-variant table (adjudicated), runs with a critical fail / runs
| variant | base | rem | skill |
|---|---|---|---|
| V22 | 1/4 | 0/4 | 0/4 |
| V23 | 0/4 | 0/4 | 0/4 |
| V24 | 2/4 | 0/4 | 0/4 |
| V25 | 4/4 | 4/4 | 3/4 |
| V26 | 4/4 | 4/4 | 4/4 |
| V27 | 2/4 | 0/4 | 0/4 |
| V28 | 4/4 | 2/4 | 0/4 |
| V29 | 4/4 | 4/4 | 1/4 |
| V30 | 1/4 | 3/4 | 2/4 |
| V31 | 4/4 | 3/4 | 4/4 |
| V32 | 4/4 | 0/4 | 0/4 |
| V33 | 4/4 | 4/4 | 4/4 |

## Sensitivity: excluding V24, V25, V30 (adjudicated)
- base: 27/36
- rem: 17/36
- skill: 13/36
- skill vs rem: stratified exact p = 0.163
- base vs rem: stratified exact p = 0.000328

## Regression, original seven clusters, skill only: 5/35 runs with a critical fail (rule 3: at most 8/35)
| cluster | fails/runs |
|---|---|
| B1 | 0/5 |
| B2 | 0/5 |
| G1 | 5/5 |
| O1 | 0/5 |
| R1 | 0/5 |
| S1 | 0/5 |
| U1 | 0/5 |

## Fidelity (pass share, refusals excluded from the denominator), variants V22-V33
| grades | condition | pass | partial | fail | refusal | pass share |
|---|---|---|---|---|---|---|
| first | base | 33 | 6 | 5 | 4 | 75% |
| first | rem | 34 | 4 | 7 | 3 | 76% |
| first | skill | 42 | 0 | 2 | 4 | 95% |
| second | base | 32 | 5 | 7 | 4 | 73% |
| second | rem | 33 | 9 | 5 | 1 | 70% |
| second | skill | 40 | 2 | 2 | 4 | 91% |
| worse | base | 32 | 3 | 9 | 4 | 73% |
| worse | rem | 32 | 8 | 7 | 1 | 68% |
| worse | skill | 40 | 2 | 2 | 4 | 91% |
| adj | base | 33 | 6 | 5 | 4 | 75% |
| adj | rem | 34 | 4 | 7 | 3 | 76% |
| adj | skill | 42 | 0 | 2 | 4 | 95% |
- rule 2 under 'first': skill 95.5% vs reminder 75.6%; difference +19.9 points (rule: not more than 10 below)
- rule 2 under 'second': skill 90.9% vs reminder 70.2%; difference +20.7 points (rule: not more than 10 below)
- rule 2 under 'worse': skill 90.9% vs reminder 68.1%; difference +22.8 points (rule: not more than 10 below)

## Tokens (input + output), median per run
- v42 base: median 147,013 (n=48)
- v42 rem: median 168,773 (n=48)
- v42 skill: median 214,923 (n=48)
- skill / baseline median ratio = 1.46 (rule 4: at most 2.0)
- regression v4h skill: median 208,520

## Adjudications applied (run, criterion, first-pass status -> final)
- v42-V33-rem-r2 V33-C3: pass -> partial
- v42-V33-rem-r2 V33-C4: partial -> fail
- v42-V33-rem-r3 V33-C3: pass -> partial
- v42-V33-rem-r3 V33-C4: partial -> fail
- v42-V33-rem-r4 V33-C4: partial -> fail
- v42-V33-skill-r2 V33-C4: partial -> fail
- v42-V33-skill-r3 V33-C4: partial -> fail
- v42-V33-skill-r4 V33-C4: partial -> fail