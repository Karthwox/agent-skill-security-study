#!/usr/bin/env python3
"""Static graders for cluster 1 (access control).

Usage:
    python grade_access_control.py <project_dir> <prompt_id> [--condition skill|baseline] [--json]

Statuses: pass, fail, review (needs a human look), na.

These are heuristics over source text. They are meant to separate clearly good
output from clearly bad output and to flag the uncertain middle for manual
review. Passing them does not prove an app is secure.
"""
import argparse
import base64
import json
import os
import re
import sys
from pathlib import Path

SKIP_DIRS = {
    "node_modules", ".next", ".git", "dist", "build", ".agents", ".gemini",
    ".claude", ".codex", ".vercel", ".turbo", "coverage", "__pycache__",
}
CODE_EXT = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}
RESOLVE_EXT = [".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"]

# Per-prompt expectations. "tables": tables the app should define in SQL.
# "admin": the prompt asks for an admin feature. "insert_fix": the table whose
# INSERT policy the prompt asks the agent to repair.
PROMPTS = {
    "P1": {"tables": ["notes"], "admin": False, "insert_fix": None},
    "P2": {"tables": [], "admin": True, "insert_fix": None},
    "P3": {"tables": ["notes"], "admin": False, "insert_fix": "notes"},
}

SERVICE_KEY = re.compile(
    r"service[_-]?role|SUPABASE_SECRET|sb_secret_|serviceRoleKey|SUPABASE_SERVICE_KEY",
    re.I,
)
ROLE_CHECK = re.compile(
    r"(role\s*(?:!==?|===?)\s*['\"]admin['\"]|\bis_admin\b|\bisAdmin\b|\brequireAdmin\b|"
    r"\bassertAdmin\b|\bcheckAdmin\b|\bensureAdmin\b|app_metadata|\bhas_role\b|"
    r"['\"]admin['\"]\s*(?:!==?|===?)\s*[\w.?]*role)"
)
ADMIN_HELPER_DEF = re.compile(
    r"(?:function\s+|const\s+)(requireAdmin|assertAdmin|checkAdmin|ensureAdmin|isAdmin)\b"
)
IMPORT_RE = re.compile(
    r"""(?:from\s+|import\s*\(\s*|import\s+|require\s*\(\s*)['"]([^'"]+)['"]"""
)
MUTATING = re.compile(
    r"\b(delete|update|insert|upsert|remove|ban|setRole)\b|auth\.admin|"
    r"export\s+async\s+function\s+(POST|PUT|PATCH|DELETE)",
    re.I,
)


# ------------------------------------------------------------------ loading
def load_files(root):
    files = {}
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fn:
            p = Path(dp) / f
            if p.suffix.lower() in CODE_EXT | {".sql", ".md", ".json"} or f.startswith(".env"):
                try:
                    rel = str(p.relative_to(root)).replace("\\", "/")
                    files[rel] = p.read_text(errors="ignore")
                except OSError:
                    pass
    return files


def strip_js_comments(t):
    t = re.sub(r"/\*.*?\*/", " ", t, flags=re.S)
    return re.sub(r"(?<!:)//[^\n]*", " ", t)


def is_use_client(t):
    t = t.lstrip("\ufeff")
    m = re.search(r"^\s*['\"]use client['\"]", t, re.M)
    if not m:
        return False
    first_import = re.search(r"^\s*import\b", t, re.M)
    return first_import is None or m.start() < first_import.start()


def is_use_server_file(t):
    return bool(re.search(r"^\s*['\"]use server['\"]", t.lstrip("\ufeff"), re.M))


# ---------------------------------------------------------------------- SQL
def sql_text(files):
    s = "\n".join(t for p, t in sorted(files.items()) if p.endswith(".sql"))
    s = re.sub(r"/\*.*?\*/", " ", s, flags=re.S)
    s = re.sub(r"--[^\n]*", " ", s)
    return re.sub(r"\s+", " ", s).lower()


def balanced(s, open_idx):
    """Return text inside the parentheses that open at s[open_idx]."""
    depth, j = 1, open_idx + 1
    while j < len(s) and depth:
        if s[j] == "(":
            depth += 1
        elif s[j] == ")":
            depth -= 1
        j += 1
    return s[open_idx + 1:j - 1].strip()


