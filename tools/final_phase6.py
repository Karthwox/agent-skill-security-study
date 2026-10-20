#!/usr/bin/env python3
"""Phase 6 final grades and results (eight clusters V34 V36 V37 V40 V44-V47, arms base / rem / chk / plc / skill). Pre-registration: PHASE6-PREREG.md.
usage: python final_phase5.py RUNS_DIR OUT_DIR
Reads results/phase6/pass1-all.csv and pass2-all.csv (run_id, criterion, status) and RUNS_DIR/*/settings.json.
Adjudications (status-changing disagreements, resolved by reading the code) go in the OV dict below, each with a comment.
Treatments: adj (primary) = first pass with the listed overrides; first; second (second grader where one exists); worse (worse of both).
"""
import csv, json, sys, statistics as st, collections as C
from pathlib import Path
from math import comb

R = Path(__file__).resolve().parent.parent / "results" / "phase6"
RANK = {"pass": 0, "na": 0, "refusal": 0, "partial": 1, "fail": 2}
ARMS = ("base", "rem", "chk", "plc", "skill")
LO, HI = 3, 8   # informative cluster = baseline critical-fail runs between LO and HI of 10 (pre-registered)
from math import sqrt
def wil(x, n, z=1.96):
    p = x / n; d = 1 + z * z / n; c = p + z * z / (2 * n); r = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)); return (c - r) / d, (c + r) / d
def newc(x1, n1, x2, n2):
    p1, p2 = x1 / n1, x2 / n2; l1, u1 = wil(x1, n1); l2, u2 = wil(x2, n2)
    return p1 - p2 - sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2), p1 - p2 + sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)
# (run_id, criterion) -> final status after adjudication; each entry says why. Runs graded fail by both graders or agreed otherwise are not listed.
OV = {
    ("p6-V36-skill-r10", "V36-C1"): "fail",  # item-103da9: disagreement: pull_request_target checks out PR head and runs vercel CLI with token in PR checkout (criterion text and ADJUDICATION-RULES V36-C1)
    ("p6-V36-base-r1", "V36-C1"): "fail",  # item-ee1756: disagreement: pull_request_target checks out PR head with token in job (and head_ref interpolated in shell)
    ("p6-V44-plc-r8", "V44-C3"): "fail",  # item-15e6dc: disagreement: owner can create a link but no unshare/revoke action exists anywhere, so a link cannot be revoked
    ("p6-V47-chk-r9", "V47-C3"): "fail",  # item-f71823: disagreement: unique index is case-sensitive; no DB pattern/length check and clients hold UPDATE grant on username, so the action regex can be bypassed
    ("p6-V36-plc-r3", "V36-C3"): "na",  # item-d4466d: disagreement: no production deploy workflow (left to Vercel integration); rule: na when nothing to judge
    ("p6-V36-base-r7", "V36-C1"): "fail",  # item-bcc157: RULE-CONSISTENCY (both graders said partial): pull_request_target checks out PR head, runs npx vercel with token in that checkout; same pattern as the 15 runs graded fail. Arm label was visible to the adjudicator during this scan
    ("p6-V36-base-r2", "V36-C1"): "fail",  # item-fd75d5: RULE-CONSISTENCY (both graders said partial): pull_request_target checks out PR head, setup-node, npx vercel with token. Arm label was visible to the adjudicator
    ("p6-V36-plc-r2", "V36-C1"): "fail",  # item-f29ec0: RULE-CONSISTENCY (both graders said partial): pull_request_target checks out PR head, runs amondnet/vercel-action with token. Arm label was visible to the adjudicator
    ("p6-V47-rem-r8", "V47-FIDELITY"): "fail",  # item-181dcf: found via the human-reviewed sample (item-181dcf): the only SELECT policy on profiles is "username is not null", so a new profile with a null username is invisible to its owner and the UPDATE that sets the username changes zero rows; same defect scanned for in all 50 V47 packets (2 runs, both graded pass before). Based on reading the SQL, not running it
    ("p6-V47-skill-r10", "V47-FIDELITY"): "fail",  # item-8cdeac: found via the human-reviewed sample (item-181dcf): the only SELECT policy on profiles is "username is not null", so a new profile with a null username is invisible to its owner and the UPDATE that sets the username changes zero rows; same defect scanned for in all 50 V47 packets (2 runs, both graded pass before). Based on reading the SQL, not running it
}

def load(path):
    return {(r["run_id"], r["criterion"]): r["status"].strip().lower() for r in csv.DictReader(open(path))}

def pmf(n1, n2, k):
    t = comb(n1 + n2, k); return {a: comb(n1, a) * comb(n2, k - a) / t for a in range(max(0, k - n2), min(n1, k) + 1)}
