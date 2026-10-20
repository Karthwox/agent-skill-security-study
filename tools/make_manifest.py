#!/usr/bin/env python3
"""Generate a randomized, reproducible run manifest and empty run folders.

Usage:
  python make_manifest.py screen
  python make_manifest.py screenx      # the 12 extended-screen prompts (I1..O1), baseline x1 each
  python make_manifest.py confirm  --prompts B1 C2 C1
  python make_manifest.py screeny      # D2 and W2, the replacements for D1 and W1
  python make_manifest.py dev2 --n 2    # V6-V9 fresh variants, baseline and skill v0.3
  python make_manifest.py dev --n 2     # V1-V5, baseline and skill, for tuning the skill
  python make_manifest.py confirmx --prompts U1 R1 G1 O1   # confirm runs for extended-screen failures
  python make_manifest.py luna --prompts B1 B2 S1 U1 R1 G1 O1 --n 5 --with-baseline   # Phase 4a, model gpt-5.6-luna
  python make_manifest.py lunascr      # Phase 4b screen: luna baseline x1 on the 18 prompts not in Phase 4a
  python make_manifest.py lunacfm --prompts <ids>   # Phase 4b confirm: 2 more luna baselines for prompts that failed the screen
  python make_manifest.py lunaprobe    # DEV probe: v0.3 skill x3 on A3 C2 D2 I2 T1 W2 (not evidence)
  python make_manifest.py v4r1 --n 3 --with-baseline   # v0.4 round 1: 12 fresh variants V10-V21 x baseline/reminder/skill x3
  python make_manifest.py v4reg --n 5 --conds skill    # v0.4 regression: the 7 original clusters, skill only x5
  python make_manifest.py v4r2 --n 4 --with-baseline   # v0.4 draft 2 round 2: 12 new variants V22-V33 x baseline/reminder/skill x4
  python make_manifest.py agy1 --n 2 --with-baseline   # Antigravity/Gemini series: V22-V33 x baseline/reminder/skill x2 (run with run_agy.py)
  python make_manifest.py p6 --n 10   # Phase 6: 8 clusters x baseline/reminder/checklist/placebo/skill x10 (400 runs)
  python make_manifest.py p5 --n 4 --with-baseline   # Phase 5: ten OWASP-mapped clusters V34-V43 x baseline/reminder/skill/public x4 (160 runs)
  python make_manifest.py v4reg2 --n 5 --conds skill   # draft 2 regression: the 7 original clusters, skill only x5
  python make_manifest.py compare  --prompts B1 B2 S1 U1 R1 G1 O1 --n 5 --with-baseline
Writes manifest-<phase>.csv (the run order is fixed by SEED, so it is reproducible)
and runs/<run_id>/{settings.json,notes.md}. Never overwrites an existing run folder.
"""
import argparse, csv, json, random, sys
from pathlib import Path

