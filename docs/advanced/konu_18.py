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

x=rng.uniform(0,5,180);shift=rng.integers(0,2,180);y=3+2*x+2*shift+1.2*x*shift+.2*x*x+rng.normal(0,1,180);d=pd.DataFrame({'x':x,'vardiya':shift,'y':y});fit=smf.ols('y ~ x * vardiya + I(x**2)',d).fit();print(fit.params.round(3));print('Etkileşim CI:',fit.conf_int().loc['x:vardiya'].round(3).tolist())
for g in [0,1]:
 xx=np.linspace(0,5,80);plt.scatter(x[shift==g],y[shift==g],s=10,alpha=.25);plt.plot(xx,fit.predict(pd.DataFrame({'x':xx,'vardiya':g})),label=f'Vardiya {g}')
plt.xlabel('Hacim');plt.ylabel('Süre');plt.legend()
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

x=rng.normal(size=250);exposure=rng.uniform(.5,3,250);mu=exposure*np.exp(.5+.6*x);y=rng.negative_binomial(3,3/(3+mu));X=sm.add_constant(x)
pois=sm.GLM(y,X,family=sm.families.Poisson(),offset=np.log(exposure)).fit();nb=sm.NegativeBinomial(y,X,offset=np.log(exposure)).fit(disp=False)
print({'Poisson_beta':pois.params.tolist(),'NB_beta_ve_alpha':nb.params.tolist(),'Poisson_Pearson_dispersion':pois.pearson_chi2/pois.df_resid})
order=np.argsort(x);plt.scatter(x,y/exposure,s=12,alpha=.25,label='Gözlenen oran');plt.plot(x[order],np.exp(X@pois.params)[order],label='Poisson');plt.plot(x[order],np.exp(X@nb.params[:2])[order],label='NB');plt.xlabel('x');plt.ylabel('Olay / maruziyet');plt.legend()
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

rows=[]
for g,n in enumerate([5,8,12,16,20,24,30,40]):
 u=rng.normal(0,2)
 for j in range(n):rows.append([str(g),10+u+rng.normal(0,3)])
d=pd.DataFrame(rows,columns=['depo','sure']);fit=smf.mixedlm('sure ~ 1',d,groups=d.depo).fit(reml=True,method='powell',disp=False);raw=d.groupby('depo').sure.mean();pooled=np.array([fit.fe_params.iloc[0]+float(fit.random_effects[g].iloc[0]) for g in raw.index]);print({'genel_ortalama':float(fit.fe_params.iloc[0]),'grup_varyansi':float(fit.cov_re.iloc[0,0]),'hata_varyansi':float(fit.scale)})
plt.plot(raw.index,raw,'o',label='Ham');plt.plot(raw.index,pooled,'o',label='Kısmi havuzlama');plt.xlabel('Depo');plt.ylabel('Beklenen süre');plt.legend()
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

x=rng.uniform(0,8,250);y=5+2*x+rng.normal(size=len(x))*(1+.5*x);X=sm.add_constant(x);grid=np.linspace(0,8,100)
for q in [.5,.9]:
 fit=sm.QuantReg(y,X).fit(q=q,max_iter=3000);print('Kantil',q,'katsayılar',fit.params.round(3));plt.plot(grid,fit.predict(sm.add_constant(grid)),label=f'q={q}')
plt.scatter(x,y,s=10,alpha=.2);plt.xlabel('Hacim');plt.ylabel('Süre');plt.legend()
plt.show()
