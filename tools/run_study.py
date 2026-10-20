#!/usr/bin/env python3
"""Scripted runner for the study. One command runs the next runs in a manifest.

  python run_study.py init --series-id S1 --model <name> --effort low --work-root <short path>   (add --skill-dir <path> before skill runs)
  python run_study.py run manifest-screen.csv            # all todo runs in manifest order
  python run_study.py run manifest-screen.csv --only scr-B1-base-r1
  python run_study.py run manifest-screen.csv --limit 3
  python run_study.py run manifest-screen.csv --dry-run  # show the command, run nothing
  python run_study.py reset manifest-screen.csv scr-B1-base-r1   # delete a run's folders and mark it todo again

Settings come from series.json (written once by `init`) so every run in a series is identical.
Items marked [verify] are codex behaviors I could not confirm; the runner records what it sees.
"""
import argparse, csv, datetime, hashlib, json, os, re, shutil, signal, subprocess, sys, time, zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TESTS = HERE.parent
SERIES_FILE = HERE / "series.json"
EXCLUDE_DIRS = {"node_modules", ".next", ".git", "dist", "build", ".venv", "__pycache__", ".turbo", ".npm-cache", ".cache", ".pnpm-store", ".yarn", ".npm"}
PATHSPEC_EXCLUDE = [f":(exclude){d}" for d in sorted(EXCLUDE_DIRS - {".git"})] + [":(exclude)package-lock.json"]

def now(): return datetime.datetime.now().astimezone().isoformat(timespec="seconds")
def codex_home(): return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))

# ---------------------------------------------------------------- init
def cmd_init(a):
    s = {"series_id": a.series_id, "codex_bin": a.codex_bin, "model": a.model, "effort": a.effort,
         "sandbox": a.sandbox, "approval": "never", "windows_sandbox": a.windows_sandbox, "ignore_user_config": not a.keep_user_config, "ignore_rules": not a.keep_rules, "network_access": not a.no_network,
         "skill_dir": str(Path(a.skill_dir).resolve()) if a.skill_dir else None, "skill_install_subpath": a.skill_subpath, "skill_install_name": a.skill_name,
         "pub_skill_dir": str(Path(a.pub_skill_dir).resolve()) if getattr(a, "pub_skill_dir", None) else None, "pub_skill_name": getattr(a, "pub_skill_name", "vibe-security"),
         "work_root": str(Path(a.work_root).resolve()), "timeout_minutes": 25, "max_followups": 2}
    SERIES_FILE.write_text(json.dumps(s, indent=2))
    print(f"wrote {SERIES_FILE}\n{json.dumps(s, indent=2)}")

# ---------------------------------------------------------------- helpers
def load_series():
    if not SERIES_FILE.exists(): sys.exit("series.json missing: run `init` first")
    return json.loads(SERIES_FILE.read_text())

def skill_for(s, cond):
    """(folder, install name) of the skill used by condition `skill` (ours) or `pub` (the public skill)."""
    if cond == "pub": return s.get("pub_skill_dir"), s.get("pub_skill_name", "vibe-security")
    return s.get("skill_dir"), s.get("skill_install_name", "vibe-skill")

def parse_id(run_id):
    m = re.fullmatch(r"([a-z0-9]+)-([A-Z]\d+)-(base|rem|chk|plc|skill|pub)-r(\d+)", run_id)
    if not m: sys.exit(f"bad run id {run_id}")
    return m.group(2), m.group(3), int(m.group(4))

def preflight(s, allow_dirty):
    """Baselines must not see global skills or rules. Refuse if the environment is not clean."""
    problems = []
    for p in [codex_home() / "skills", Path.home() / ".agents" / "skills"]:
        extra = [x.name for x in p.iterdir() if x.name != ".system"] if p.exists() else []   # .system = Codex's bundled skills (stock harness)
        if extra: problems.append(f"{p} contains user skills: {extra[:5]}")
    for p in [codex_home() / "AGENTS.md", Path.home() / "AGENTS.md"]:
        if p.exists(): problems.append(f"{p} exists (global instructions)")
    if problems and not allow_dirty:
        print("PREFLIGHT FAILED (would contaminate baselines):"); [print("  -", x) for x in problems]
        sys.exit("move/remove those, or pass --allow-dirty and note it in the paper")
    if shutil.which(s["codex_bin"]) is None: sys.exit(f"{s['codex_bin']} not found on PATH")
    return problems

def sh(cmd, cwd, **kw):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)

