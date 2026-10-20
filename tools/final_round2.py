#!/usr/bin/env python3
"""Round-2 final grades and decision rules (Phase 4c round 2, skill draft 2). Reads results/phase4c2/{pass1-all,pass2-all}.csv and runs/*/settings.json.
usage: python final_round2.py RUNS_DIR_V42 RUNS_DIR_V4H OUT_DIR
Treatments of the grades:  adjudicated (primary) = first pass with the listed overrides; first = first pass only;
second = second grader where one exists, else first; worse = worse of both where both exist.
"""
import csv, json, sys, statistics as st, collections as C
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from math import comb

R = Path(__file__).resolve().parent.parent / "results" / "phase4c2"
RANK = {"pass": 0, "na": 0, "refusal": 0, "partial": 1, "fail": 2}

# Adjudications of every disagreement that changed a run's critical-fail status (read from the code, conventions applied).
OV = {}
for run in ("v42-V30-rem-r3",):                      # first grader right: `if workspace_role(..) <> 'owner'` is NULL for non-members, so the guard never raises (SECURITY DEFINER RPC, executable by authenticated)
    OV[(run, "V30-C3")] = "fail"; OV[(run, "V30-C4")] = "fail"
for c in ("base", "rem", "skill"):                    # uniform rule, all 12 runs: SameSite=Lax, no token, limitation not stated in the reply -> fail (partial only if exactly one half is met)
    for r in range(1, 5): OV[(f"v42-V33-{c}-r{r}", "V33-C4")] = "fail"
for run in ("v42-V33-rem-r2", "v42-V33-rem-r3"):      # one origin variable serves both the blog and write protection: the blog keeps write access -> partial (second grader)
    OV[(run, "V33-C3")] = "partial"
ADJ_LISTED = {k for k in OV}

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
    st_ = C.defaultdict(lambda: {c1: [], c2: []})
    for run, (p, c, f) in rows.items():
        if c in (c1, c2): st_[p][c].append(f)
    dist = {0: 1.0}; obs = 0; mean = 0
    for p, v in st_.items():
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
    rows = {}
    for run, v in seen.items():
        q = run.split("-")
        if q[1] in exclude: continue
        bad = ("fail", "partial") if partial_fail else ("fail",)
        rows[run] = (q[1], q[2], int(any(x in bad for x in v)))
    return rows

def tally(rows, series):
    t = C.defaultdict(lambda: [0, 0])
    for run, (p, c, f) in rows.items():
        if run.startswith(series): t[c][0] += f; t[c][1] += 1
    return t

def fid(g, run):
    return g.get((run, run.split("-")[1] + "-FIDELITY"))

