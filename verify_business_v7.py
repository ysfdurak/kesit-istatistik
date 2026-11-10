import json
from pathlib import Path
import zipfile
import numpy as np
import pandas as pd
from scipy.stats import binomtest, ttest_ind
from sklearn.linear_model import LinearRegression
from sklearn.metrics import brier_score_loss
D=Path('docs')
p=D/'business-content-v7.js'
B=json.loads(p.read_text()[len('Object.assign(window.BUSINESS_DATA,'):-2])
assert len(B)==7
def case(k,s='default'):
    return B[k]['scenes'][s]
def data(k,s='default',i=0):
    return pd.read_csv(D/case(k,s)['datasets'][i]['file'])
for k,c in B.items():
    assert c['scenes'].keys()==dict(c['scenarios']).keys()
    for s,r in c['scenes'].items():
        for x in r['datasets']:
            assert len(pd.read_csv(D/x['file']))==x['rows']
        assert np.isfinite(r['exercise']['answer']) and len(r['focus'])==3
        for plot in r['plots']:
            assert (D/plot['file']).read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
    nb=json.loads((D/c['notebook']).read_text())
    assert len([x for x in nb['cells'] if x.get('outputs')])==2
    for x in nb['cells']:
        if x['cell_type']=='code':compile(''.join(x['source']),k,'exec')
d=case('sla-mix')['diagnostics']; assert np.allclose([d['crude_before'],d['crude_after'][0],d['fixed'][0]],[.962,.885,.975])
d=case('sla-mix','unknown')['diagnostics'];assert np.allclose(d['crude_after'],[.849,.897])
a,b=data('audit-sample'),data('audit-sample','nonresponse')
assert a.iloc[:,:2].equals(b.iloc[:,:2])
assert np.array_equal(a.iloc[:,2][b.iloc[:,2].notna()],b.iloc[:,2].dropna())
w=np.array([8000,3000,1000])/12000
s=case('audit-sample')['diagnostics'];assert np.isclose(s['weighted_bounds'][0],w@a.iloc[:,2].groupby(a.Tabaka,sort=False).mean())
assert s['ci'][0]<.06<s['ci'][1] and case('audit-sample','nonresponse')['diagnostics']['ci'] is None
for key in ['default','complaints']:
    e=case('experiment-guardrail',key)['diagnostics']
    n=e['n_arm']
    for row in e['rows']:
        _,a,b,_,_,point,low,high,_=row
        pa,pb=a/n,b/n
        wa=binomtest(a,n).proportion_ci(method='wilson')
        wb=binomtest(b,n).proportion_ci(method='wilson')
        expected=[pb-pa,(pb-pa)-np.hypot(pb-wb.low,wa.high-pa),(pb-pa)+np.hypot(wb.high-pb,pa-wa.low)]
        assert np.allclose([point,low,high],np.array(expected)*100)
assert case('experiment-guardrail')['diagnostics']['pass_guard'] and not case('experiment-guardrail','complaints')['diagnostics']['pass_guard']
assert np.array_equal(data('experiment-guardrail').Dönüşüm,data('experiment-guardrail','complaints').Dönüşüm)
for s in ['default','peak']:
    f=data('capacity-fit',s)
    x=f[['Sipariş','Karmaşık payı']]
    fit=LinearRegression().fit(x[:150],f['Adam-saat'][:150])
    r=case('capacity-fit',s)['diagnostics']
    assert np.allclose(r['coef'],np.r_[fit.intercept_,fit.coef_])
    assert r['prediction_half']>r['mean_half']
    assert np.isclose(r['mae'],np.abs(fit.predict(x[150:])-f['Adam-saat'][150:]).mean())
assert np.allclose(case('capacity-fit')['diagnostics']['coef'],case('capacity-fit','peak')['diagnostics']['coef'])
assert case('capacity-fit')['diagnostics']['cover']>case('capacity-fit','peak')['diagnostics']['cover']
for s in ['default','pretrend']:
    f=data('wms-impact',s,1)
    a,b=(f.loc[f.Pilot,'Sonra − önce · dk'],f.loc[~f.Pilot,'Sonra − önce · dk'])
    assert np.allclose(ttest_ind(a,b,equal_var=False).confidence_interval(),case('wms-impact',s)['diagnostics']['ci'])
assert abs(case('wms-impact')['diagnostics']['placebo'])<.2
assert abs(case('wms-impact','pretrend')['diagnostics']['placebo'])>.5
for s in ['default','shift']:
    f=data('risk-monitor',s)
    f=f[(f.Pencere=='Yeni') & f['Etiket olgun']]
    assert len(f)==1800 and f.Gecikme.notna().all()
    assert np.isclose(brier_score_loss(f.Gecikme,f['Sabit risk skoru']),case('risk-monitor',s)['metrics']['Olgun etiket · Brier'])
old,new=case('stock-service')['diagnostics'],case('stock-service','surge')['diagnostics']
assert old['stock']==new['stock']==94 and old['test_cycle']>new['test_cycle'] and old['test_fill']>old['test_cycle']
with zipfile.ZipFile(D/'business-v7/Kesit_Is_Vakalari_V7.zip') as z:
    assert z.testzip() is None and sum(n.endswith('.ipynb') for n in z.namelist())==7
print('PASS: CSV satırları, bağımsız Wilson/Newcombe, OLS ve Brier referansları, Welch aralığı, kayıp adres eşlemesi, stok, defter ve ZIP.')
