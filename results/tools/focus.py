import sys,re
sys.path.insert(0,"/mnt/user-data/outputs/vibe-skill-tests/graders")
from static_checks import parse_patch
root="/tmp/claude-0/p3/"
pat=re.compile(sys.argv[2],re.I)
ctx=int(sys.argv[3]) if len(sys.argv)>3 else 1
run=sys.argv[1]
f=parse_patch(open(root+run+"/changes.patch",encoding="utf-8",errors="replace").read())
print("===",run,"| FILES:",", ".join(f"{k}({len(v.splitlines())})" for k,v in f.items() if not re.search('package-lock|\\.css|tsconfig|next-env',k)))
for k,v in f.items():
    if re.search(r'package-lock|\.test\.|\.spec\.|tests/|\.css$|\.md$|\.example$',k): continue
    L=v.splitlines(); keep=set()
    for i,l in enumerate(L):
        if pat.search(l):
            keep.update(range(max(0,i-ctx),min(len(L),i+ctx+1)))
    if keep:
        print("##",k)
        last=-2
        for i in sorted(keep):
            if i!=last+1: print("  ...")
            print(L[i][:150]); last=i
print("--- MESSAGE"); print(open(root+run+"/last_message_1.txt",encoding="utf-8",errors="replace").read()[:1200])
