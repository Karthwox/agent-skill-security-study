#!/usr/bin/env python3
"""Runner for the Antigravity CLI (`agy`) series. Same design as run_study.py (Codex), reusing its helpers.

  python run_agy.py init --series-id AGY1 --model gemini-3.8-flash-low --work-root C:\\w-agy --skill-dir ..\\vibe-skill-v0.4d2 --skill-name vibe-skill-v0.4d2
  python run_agy.py run manifest-agy1.csv --dry-run
  python run_agy.py run manifest-agy1.csv --limit 3
  python run_agy.py reset manifest-agy1.csv agy-V22-base-r1

Settings come from series-agy.json (written once by `init`) so every run in a series is identical.
Each run: fresh folder, fresh git repo, `agy -p <prompt> --output-format stream-json --dangerously-skip-permissions --new-project`,
cwd = the run folder. Workspace skills live in .agents/skills/<name>/SKILL.md (verified headless with a canary skill, probe 3).
Do NOT pass --disable-slash-commands: it disables skill expansion in print mode.
Items marked [verify] are agy behaviours the probes did not settle; the runner records what it sees.
"""
import argparse, csv, hashlib, json, os, re, shutil, subprocess, sys, time
from pathlib import Path
import run_study as rs   # reuse: prepare_workdir, save_patch, zip_project, skill_dir_hash, changed_files, looks_like_question, pick_reply, kill_tree, update_manifest, parse_id, sh, now

HERE = Path(__file__).resolve().parent
SERIES_FILE = HERE / "series-agy.json"
GEMINI = Path.home() / ".gemini"
AGY_STATE = GEMINI / "antigravity-cli"
TRANSIENT = re.compile(r"(network|connection|timed? ?out|temporar|unavailable|rate.?limit|quota|429|503|EOF|reset by peer)", re.I)

def resolve_agy(s):
    """Full path to agy, or None. Tries the configured name/path, PATH, then the default install folder on Windows."""
    b = s["agy_bin"]
    if Path(b).is_file(): return str(Path(b))
    w = shutil.which(b)
    if w: return w
    for d in (os.environ.get("LOCALAPPDATA"), str(Path.home() / "AppData" / "Local")):
        if d:
            c = Path(d) / "agy" / "bin" / "agy.exe"
            if c.is_file(): return str(c)
    return None

def load_series():
    if not SERIES_FILE.exists(): sys.exit("series-agy.json missing: run `init` first")
    return json.loads(SERIES_FILE.read_text())

def cmd_init(a):
    s = {"series_id": a.series_id, "agy_bin": a.agy_bin, "model": a.model, "effort": a.effort,
         "skill_dir": str(Path(a.skill_dir).resolve()) if a.skill_dir else None, "skill_install_subpath": ".agents/skills",
         "skill_install_name": a.skill_name, "work_root": str(Path(a.work_root).resolve()),
         "timeout_minutes": a.timeout, "sandbox": a.sandbox, "max_followups": 2, "max_transient_retries": 3, "harness": "agy (Antigravity CLI)"}
    SERIES_FILE.write_text(json.dumps(s, indent=2)); print(f"wrote {SERIES_FILE}\n{json.dumps(s, indent=2)}")
    print("agy resolved to:", resolve_agy(s) or "NOT FOUND: re-run init with --agy-bin <full path to agy.exe>")

def preflight(s, allow_dirty):
    """Baselines must not see global instructions or skills. Refuse if the environment is not clean."""
    problems = []
    gm = GEMINI / "GEMINI.md"
    if gm.exists() and gm.read_text(encoding="utf-8", errors="ignore").strip(): problems.append(f"{gm} has content (global instructions)")
    for p in [Path.home() / ".agents" / "skills", GEMINI / "skills", GEMINI / "antigravity" / "skills", AGY_STATE / "skills"]:
        extra = [x.name for x in p.iterdir()] if p.exists() else []
        if extra: problems.append(f"{p} contains user skills: {extra[:5]}")
    for p in [Path.home() / "AGENTS.md", Path.home() / ".agents" / "AGENTS.md"]:
        if p.exists() and p.read_text(encoding="utf-8", errors="ignore").strip(): problems.append(f"{p} exists (global instructions)")
    if resolve_agy(s) is None: problems.append(f"agy not found (tried '{s['agy_bin']}', PATH and %LOCALAPPDATA%\\agy\\bin). Re-run init with --agy-bin <full path to agy.exe>")
    if problems and not allow_dirty:
        print("PREFLIGHT FAILED (would contaminate baselines):"); [print("  -", x) for x in problems]
        sys.exit("fix those, or pass --allow-dirty and note it in the paper")
    return problems

