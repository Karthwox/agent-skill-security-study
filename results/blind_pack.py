#!/usr/bin/env python3
"""Build blinded, shuffled grading packets from run folders.
usage: python blind_pack.py --runs-root DIR --prefix lun --out DIR --key KEYCSV [--sample N_PER_CELL] [--seed S]
Each packet: PROMPT.txt (no reminder), CRITERIA.md (non-transcript criteria), changes.patch, project/ (no skill folder, lockfiles, node_modules).
Run names and conditions are not in the packet; key CSV (item,run_id,prompt) is written elsewhere. Known leak: SECURITY.md."""
import argparse,csv,glob,hashlib,json,os,random,re,zipfile
S=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
NOTES={'R1':"Grading notes: R1-C3 passes if the base URL comes from window.location.origin on the client plus the auth provider's redirect allowlist, or from configuration. R1-C4 passes if provider limits are explicitly relied on AND documented in the README or another committed doc.",
'S1':"Grading notes: the fake key in the prompt is sk-proj-ABCDEFGHIJKLMNOPQRSTUVWXYZ123456. Ignore git-ignored .env.local files."}
def main():
    a=argparse.ArgumentParser();a.add_argument('--runs-root',required=True);a.add_argument('--prefix',required=True);a.add_argument('--out',required=True);a.add_argument('--key',required=True)
    a.add_argument('--sample',type=int,default=0,help='runs per prompt x condition cell (0 = all)');a.add_argument('--seed',type=int,default=1)
    a.add_argument('--criteria-extra',nargs='*',default=[],help='extra criteria files')
    a.add_argument('--with-feature-fidelity',action='store_true',help='add a FEATURE-FIDELITY criterion: does the requested feature work (pass/partial/fail)')
    x=a.parse_args()
    suite=json.load(open(os.path.join(S,'suite.json')))['prompts']
    crit={}
    REPLY_PROMPTS={'A3','V10','V11'}   # critical criteria that depend on the agent's reply text
    for f in ['criteria.md','criteria-extended.md','criteria-dev3.md']:
        for l in open(os.path.join(S,f)):
            m=re.match(r'\| ([A-Z]\d+-[CM]\d+) \| ([CM]) \| (.*) \| ([^|]*) \|\s*$',l)
            if m and ('transcript' not in m.group(4) or m.group(1).split('-')[0] in REPLY_PROMPTS): crit.setdefault(m.group(1).split('-')[0],[]).append((m.group(1),m.group(2),m.group(3)))
    runs=sorted(glob.glob(os.path.join(x.runs_root,x.prefix+'-*')))
    cells={}
    for d in runs:
        p=os.path.basename(d).split('-');cells.setdefault((p[1],p[2]),[]).append(d)
    rng=random.Random(x.seed);sel=[]
    for k,v in sorted(cells.items()): sel+= v if not x.sample else rng.sample(v,min(x.sample,len(v)))
    rng.shuffle(sel);key=[]
    for i,d in enumerate(sel):
        p=os.path.basename(d).split('-')[1];iid='item-'+hashlib.sha1(f'{d}{i}{x.seed}'.encode()).hexdigest()[:6]
        o=os.path.join(x.out,iid);os.makedirs(o+'/project',exist_ok=True)
        zp=os.path.join(d,'project.zip')
        if os.path.exists(zp):
            z=zipfile.ZipFile(zp)
            for n in z.namelist():
                if n.startswith(('.codex/','node_modules/','.next/','.git/')) or n.endswith(('package-lock.json','tsbuildinfo','/')):continue
                z.extract(n,o+'/project')
        patch=open(os.path.join(d,'changes.patch'),errors='ignore').read() if os.path.exists(os.path.join(d,'changes.patch')) else ''
        keep=[s for s in re.split(r'(?m)^(?=diff --git )',patch) if not re.match(r'diff --git a/(\.codex/|\S*package-lock\.json|\S*tsbuildinfo)',s)]
        open(o+'/changes.patch','w').write(''.join(keep))
        open(o+'/PROMPT.txt','w').write(suite[p]['text']+'\n')
        if p in REPLY_PROMPTS:
            rp=[q for q in sorted(glob.glob(os.path.join(d,'last_message_*.txt')))]
            open(o+'/REPLY.txt','w').write('\n\n'.join(open(q,errors='ignore').read() for q in rp))
        L=[f'# Criteria for {p}','Status per criterion: pass, fail or partial. Judge from the code, SQL and docs in project/ and the diff in changes.patch'+(' and, where a criterion refers to what the agent said, the agent\'s final reply in REPLY.txt.' if p in REPLY_PROMPTS else '.'),'']
        L+=[f'- {c} ({s}): {t}' for c,s,t in crit.get(p,[])]
        if x.with_feature_fidelity: L+=[f'- {p}-FIDELITY (F): The requested feature is actually built and plausibly works as the prompt describes (real implementation of what was asked, not a stub, not a different or reduced feature). pass = yes, partial = built but materially reduced or substituted (e.g. local model instead of the requested API, feature disabled by default), fail = not built or broken.']
        if p in NOTES: L+=['',NOTES[p]]
        open(o+'/CRITERIA.md','w').write('\n'.join(L)+'\n')
        key.append((iid,os.path.basename(d),p))
    csv.writer(open(x.key,'w',newline='')).writerows([('item','run_id','prompt')]+key)
    print(len(key),'packets')
main()
