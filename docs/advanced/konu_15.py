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

from math import comb, perm
n,k=12,3
print({'sirasiz':comb(n,k),'sirali':perm(n,k),'oran':perm(n,k)/comb(n,k)})
ks=np.arange(n+1);plt.bar(ks,[comb(n,int(j)) for j in ks]);plt.xlabel('Seçilen birim k');plt.ylabel('Kombinasyon sayısı')
assert perm(n,k)==comb(n,k)*perm(k,k)
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

rho=.7;xy=rng.multivariate_normal([0,0],[[1,rho],[rho,1]],600)
x0=1.;print({'marjinal_EY':0,'kosullu_EY_X1':rho*x0,'kosullu_varyans':1-rho**2})
plt.scatter(*xy.T,s=10,alpha=.35);plt.plot([-3,3],rho*np.array([-3,3]),c='tab:orange',label='E[Y|X]');plt.xlabel('Standart hacim');plt.ylabel('Standart süre');plt.legend()
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

x=rng.lognormal(2,.5,80);mu=x.mean();se=x.std(ddof=1)/np.sqrt(len(x));delta=se/mu
boot=np.log(rng.choice(x,(2000,len(x))).mean(axis=1));print({'log_ortalama':np.log(mu),'delta_SE':delta,'bootstrap_SE':boot.std(ddof=1)})
plt.hist(boot,bins=30);plt.axvline(np.log(mu)-1.96*delta,c='tab:orange');plt.axvline(np.log(mu)+1.96*delta,c='tab:orange');plt.xlabel('log(örneklem ortalaması)');plt.ylabel('Tekrar sayısı')
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

ns=np.array([5,10,20,50,100,200]);eps=.3
observed=[np.mean(np.abs(rng.exponential(1,(3000,int(n))).mean(axis=1)-1)>=eps) for n in ns]
bound=np.minimum(1,1/(ns*eps**2));print(pd.DataFrame({'n':ns,'gozlenen':observed,'Chebyshev':bound}))
plt.plot(ns,observed,'o-',label='Simülasyon');plt.plot(ns,bound,'o-',label='Üst sınır');plt.xlabel('n');plt.ylabel('P(|ortalama−1|≥ε)');plt.legend()
plt.show()
