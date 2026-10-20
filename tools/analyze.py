#!/usr/bin/env python3
"""Tallies and stratified exact permutation test from a grades CSV (run_id,criterion,status).
usage: python analyze.py GRADES.csv [--conds base rem skill]
Outcome: run has >=1 critical (-C) criterion with status fail. Strata = prompts. Two-sided exact p (hypergeometric convolution)."""
import csv,sys,collections as C
from math import comb
def pmf(n1,n2,k):
    t=comb(n1+n2,k);return {a:comb(n1,a)*comb(n2,k-a)/t for a in range(max(0,k-n2),min(n1,k)+1)}
def conv(d1,d2):
    r=C.defaultdict(float)
    for a,p in d1.items():
        for b,q in d2.items(): r[a+b]+=p*q
    return r
def perm(rows,c1,c2):
    st=C.defaultdict(lambda:{c1:[],c2:[]})
    for run,(p,c,f) in rows.items():
        if c in (c1,c2): st[p][c].append(f)
    dist={0:1.0};obs=0;mean=0
    for p,v in st.items():
        n1,n2=len(v[c1]),len(v[c2]);k=sum(v[c1])+sum(v[c2]);d=pmf(n1,n2,k);dist=conv(dist,d)
        obs+=sum(v[c1]);mean+=n1*k/(n1+n2)
    pv=sum(q for a,q in dist.items() if abs(a-mean)>=abs(obs-mean)-1e-12)
    return obs,pv
def main():
    g=sys.argv[1];rows={};seen=C.defaultdict(list)
    for r in csv.DictReader(open(g)):
        if '-C' in r['criterion']: seen[r['run_id']].append(r['status'].strip().lower())
    for run,v in seen.items():
        q=run.split('-');rows[run]=(q[1],q[2],int('fail' in v))
    conds=['base','rem','skill'];tab=C.defaultdict(lambda:[0,0])
    for run,(p,c,f) in rows.items(): tab[(p,c)][0]+=f;tab[(p,c)][1]+=1
    ps=sorted({p for p,_ in tab})
    print('runs with >=1 critical fail / runs')
    print('prompt  '+'  '.join(f'{c:>8}' for c in conds))
    for p in ps: print(f'{p:6}  '+'  '.join(f'{tab[(p,c)][0]}/{tab[(p,c)][1]}'.rjust(8) for c in conds))
    print('total   '+'  '.join(f"{sum(tab[(p,c)][0] for p in ps)}/{sum(tab[(p,c)][1] for p in ps)}".rjust(8) for c in conds))
    for a,b in [('skill','rem'),('base','rem'),('base','skill')]:
        if any(c==a for _,c,_ in rows.values()) and any(c==b for _,c,_ in rows.values()):
            o,p=perm(rows,a,b);print(f'{a} vs {b}: fails in {a} = {o}, stratified exact two-sided p = {p:.3g}')
main()
