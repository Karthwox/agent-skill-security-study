import sys,re
sys.path.insert(0,"/mnt/user-data/outputs/vibe-skill-tests/graders")
from static_checks import parse_patch
root="/tmp/claude-0/p3/"
run=sys.argv[1]; mode=sys.argv[2] if len(sys.argv)>2 else "sec"
f=parse_patch(open(root+run+"/changes.patch",encoding="utf-8",errors="replace").read())
SKIP=re.compile(r'package-lock|\.css$|\.svg$|\.md$|\.test\.|\.spec\.|__tests__|tsconfig|next-env|\.gitignore|globals')
print("=== ",run)
print("FILES:", ", ".join(f"{k}({len(v.splitlines())})" for k,v in f.items() if 'package-lock' not in k))
if mode=="msg":
    print(open(root+run+"/last_message_1.txt",encoding="utf-8",errors="replace").read()); sys.exit()
for k,v in f.items():
    if SKIP.search(k): continue
    if mode=="sec" and re.search(r'components/|app/.*page\.tsx$|layout\.tsx$',k) and not re.search(r'fetch\(|supabase|storage|upload|api/',v): continue
    if re.search(r'lib/supabase/(server|client)\.ts$',k): continue
    if v.lstrip().startswith('"use client"'):
        refs=[l.strip()[:100] for l in v.splitlines() if re.search(r'process\.env|NEXT_PUBLIC|OPENAI|apiKey|fetch\(',l)]
        print("##",k,"[client component]",len(v.splitlines()),"lines; refs:",refs); continue
    print("##",k)
    for l in v.splitlines():
        if l.strip(): print(l[:160])
print("--- MESSAGE"); print(open(root+run+"/last_message_1.txt",encoding="utf-8",errors="replace").read()[:1500])
