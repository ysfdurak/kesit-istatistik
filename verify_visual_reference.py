import json
from scipy import stats
from statsmodels.stats.multitest import multipletests
p=[.004,.015,.03,.04,.2,.6]
json.dump({'raw':p,'holm':multipletests(p,method='holm')[1].tolist(),'bh':multipletests(p,method='fdr_bh')[1].tolist(),'z_p':float(2*stats.norm.sf(1/(2*4**2/30)**.5)),'ci_width':float(2*stats.norm.ppf(.975)*10/25**.5)},open('visualrefs.json','w'))