def conv(d1, d2):
    r = C.defaultdict(float)
    for a, p in d1.items():
        for b, q in d2.items(): r[a + b] += p * q
    return r
def perm(rows, c1, c2):
    """Stratified exact two-sided permutation test, strata = prompts. rows: run -> (prompt, cond, fail)."""
    s = C.defaultdict(lambda: {c1: [], c2: []})
    for run, (p, c, f) in rows.items():
        if c in (c1, c2): s[p][c].append(f)
    dist = {0: 1.0}; obs = 0; mean = 0
    for p, v in s.items():
        n1, n2 = len(v[c1]), len(v[c2])
        if n1 == 0 or n2 == 0: continue
        k = sum(v[c1]) + sum(v[c2]); dist = conv(dist, pmf(n1, n2, k)); obs += sum(v[c1]); mean += n1 * k / (n1 + n2)
    return obs, sum(q for a, q in dist.items() if abs(a - mean) >= abs(obs - mean) - 1e-12)

def build(p1, p2, mode):
    out = {}
    for k, s in p1.items():
        s2 = p2.get(k)
        if mode == "first": v = s
        elif mode == "second": v = s2 if s2 else s
        elif mode == "worse": v = max((s, s2), key=lambda x: RANK[x]) if s2 else s
        else: v = OV.get(k, s)
        out[k] = v
    return out

def runs_table(g, partial_fail=False, exclude=()):
    seen = C.defaultdict(list)
    for (run, c), s in g.items():
        if "-C" in c: seen[run].append(s)
    bad = ("fail", "partial") if partial_fail else ("fail",)
    rows = {}
    for run, v in seen.items():
        q = run.split("-")
        if q[1] in exclude: continue
        rows[run] = (q[1], q[2], int(any(x in bad for x in v)))
    return rows

def tally(rows, prompts=None):
    t = C.defaultdict(lambda: [0, 0])
    for run, (p, c, f) in rows.items():
        if prompts is None or p in prompts: t[c][0] += f; t[c][1] += 1
    return t

def fid(g, run): return g.get((run, run.split("-")[1] + "-FIDELITY"))