SEED = {"screen": 20261017, "confirm": 20261018, "compare": 20261019, "screenx": 20261020, "confirmx": 20261021, "screeny": 20261022, "dev": 20261023, "dev2": 20261024, "luna": 20261025, "lunascr": 20261029, "lunacfm": 20261030, "lunaprobe": 20261102, "v4r1": 20261104, "v4reg": 20261105, "pub": 20261107, "v4r2": 20261110, "v4reg2": 20261111, "agy1": 20261120, "p5": 20261125, "p6": 20261201}
SERIES = {"screen": "scr", "confirm": "cfm", "compare": "cmp", "screenx": "scx", "confirmx": "cfx", "screeny": "scy", "dev": "dev", "dev2": "dv2", "luna": "lun", "lunascr": "lns", "lunacfm": "lnc", "lunaprobe": "lnp", "v4r1": "v41", "v4reg": "v4g", "pub": "pub", "v4r2": "v42", "v4reg2": "v4h", "agy1": "agy", "p5": "p5", "p6": "p6"}
ALL_PROMPTS = ["P1","P2","P3","A1","A2","A3","S1","S2","B1","B2","B3","C1","C2"]
DEV_PROMPTS = ["V1","V2","V3","V4","V5"]
DEV2_PROMPTS = ["V6","V7","V8","V9"]   # fresh variants after skill v0.3 tuning; also never Phase 3 evidence   # skill-tuning set, never used as Phase 3 evidence
REPLACEMENT_PROMPTS = ["D2","W2"]   # replace D1 and W1 (retired: weak probes)
EXT_PROMPTS = ["I1","I2","I3","U1","R1","R2","L1","T1","D1","G1","W1","O1"]
LUNA_SCREEN_PROMPTS = ["P1","P2","P3","A1","A2","A3","S2","B3","C1","C2","I1","I2","I3","R2","L1","T1","D2","W2"]   # 25 active prompts minus the 7 of Phase 4a
DEV4_PROMPTS = ["V%d" % i for i in range(22, 34)]   # round-2 fresh variants (criteria-dev4.md)
DEV6_PROMPTS = ["V34","V36","V37","V40","V44","V45","V46","V47"]   # Phase 6: four Phase 5 clusters with headroom plus four new ones (criteria-p5.md, criteria-p6.md)
DEV5_PROMPTS = ["V%d" % i for i in range(34, 44)]   # Phase 5: ten OWASP-mapped clusters (criteria-p5.md)
DEV3_PROMPTS = ["V%d" % i for i in range(10, 22)]   # fresh variants of the six luna-only clusters (criteria-dev3.md)
COND = {"base": "baseline", "rem": "reminder", "skill": "skill", "pub": "public", "chk": "checklist", "plc": "placebo"}

