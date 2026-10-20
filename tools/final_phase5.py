#!/usr/bin/env python3
"""Phase 5 final grades and results (ten clusters V34-V43, arms base / rem / skill / pub). Pre-registration: PHASE5-PREREG.md.
usage: python final_phase5.py RUNS_DIR OUT_DIR
Reads results/phase5/pass1-all.csv and pass2-all.csv (run_id, criterion, status) and RUNS_DIR/*/settings.json.
Adjudications (status-changing disagreements, resolved by reading the code) go in the OV dict below, each with a comment.
Treatments: adj (primary) = first pass with the listed overrides; first; second (second grader where one exists); worse (worse of both).
"""
import csv, json, sys, statistics as st, collections as C
from pathlib import Path
from math import comb

R = Path(__file__).resolve().parent.parent / "results" / "phase5"
RANK = {"pass": 0, "na": 0, "refusal": 0, "partial": 1, "fail": 2}
ARMS = ("base", "rem", "skill", "pub")
COVER = {  # pre-registered classification of OUR skill (PHASE5-PREREG.md section 3)
    "explicit": ("V34", "V41", "V42"), "adjacent": ("V35", "V38", "V39", "V40"), "not covered": ("V36", "V37", "V43")}
COVER_PUB = {"explicit": ("V34", "V38", "V41"), "adjacent": ("V35", "V39", "V40"), "not covered": ("V36", "V37", "V42", "V43")}
OV = {   # (run_id, criterion) -> final status, from adjudication by reading the code (done blind, by item id, before the key was joined)
    # V36-C1: preview.yml is a workflow_run job. For fork PRs workflow_run.pull_requests is empty, so the preview job is skipped (or fails before the token step), and the VERCEL_TOKEN is exposed only to the final step. The remaining weakness (PR code is installed in the same job before the token step) concerns same-repo authors, who already have write access. Not a fail under C1; partial because the fork protection relies on an implicit GitHub behaviour and not an explicit fork check.
    ("p5-V36-pub-r2", "V36-C1"): "partial",
    ("p5-V36-skill-r3", "V36-C1"): "partial",
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
    w = csv.writer(open(out / "final-p5.csv", "w", newline="")); w.writerow(["run_id", "criterion", "status", "basis", "first", "second"])
    for (run, c), s in sorted(G["adj"].items()):
        basis = "adjudicated" if (run, c) in OV and OV[(run, c)] != p1[(run, c)] else ("second-graded" if (run, c) in p2 else "first")
        w.writerow([run, c, s, basis, p1[(run, c)], p2.get((run, c), "")])
    L = []; P = L.append
    P("# Phase 5 results (frozen skill 43abd693e0bf, public skill 3408bccfe0e5)\n")
    def block(title, rows, prompts=None):
        t = tally(rows, prompts)
        P(f"## {title}"); P("| arm | runs with a critical fail | runs | share |\n|---|---|---|---|")
        for c in ARMS: P(f"| {c} | {t[c][0]} | {t[c][1]} | {(t[c][0] / t[c][1]) if t[c][1] else float('nan'):.0%} |")
        sub = {r: v for r, v in rows.items() if prompts is None or v[0] in prompts}
        for a, b in (("skill", "rem"), ("rem", "base"), ("skill", "base"), ("pub", "rem"), ("pub", "base"), ("skill", "pub")):
            o, p = perm(sub, a, b); P(f"- {a} vs {b}: fails in {a} = {o}; stratified exact two-sided p = {p:.3g}" + (" (CONFIRMATORY)" if (a, b) == ("skill", "rem") and prompts is None and title.startswith("Critical-fail share, all ten clusters, grades: adj") else ""))
        P("")
    for mode in ("adj", "first", "second", "worse"):
        block(f"Critical-fail share, all ten clusters, grades: {mode}", runs_table(G[mode]))
    block("Sensitivity: partial counted as fail (adjudicated)", runs_table(G["adj"], True))
    block("Sensitivity: excluding V36 (adjudicated)", runs_table(G["adj"], False, ("V36",)))
    rows = runs_table(G["adj"])
    P("## Per-cluster table (adjudicated): runs with a critical fail / runs\n| cluster | our-skill coverage | public coverage | base | rem | skill | pub |\n|---|---|---|---|---|---|---|")
    tp = C.defaultdict(lambda: [0, 0])
    for r, (p, c, f) in rows.items(): tp[(p, c)][0] += f; tp[(p, c)][1] += 1
    cov = {p: g for g, ps in COVER.items() for p in ps}; covp = {p: g for g, ps in COVER_PUB.items() for p in ps}
    for p in sorted({p for p, _ in tp}, key=lambda x: int(x[1:])):
        P(f"| {p} | {cov.get(p, '?')} | {covp.get(p, '?')} | " + " | ".join(f"{tp[(p, c)][0]}/{tp[(p, c)][1]}" for c in ARMS) + " |")
    P("")
    P("## By pre-registered coverage group (adjudicated, descriptive, not powered for a group test)")
    for title, groups in (("our skill", COVER), ("public skill", COVER_PUB)):
        P(f"### grouping by {title} coverage\n| group | clusters | base | rem | skill | pub |\n|---|---|---|---|---|---|")
        for g, ps in groups.items():
            t = tally(rows, ps); P(f"| {g} | {' '.join(ps)} | " + " | ".join(f"{t[c][0]}/{t[c][1]}" for c in ARMS) + " |")
        P("")
    P("## Per-criterion critical fails by arm (adjudicated; counts of runs with status fail)\n| criterion | base | rem | skill | pub |\n|---|---|---|---|---|")
    pc = C.defaultdict(lambda: C.Counter()); n = C.Counter()
    for (run, c), s in G["adj"].items():
        if "-C" in c:
            arm = run.split("-")[2]
            pc[c][arm] += (s == "fail")
    for run in {k[0] for k in G["adj"]}: n[run.split("-")[2]] += 1
    for c in sorted(pc, key=lambda x: (int(x[1:3]), x)): P(f"| {c} | " + " | ".join(str(pc[c][a]) for a in ARMS) + " |")
    P("")
    P("## Fidelity (pass share, refusals excluded from the denominator)\n| grades | arm | pass | partial | fail | refusal | pass share |\n|---|---|---|---|---|---|---|")
    fres = {}
    for mode in ("first", "second", "worse", "adj"):
        for c in ARMS:
            cnt = C.Counter(fid(G[mode], r) for r in {k[0] for k in G[mode] if k[0].split("-")[2] == c})
            den = cnt["pass"] + cnt["partial"] + cnt["fail"]; fres[(mode, c)] = cnt["pass"] / den if den else float("nan")
            P(f"| {mode} | {c} | {cnt['pass']} | {cnt['partial']} | {cnt['fail']} | {cnt['refusal']} | {fres[(mode, c)]:.0%} |")
    for mode in ("first", "second", "worse"):
        P(f"- rule 2 under '{mode}': skill {fres[(mode, 'skill')]:.1%} vs reminder {fres[(mode, 'rem')]:.1%}; difference {100 * (fres[(mode, 'skill')] - fres[(mode, 'rem')]):+.1f} points (rule: not more than 10 below)")
    P("")
    tok = C.defaultdict(list); opened = C.defaultdict(lambda: [0, 0])
    for s in runs_dir.glob("p5-*/settings.json"):
        j = json.loads(s.read_text()); t = j["tokens"]; cnd = j["run_id"].split("-")[2]
        tok[cnd].append(t["input_tokens"] + t["output_tokens"])
        if cnd in ("skill", "pub"): opened[cnd][1] += 1; opened[cnd][0] += bool(j.get("skill_mentioned_in_log") is True)
    P("## Tokens (input + output), median per run")
    for c in ARMS:
        if tok[c]: P(f"- {c}: median {st.median(tok[c]):,.0f} (n={len(tok[c])})")
    if tok["skill"] and tok["base"]: P(f"- skill / baseline median ratio = {st.median(tok['skill']) / st.median(tok['base']):.2f} (rule 3: at most 2.0)")
    if tok["pub"] and tok["base"]: P(f"- public / baseline median ratio = {st.median(tok['pub']) / st.median(tok['base']):.2f}")
    P("")
    P("## Did the skill arm open its skill? (settings.json `skill_mentioned_in_log`, a text match; confirm by hand)")
    for c in ("skill", "pub"): P(f"- {c}: {opened[c][0]}/{opened[c][1]} runs mention SKILL.md in the log")
    P("")
    # critical fail split by opened-or-not
    split = C.defaultdict(lambda: [0, 0])
    for s in runs_dir.glob("p5-*/settings.json"):
        j = json.loads(s.read_text()); rid = j["run_id"]; cnd = rid.split("-")[2]
        if cnd in ("skill", "pub") and rid in rows:
            k = (cnd, bool(j.get("skill_mentioned_in_log") is True)); split[k][0] += rows[rid][2]; split[k][1] += 1
    P("## Critical-fail share by whether the skill was opened (adjudicated; not randomised, exploratory)\n| arm | opened | fails | runs |\n|---|---|---|---|")
    for (c, o), (f, n_) in sorted(split.items()): P(f"| {c} | {'yes' if o else 'no'} | {f} | {n_} |")
    P("")
    P("## Adjudications applied (run, criterion, first-pass status -> final)")
    for (run, c), v in sorted(OV.items()):
        if p1.get((run, c)) != v: P(f"- {run} {c}: {p1.get((run, c))} -> {v}")
    (out / "phase5-results.md").write_text("\n".join(L), encoding="utf-8"); print("\n".join(L))
main()
