"""Sensitivities motivated by the human sample (run after final_phase6.py). Usage: python sens_phase6_human.py results/phase6"""
import csv,sys,re,collections as C
from math import comb
R=sys.argv[1]
g={(r['run_id'],r['criterion']):r['status'] for r in csv.DictReader(open(R+'/final-p6.csv'))}
note={}
for f in ('pass1-all.csv','pass2-all.csv'):
    for r in csv.DictReader(open(f'{R}/{f}')): note[(r['run_id'],r['criterion'],f)]=r['note']
def oneshot(run):
    if run.split('-')[1]!='V37' or g[(run,'V37-C1')]!='pass': return False
    t=note.get((run,'V37-C1','pass1-all.csv'),'')+' '+note.get((run,'V37-C1','pass2-all.csv'),'')
    return bool(re.search(r'never stored|not stored|nothing stored|no storage|never persisted|not persisted|no connect|per request|per gist',t,re.I))
def adjust(mode):
    h=dict(g)
    for (run,c),s in g.items():
        if 'oneshot' in mode.split('+') and c=='V37-C1' and oneshot(run): h[(run,c)]='fail'
        if 'v40' in mode.split('+') and c=='V40-C3' and s=='fail': h[(run,c)]='partial'
    return h
def runs(h):
    out={}
    for (run,c),s in h.items():
        if '-C' in c: out.setdefault(run,[]).append(s)
    return {r:(r.split('-')[1],r.split('-')[2],int('fail' in v)) for r,v in out.items()}
def pmf(n1,n2,k):
    t=comb(n1+n2,k);return {a:comb(n1,a)*comb(n2,k-a)/t for a in range(max(0,k-n2),min(n1,k)+1)}
def conv(a,b):
    r=C.defaultdict(float)
    for x,p in a.items():
        for y,q in b.items(): r[x+y]+=p*q
    return r
def perm(rows,c1,c2,sub):
    st=C.defaultdict(lambda:{c1:[],c2:[]})
    for run,(p,c,f) in rows.items():
        if c in(c1,c2) and p in sub: st[p][c].append(f)
    d={0:1.0};o=0;m=0
    for p,v in st.items():
        n1,n2=len(v[c1]),len(v[c2]);k=sum(v[c1])+sum(v[c2]);d=conv(d,pmf(n1,n2,k));o+=sum(v[c1]);m+=n1*k/(n1+n2)
    return sum(q for a,q in d.items() if abs(a-m)>=abs(o-m)-1e-12)
INF=('V36','V37','V40');ALL=('V34','V36','V37','V40','V44','V45','V46','V47')
for mode in ('none','oneshot','v40','oneshot+v40'):
    rows=runs(adjust(mode))
    print(f'## treatment: {mode}  (one-shot V37 token designs counted as C1 fail: {"oneshot" in mode.split("+")}; V40-C3 fail -> partial: {"v40" in mode.split("+")})')
    for name,sub in (('primary clusters',INF),('all eight',ALL)):
        cnt={a:sum(f for (p,c,f) in rows.values() if c==a and p in sub) for a in ('base','rem','chk','plc','skill')}
        n={a:sum(1 for (p,c,f) in rows.values() if c==a and p in sub) for a in cnt}
        print(f'- {name}: '+', '.join(f'{a} {cnt[a]}/{n[a]}' for a in cnt)+f'; skill vs reminder p = {perm(rows,"skill","rem",sub):.2f}; checklist vs reminder p = {perm(rows,"chk","rem",sub):.2f}; placebo vs baseline p = {perm(rows,"plc","base",sub):.2f}')
n=sum(1 for r in {k[0] for k in g if k[0].split('-')[1]=='V37'} if oneshot(r));print('V37 one-shot designs by arm:',C.Counter(r.split('-')[2] for r in {k[0] for k in g if k[0].split('-')[1]=='V37'} if oneshot(r)))