def prepare_workdir(s, suite, prompt_id, cond, run_id):
    wd = Path(s["work_root"]) / run_id
    if wd.exists(): sys.exit(f"{wd} already exists; refusing to reuse a run folder")
    start = suite["prompts"][prompt_id]["start"]
    if start == "empty": wd.mkdir(parents=True)
    else: shutil.copytree(TESTS / "fixtures" / start, wd, ignore=shutil.ignore_patterns("node_modules", ".next", ".git"))
    if cond in ("skill", "pub"):
        sdir, sname = skill_for(s, cond)
        if not sdir or not Path(sdir).is_dir():
            sys.exit(f"{cond} run requested but its skill folder is not set/valid in series.json: re-run init with --skill-dir / --pub-skill-dir")
        dest = wd / s["skill_install_subpath"] / sname
        shutil.copytree(sdir, dest, ignore=shutil.ignore_patterns("_authoring", ".git", "__pycache__"))
    sh(["git", "init", "-q"], wd)
    (wd / ".gitkeep").touch() if start == "empty" and cond not in ("skill", "pub") else None
    sh(["git", "add", "-A"], wd)
    sh(["git", "-c", "user.name=study", "-c", "user.email=study@example.invalid", "commit", "-q", "-m", "initial", "--allow-empty"], wd)
    return wd

def base_flags(s):
    f = ["--json", "-m", s["model"],
         "-c", f'sandbox_mode="{s["sandbox"]}"',
         "-c", f'approval_policy="{s["approval"]}"',
         "-c", f'model_reasoning_effort="{s["effort"]}"',               # [verify] key name
         "-c", f'sandbox_workspace_write.network_access={str(s["network_access"]).lower()}',  # [verify]
         ]
    if s.get("windows_sandbox"): f += ["-c", f'windows.sandbox="{s["windows_sandbox"]}"']
    if s.get("ignore_user_config", True): f.append("--ignore-user-config")
    if s.get("ignore_rules", True): f.append("--ignore-rules")
    return f

def kill_tree(p):
    try:
        if os.name == "nt": subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True)
        else: os.killpg(p.pid, signal.SIGKILL)
    except Exception: pass

def run_codex(s, wd, argv_tail, prompt, events_path, stderr_path, last_path, timeout_s):
    cmd = [shutil.which(s["codex_bin"]), "exec"] + argv_tail
    kw = dict(cwd=wd, stdin=subprocess.PIPE, stdout=open(events_path, "ab"), stderr=open(stderr_path, "ab"), text=True, encoding="utf-8", errors="replace")
    if os.name != "nt": kw["start_new_session"] = True
    p = subprocess.Popen(cmd, **kw)
    try:
        p.communicate(prompt, timeout=timeout_s); return p.returncode, False
    except subprocess.TimeoutExpired:
        kill_tree(p); p.wait(); return -9, True

def looks_like_question(text):
    """True only if one of the last three non-empty lines actually ends in a question mark
    (code spans, links and URLs such as `GET /api/search?q=` are ignored)."""
    lines = [l for l in text.strip().splitlines() if l.strip()][-3:]
    for l in lines:
        l = re.sub(r"`[^`]*`", "", l)
        l = re.sub(r"\[[^\]]*\]\([^)]*\)", "", l)
        l = re.sub(r"https?://\S+", "", l)
        if re.search(r"\?[\s\"')\]*_]*$", l.strip()): return True
    return False

def pick_reply(suite, prompt_id, text):
    r = suite["replies"]
    if prompt_id in r: return r[prompt_id]
    if re.search(r"\b(api key|key|url|credential|secret|\.env|token)\b", text, re.I): return r["credentials"]
    return r["default"]

def changed_files(wd):
    out = sh(["git", "status", "--porcelain"], wd).stdout.strip().splitlines()
    return len(out)

def save_patch(wd, out):
    """Stage everything except junk dirs and save the diff vs the initial commit; return list of changed source files."""
    sh(["git", "add", "-A", "--", "."] + PATHSPEC_EXCLUDE, wd)
    names = sh(["git", "diff", "--cached", "--name-only"] + ["--", "."] + PATHSPEC_EXCLUDE, wd).stdout.split()
    Path(out).write_text(sh(["git", "diff", "--cached", "--binary"] + ["--", "."] + PATHSPEC_EXCLUDE, wd).stdout or "", encoding="utf-8")
    return names

