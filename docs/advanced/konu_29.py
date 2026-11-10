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

x=rng.normal(size=1000);prop=special.expit(x);t=rng.binomial(1,prop);y=2*t+3*x+rng.normal(size=1000);m=LogisticRegression(C=1e5).fit(x[:,None],t);e=m.predict_proba(x[:,None])[:,1]
if np.min(e)<.01 or np.max(e)>.99:print('UYARI: zayıf destek / uç ağırlık')
w1=t/e;w0=(1-t)/(1-e);effect=np.sum(w1*y)/w1.sum()-np.sum(w0*y)/w0.sum();ess=lambda w:w.sum()**2/(w@w)
print({'ham_fark':y[t==1].mean()-y[t==0].mean(),'Hajek_IPW':effect,'gercek_etki':2,'tedavi_ESS':ess(w1),'kontrol_ESS':ess(w0)})
plt.hist(e[t==0],bins=20,alpha=.5,label='Kontrol');plt.hist(e[t==1],bins=20,alpha=.5,label='Tedavi');plt.xlabel('Tahmin edilen eğilim');plt.ylabel('Kayıt');plt.legend()
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

n=1200;z=rng.normal(size=n);u=rng.normal(size=n);t=z+.8*u+rng.normal(size=n);y=2*t+u+rng.normal(size=n);first=sm.OLS(t,sm.add_constant(z)).fit();that=first.fittedvalues;beta_iv=sm.OLS(y,sm.add_constant(that)).fit().params[1];ols=sm.OLS(y,sm.add_constant(t)).fit().params[1]
print({'OLS':ols,'2SLS_nokta':beta_iv,'gercek':2,'ilk_asama_F':float(first.fvalue),'CI':'Bu örnekte IV güven aralığı hesaplanmadı'})
plt.bar(['OLS','2SLS','Gerçek'],[ols,beta_iv,2]);plt.ylabel('Etki tahmini')
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

x=rng.uniform(-2,2,800);t=(x>=0).astype(int);y=5+2*x+1.5*t+.4*x*t+rng.normal(size=len(x));band=.6;keep=np.abs(x)<=band;df=pd.DataFrame({'x':x[keep],'t':t[keep],'y':y[keep]});fit=smf.ols('y ~ x * t',df).fit(cov_type='HC1');print({'yerel_n':int(keep.sum()),'sicrama':fit.params['t'],'HC1_CI':fit.conf_int().loc['t'].tolist(),'gercek':1.5})
plt.scatter(df.x,df.y,s=10,alpha=.25)
for g in [0,1]:
 grid=np.linspace(-band,0,60) if g==0 else np.linspace(0,band,60);plt.plot(grid,fit.predict(pd.DataFrame({'x':grid,'t':g})))
plt.axvline(0,c='gray');plt.xlabel('Eşiğe uzaklık');plt.ylabel('Sonuç')
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

n=800;pre=rng.normal(size=n);t=rng.binomial(1,.5,n);y=.15*t+.8*pre+rng.normal(size=n);theta=np.cov(y,pre,ddof=1)[0,1]/np.var(pre,ddof=1);adjusted=y-theta*(pre-pre.mean());looks=[200,400,600,800];p=[]
for k in looks:p.append(stats.ttest_ind(y[:k][t[:k]==1],y[:k][t[:k]==0],equal_var=False).pvalue)
print({'bakis_p':p,'planli_esik':.05/len(looks),'ham_varyans':np.var(y),'CUPED_varyans':np.var(adjusted),'theta':theta});plt.plot(looks,p,'o-');plt.axhline(.05/len(looks),c='tab:orange');plt.xlabel('Planlı bakış n');plt.ylabel('İki yönlü p')
plt.show()