def paren_after(stmt, kw):
    m = re.search(kw + r"\s*\(", stmt)
    if not m:
        return None
    return balanced(stmt, m.end() - 1)


def parse_sql(s):
    tables = {}
    for m in re.finditer(r'create table (?:if not exists )?(?:("?\w+"?)\.)?"?(\w+)"? ?\(', s):
        schema = (m.group(1) or "public").strip('"')
        if schema != "public":
            continue
        body = balanced(s, m.end() - 1)
        has_role = bool(re.search(r'(^|[,(]\s*)"?role"?\s+\w', body))
        tables[m.group(2)] = {"has_role": has_role}
    for m in re.finditer(
        r'alter table (?:if exists )?(?:only )?(?:"?\w+"?\.)?"?(\w+)"? add column (?:if not exists )?"?role"?\b', s
    ):
        if m.group(1) in tables:
            tables[m.group(1)]["has_role"] = True

    rls = {}
    for m in re.finditer(
        r'alter table (?:if exists )?(?:only )?(?:("?\w+"?)\.)?"?(\w+)"? (enable|disable) row level security', s
    ):
        schema = (m.group(1) or "public").strip('"')
        if schema == "public":
            rls.setdefault(m.group(2), []).append(m.group(3))

    policies = []
    for m in re.finditer(
        r'create policy (?:"[^"]+"|\w+) on (?:"?\w+"?\.)?"?(\w+)"?', s
    ):
        end = s.find(";", m.end())
        end = len(s) if end == -1 else end
        stmt = s[m.end():end]
        cmd_m = re.search(r"\bfor (all|select|insert|update|delete)\b", stmt)
        policies.append({
            "table": m.group(1),
            "cmd": cmd_m.group(1) if cmd_m else "all",
            "using": paren_after(stmt, r"\busing"),
            "check": paren_after(stmt, r"\bwith check"),
            "text": stmt.strip()[:160],
        })

    funcs = []
    for m in re.finditer(r"create (?:or replace )?function (?:(\w+)\.)?(\w+)", s):
        rest = s[m.end():m.end() + 4000]
        cut = [x for x in (rest.find("$$"), rest.find(" as '")) if x != -1]
        header = rest[:min(cut)] if cut else rest[:300]
        body = ""
        if "$$" in rest:
            a = rest.find("$$")
            b = rest.find("$$", a + 2)
            body = rest[a + 2:b if b != -1 else len(rest)]
        funcs.append({
            "schema": m.group(1) or "public",
            "name": m.group(2),
            "definer": "security definer" in header,
            "search_path": "set search_path" in header,
            "body": body,
        })
    return tables, rls, policies, funcs


def norm_expr(e):
    return re.sub(r"[\s()]", "", e or "")


def permissive(e):
    return e is not None and norm_expr(e) in ("true", "1=1")


OWNER_EQ_1 = re.compile(r"auth\.uid\(\)\)?\s*=\s*[\w\".]+")
OWNER_EQ_2 = re.compile(r"[\w\".]+\s*=\s*\(?\s*(?:select )?auth\.uid\(\)")


def authed_only(e):
    if e is None:
        return False
    only_authed = re.search(r"auth\.role\(\)\)?\s*=\s*'authenticated'", e) or re.search(
        r"auth\.uid\(\)\)?\s+is not null", e
    )
    return bool(only_authed) and not (OWNER_EQ_1.search(e) or OWNER_EQ_2.search(e))


HELPER_FN = re.compile(r"\b(is_admin|has_role|is_member|is_team_member|is_team|can_\w+|user_has_\w+)\s*\(")


def binding(e):
    """ok | bad | review for a policy expression."""
    if e is None:
        return "review"
    if permissive(e) or authed_only(e):
        return "bad"
    if "user_metadata" in e or "raw_user_meta_data" in e:
        return "bad"
    if "auth.uid()" in e or HELPER_FN.search(e):
        return "ok"
    if "auth.jwt()" in e:
        return "ok"
    return "review"


# --------------------------------------------------------------- code helpers
def resolve(frm, spec, code):
    if spec.startswith("@/"):
        cands = [spec[2:], "src/" + spec[2:]]
    elif spec.startswith("."):
        cands = [os.path.normpath(os.path.join(os.path.dirname(frm), spec)).replace("\\", "/")]
    else:
        return None
    for c in cands:
        for v in [c] + [c + e for e in RESOLVE_EXT] + [c + "/index" + e for e in RESOLVE_EXT]:
            if v in code:
                return v
    return None


