import json,ast,zipfile
from pathlib import Path
import numpy as np,pandas as pd
from scipy.stats import tukey_hsd,ttest_rel
from statsmodels.stats.contingency_tables import mcnemar
D=Path('docs');B=json.loads((D/'business-content.js').read_text()[21:-1]);assert len(B)==7
for key,c in B.items():
 nb=json.loads((D/c['notebook']).read_text());assert nb['nbformat']==4
 for cell in nb['cells']:
  if cell['cell_type']=='code':
   ast.parse(''.join(cell['source']));assert cell['execution_count'] and len(cell['outputs'])>=2
 for sid,s in c['scenes'].items():
  for f in s['datasets']:assert len(pd.read_csv(D/f['file']))==f['rows']
  if key=='posthoc':
   raw=pd.read_csv(D/s['datasets'][0]['file']);groups=[g.seconds.values for _,g in raw.groupby('method')];ref=tukey_hsd(*groups,equal_var=False);ci=ref.confidence_interval()
   for row,(i,j) in zip(s['diagnostics']['gh'],[(0,1),(0,2),(1,2)]):
    np.testing.assert_allclose([row['difference'],row['p_adjusted'],row['lower'],row['upper']],[ref.statistic[i,j],ref.pvalue[i,j],ci.low[i,j],ci.high[i,j]],rtol=1e-8,atol=1e-10)
  if key=='picking':
   f=next(f for f in s['datasets']if f['name']=='operator_ortalamalari');raw=pd.read_csv(D/f['file']);r=ttest_rel(raw.A,raw.B);np.testing.assert_allclose(r.pvalue,s['diagnostics']['p'],rtol=1e-9);assert len(raw)==36
  if key=='model-pairs':
   assert np.isclose(mcnemar(s['diagnostics']['table'],exact=True).pvalue,s['diagnostics']['exact_p'])
  if key=='classifier':
   d=s['diagnostics'];assert d['train_max_day']<d['val_min_day']<=d['val_max_day']<d['test_min_day'];assert sum(d[x]for x in ['TP','FP','FN','TN'])==d['n_test'];assert ('final_duration_hours'in d['features'])==(sid=='leaky')
# Son testteki şok, önceden seçilmiş modeli veya donmuş referans sınırlarını değiştirmemeli.
a,b=[B['demand']['scenes'][x]['diagnostics']for x in ['default','shift']]
for k in ['validation_rows','selected_order','selected_season','test_start','test_n']:assert a[k]==b[k],k
assert a['mae_sarima']<a['mae_baseline'] and b['mae_sarima']>b['mae_baseline']
a,b=[B['control']['scenes'][x]['diagnostics']for x in ['default','stable']]
for k in ['Xbar_limits','R_upper','pbar','ubar','reference_n']:assert a[k]==b[k],k
assert a['mean_flags']==[36,37,38,39,40]and b['mean_flags']==[]and not a['reference_any_signal']
with zipfile.ZipFile(D/'business/Kesit_Is_Vakalari.zip')as z:assert z.testzip()is None and len([n for n in z.namelist()if n.endswith('.ipynb')])==7
print('PASS: bağımsız SciPy Games–Howell/eşli t referansları; McNemar; veri satırları; çalıştırılmış defterler; zaman ayrımı; değişmeyen referans ve ZIP.')