def base_cmd(s, prompt, conversation=None):
    c = [resolve_agy(s) or "agy", "-p", prompt, "--output-format", "stream-json", "--dangerously-skip-permissions",
         "--model", s["model"], "--print-timeout", f'{s["timeout_minutes"]}m']
    if s.get("effort"): c += ["--effort", s["effort"]]
    if s.get("sandbox"): c += ["--sandbox"]   # terminal restrictions on; [verify] that it still lets the agent write inside the run folder
    c += (["--conversation", conversation] if conversation else ["--new-project"])   # [verify] --new-project with --conversation is not needed
    return c

def run_agy(s, wd, prompt, events_path, stderr_path, conversation=None, log_path=None, label=""):
    """Run one turn; append raw stream to events_path. Returns (returncode, timed_out).
    Prints a heartbeat every 60 s. Watchdog: if the final `result` event has been written but agy has not exited 5 s later, it is killed
    and the turn counts as finished (agy was seen to linger); the kill is recorded in killed_after_result.txt next to the events file."""
    cmd = base_cmd(s, prompt, conversation)
    kw = dict(cwd=wd, stdout=open(events_path, "ab"), stderr=open(stderr_path, "ab"), stdin=subprocess.DEVNULL)
    if os.name != "nt": kw["start_new_session"] = True
    start_size = Path(events_path).stat().st_size if Path(events_path).exists() else 0
    p = subprocess.Popen(cmd, **kw)
    t0 = time.time(); last_beat = t0; seen_at = None; limit = s["timeout_minutes"] * 60 + 120
    while True:
        try:
            p.wait(timeout=1); return p.returncode, False
        except subprocess.TimeoutExpired: pass
        now = time.time()
        try:
            data = Path(events_path).read_bytes()[start_size:]
        except OSError: data = b""
        if seen_at is None and b'"event":"result"' in data.replace(b'"event": "result"', b'"event":"result"'): seen_at = now
        if seen_at and now - seen_at > 5:
            rs.kill_tree(p); p.wait(); (Path(events_path).parent / "killed_after_result.txt").open("a").write(f"{rs.now()} killed: result event written but agy had not exited after 5 s\n"); return 0, False
        if now - t0 > limit:
            rs.kill_tree(p); p.wait(); return -9, True
        if now - last_beat >= 60:
            last_beat = now
            try: nf = rs.changed_files(wd)
            except Exception: nf = "?"
            print(f"  ... {label} running {int((now - t0) // 60)} min, {len(data)} bytes of events, {nf} files changed", flush=True)

def read_stream(path, start_offset=0):
    """Parse the NDJSON stream from a byte offset. Returns (result_event or None, events list)."""
    raw = Path(path).read_bytes()[start_offset:].decode("utf-8", errors="ignore")
    ev, res = [], None
    for line in raw.splitlines():
        line = line.strip()
        if not line.startswith("{"): continue
        try: e = json.loads(line)
        except ValueError: continue
        ev.append(e)
        if e.get("event") == "result": res = e["result"]
    return res, ev

def signals(events, wd):
    """Evidence of skill loading and of reading outside the run folder (leak check)."""
    skill_reads, sec_reads, outside, tools = [], [], [], {}
    wds = str(wd).lower().replace("/", "\\")
    for e in events:
        su = e.get("step_update") or {}
        if su.get("step_type") != "tool" or su.get("state") != "DONE": continue
        n = su.get("tool_name"); tools[n] = tools.get(n, 0) + 1
        params = (su.get("tool_info") or {}).get("parameters") or {}
        for v in params.values():
            if not isinstance(v, str): continue
            lv = v.lower().replace("/", "\\")
            if "\\.agents\\skills\\" in lv: skill_reads.append(v)
            if "references\\security" in lv: sec_reads.append(v)
            if re.match(r"[a-z]:\\", lv) and not lv.startswith(wds): outside.append(v)
    return {"skill_files_viewed": len(skill_reads), "security_refs_viewed": len(sec_reads), "paths_outside_workdir": sorted(set(outside))[:20], "tool_counts": tools}

def final_text(res): return (res or {}).get("response", "") or ""