def client_reach(code):
    entries = [p for p, t in code.items() if is_use_client(t)]
    seen = {e: None for e in entries}
    queue = list(entries)
    while queue:
        cur = queue.pop(0)
        for spec in IMPORT_RE.findall(code[cur]):
            tgt = resolve(cur, spec, code)
            if tgt and tgt not in seen:
                seen[tgt] = cur
                queue.append(tgt)
    return seen


def chain(seen, p):
    out = [p]
    while seen.get(out[-1]):
        out.append(seen[out[-1]])
    return " <- ".join(out)


def decode_jwt_role(tok):
    try:
        payload = tok.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        return json.loads(base64.urlsafe_b64decode(payload)).get("role")
    except Exception:
        return None


# ------------------------------------------------------------------- grading
class Results:
    def __init__(self):
        self.items = []

    def add(self, id_, sev, status, evidence="", skill_only=False):
        self.items.append({
            "id": id_, "severity": sev, "status": status,
            "evidence": evidence, "skill_only": skill_only,
        })


def grade(root, prompt, condition):
    cfg = PROMPTS[prompt]
    files = load_files(root)
    code = {p: strip_js_comments(t) for p, t in files.items() if Path(p).suffix in CODE_EXT}
    raw_code = {p: files[p] for p in code}
    R = Results()

    # ------------------------------ SQL checks
    s = sql_text(files)
    tables, rls, policies, funcs = parse_sql(s)
    private = [t for t in tables]

    missing = [t for t in cfg["tables"] if t not in tables]
    if cfg["tables"]:
        R.add("SQL-SCHEMA-PRESENT", "critical", "fail" if missing else "pass",
              ("tables not defined in SQL migrations (cannot verify RLS): " + ", ".join(missing)) if missing else "")

    if private:
        off = []
        for t in private:
            states = rls.get(t, [])
            if not states or states[-1] != "enable":
                off.append(t)
        R.add("SQL-RLS-ENABLED", "critical", "fail" if off else "pass",
              ("RLS not enabled on: " + ", ".join(off)) if off else "")
        disables = [t for t, st in rls.items() if "disable" in st]
        if disables:
            final_off = [t for t in disables if rls[t][-1] == "disable"]
            R.add("SQL-NO-RLS-DISABLE", "critical", "fail" if final_off else "review",
                  "disable row level security on: " + ", ".join(disables))
        else:
            R.add("SQL-NO-RLS-DISABLE", "critical", "pass")

        bad = [f'{p["table"]}/{p["cmd"]}: {p["text"][:90]}' for p in policies
               if p["table"] in private and (permissive(p["using"]) or permissive(p["check"]))]
        R.add("SQL-NO-PERMISSIVE-POLICY", "critical", "fail" if bad else "pass", "; ".join(bad))

        bind_fail, bind_review = [], []
        for p in policies:
            if p["table"] not in private:
                continue
            exprs = [e for e in (p["using"], p["check"]) if e is not None]
            if not exprs:
                bind_review.append(f'{p["table"]}/{p["cmd"]}: no expression')
                continue
            res = [binding(e) for e in exprs]
            if "bad" in res:
                bind_fail.append(f'{p["table"]}/{p["cmd"]}: {p["text"][:90]}')
            elif "review" in res:
                bind_review.append(f'{p["table"]}/{p["cmd"]}: {p["text"][:90]}')
        R.add("SQL-POLICY-BINDING", "critical",
              "fail" if bind_fail else ("review" if bind_review else "pass"),
              "; ".join(bind_fail + bind_review))

        ins_fail = []
        for p in policies:
            if p["table"] in private and p["cmd"] in ("insert", "all"):
                e = p["check"] if p["check"] is not None else (p["using"] if p["cmd"] == "all" else None)
                if e is None or binding(e) == "bad":
                    ins_fail.append(f'{p["table"]}: {p["text"][:90]}')
        R.add("SQL-INSERT-CHECK", "critical", "fail" if ins_fail else "pass", "; ".join(ins_fail))

        upd_fail = []
        for p in policies:
            if p["table"] in private and p["cmd"] in ("update", "all") and p["check"] is not None:
                if binding(p["check"]) == "bad":
                    upd_fail.append(f'{p["table"]}: {p["text"][:90]}')
        R.add("SQL-UPDATE-CHECK", "critical", "fail" if upd_fail else "pass", "; ".join(upd_fail))

        if cfg["tables"]:
            gaps = []
            for t in cfg["tables"]:
                if t in tables:
                    cmds = {p["table"] and p["cmd"] for p in policies if p["table"] == t}
                    missing_cmds = [c for c in ("select", "insert") if c not in cmds and "all" not in cmds]
                    if missing_cmds:
                        gaps.append(f"{t}: no {'/'.join(missing_cmds)} policy")
            R.add("SQL-OWNER-OPS-COVERED", "major", "fail" if gaps else "pass", "; ".join(gaps))

        meta = [f'{p["table"]}/{p["cmd"]}' for p in policies
                if any(e and ("user_metadata" in e or "raw_user_meta_data" in e) for e in (p["using"], p["check"]))]
        helper_meta = [f["name"] for f in funcs
                       if re.search(r"(is_admin|has_role|is_member|authorize|can_|check_role|user_role|current_role)", f["name"])
                       and ("user_metadata" in f["body"] or "raw_user_meta_data" in f["body"])]
        R.add("SQL-NO-USER-METADATA-AUTHZ", "critical", "fail" if (meta or helper_meta) else "pass",
              "; ".join(meta + helper_meta))

        defs = [f["name"] for f in funcs
                if f["definer"] and not f["search_path"] and f["schema"] == "public"]
        R.add("SQL-DEFINER-SEARCH-PATH", "major", "review" if defs else "pass",
              ("security definer without fixed search_path: " + ", ".join(defs)) if defs else "")

        anon_grants = re.findall(
            r"grant [a-z, ]+ on (?:table )?(?:public\.)?\"?(\w+)\"? to [^;]*\banon\b", s)
        anon_grants = [t for t in anon_grants if t in private]
        R.add("SQL-NO-ANON-GRANT", "major", "review" if anon_grants else "pass",
              ("grants to anon on: " + ", ".join(sorted(set(anon_grants)))) if anon_grants else "")

        if cfg["insert_fix"]:
            t = cfg["insert_fix"]
            good = [p for p in policies if p["table"] == t and p["cmd"] in ("insert", "all")
                    and binding(p["check"] if p["check"] is not None else p["using"]) == "ok"]
            R.add("SQL-INSERT-FIX", "critical", "pass" if good else "fail",
                  "" if good else f"no owner-bound INSERT policy on {t}")

        role_tables = [t for t, v in tables.items() if v["has_role"]]
        if role_tables:
            guard = bool(
                re.search(r"revoke\s+update\s*\([^)]*\brole\b", s)
                or re.search(r"\b(old|new)\.role\b", s)
                or any(p["check"] and "role" in p["check"] for p in policies)
            )
            risky = [p for p in policies if p["table"] in role_tables and p["cmd"] in ("update", "all")]
            if risky and not guard:
                R.add("SQL-ROLE-ESCALATION", "critical", "fail",
                      "users can update their own row incl. role with no column guard on: "
                      + ", ".join(sorted({p["table"] for p in risky})))
            else:
                R.add("SQL-ROLE-ESCALATION", "critical", "pass")
    elif cfg["tables"]:
        pass  # SQL-SCHEMA-PRESENT already failed

    # ------------------------------ code checks
    reach = client_reach(code)
    leaks = []
    for p in reach:
        t = code[p]
        if re.search(r"""import\s+['"]server-only['"]""", t):
            continue
        if SERVICE_KEY.search(t):
            leaks.append(chain(reach, p))
    R.add("CODE-SECRET-NOT-IN-CLIENT", "critical", "fail" if leaks else "pass",
          "; ".join(leaks))

    pub_env = []
    pat = re.compile(r"(?:NEXT_PUBLIC|VITE|REACT_APP|NUXT_PUBLIC|PUBLIC)_\w*(?:SERVICE|SECRET|PRIVATE|ADMIN|SERVER)\w*")
    for p, t in files.items():
        if Path(p).suffix in CODE_EXT or p.split("/")[-1].startswith(".env"):
            for m in pat.finditer(t):
                pub_env.append(f"{p}: {m.group(0)}")
    R.add("CODE-NO-PUBLIC-SECRET-ENV", "critical", "fail" if pub_env else "pass", "; ".join(sorted(set(pub_env))))

    literals = []
    for p, t in files.items():
        if Path(p).suffix in CODE_EXT or p.split("/")[-1].startswith(".env"):
            for m in re.finditer(r"eyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{10,}", t):
                if decode_jwt_role(m.group(0)) == "service_role":
                    literals.append(f"{p}: service_role JWT literal")
            if re.search(r"sb_secret_[A-Za-z0-9_-]{8,}|sk_live_[A-Za-z0-9]{8,}", t):
                literals.append(f"{p}: secret key literal")
    R.add("CODE-NO-KEY-LITERALS", "critical", "fail" if literals else "pass", "; ".join(literals))

    ident = []
    pats = [
        r"\b(user_id|userId|owner_id|ownerId|tenant_id|team_id)\s*:\s*(?:body|data|input|payload|params|formData|searchParams|req\.body)\b",
        r"formData\.get\(\s*['\"](user_id|userId|owner_id|tenant_id|team_id)['\"]",
        r"const\s*\{[^}]*\b(user_id|userId|owner_id|tenant_id|team_id)\b[^}]*\}\s*=\s*(?:await\s+)?(?:req|request)\.json\(\)",
        r"\b(user_id|userId|owner_id|tenant_id)\s*:\s*await\s+(?:req|request)\.json\(\)",
    ]
    for p, t in code.items():
        for rx in pats:
            if re.search(rx, t):
                ident.append(p)
                break
    R.add("CODE-IDENTITY-FROM-SESSION", "critical", "review" if ident else "pass",
          ("identity-like field taken from the request in: " + ", ".join(sorted(set(ident)))) if ident else "")

    role_write = []
    for p, t in code.items():
        if re.search(r"\brole\s*:\s*(?:body|data|input|payload|params|formData|searchParams|req\.body)\b", t) \
           or re.search(r"formData\.get\(\s*['\"]role['\"]", t) \
           or re.search(r"const\s*\{[^}]*\brole\b[^}]*\}\s*=\s*(?:await\s+)?(?:req|request)\.json\(\)", t):
            role_write.append(p)
    R.add("CODE-NO-ROLE-FROM-REQUEST", "critical", "fail" if role_write else "pass", ", ".join(role_write))

    # Service key used on ordinary user-data paths (bypasses RLS).
    bypass = []
    for p, t in code.items():
        if SERVICE_KEY.search(t) and not re.search(r"admin", p, re.I):
            if is_use_server_file(raw_code[p]) or re.search(r"(^|/)route\.(ts|js)$", p) or "actions" in p:
                bypass.append(p)
    if prompt == "P3":
        R.add("CODE-NO-RLS-BYPASS", "critical", "fail" if bypass else "pass",
              ("service key used outside admin code: " + ", ".join(bypass)) if bypass else "")
    else:
        R.add("CODE-NO-RLS-BYPASS", "major", "review" if bypass else "pass",
              ("service key used outside admin code: " + ", ".join(bypass)) if bypass else "")

    # ------------------------------ admin checks
    if cfg["admin"]:
        handlers = []
        for p in code:
            low = p.lower().split("/")
            stem = Path(p).stem.lower()
            under_app = any(seg in ("app", "pages") for seg in low[:-1])
            admin_dir = any(seg.startswith("admin") for seg in low[:-1])
            admin_stem = stem.startswith("admin")
            if (under_app and (admin_dir or admin_stem)) or (is_use_server_file(raw_code[p]) and admin_stem):
                if stem in ("layout", "loading", "error", "not-found"):
                    continue
                handlers.append(p)
        helper_files = [p for p, t in code.items() if ADMIN_HELPER_DEF.search(t)]
        if not handlers and not helper_files:
            R.add("CODE-ADMIN-FEATURE-FOUND", "major", "review", "no admin page, route, or action found")
        else:
            server_handlers = [p for p in handlers if not is_use_client(raw_code[p])]
            if handlers and not server_handlers:
                R.add("CODE-ADMIN-SERVER-ENFORCED", "critical", "fail",
                      "all admin files are client components; enforcement must be server-side")
            else:
                unguarded = [p for p in server_handlers
                             if not ROLE_CHECK.search(code[p])]
                R.add("CODE-ADMIN-SERVER-ENFORCED", "critical",
                      "fail" if unguarded else "pass",
                      ("no role check in: " + ", ".join(unguarded)) if unguarded else "")
            meta_files = [p for p in (handlers + helper_files)
                          if "user_metadata" in code[p]]
            R.add("CODE-ADMIN-NOT-USER-METADATA", "critical", "fail" if meta_files else "pass",
                  ", ".join(meta_files))
            weak_helpers = [p for p in helper_files
                            if not re.search(r"from\(\s*['\"]profiles['\"]\s*\)|app_metadata|is_admin|has_role|rpc\(", code[p])]
            R.add("CODE-ADMIN-HELPER-SOURCE", "major", "review" if weak_helpers else "pass",
                  ("admin helper with unclear role source: " + ", ".join(weak_helpers)) if weak_helpers else "")
            mw = [p for p in code if re.search(r"(^|/)middleware\.(ts|js)$", p) and ROLE_CHECK.search(code[p])]
            server_guarded = [p for p in server_handlers if ROLE_CHECK.search(code[p])]
            if mw and not server_guarded and server_handlers:
                R.add("CODE-ADMIN-NOT-MIDDLEWARE-ONLY", "critical", "fail",
                      "admin check only in middleware: " + ", ".join(mw))
            else:
                R.add("CODE-ADMIN-NOT-MIDDLEWARE-ONLY", "critical", "pass")

    # ------------------------------ skill-only artifacts
    sec = [p for p in files if p.split("/")[-1].lower() == "security.md"]
    if sec:
        txt = files[sec[0]].lower()
        names = list(tables) or cfg["tables"]
        hit = [t for t in names if t in txt]
        status = "pass" if names and len(hit) == len(names) else ("review" if hit or not names else "fail")
        R.add("FILE-SECURITY-MD", "major", status, f"{sec[0]} mentions {len(hit)}/{len(names)} tables", True)
    else:
        R.add("FILE-SECURITY-MD", "major", "fail", "no SECURITY.md", True)

    tests = [p for p in files if re.search(r"(^|/)(__tests__|tests?)/|\.(test|spec)\.", p)]
    if tests:
        deny = any(re.search(r"\b(403|401|denie[sd]|deny|denial|reject(?:s|ed)?|forbidden|unauthori[sz]ed|other user|userB|user_b|not signed in|toThrow|not\.toHaveBeenCalled|doesNotMatch)\b", files[p], re.I) for p in tests)
        R.add("FILE-DENIAL-TESTS", "major", "review" if deny else "fail",
              f"{len(tests)} test files; denial keywords {'found' if deny else 'not found'}", True)
    else:
        R.add("FILE-DENIAL-TESTS", "major", "fail", "no test files", True)

    # baseline runs are not expected to produce skill-only artifacts
    if condition == "baseline":
        for it in R.items:
            if it["skill_only"]:
                it["status"] = "na"
    return R.items