def plan(phase, prompts, n, with_baseline=False, conds=None, spec=None):
    rows = []
    if phase in ("screen", "screenx", "screeny", "lunascr"):
        # one baseline run per prompt
        rows = [(p, "base", 1) for p in prompts]
    elif phase in ("confirm", "confirmx", "lunacfm"):
        # two MORE baseline runs (r2, r3) on prompts that failed in screening
        rows = [(p, "base", r) for p in prompts for r in (2, 3)]
    elif phase == "lunaprobe":
        rows = [(p, "skill", r) for p in prompts for r in range(1, n + 1)]
    elif phase in ("dev", "dev2"):
        # baseline and skill, n runs each, for tuning the skill
        rows = [(p, c, r) for p in prompts for c in ("base", "skill") for r in range(1, n + 1)]
    else:
        # Phase 3: fresh baseline, reminder and skill, n runs each, interleaved in one random order.
        # Fresh baselines (not the screening/confirm runs): those prompts were SELECTED because the baseline failed,
        # so reusing them would overstate the baseline failure rate (selection bias).
        if spec:   # e.g. 'base:1-3,rem:1-5': exactly these replicates of these conditions
            out = []
            for part in spec.split(','):
                c, rr = part.split(':'); lo, hi = (rr.split('-') + [rr])[:2] if '-' in rr else (rr, rr)
                out += [(p, c, r) for p in prompts for r in range(int(lo), int(hi) + 1)]
            return out
        conds = tuple(conds) if conds else (("base", "rem", "skill") if with_baseline else ("rem", "skill"))
        rows = [(p, c, r) for p in prompts for c in conds for r in range(1, n + 1)]
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("phase", choices=SERIES)
    ap.add_argument("--prompts", nargs="+", default=ALL_PROMPTS)
    ap.add_argument("--n", type=int, default=5)
    ap.add_argument("--conds", nargs="+", choices=["base","rem","skill","pub","chk","plc"], help="compare phase: only these conditions (use to split the run into parts)")
    ap.add_argument("--spec", help="compare phase: exact cells, e.g. base:1-3,rem:1-5")
    ap.add_argument("--tag", default="", help="suffix for the manifest file name, e.g. -a")
    ap.add_argument("--with-baseline", action="store_true", help="compare phase: include fresh baseline runs")
    a = ap.parse_args()
    if a.phase == "screenx" and a.prompts == ALL_PROMPTS: a.prompts = EXT_PROMPTS
    if a.phase == "screeny" and a.prompts == ALL_PROMPTS: a.prompts = REPLACEMENT_PROMPTS
    if a.phase == "lunascr" and a.prompts == ALL_PROMPTS: a.prompts = LUNA_SCREEN_PROMPTS
    if a.phase == "lunaprobe" and a.prompts == ALL_PROMPTS: a.prompts = ["A3","C2","D2","I2","T1","W2"]
    if a.phase == "v4r1" and a.prompts == ALL_PROMPTS: a.prompts = DEV3_PROMPTS
    if a.phase in ("v4r2", "agy1") and a.prompts == ALL_PROMPTS: a.prompts = DEV4_PROMPTS
    if a.phase == "p5" and a.prompts == ALL_PROMPTS: a.prompts = DEV5_PROMPTS
    if a.phase == "p6" and a.prompts == ALL_PROMPTS: a.prompts = DEV6_PROMPTS
    if a.phase in ("v4reg", "v4reg2") and a.prompts == ALL_PROMPTS: a.prompts = ["B1","B2","S1","U1","R1","G1","O1"]
    if a.phase == "pub":
        if a.prompts == ALL_PROMPTS: a.prompts = ["B1","B2","S1","U1","R1","G1","O1"]
        # public-skill phase: reminder and public skill, interleaved (baseline reused from Phase 4a, see PHASE4D-PREREG.md)
    if a.phase == "dev" and a.prompts == ALL_PROMPTS: a.prompts = DEV_PROMPTS
    if a.phase == "dev2" and a.prompts == ALL_PROMPTS: a.prompts = DEV2_PROMPTS
    bad = [p for p in a.prompts if p not in ALL_PROMPTS + EXT_PROMPTS + REPLACEMENT_PROMPTS + DEV_PROMPTS + DEV2_PROMPTS + DEV3_PROMPTS + DEV4_PROMPTS + DEV5_PROMPTS + DEV6_PROMPTS + ["V44","V45","V46","V47"]]
    if bad: sys.exit(f"unknown prompt ids: {bad}")
    if a.phase == "p5" and not a.conds: a.conds = ["base", "rem", "skill", "pub"]
    if a.phase == "p6" and not a.conds: a.conds = ["base", "rem", "chk", "plc", "skill"]
    rows = plan(a.phase, a.prompts, a.n, a.with_baseline, a.conds, a.spec)
    if a.phase == "pub":   # original seven clusters x5, plus the six luna-only clusters x3, reminder and public skill, one interleaved order
        rows = [(p, c, r) for p in ["B1","B2","S1","U1","R1","G1","O1"] for c in ("rem","skill") for r in range(1, 6)]
        rows += [(p, c, r) for p in ["A3","C2","D2","I2","T1","W2"] for c in ("rem","skill") for r in range(1, 4)]
    if a.phase == "agy1":   # replicate-blocked order: every cell's r1 first, then every r2 (a usage limit then leaves a balanced design)
        blocks = []
        for rep in sorted({r for _, _, r in rows}):
            blk = [y for y in rows if y[2] == rep]; random.Random(SEED[a.phase] + rep).shuffle(blk); blocks += blk
        rows = blocks
    else:
        rng = random.Random(SEED[a.phase]); rng.shuffle(rows)
    here = Path(__file__).parent
    out = here / f"manifest-{a.phase}{a.tag}.csv"
    with out.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["order","run_id","prompt","condition","run","status","date_run"])
        for i, (p, c, r) in enumerate(rows, 1):
            rid = f"{SERIES[a.phase]}-{p}-{c}-r{r}"
            w.writerow([i, rid, p, COND[c], r, "todo", ""])
            d = here / "runs" / rid
            if not d.exists():
                d.mkdir(parents=True)
                (d / "settings.json").write_text(json.dumps({
                    "run_id": rid, "prompt": p, "condition": COND[c],
                    "harness": "", "harness_version": "", "model": "", "reasoning_effort": "",
                    "sandbox_mode": "", "approval_policy": "", "skill_version": "" if c == "skill" else "n/a",
                    "skill_install_path": "" if c == "skill" else "n/a", "date": ""}, indent=2))
                (d / "notes.md").write_text(f"# {rid}\n\nOddities (crashes, manual interventions, questions asked):\n")
    print(f"wrote {out} ({len(rows)} runs)")

if __name__ == "__main__":
    main()
