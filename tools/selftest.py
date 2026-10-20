#!/usr/bin/env python3
"""Self-test for grade_access_control.py.

Builds small projects from the healthy fixture, mutates them, and checks that
the grader reports the expected statuses. Run before trusting any grader result:

    python selftest.py
"""
import base64
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import grade_access_control as g  # noqa: E402

FIX = Path(__file__).parent.parent / "fixtures" / "notes-app-healthy"
MIG = "supabase/migrations/20250101000000_init.sql"


def build(edits=None, appends=None, delete=None):
    d = Path(tempfile.mkdtemp())
    shutil.copytree(FIX, d / "p")
    root = d / "p"
    for rel in delete or []:
        (root / rel).unlink()
    for rel, text in (edits or {}).items():
        f = root / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text)
    for rel, text in (appends or {}).items():
        with open(root / rel, "a") as fh:
            fh.write("\n" + text + "\n")
    return root


def b64(obj):
    return base64.urlsafe_b64encode(json.dumps(obj).encode()).decode().rstrip("=")


SERVICE_JWT = f"{b64({'alg': 'HS256', 'typ': 'JWT'})}.{b64({'role': 'service_role', 'iss': 'supabase'})}.abcdefghijklmnop"

ADMIN_HELPER_OK = """import { createClient } from "@/lib/supabase/server";

export async function requireAdmin() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) throw new Error("Not signed in");
  const { data } = await supabase.from("profiles").select("role").eq("id", user.id).single();
  if (data?.role !== "admin") throw new Error("Forbidden");
  return user;
}
"""
ADMIN_CLIENT = """import "server-only";
import { createClient } from "@supabase/supabase-js";

export function adminClient() {
  return createClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.SUPABASE_SERVICE_ROLE_KEY!);
}
"""
ADMIN_ACTIONS_OK = """"use server";
import { requireAdmin } from "@/lib/auth/require-admin";
import { adminClient } from "@/lib/supabase/admin";

export async function deleteUser(id: string) {
  await requireAdmin();
  await adminClient().auth.admin.deleteUser(id);
}
"""
ADMIN_PAGE_OK = """import { requireAdmin } from "@/lib/auth/require-admin";
import { adminClient } from "@/lib/supabase/admin";

export default async function AdminPage() {
  await requireAdmin();
  const { data } = await adminClient().from("profiles").select("id, display_name, plan");
  return <ul>{(data ?? []).map((u) => <li key={u.id}>{u.display_name}</li>)}</ul>;
}
"""

CASES = []


def case(name, prompt, builder, expect, condition="skill"):
    CASES.append((name, prompt, builder, expect, condition))


case("healthy fixture, P1", "P1", lambda: build(),
     {"SQL-RLS-ENABLED": "pass", "SQL-POLICY-BINDING": "pass", "SQL-INSERT-CHECK": "pass",
      "SQL-UPDATE-CHECK": "pass", "CODE-SECRET-NOT-IN-CLIENT": "pass",
      "CODE-NO-PUBLIC-SECRET-ENV": "pass", "CODE-IDENTITY-FROM-SESSION": "pass",
      "SQL-ROLE-ESCALATION": "pass", "SQL-OWNER-OPS-COVERED": "pass"})

case("RLS enabled but no policies (deny all), P1", "P1",
     lambda: build(edits={MIG: "create table public.notes (id int, user_id uuid);\nalter table public.notes enable row level security;\n"}),
     {"SQL-RLS-ENABLED": "pass", "SQL-OWNER-OPS-COVERED": "fail"})

case("no SQL at all, P1", "P1", lambda: build(delete=[MIG]),
     {"SQL-SCHEMA-PRESENT": "fail"})

case("using (true) policy", "P1",
     lambda: build(appends={MIG: 'create policy "all notes" on public.notes for select to authenticated using (true);'}),
     {"SQL-NO-PERMISSIVE-POLICY": "fail", "SQL-POLICY-BINDING": "fail"})

case("authenticated-only policy", "P1",
     lambda: build(appends={MIG: "create policy \"any user\" on public.notes for select to authenticated using (auth.role() = 'authenticated');"}),
     {"SQL-POLICY-BINDING": "fail"})

