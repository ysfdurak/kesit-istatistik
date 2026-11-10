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

from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
x=rng.normal(size=250);z=.6*x+rng.normal(size=250);y=1+2*x+z+rng.normal(size=250);data=np.c_[x,z,y];mask=rng.uniform(size=250)<.25;data[mask,0]=np.nan;est=[];vars=[]
for seed in range(10):
 complete=IterativeImputer(estimator=BayesianRidge(),sample_posterior=True,random_state=seed,max_iter=10).fit_transform(data);fit=sm.OLS(complete[:,2],sm.add_constant(complete[:,:2])).fit();est.append(fit.params[1]);vars.append(fit.cov_params()[1,1])
within=np.mean(vars);between=np.var(est,ddof=1);total=within+1.1*between;print({'havuz_egim':np.mean(est),'ic_varyans':within,'arasi_varyans':between,'Rubin_SE':np.sqrt(total)})
plt.plot(range(1,11),est,'o');plt.axhline(np.mean(est),c='tab:orange');plt.xlabel('Atama');plt.ylabel('Tamamlanmış veri eğimi')
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

y=rng.normal(10,2,100);w=np.r_[np.ones(99),15.];estimate=np.average(y,weights=w);ess=w.sum()**2/(w@w);print({'agirlikli_ortalama':estimate,'ham_n':len(y),'Kish_ESS':ess,'yalniz_agirlik_DEFF':len(y)/ess})
plt.plot(w,'o');plt.xlabel('Yanıtlayan');plt.ylabel('Anket ağırlığı')
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

x=rng.normal(size=1000);y=3*x+rng.normal(size=1000);xm=x+rng.normal(0,1.5,len(x));btrue=stats.linregress(x,y).slope;bmeas=stats.linregress(xm,y).slope
baseline=rng.normal(size=1000);first=baseline+rng.normal(size=1000);second=baseline+rng.normal(size=1000);selected=first>np.quantile(first,.9)
print({'gercek_x_egim':btrue,'hata_x_egim':bmeas,'secili_ilk_ortalama':first[selected].mean(),'secili_tekrar_ortalama':second[selected].mean()})
plt.scatter(xm,y,s=8,alpha=.2);grid=np.linspace(-5,5,50);plt.plot(grid,bmeas*grid,c='tab:orange');plt.xlabel('Hatalı x');plt.ylabel('y')
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

import hashlib
observed=rng.normal(10,2,80);missing_n=20;deltas=np.linspace(-2,2,9);means=[(observed.sum()+missing_n*(observed.mean()+d))/(len(observed)+missing_n) for d in deltas]
print(pd.DataFrame({'delta':deltas,'tam_ortalama':means}));print('Veri SHA256:',hashlib.sha256(observed.tobytes()).hexdigest());plt.plot(deltas,means,'o-');plt.axhline(10,c='tab:orange');plt.xlabel('Eksik ortalaması − gözlenen ortalama');plt.ylabel('Duyarlılık ortalaması')
plt.show()