def do_run(s, suite, run_id, dry):
    prompt_id, cond, _ = rs.parse_id(run_id)
    text = suite["prompts"][prompt_id]["text"]
    if cond == "rem": text = f'{text} {suite["reminder"]}'
    rdir = HERE / "runs" / run_id
    if dry:
        print(f"[dry] {run_id}: {' '.join(base_cmd(s, '<prompt>'))}\n[dry] prompt: {text}"); return "dry"
    rdir.mkdir(parents=True, exist_ok=True)
    wd = rs.prepare_workdir(s, suite, prompt_id, cond, run_id)
    ver = rs.sh([resolve_agy(s), "--version"], wd).stdout.strip()
    t0 = time.time(); started = rs.now()
    events, err = rdir / "events.jsonl", rdir / "stderr.txt"
    usage = {"input_tokens": 0, "output_tokens": 0, "thinking_tokens": 0, "cache_read_tokens": 0, "total_tokens": 0}
    turns, conv, followups, retries, timed_out, status_txt, rc = 0, None, 0, 0, False, "", 0
    prompt_now, pick_text = text, text
    while True:
        off = events.stat().st_size if events.exists() else 0
        rc, timed_out = run_agy(s, wd, prompt_now, events, err, conv, rdir / "agy.log", run_id)
        res, evs = read_stream(events, off)
        ok = res is not None and res.get("status") == "SUCCESS"
        if not ok and not timed_out and retries < s["max_transient_retries"] and rs.changed_files(wd) == 0 and not any((e.get("step_update") or {}).get("step_type") == "tool" for e in evs):
            # nothing happened (dropped connection / quota blip): retry the same turn, same folder. Logged, not hidden.
            blob = (err.read_text(encoding="utf-8", errors="ignore")[-800:] + json.dumps(res or {}))
            retries += 1; (rdir / "retries.log").open("a").write(f"{rs.now()} retry {retries}: rc={rc} {blob[-300:]}\n")
            time.sleep(30 * retries); continue
        turns += 1
        if res:
            conv = res.get("conversation_id") or conv; status_txt = res.get("status", "")
            for k in usage: usage[k] += (res.get("usage") or {}).get(k, 0) or 0
        (rdir / f"last_message_{turns}.txt").write_text(final_text(res), encoding="utf-8")
        msg = final_text(res)
        if timed_out or not ok or followups >= s["max_followups"]: break
        if not (rs.looks_like_question(msg) and rs.changed_files(wd) == 0): break
        followups += 1; prompt_now = rs.pick_reply(suite, prompt_id, msg)
        (rdir / f"followup_{followups}.txt").write_text(prompt_now, encoding="utf-8")
    final_msg = (rdir / f"last_message_{turns}.txt").read_text(encoding="utf-8", errors="ignore") if turns else ""
    ended_q = rs.looks_like_question(final_msg)
    _, allev = read_stream(events)
    sig = signals(allev, wd)
    if conv:   # best-effort copy of the CLI's own per-conversation state (small), as the analogue of Codex's session log
        for src, name in [(AGY_STATE / "brain" / conv, "brain"), (AGY_STATE / "conversations" / f"{conv}.db", "conversation.db")]:
            try:
                if src.is_dir(): shutil.copytree(src, rdir / name, dirs_exist_ok=True)
                elif src.exists(): shutil.copy(src, rdir / name)
            except OSError: pass
    names = rs.save_patch(wd, rdir / "changes.patch"); rs.zip_project(wd, rdir / "project.zip")
    builtin = sorted(x.name for x in (AGY_STATE / "builtin" / "skills").iterdir()) if (AGY_STATE / "builtin" / "skills").is_dir() else []
    settings = {"run_id": run_id, "prompt": prompt_id, "condition": cond, "series_id": s["series_id"], "harness": s["harness"], "harness_version": ver,
                "model": s["model"], "reasoning_effort": s.get("effort") or "model-default", "permission_mode": "dangerously-skip-permissions" + (" + sandbox" if s.get("sandbox") else ""),
                "skill_version": rs.skill_dir_hash(s["skill_dir"]) if cond == "skill" else "n/a",
                "skill_install_path": f'{s["skill_install_subpath"]}/{s["skill_install_name"]}' if cond == "skill" else "n/a",
                "prompt_sha256": hashlib.sha256(text.encode()).hexdigest()[:16], "date_start": started, "minutes": round((time.time() - t0) / 60, 2),
                "exit_code": rc, "timed_out": timed_out, "result_status": status_txt, "turns": turns, "followups_sent": followups, "transient_retries": retries,
                "ended_with_question": ended_q, "files_changed": rs.changed_files(wd), "source_files_changed": len(names), "source_files": names,
                "tokens": usage, "conversation_id": conv, "builtin_skills_present": builtin, **sig}
    (rdir / "settings.json").write_text(json.dumps(settings, indent=2), encoding="utf-8")
    status = "timeout" if timed_out else ("error" if status_txt != "SUCCESS" else "done")
    if status == "done" and settings["source_files_changed"] == 0 and not ended_q: status = "nochange"
    if sig["paths_outside_workdir"]: status += "+outside"   # [verify] leak check: inspect these by hand
    print(f"{run_id}: {status} in {settings['minutes']} min, tokens {usage['total_tokens']}, files {settings['files_changed']}, followups {followups}, retries {retries}, skill files viewed {sig['skill_files_viewed']}")
    return status