case("RLS disabled", "P3",
     lambda: build(appends={MIG: "alter table public.notes disable row level security;"}),
     {"SQL-RLS-ENABLED": "fail", "SQL-NO-RLS-DISABLE": "fail"})

case("insert with check (true)", "P3",
     lambda: build(appends={MIG: 'create policy "open insert" on public.notes for insert to authenticated with check (true);'}),
     {"SQL-INSERT-CHECK": "fail", "SQL-NO-PERMISSIVE-POLICY": "fail"})

case("loose update check", "P1",
     lambda: build(appends={MIG: 'create policy "loose" on public.notes for update to authenticated using ((select auth.uid()) = user_id) with check (true);'}),
     {"SQL-UPDATE-CHECK": "fail"})

case("user_metadata policy", "P2",
     lambda: build(appends={MIG: "create policy \"admin read\" on public.notes for select to authenticated using ((auth.jwt() -> 'user_metadata' ->> 'role') = 'admin');"}),
     {"SQL-NO-USER-METADATA-AUTHZ": "fail", "SQL-POLICY-BINDING": "fail"})

case("service key in client module", "P1",
     lambda: build(edits={"lib/supabase/client.ts": 'import { createBrowserClient } from "@supabase/ssr";\nexport function createClient() {\n  return createBrowserClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.SUPABASE_SERVICE_ROLE_KEY!);\n}\n'}),
     {"CODE-SECRET-NOT-IN-CLIENT": "fail"})

case("service key only in server-only admin module", "P2",
     lambda: build(edits={"lib/supabase/admin.ts": ADMIN_CLIENT, "lib/auth/require-admin.ts": ADMIN_HELPER_OK,
                          "app/admin/actions.ts": ADMIN_ACTIONS_OK, "app/admin/page.tsx": ADMIN_PAGE_OK}),
     {"CODE-SECRET-NOT-IN-CLIENT": "pass", "CODE-ADMIN-SERVER-ENFORCED": "pass",
      "CODE-ADMIN-NOT-USER-METADATA": "pass", "CODE-ADMIN-NOT-MIDDLEWARE-ONLY": "pass",
      "CODE-NO-RLS-BYPASS": "pass"})

case("public env var holds service key", "P1",
     lambda: build(edits={".env.example": "NEXT_PUBLIC_SUPABASE_URL=\nNEXT_PUBLIC_SUPABASE_SERVICE_ROLE_KEY=\n"}),
     {"CODE-NO-PUBLIC-SECRET-ENV": "fail"})

case("service_role JWT literal", "P1",
     lambda: build(edits={"lib/keys.ts": f'export const KEY = "{SERVICE_JWT}";\n'}),
     {"CODE-NO-KEY-LITERALS": "fail"})

case("user_id taken from form data", "P1",
     lambda: build(edits={"app/notes/actions.ts": '"use server";\nimport { createClient } from "@/lib/supabase/server";\nexport async function createNote(formData: FormData) {\n  const supabase = await createClient();\n  await supabase.from("notes").insert({ user_id: formData.get("user_id"), title: String(formData.get("title")) });\n}\n'}),
     {"CODE-IDENTITY-FROM-SESSION": "review"})

case("role written from request body", "P2",
     lambda: build(edits={"app/api/users/route.ts": 'export async function POST(request: Request) {\n  const body = await request.json();\n  await db.update({ role: body.role });\n}\n'}),
     {"CODE-NO-ROLE-FROM-REQUEST": "fail"})

case("profiles update policy without role guard", "P2",
     lambda: build(appends={MIG: 'create policy "profiles: update own" on public.profiles for update to authenticated using ((select auth.uid()) = id) with check ((select auth.uid()) = id);'}),
     {"SQL-ROLE-ESCALATION": "fail"})

case("profiles update policy with role guard", "P2",
     lambda: build(appends={MIG: 'create policy "profiles: update own" on public.profiles for update to authenticated using ((select auth.uid()) = id) with check ((select auth.uid()) = id);\nrevoke update (role) on public.profiles from authenticated;'}),
     {"SQL-ROLE-ESCALATION": "pass"})

