import csv,sys,os
# usage: g.py RUN "C1=pass,C2=fail:note;..."  (crit prefix is added by caller)
p='/tmp/claude-0/grades/manual-grades.csv'
run=sys.argv[1]
rows=[]
for item in sys.argv[2].split(';'):
    item=item.strip()
    if not item: continue
    k,v=item.split('=',1)
    s,_,n=v.partition(':')
    rows.append((run,k,s,n))
exist=list(csv.reader(open(p)))
keep=[r for r in exist if not (r[0]==run and r[1] in {x[1] for x in rows})]
with open(p,'w',newline='') as f:
    w=csv.writer(f); w.writerows(keep); w.writerows(rows)
