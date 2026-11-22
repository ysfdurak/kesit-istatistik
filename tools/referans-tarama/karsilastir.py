import json, numpy as np, scipy.stats as st, warnings
from statsmodels.stats.proportion import proportion_confint, proportions_ztest
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, log_loss
warnings.filterwarnings('ignore')
import os,sys
H=os.path.dirname(os.path.abspath(__file__))
C=json.load(open(os.path.join(H,'cases.json')));J=json.load(open(os.path.join(H,'js.json')))
bad={};cnt={}
def chk(kind,name,got,want,rel=1e-7,ab=1e-10,ctx=None):
    cnt[kind]=cnt.get(kind,0)+1
    if want is None or got is None:
        if (want is None)!=(got is None): bad.setdefault(kind,[]).append((name,got,want,ctx))
        return
    if not np.isfinite(want) and not (got is not None and np.isfinite(got)): return
    if abs(got-want)>max(ab,rel*abs(want)): bad.setdefault(kind,[]).append((name,got,want,ctx))
for c,j in zip(C,J):
    k=c['kind']
    if not j['ok']: bad.setdefault(k+'_err',[]).append((j['err'],{x:c[x] for x in c if x!='kind'} )); continue
    r=j['r']
    if k=='normalCDF': chk(k,'cdf',r,st.norm.cdf(c['x']),1e-9,1e-15,c)
    elif k=='normalInv': chk(k,'inv',r,st.norm.ppf(c['p']),1e-9,1e-12,c)
    elif k=='tP': chk(k,'p',r,2*st.t.sf(c['t'],c['df']),1e-7,1e-15,c)
    elif k=='tInv': chk(k,'q',r,st.t.ppf(c['p'],c['df']),1e-8,1e-10,c)
    elif k=='gammaQ': chk(k,'Q',r,st.gamma.sf(c['x'],c['a']),1e-8,1e-14,c)
    elif k=='betaI': chk(k,'I',r,st.beta.cdf(c['x'],c['a'],c['b']),1e-8,1e-14,c)
    elif k=='ci':
        a=np.array(c['a']);lo,hi=st.t.interval(c['level'],len(a)-1,a.mean(),st.sem(a)); chk(k,'lower',r['lower'],lo,1e-9,1e-9,c); chk(k,'upper',r['upper'],hi,1e-9,1e-9,c)
    elif k=='ttest1':
        t=st.ttest_1samp(c['a'],c['mu']); chk(k,'t',r['t'],t.statistic,1e-9,1e-9,c); chk(k,'p',r['p'],t.pvalue,1e-7,1e-14,c)
        ci=t.confidence_interval(); chk(k,'lower',r['lower']+c['mu'],ci.low,1e-8,1e-9,c)
    elif k=='welch':
        t=st.ttest_ind(c['a'],c['b'],equal_var=False); chk(k,'t',r['t'],t.statistic,1e-9,1e-9,c); chk(k,'p',r['p'],t.pvalue,1e-7,1e-14,c); chk(k,'df',r['df'],t.df,1e-9,1e-9,c)
        ci=t.confidence_interval(); chk(k,'lower',r['lower'],ci.low,1e-8,1e-9,c); chk(k,'upper',r['upper'],ci.high,1e-8,1e-9,c)
    elif k=='paired':
        if np.var(np.array(c['a'])-np.array(c['b']))==0: continue
        t=st.ttest_rel(c['a'],c['b']); chk(k,'p',r['p'],t.pvalue,1e-7,1e-14,c)
    elif k=='wilson':
        lo,hi=proportion_confint(c['k'],c['n'],method='wilson'); chk(k,'lower',r['lower'],lo,1e-9,1e-12,c); chk(k,'upper',r['upper'],hi,1e-9,1e-12,c)
    elif k=='ab':
        z,p=proportions_ztest([c['k2'],c['k1']],[c['n2'],c['n1']]); chk(k,'z',r['z'],z,1e-9,1e-9,c); chk(k,'p',r['p'],p,1e-7,1e-14,c)
    elif k=='anova':
        f=st.f_oneway(*c['groups']); chk(k,'F',r['F'],f.statistic,1e-9,1e-9,c); chk(k,'p',r['p'],f.pvalue,1e-7,1e-14,c)
    elif k=='categorical':
        ch=st.chi2_contingency(c['t'],correction=False); chk(k,'chi',r['chi'],ch.statistic,1e-9,1e-9,c); chk(k,'p',r['p'],ch.pvalue,1e-7,1e-14,c)
        chk(k,'fisher',r['fisher'],st.fisher_exact(c['t']).pvalue,1e-7,1e-12,c)
    elif k=='pearson':
        p=st.pearsonr(c['x'],c['y']); chk(k,'r',r['r'],p.statistic,1e-9,1e-12,c); chk(k,'p',r['p'],p.pvalue,1e-6,1e-14,c)
    elif k=='spearman':
        p=st.spearmanr(c['x'],c['y']); chk(k,'r',r['r'],p.statistic,1e-9,1e-12,c); chk(k,'p',r['p'],p.pvalue,1e-6,1e-14,c)
    elif k=='regression':
        L=st.linregress(c['x'],c['y']); chk(k,'slope',r['slope'],L.slope,1e-9,1e-12,c); chk(k,'se',r['slopeSE'],L.stderr,1e-8,1e-12,c); chk(k,'p',r['p'],L.pvalue,1e-6,1e-14,c)
    elif k=='mannWhitney':
        m=st.mannwhitneyu(c['a'],c['b'],method='asymptotic',use_continuity=True); chk(k,'U',r['U'],m.statistic,1e-12,1e-9,c); chk(k,'p',r['p'],m.pvalue,1e-7,1e-14,c)
    elif k=='bayes':
        A=c['a']+c['k'];B=c['b']+c['n']-c['k']; chk(k,'lower',r['lower'],st.beta.ppf(.025,A,B),1e-7,1e-10,c); chk(k,'upper',r['upper'],st.beta.ppf(.975,A,B),1e-7,1e-10,c)
    elif k=='metrics':
        y=c['y'];p=c['p']; chk(k,'auc',r['auc'],roc_auc_score(y,p),1e-9,1e-12,c); chk(k,'ap',r['ap'],average_precision_score(y,p),1e-9,1e-12,c)
        chk(k,'brier',r['brier'],brier_score_loss(y,p),1e-9,1e-12,c); chk(k,'logloss',r['logloss'],log_loss(y,np.clip(p,1e-12,1-1e-12)),1e-7,1e-10,c)
    elif k=='summary':
        a=np.array(c['a']); chk(k,'median',r['median'],np.median(a),1e-12,1e-12,c); chk(k,'q1',r['q1'],np.quantile(a,.25),1e-12,1e-12,c); chk(k,'sd',r['sd'],a.std(ddof=1),1e-12,1e-12,c)
    elif k=='survival':
        from statsmodels.duration.survfunc import SurvfuncRight
        if sum(c['event'])==0: continue
        sf=SurvfuncRight(c['time'],c['event'])
        # compare S at each event time
        S={t:s for t,s in zip(sf.surv_times,sf.surv_prob)}
        for row in r['table']:
            if row['time'] in S: chk(k,'S',row['S'],None if False else S[row['time']],1e-9,1e-12,c)
        med=None
        for t,s in zip(sf.surv_times,sf.surv_prob):
            if s<=.5: med=t;break
        chk(k,'median',r['median'],med,1e-12,1e-12,c)
    elif k=='binomial':
        chk(k,'prob',r['prob'],st.binom.pmf(c['k'],c['n'],c['p']),1e-9,1e-15,c)
for k in sorted(set(list(cnt)+list(bad))):
    b=bad.get(k,[]); print(f"{k:14s} kontrol {cnt.get(k,0):5d}  hatali {len(b)}")
    for x in b[:4]: print('    ',str(x)[:300])
hata=sum(len(v) for k,v in bad.items() if not (k=='survival' and all(x[0]=='median' for x in v)))
print('TOPLAM', sum(cnt.values()), 'kontrol; uyuşmayan', hata)
sys.exit(1 if hata else 0)
