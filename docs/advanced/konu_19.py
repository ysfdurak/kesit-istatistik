# -*- coding: utf-8 -*-

# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats, special
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, StratifiedKFold, KFold
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression, Ridge, LogisticRegression, BayesianRidge
from sklearn.metrics import mean_squared_error, log_loss, brier_score_loss, roc_auc_score, average_precision_score
from sklearn.datasets import make_classification, make_moons
import statsmodels.api as sm
import statsmodels.formula.api as smf
rng=np.random.default_rng(20261108)
np.set_printoptions(precision=4, suppress=True)
pd.set_option('display.max_columns',8)
plt.rcParams.update({'figure.figsize':(8,4),'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':.15})

a,b=2,18;groups=[(1,8),(10,80),(30,200)];p=np.linspace(.001,.999,400)
for k,n in groups:
 post=stats.beta(a+k,b+n-k);print({'k':k,'n':n,'ham':k/n,'sonsal':post.mean(),'CI95':post.ppf([.025,.975]).tolist()});plt.plot(p,post.pdf(p),label=f'{k}/{n}')
plt.xlabel('Grup olay olasılığı');plt.ylabel('Sonsal yoğunluk');plt.legend()
plt.show()

# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats, special
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, StratifiedKFold, KFold
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression, Ridge, LogisticRegression, BayesianRidge
from sklearn.metrics import mean_squared_error, log_loss, brier_score_loss, roc_auc_score, average_precision_score
from sklearn.datasets import make_classification, make_moons
import statsmodels.api as sm
import statsmodels.formula.api as smf
rng=np.random.default_rng(20261108)
np.set_printoptions(precision=4, suppress=True)
pd.set_option('display.max_columns',8)
plt.rcParams.update({'figure.figsize':(8,4),'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':.15})

a,b,step=5,9,.12;chains=[];accepted=0
for start in [.1,.35,.65,.9]:
 z=start;out=[]
 for i in range(2400):
  proposal=z+rng.normal(0,step)
  if 0<proposal<1 and np.log(rng.uniform())<stats.beta.logpdf(proposal,a,b)-stats.beta.logpdf(z,a,b):z=proposal;accepted+=1
  if i>=800:out.append(z)
 chains.append(out)
c=np.array(chains);split=c.reshape(8,800);W=split.var(axis=1,ddof=1).mean();B=800*split.mean(axis=1).var(ddof=1);rhat=np.sqrt(((799/800)*W+B/800)/W)
print({'kabul':accepted/9600,'klasik_split_Rhat':rhat,'cekim_ortalama':c.mean(),'analitik':a/(a+b)})
plt.plot(c.T[::8],alpha=.65);plt.xlabel('Saklanan çekim / 8');plt.ylabel('p')
plt.show()

# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats, special
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, StratifiedKFold, KFold
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression, Ridge, LogisticRegression, BayesianRidge
from sklearn.metrics import mean_squared_error, log_loss, brier_score_loss, roc_auc_score, average_precision_score
from sklearn.datasets import make_classification, make_moons
import statsmodels.api as sm
import statsmodels.formula.api as smf
rng=np.random.default_rng(20261108)
np.set_printoptions(precision=4, suppress=True)
pd.set_option('display.max_columns',8)
plt.rcParams.update({'figure.figsize':(8,4),'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':.15})

k,n=12,100;p=rng.beta(2+k,18+n-k,4000);rep=rng.binomial(n,p);print({'yeni_sayim_ortalama':rep.mean(),'ongoru_95':np.quantile(rep,[.025,.975]).tolist(),'gozlenen':k,'parametre_95':np.quantile(p,[.025,.975]).tolist()})
plt.hist(rep,bins=np.arange(rep.max()+2)-.5);plt.axvline(k,c='tab:orange',label='Gözlenen');plt.xlabel('Yeni 100 kayıtta hata sayısı');plt.ylabel('Tekrar');plt.legend()
plt.show()

# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats, special
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, StratifiedKFold, KFold
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression, Ridge, LogisticRegression, BayesianRidge
from sklearn.metrics import mean_squared_error, log_loss, brier_score_loss, roc_auc_score, average_precision_score
from sklearn.datasets import make_classification, make_moons
import statsmodels.api as sm
import statsmodels.formula.api as smf
rng=np.random.default_rng(20261108)
np.set_printoptions(precision=4, suppress=True)
pd.set_option('display.max_columns',8)
plt.rcParams.update({'figure.figsize':(8,4),'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':.15})

k,n,p0=18,100,.1;rows=[]
for a,b in [(1,1),(2,18),(10,90)]:
 logBF=special.betaln(a+k,b+n-k)-special.betaln(a,b)-k*np.log(p0)-(n-k)*np.log1p(-p0);prob=stats.beta.sf(p0,a+k,b+n-k);rows.append([f'{a},{b}',prob,np.exp(logBF)])
print(pd.DataFrame(rows,columns=['Beta_onsel','P_p_buyuk_H0','BF10']));C_FP,C_FN=2,10;print('Pozitif karar eşiği:',C_FP/(C_FP+C_FN))
plt.bar([r[0] for r in rows],[r[1] for r in rows]);plt.ylim(0,1);plt.xlabel('Önsel');plt.ylabel('P(p > H0 | veri)')
plt.show()