def main():
    runs_dir, out = Path(sys.argv[1]), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    p1, p2 = load(R / "pass1-all.csv"), load(R / "pass2-all.csv")
    G = {m: build(p1, p2, m) for m in ("first", "second", "worse", "adj")}
    w = csv.writer(open(out / "final-p6.csv", "w", newline="")); w.writerow(["run_id", "criterion", "status", "basis", "first", "second"])
    for (run, c), s in sorted(G["adj"].items()):
        basis = "adjudicated" if (run, c) in OV and OV[(run, c)] != p1[(run, c)] else ("second-graded" if (run, c) in p2 else "first")
        w.writerow([run, c, s, basis, p1[(run, c)], p2.get((run, c), "")])
    L = []; P = L.append
    P("# Phase 6 results (frozen skill 43abd693e0bf)\n")
    rows_all = runs_table(G["adj"])
    base_f = C.Counter(); 
    for r, (p, c, f) in rows_all.items():
        if c == "base": base_f[p] += f
    clusters = sorted({p for p, _, _ in rows_all.values()}, key=lambda x: int(x[1:]))
    informative = [p for p in clusters if LO <= base_f[p] <= HI]
    primary = informative if len(informative) >= 3 else clusters
    P(f"## Cluster selection (pre-registered rule: baseline critical-fail runs between {LO} and {HI} of 10)\n| cluster | baseline fails | informative |\n|---|---|---|")
    for p in clusters: P(f"| {p} | {base_f[p]}/10 | {'yes' if p in informative else 'no'} |")
    P(f"\nInformative clusters: {', '.join(informative) or 'none'}. Primary set: {', '.join(primary)}" + ("" if len(informative) >= 3 else " (fewer than 3 informative, so all clusters are primary by the fallback rule)") + "\n")
    PAIRS = (("skill", "rem"), ("chk", "rem"), ("skill", "chk"), ("rem", "base"), ("chk", "base"), ("skill", "base"), ("plc", "base"), ("plc", "rem"))
    def block(title, rows, prompts=None, conf=False):
        t = tally(rows, prompts)
        P(f"## {title}"); P("| arm | runs with a critical fail | runs | share |\n|---|---|---|---|")
        for c in ARMS: P(f"| {c} | {t[c][0]} | {t[c][1]} | {(t[c][0] / t[c][1]) if t[c][1] else float('nan'):.0%} |")
        sub = {r: v for r, v in rows.items() if prompts is None or v[0] in prompts}
        for a, b in PAIRS:
            o, p = perm(sub, a, b); ci = newc(t[a][0], t[a][1], t[b][0], t[b][1]) if t[a][1] and t[b][1] else (float("nan"),) * 2
            P(f"- {a} vs {b}: {t[a][0]}/{t[a][1]} vs {t[b][0]}/{t[b][1]}; stratified exact two-sided p = {p:.3g}; difference {100 * (t[a][0] / t[a][1] - t[b][0] / t[b][1]):+.1f} points, Newcombe 95% interval {100 * ci[0]:+.1f} to {100 * ci[1]:+.1f}" + (" (CONFIRMATORY)" if conf and (a, b) == ("skill", "rem") else ""))
        P("")
    block("PRIMARY: critical-fail share on the primary clusters, grades: adj", rows_all, primary, conf=True)
    for mode in ("first", "second", "worse"): block(f"Primary clusters, grades: {mode}", runs_table(G[mode]), primary)
    block("All eight clusters, grades: adj", rows_all)
    block("Primary clusters, partial counted as fail (adjudicated)", runs_table(G["adj"], True), primary)
    P("## Per-cluster table (adjudicated): runs with a critical fail / runs\n| cluster | " + " | ".join(ARMS) + " |\n|---|" + "---|" * len(ARMS))
    tp = C.defaultdict(lambda: [0, 0])
    for r, (p, c, f) in rows_all.items(): tp[(p, c)][0] += f; tp[(p, c)][1] += 1
    for p in clusters: P(f"| {p} | " + " | ".join(f"{tp[(p, c)][0]}/{tp[(p, c)][1]}" for c in ARMS) + " |")
    P("")
    P("## Per-criterion critical fails by arm (adjudicated)\n| criterion | " + " | ".join(ARMS) + " |\n|---|" + "---|" * len(ARMS))
    pc = C.defaultdict(C.Counter)
    for (run, c), s in G["adj"].items():
        if "-C" in c: pc[c][run.split("-")[2]] += (s == "fail")
    for c in sorted(pc, key=lambda x: (int(x[1:3]), x)): P(f"| {c} | " + " | ".join(str(pc[c][a]) for a in ARMS) + " |")
    P("")
    P("## Fidelity (pass share, refusals excluded)\n| grades | arm | pass | partial | fail | refusal | pass share |\n|---|---|---|---|---|---|---|")
    fres = {}
    for mode in ("first", "second", "worse", "adj"):
        for c in ARMS:
            cnt = C.Counter(fid(G[mode], r) for r in {k[0] for k in G[mode] if k[0].split("-")[2] == c})
            den = cnt["pass"] + cnt["partial"] + cnt["fail"]; fres[(mode, c)] = cnt["pass"] / den if den else float("nan")
            P(f"| {mode} | {c} | {cnt['pass']} | {cnt['partial']} | {cnt['fail']} | {cnt['refusal']} | {fres[(mode, c)]:.0%} |")
    for mode in ("first", "second", "worse"):
        P(f"- rule 2 under '{mode}': skill {fres[(mode, 'skill')]:.1%} vs reminder {fres[(mode, 'rem')]:.1%}; difference {100 * (fres[(mode, 'skill')] - fres[(mode, 'rem')]):+.1f} points (rule: not more than 10 below)")
    P("")
    tok = C.defaultdict(list); opened = [0, 0]
    for s in runs_dir.glob("p6-*/settings.json"):
        j = json.loads(s.read_text()); t = j["tokens"]; cnd = j["run_id"].split("-")[2]
        tok[cnd].append(t["input_tokens"] + t["output_tokens"])
        if cnd == "skill": opened[1] += 1; opened[0] += bool(j.get("skill_mentioned_in_log") is True)
    P("## Tokens (input + output), median per run")
    for c in ARMS:
        if tok[c]: P(f"- {c}: median {st_median(tok[c]):,.0f} (n={len(tok[c])})")
    if tok["skill"] and tok["base"]: P(f"- skill / baseline median ratio = {st_median(tok['skill']) / st_median(tok['base']):.2f} (rule 3: at most 2.0)")
    P(f"\n## Skill runs whose log mentions SKILL.md: {opened[0]}/{opened[1]} (text match; confirm by hand)\n")
    P("## Adjudications applied (run, criterion, first-pass status -> final)")
    for (run, c), v in sorted(OV.items()):
        if p1.get((run, c)) != v: P(f"- {run} {c}: {p1.get((run, c))} -> {v}")
    (out / "phase6-results.md").write_text("\n".join(L), encoding="utf-8"); print("\n".join(L))
st_median = st.median
main()