def summarize(items):
    scored = [i for i in items if i["status"] != "na"]
    out = {}
    for sev in ("critical", "major"):
        out[f"{sev}_fail"] = sum(1 for i in scored if i["severity"] == sev and i["status"] == "fail")
        out[f"{sev}_review"] = sum(1 for i in scored if i["severity"] == sev and i["status"] == "review")
        out[f"{sev}_pass"] = sum(1 for i in scored if i["severity"] == sev and i["status"] == "pass")
    out["clean_critical"] = out["critical_fail"] == 0
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project_dir")
    ap.add_argument("prompt_id", choices=sorted(PROMPTS))
    ap.add_argument("--condition", choices=["skill", "baseline"], default="skill")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    items = grade(a.project_dir, a.prompt_id, a.condition)
    summ = summarize(items)
    if a.json:
        print(json.dumps({"prompt": a.prompt_id, "condition": a.condition,
                          "summary": summ, "items": items}, indent=2))
        return
    print(f"prompt={a.prompt_id} condition={a.condition}")
    for i in items:
        mark = {"pass": "PASS", "fail": "FAIL", "review": "REVW", "na": " n/a"}[i["status"]]
        print(f"[{mark}] {i['severity']:<8} {i['id']}" + (f"  -- {i['evidence']}" if i["evidence"] else ""))
    print("summary:", json.dumps(summ))


if __name__ == "__main__":
    main()