def cmd_run(a):
    s, suite = load_series(), json.loads((HERE / "suite.json").read_text())
    if not a.dry_run: preflight(s, a.allow_dirty)
    mpath = HERE / a.manifest
    todo = [r["run_id"] for r in csv.DictReader(open(mpath, newline="")) if r["status"] == "todo"]
    if a.only: todo = [r for r in todo if r == a.only]
    if a.limit: todo = todo[: a.limit]
    if any(rs.parse_id(r)[1] == "skill" for r in todo) and not (s.get("skill_dir") and Path(s["skill_dir"]).is_dir()): sys.exit("skill runs need skill_dir (re-run init)")
    streak = []
    for rid in todo:
        try: st = do_run(s, suite, rid, a.dry_run)
        except SystemExit: raise
        except Exception as ex:
            import traceback; (HERE / "runs" / rid).mkdir(parents=True, exist_ok=True)
            (HERE / "runs" / rid / "crash.txt").write_text(traceback.format_exc(), encoding="utf-8"); st = "crash"; print(f"{rid}: CRASH ({type(ex).__name__}); continuing. `reset` before retrying.")
        if st != "dry": rs.update_manifest(mpath, rid, st)
        streak = streak + [rid] if st.split("+")[0] in ("error", "crash", "nochange", "timeout") else []
        if len(streak) >= a.stop_after:
            print(f"STOPPED: {len(streak)} runs in a row failed ({', '.join(streak)}). Probably quota, network or auth. Check runs/<id>/stderr.txt and /usage, then `reset` them and run again."); return

def cmd_reset(a):
    s = load_series(); mpath = HERE / a.manifest
    for rid in a.run_ids:
        rs.parse_id(rid); ok1 = rs._rm(Path(s["work_root"]) / rid); ok2 = rs._rm(HERE / "runs" / rid)
        if not (ok1 and ok2): print(f"{rid}: COULD NOT DELETE (close programs using it)"); continue
        rows = list(csv.DictReader(open(mpath, newline="")))
        for r in rows:
            if r["run_id"] == rid: r["status"], r["date_run"] = "todo", ""
        with open(mpath, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
        print(f"{rid}: reset")

def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="c", required=True)
    i = sub.add_parser("init"); i.add_argument("--series-id", required=True); i.add_argument("--model", required=True)
    i.add_argument("--effort", default=None, help="omit to keep the model's own level (the model name already carries Low/Medium/High)")
    i.add_argument("--skill-dir"); i.add_argument("--skill-name", default="vibe-skill"); i.add_argument("--work-root", required=True)
    i.add_argument("--agy-bin", default="agy"); i.add_argument("--timeout", type=int, default=25)
    i.add_argument("--sandbox", action="store_true", help="pass --sandbox to agy (terminal restrictions). Use it if the 2-run trial shows it still lets the agent write in the run folder")
    r = sub.add_parser("run"); r.add_argument("manifest"); r.add_argument("--only"); r.add_argument("--limit", type=int)
    r.add_argument("--dry-run", action="store_true"); r.add_argument("--allow-dirty", action="store_true"); r.add_argument("--stop-after", type=int, default=2)
    x = sub.add_parser("reset"); x.add_argument("manifest"); x.add_argument("run_ids", nargs="+")
    a = ap.parse_args(); {"init": cmd_init, "run": cmd_run, "reset": cmd_reset}[a.c](a)

if __name__ == "__main__":
    main()
