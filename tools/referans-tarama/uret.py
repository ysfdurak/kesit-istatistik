import numpy as np, json
rng=np.random.default_rng(7)
C=[]
def add(kind,**kw): C.append(dict(kind=kind,**kw))
for _ in range(300):
    x=float(rng.normal(0,3)); add('normalCDF',x=x)
for p in list(rng.uniform(1e-6,1-1e-6,200))+[1e-9,1e-12,.5,.999999]: add('normalInv',p=float(p))
for _ in range(400):
    df=float(rng.choice([1,2,3,5,10,30,100,1000]) if rng.random()<.6 else rng.uniform(1.1,300)); t=float(abs(rng.standard_t(3))*rng.choice([.3,1,3,10])); add('tP',t=t,df=df)
for _ in range(200):
    df=float(rng.choice([1,2,4,9,29,99]) if rng.random()<.6 else rng.uniform(1.5,200)); p=float(rng.choice([.9,.95,.975,.99,.995,.9995])); add('tInv',p=p,df=df)
for _ in range(300):
    a=float(rng.uniform(.05,60)); x=float(rng.uniform(0,3*a+5)); add('gammaQ',a=a,x=x)
for _ in range(300):
    a=float(rng.uniform(.05,200)); b=float(rng.uniform(.05,200)); x=float(rng.uniform(0,1)); add('betaI',x=x,a=a,b=b)
def sample(n): 
    k=rng.integers(3)
    return [float(round(v,2)) for v in (rng.normal(50,10,n) if k==0 else rng.exponential(5,n) if k==1 else rng.integers(0,6,n))]
for _ in range(150):
    n=int(rng.integers(2,60)); a=sample(n); 
    if np.var(a)==0: continue
    add('ci',a=a,level=float(rng.choice([.9,.95,.99])))
    add('ttest1',a=a,mu=float(round(np.mean(a)+rng.normal(0,2),2)))
    m=int(rng.integers(2,60)); b=sample(m)
    if np.var(b)>0: add('welch',a=a,b=b)
    b2=[float(round(v+rng.normal(0.5,1),2)) for v in a]; add('paired',a=a,b=b2)
for _ in range(200):
    n=int(rng.integers(1,5000)); k=int(rng.integers(0,n+1)); add('wilson',k=k,n=n)
for _ in range(150):
    n1=int(rng.integers(5,3000)); n2=int(rng.integers(5,3000)); k1=int(rng.integers(0,n1+1)); k2=int(rng.integers(0,n2+1))
    if (k1+k2)==0 or (k1+k2)==n1+n2: continue
    add('ab',k1=k1,n1=n1,k2=k2,n2=n2)
for _ in range(100):
    g=int(rng.integers(3,9)); add('anova',groups=[sample(int(rng.integers(2,20))) for _ in range(g)])
for _ in range(200):
    t=[[int(rng.integers(0,60)) for _ in range(2)] for _ in range(2)]
    if min(t[0][0]+t[0][1],t[1][0]+t[1][1],t[0][0]+t[1][0],t[0][1]+t[1][1])==0: continue
    add('categorical',t=t)
for _ in range(150):
    n=int(rng.integers(3,80)); x=sample(n); y=[float(round(v*rng.normal(.5,1)+rng.normal(0,5),2)) for v in x]
    if np.var(x)==0 or np.var(y)==0: continue
    add('pearson',x=x,y=y); add('spearman',x=x,y=y); add('regression',x=x,y=y)
for _ in range(150):
    a=sample(int(rng.integers(2,40))); b=sample(int(rng.integers(2,40)))
    if len(set(a+b))==1: continue
    add('mannWhitney',a=a,b=b)
for _ in range(100):
    n=int(rng.integers(1,500)); k=int(rng.integers(0,n+1)); add('bayes',k=k,n=n,a=float(rng.uniform(.5,20)),b=float(rng.uniform(.5,20)))
for _ in range(80):
    n=int(rng.integers(5,100)); y=[int(v) for v in rng.integers(0,2,n)]; p=[float(round(v,2)) for v in rng.uniform(0,1,n)]
    if len(set(y))<2: continue
    add('metrics',y=y,p=p)
for _ in range(80):
    n=int(rng.integers(2,60)); add('summary',a=sample(n))
for _ in range(80):
    n=int(rng.integers(5,40)); t=[float(round(v,1)) for v in rng.exponential(10,n)]; e=[int(v) for v in rng.integers(0,2,n)]; add('survival',time=t,event=e)
for _ in range(60):
    n=int(rng.integers(1,200)); k=int(rng.integers(0,n+1)); add('binomial',n=n,p=float(rng.uniform(0,1)),k=k)
json.dump(C,open(__import__('os').path.join(__import__('os').path.dirname(__file__),'cases.json'),'w'))
print(len(C))