def log_signals(blob):
    """Cheap text signals from the session log (confirm by hand): bundled-skill reads, web tool use."""
    return {"bundled_skill_reads": sorted(set(re.findall(r"skills[/\\]+\.system[/\\]+([A-Za-z0-9_-]+)", blob))),
            "web_tool_calls": len(re.findall(r"tools\.web__run", blob))}

def find_session_logs(wd, since):
    root = codex_home() / "sessions"
    if not root.exists(): return []
    needle = json.dumps(str(wd))[1:-1]
    hits = []
    for f in root.rglob("*.jsonl"):
        if f.stat().st_mtime >= since - 2:
            try:
                with f.open("r", encoding="utf-8", errors="ignore") as fh:
                    if needle in fh.read(200_000): hits.append(f)
            except OSError: pass
    return sorted(hits, key=lambda x: x.stat().st_mtime)

def token_totals(events_path):
    tot = {"input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0, "reasoning_output_tokens": 0}
    for line in Path(events_path).read_text(encoding="utf-8", errors="ignore").splitlines():
        try: e = json.loads(line)
        except ValueError: continue
        if e.get("type") == "turn.completed":
            for k in tot: tot[k] += (e.get("usage") or {}).get(k, 0) or 0
    return tot

def zip_project(wd, out):
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(wd):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for fn in files: z.write(Path(root) / fn, Path(root, fn).relative_to(wd))

def bundled_skills():
    """Names of Codex's own built-in skills (stock harness), recorded per run for the paper."""
    d = codex_home() / "skills" / ".system"
    return sorted(x.name for x in d.iterdir()) if d.is_dir() else []

def skill_dir_hash(d):
    h = hashlib.sha256()
    d = Path(d)
    files = [f for f in d.rglob("*") if f.is_file() and "_authoring" not in f.parts and "__pycache__" not in f.parts]
    for f in sorted(files, key=lambda f: f.relative_to(d).as_posix()):   # same order and separators on Windows and Linux
        h.update(f.relative_to(d).as_posix().encode()); h.update(f.read_bytes())
    return h.hexdigest()[:12]

# ---------------------------------------------------------------- one run
def do_run(s, suite, run_id, dry):
    prompt_id, cond, _ = parse_id(run_id)
    text = suite["prompts"][prompt_id]["text"]
    if cond == "rem": text = f'{text} {suite["reminder"]}'
    if cond == "chk": text = f'{text} {suite["checklist"]}'
    if cond == "plc": text = f'{text} {suite["placebo"]}'
    rdir = HERE / "runs" / run_id; rdir.mkdir(parents=True, exist_ok=True)
    if dry:
        print(f"[dry] {run_id}: codex exec {' '.join(base_flags(s))} -C <workdir> -   (prompt via stdin)\n[dry] prompt: {text}"); return "dry"
    wd = prepare_workdir(s, suite, prompt_id, cond, run_id)
    ver = sh([shutil.which(s["codex_bin"]), "--version"], wd).stdout.strip()
    t0 = time.time(); started = now()
    events, err = rdir / "events.jsonl", rdir / "stderr.txt"
    turns, followups, timed_out, rc = [], 0, False, 0
    flags = base_flags(s) + ["-C", str(wd), "-o", str(rdir / "last_message_1.txt")]
    rc, timed_out = run_codex(s, wd, flags, text, events, err, None, s["timeout_minutes"] * 60)
    n = 1
    while not timed_out and rc == 0 and followups < s["max_followups"]:
        last = (rdir / f"last_message_{n}.txt")
        msg = last.read_text(encoding="utf-8", errors="ignore") if last.exists() else ""
        if not (looks_like_question(msg) and changed_files(wd) == 0): break
        reply = pick_reply(suite, prompt_id, msg); followups += 1; n += 1
        (rdir / f"followup_{followups}.txt").write_text(reply, encoding="utf-8")
        tail = ["resume", "--last"] + [x for x in base_flags(s) if x not in ("--ignore-rules",)] + ["-o", str(rdir / f"last_message_{n}.txt")]  # [verify] resume flags
        rc, timed_out = run_codex(s, wd, tail, reply, events, err, None, s["timeout_minutes"] * 60)
    final = rdir / f"last_message_{n}.txt"
    final_msg = final.read_text(encoding="utf-8", errors="ignore") if final.exists() else ""
    ended_q = looks_like_question(final_msg)
    logs = find_session_logs(wd, t0)
    blob = ""
    for i, f in enumerate(logs, 1):
        shutil.copy(f, rdir / (f"session.jsonl" if len(logs) == 1 else f"session_{i}.jsonl")); blob += f.read_text(encoding="utf-8", errors="ignore")
    changed_names = save_patch(wd, rdir / "changes.patch")
    zip_project(wd, rdir / "project.zip")
    settings = {
        "run_id": run_id, "prompt": prompt_id, "condition": cond, "series_id": s["series_id"],
        "harness": "codex exec", "harness_version": ver, "model": s["model"], "reasoning_effort": s["effort"],
        "sandbox_mode": s["sandbox"], "approval_policy": s["approval"], "network_access": s["network_access"],
        "skill_version": skill_dir_hash(skill_for(s, cond)[0]) if cond in ("skill", "pub") else "n/a",
        "skill_install_path": (s["skill_install_subpath"] + "/" + skill_for(s, cond)[1]) if cond in ("skill", "pub") else "n/a",
        "prompt_sha256": hashlib.sha256(text.encode()).hexdigest()[:16],
        "date_start": started, "minutes": round((time.time() - t0) / 60, 2), "exit_code": rc, "timed_out": timed_out,
        "followups_sent": followups, "ended_with_question": ended_q, "files_changed": changed_files(wd), "source_files_changed": len(changed_names), "source_files": changed_names, **log_signals(blob),
        "tokens": token_totals(events), "session_logs_found": len(logs), "bundled_system_skills": bundled_skills(),
        "skill_mentioned_in_log": ("SKILL.md" in blob) if cond in ("skill", "pub") else "n/a",   # grep only; confirm from log by hand
        "security_reference_in_log": ("references/" in blob) if cond in ("skill", "pub") else "n/a",
    }
    (rdir / "settings.json").write_text(json.dumps(settings, indent=2), encoding="utf-8")
    status = "timeout" if timed_out else ("error" if rc != 0 else "done")
    if status == "done" and settings["source_files_changed"] == 0 and not ended_q: status = "nochange"   # agent did nothing: check stderr.txt (sandbox/auth problem?)
    if status == "done" and "blocked by policy" in err.read_text(encoding="utf-8", errors="ignore"): status = "blocked"
    if not logs: status += "+nolog"
    print(f"{run_id}: {status} in {settings['minutes']} min, files changed {settings['files_changed']}, followups {followups}, ended_with_question {ended_q}")
    return status

def update_manifest(path, run_id, status):
    rows = list(csv.DictReader(open(path, newline="")))
    for r in rows:
        if r["run_id"] == run_id: r["status"], r["date_run"] = status, now()
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

def _rm(path):
    """rmtree that also clears read-only bits (git objects on Windows)."""
    def onerr(fn, p, exc):
        try: os.chmod(p, 0o700); fn(p)
        except Exception: pass
    if Path(path).exists(): shutil.rmtree(path, onerror=onerr)
    return not Path(path).exists()

def cmd_reset(a):
    s = load_series(); mpath = HERE / a.manifest
    for rid in a.run_ids:
        parse_id(rid)
        wd = Path(s["work_root"]) / rid
        ok1 = _rm(wd); ok2 = _rm(HERE / "runs" / rid)
        if not (ok1 and ok2):
            print(f"{rid}: COULD NOT DELETE {'work folder ' + str(wd) if not ok1 else ''} {'run folder' if not ok2 else ''}")
            print("  Close any terminal/Codex using it, then try again. If it still fails (files owned by the sandbox account), run in an ADMIN PowerShell:")
            print(f'    takeown /f "{wd}" /r /d y ; icacls "{wd}" /grant "$env:USERNAME:(OI)(CI)F" /t ; Remove-Item -Recurse -Force "{wd}"')
            continue
        rows = list(csv.DictReader(open(mpath, newline="")))
        for r in rows:
            if r["run_id"] == rid: r["status"], r["date_run"] = "todo", ""
        with open(mpath, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
        print(f"{rid}: reset (work folder and run folder deleted, manifest row set to todo)")

def cmd_run(a):
    import types
    s, suite = load_series(), json.loads((HERE / "suite.json").read_text())
    if not a.dry_run: preflight(s, a.allow_dirty)
    mpath = HERE / a.manifest
    def get_todo():
        t = [r["run_id"] for r in csv.DictReader(open(mpath, newline="")) if r["status"] == "todo"]
        if a.only: t = [r for r in t if r == a.only]
        if a.limit: t = t[: a.limit]
        return t
    for c_ in ("skill", "pub"):
        if any(parse_id(r)[1] == c_ for r in get_todo()) and not (skill_for(s, c_)[0] and Path(skill_for(s, c_)[0]).is_dir()):
            sys.exit(f"manifest contains {c_} runs but their skill folder is not set: re-run init with --skill-dir and --pub-skill-dir")
    waits = 0
    while True:
        todo, streak, tripped = get_todo(), [], False
        for rid in todo:
            try:
                st = do_run(s, suite, rid, a.dry_run)
            except SystemExit: raise
            except Exception as ex:   # one bad run must not kill the batch
                import traceback; traceback.print_exc()
                (HERE / "runs" / rid).mkdir(parents=True, exist_ok=True)
                (HERE / "runs" / rid / "crash.txt").write_text(traceback.format_exc(), encoding="utf-8")
                st = "crash"; print(f"{rid}: CRASH ({type(ex).__name__}); continuing. Use `reset` before retrying it.")
            if st != "dry": update_manifest(mpath, rid, st)
            bad = st.split("+")[0] in ("error", "crash", "nochange")
            streak = streak + [rid] if bad else []
            if len(streak) >= a.stop_after:      # circuit breaker: usually a usage limit or an auth/sandbox problem
                tripped = True; break
        if not tripped: break
        log = HERE / "failed-attempts.log"
        with log.open("a", encoding="utf-8") as f:
            for rid in streak:
                e = HERE / "runs" / rid / "stderr.txt"
                f.write(f"--- {now()} {rid}\n" + (e.read_text(encoding="utf-8", errors="ignore")[-1500:] if e.exists() else "(no stderr)") + "\n")
        print(f"STOPPED: {len(streak)} runs in a row failed ({', '.join(streak)}). Likely a usage limit or a sandbox/auth problem. stderr tails saved to {log.name}.")
        cmd_reset(types.SimpleNamespace(manifest=a.manifest, run_ids=streak))   # failed rows go back to todo
        waits += 1
        if a.wait_minutes <= 0 or waits > a.max_waits:
            print("Not retrying. Fix the cause, then run the same command again; the failed runs are already back to todo." if a.wait_minutes <= 0 else "Gave up after the maximum number of waits; the failed runs are back to todo.")
            return
        print(f"Waiting {a.wait_minutes} min, then resuming (wait {waits} of {a.max_waits}). Ctrl+C to stop.")
        time.sleep(a.wait_minutes * 60)

def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="c", required=True)
    i = sub.add_parser("init"); i.add_argument("--series-id", required=True); i.add_argument("--model", required=True)
    i.add_argument("--effort", default="low"); i.add_argument("--skill-dir", default=None, help="only needed for skill runs")
    i.add_argument("--skill-subpath", default=".codex/skills"); i.add_argument("--pub-skill-dir", help="folder of the public skill, installed for condition pub"); i.add_argument("--pub-skill-name", default="vibe-security"); i.add_argument("--skill-name", default="vibe-skill", help="folder name the skill is installed under (must match the skill's own name)"); i.add_argument("--work-root", required=True)
    i.add_argument("--codex-bin", default="codex"); i.add_argument("--sandbox", default="workspace-write", choices=["read-only","workspace-write","danger-full-access"])
    i.add_argument("--windows-sandbox", default=None, choices=["elevated","unelevated"], help="Windows only: sets windows.sandbox (copy the value from your config.toml [windows] section)")
    i.add_argument("--keep-user-config", action="store_true", help="do NOT pass --ignore-user-config"); i.add_argument("--keep-rules", action="store_true", help="do NOT pass --ignore-rules"); i.add_argument("--no-network", action="store_true")
    r = sub.add_parser("run"); r.add_argument("manifest"); r.add_argument("--only"); r.add_argument("--limit", type=int)
    r.add_argument("--dry-run", action="store_true"); r.add_argument("--allow-dirty", action="store_true")
    r.add_argument("--stop-after", type=int, default=2, help="stop after this many consecutive failed runs (default 2)")
    r.add_argument("--wait-minutes", type=int, default=0, help="after a stop, wait this long and resume (for overnight runs and usage limits)")
    r.add_argument("--max-waits", type=int, default=10)
    hh = sub.add_parser("hash"); hh.add_argument("skill_dir")
    x = sub.add_parser("reset"); x.add_argument("manifest"); x.add_argument("run_ids", nargs="+")
    a = ap.parse_args()
    {"init": cmd_init, "run": cmd_run, "reset": cmd_reset, "hash": lambda a: print(skill_dir_hash(a.skill_dir))}[a.c](a)

if __name__ == "__main__":
    main()