case("admin enforced, no role check in actions", "P2",
     lambda: build(edits={"lib/supabase/admin.ts": ADMIN_CLIENT,
                          "app/admin/actions.ts": '"use server";\nimport { adminClient } from "@/lib/supabase/admin";\nexport async function deleteUser(id: string) {\n  await adminClient().auth.admin.deleteUser(id);\n}\n',
                          "app/admin/page.tsx": ADMIN_PAGE_OK, "lib/auth/require-admin.ts": ADMIN_HELPER_OK}),
     {"CODE-ADMIN-SERVER-ENFORCED": "fail"})

case("admin check uses user_metadata", "P2",
     lambda: build(edits={"lib/supabase/admin.ts": ADMIN_CLIENT,
                          "app/admin/actions.ts": '"use server";\nimport { createClient } from "@/lib/supabase/server";\nimport { adminClient } from "@/lib/supabase/admin";\nexport async function deleteUser(id: string) {\n  const s = await createClient();\n  const { data: { user } } = await s.auth.getUser();\n  if (user?.user_metadata?.role !== "admin") throw new Error("no");\n  await adminClient().auth.admin.deleteUser(id);\n}\n'}),
     {"CODE-ADMIN-NOT-USER-METADATA": "fail"})

case("admin only a client component", "P2",
     lambda: build(edits={"app/admin/page.tsx": '"use client";\nimport { useState } from "react";\nexport default function Admin() {\n  const [u] = useState([]);\n  return <div>{u.length}</div>;\n}\n'}),
     {"CODE-ADMIN-SERVER-ENFORCED": "fail"})

case("admin check only in middleware", "P2",
     lambda: build(edits={"middleware.ts": 'import { NextResponse } from "next/server";\nexport function middleware(req: Request) {\n  const role = "user";\n  if (role !== "admin") return NextResponse.redirect(new URL("/", req.url));\n}\n',
                          "lib/supabase/admin.ts": ADMIN_CLIENT,
                          "app/admin/page.tsx": 'import { adminClient } from "@/lib/supabase/admin";\nexport default async function A() {\n  const { data } = await adminClient().from("profiles").select("*");\n  return <div>{data?.length}</div>;\n}\n'}),
     {"CODE-ADMIN-NOT-MIDDLEWARE-ONLY": "fail", "CODE-ADMIN-SERVER-ENFORCED": "fail"})

case("service key bypass in user actions (P3)", "P3",
     lambda: build(edits={"app/notes/actions.ts": '"use server";\nimport { createClient } from "@supabase/supabase-js";\nconst admin = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.SUPABASE_SERVICE_ROLE_KEY!);\nexport async function createNote(formData: FormData) {\n  await admin.from("notes").insert({ title: String(formData.get("title")) });\n}\n'}),
     {"CODE-NO-RLS-BYPASS": "fail"})

case("SECURITY.md present, skill condition", "P1",
     lambda: build(edits={"SECURITY.md": "# SECURITY.md\n## Access matrix\n| notes | owner CRUD |\n| profiles | owner R |\n"}),
     {"FILE-SECURITY-MD": "pass"})

case("SECURITY.md missing, skill condition", "P1", lambda: build(),
     {"FILE-SECURITY-MD": "fail"})

case("tests that assert denial are recognised", "P1",
     lambda: build(edits={"tests/a.test.ts": 'it("denies role user for both actions", () => {});\nit("rejects injected role fields", () => {});\n'}),
     {"FILE-DENIAL-TESTS": "review"})

case("tests without any denial assertions", "P1",
     lambda: build(edits={"tests/a.test.ts": 'it("renders the page", () => { expect(1).toBe(1); });\n'}),
     {"FILE-DENIAL-TESTS": "fail"})

case("SECURITY.md missing, baseline", "P1", lambda: build(),
     {"FILE-SECURITY-MD": "na"}, condition="baseline")


def main():
    failures = 0
    for name, prompt, builder, expect, cond in CASES:
        root = builder()
        got = {i["id"]: i["status"] for i in g.grade(str(root), prompt, cond)}
        bad = {k: (v, got.get(k, "missing")) for k, v in expect.items() if got.get(k) != v}
        if bad:
            failures += 1
            print(f"FAIL  {name}")
            for k, (want, have) in bad.items():
                print(f"        {k}: expected {want}, got {have}")
        else:
            print(f"ok    {name}")
        shutil.rmtree(root.parent, ignore_errors=True)
    print(f"\n{len(CASES) - failures}/{len(CASES)} cases passed")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