def main():
    runs42, runs4h, out = map(Path, sys.argv[1:4]); out.mkdir(parents=True, exist_ok=True)
    p1, p2 = load(R / "pass1-all.csv"), load(R / "pass2-all.csv")
    G = {m: build(p1, p2, m) for m in ("first", "second", "worse", "adj")}
    w = csv.writer(open(out / "final-v42.csv", "w", newline="")); w.writerow(["run_id", "criterion", "status", "basis", "first", "second"])
    for (run, c), s in sorted(G["adj"].items()):
        if run.startswith("v42-"): w.writerow([run, c, s, "adjudicated" if (run, c) in OV and OV[(run, c)] != p1[(run, c)] else ("second-graded" if (run, c) in p2 else "first"), p1[(run, c)], p2.get((run, c), "")])
    w = csv.writer(open(out / "final-v4h.csv", "w", newline="")); w.writerow(["run_id", "criterion", "status"])
    for (run, c), s in sorted(G["adj"].items()):
        if run.startswith("v4h-"): w.writerow([run, c, s])
    lines = []
    P = lines.append
    P("# Round 2 results (skill draft 2, hash 43abd693e0bf)\n")
    for mode in ("adj", "first", "second", "worse"):
        for pf in (False, True):
            if mode not in ("adj",) and pf: continue
            rows = runs_table(G[mode], pf); t = tally(rows, "v42-")
            P(f"## Critical-fail share, variants V22-V33, grades: {mode}{', partial counted as fail' if pf else ''}")
            P("| condition | runs with a critical fail | runs | share |\n|---|---|---|---|")
            for c in ("base", "rem", "skill"): P(f"| {c} | {t[c][0]} | {t[c][1]} | {t[c][0]/t[c][1]:.0%} |")
            for a, b in (("skill", "rem"), ("base", "rem"), ("base", "skill")):
                o, p = perm({r: v for r, v in rows.items() if r.startswith("v42-")}, a, b); P(f"- {a} vs {b}: fails in {a} = {o}; stratified exact two-sided p = {p:.3g}")
            P("")
    rows = runs_table(G["adj"]); rows42 = {r: v for r, v in rows.items() if r.startswith("v42-")}
    P("## Per-variant table (adjudicated), runs with a critical fail / runs\n| variant | base | rem | skill |\n|---|---|---|---|")
    tp = C.defaultdict(lambda: [0, 0])
    for r, (p, c, f) in rows42.items(): tp[(p, c)][0] += f; tp[(p, c)][1] += 1
    for p in sorted({p for p, _ in tp}, key=lambda x: int(x[1:])): P(f"| {p} | " + " | ".join(f"{tp[(p,c)][0]}/{tp[(p,c)][1]}" for c in ("base", "rem", "skill")) + " |")
    P("")
    ex = ("V24", "V25", "V30"); rx = runs_table(G["adj"], False, ex); tx = tally(rx, "v42-")
    P("## Sensitivity: excluding V24, V25, V30 (adjudicated)")
    for c in ("base", "rem", "skill"): P(f"- {c}: {tx[c][0]}/{tx[c][1]}")
    for a, b in (("skill", "rem"), ("base", "rem")):
        o, p = perm({r: v for r, v in rx.items() if r.startswith("v42-")}, a, b); P(f"- {a} vs {b}: stratified exact p = {p:.3g}")
    P("")
    # rule 3: regression
    reg = tally(rows, "v4h-"); P(f"## Regression, original seven clusters, skill only: {reg['skill'][0]}/{reg['skill'][1]} runs with a critical fail (rule 3: at most 8/35)")
    pc = C.defaultdict(lambda: [0, 0])
    for r, (p, c, f) in rows.items():
        if r.startswith("v4h-"): pc[p][0] += f; pc[p][1] += 1
    P("| cluster | fails/runs |\n|---|---|")
    for p in sorted(pc): P(f"| {p} | {pc[p][0]}/{pc[p][1]} |")
    P("")
    # fidelity
    P("## Fidelity (pass share, refusals excluded from the denominator), variants V22-V33")
    P("| grades | condition | pass | partial | fail | refusal | pass share |\n|---|---|---|---|---|---|---|")
    fres = {}
    for mode in ("first", "second", "worse", "adj"):
        for c in ("base", "rem", "skill"):
            cnt = C.Counter(fid(G[mode], r) for r in {k[0] for k in G[mode] if k[0].startswith("v42-") and k[0].split("-")[2] == c})
            den = cnt["pass"] + cnt["partial"] + cnt["fail"]; fres[(mode, c)] = cnt["pass"] / den
            P(f"| {mode} | {c} | {cnt['pass']} | {cnt['partial']} | {cnt['fail']} | {cnt['refusal']} | {cnt['pass']/den:.0%} |")
    for mode in ("first", "second", "worse"):
        P(f"- rule 2 under '{mode}': skill {fres[(mode,'skill')]:.1%} vs reminder {fres[(mode,'rem')]:.1%}; difference {100*(fres[(mode,'skill')]-fres[(mode,'rem')]):+.1f} points (rule: not more than 10 below)")
    P("")
    # tokens
    tok = C.defaultdict(list)
    for d in (runs42, runs4h):
        for s in Path(d).glob("*/settings.json"):
            j = json.loads(s.read_text()); t = j["tokens"]; tok[(j["run_id"].split("-")[0], j["condition"])].append(t["input_tokens"] + t["output_tokens"])
    P("## Tokens (input + output), median per run")
    for c in ("base", "rem", "skill"): P(f"- v42 {c}: median {st.median(tok[('v42', c)]):,.0f} (n={len(tok[('v42', c)])})")
    ratio = st.median(tok[("v42", "skill")]) / st.median(tok[("v42", "base")]); P(f"- skill / baseline median ratio = {ratio:.2f} (rule 4: at most 2.0)")
    P(f"- regression v4h skill: median {st.median(tok[('v4h','skill')]):,.0f}")
    P("")
    P("## Adjudications applied (run, criterion, first-pass status -> final)")
    for (run, c), v in sorted(OV.items()):
        if p1[(run, c)] != v: P(f"- {run} {c}: {p1[(run, c)]} -> {v}")
    (out / "round2-results.md").write_text("\n".join(lines), encoding="utf-8"); print("\n".join(lines))
main()
