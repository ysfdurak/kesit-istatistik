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

from statsmodels.tsa.stattools import acf,pacf
from statsmodels.stats.diagnostic import acorr_ljungbox
x=np.zeros(240)
for t in range(1,len(x)):x[t]=.7*x[t-1]+rng.normal()
a=acf(x,nlags=16);p=pacf(x,nlags=16);print(acorr_ljungbox(x,lags=[8,16],return_df=True));plt.plot(range(1,17),a[1:],'o-',label='ACF');plt.plot(range(1,17),p[1:],'o-',label='PACF');plt.axhline(0,c='black',lw=.7);plt.xlabel('Gecikme');plt.ylabel('Korelasyon');plt.legend()
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

x=np.r_[rng.normal(10,1,80),rng.normal(13,1,80)];candidates=np.arange(20,len(x)-20);loss=np.array([((x[:k]-x[:k].mean())**2).sum()+((x[k:]-x[k:].mean())**2).sum() for k in candidates]);best=int(candidates[loss.argmin()]);print({'secilen_kirilma':best,'once':x[:best].mean(),'sonra':x[best:].mean()})
plt.plot(x,label='Ölçüm');plt.axvline(best,c='tab:orange',label='Tarama minimumu');plt.xlabel('Zaman');plt.ylabel('Süreç seviyesi');plt.legend()
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

Q,R=.08,1.;true=np.cumsum(rng.normal(0,np.sqrt(Q),120));obs=true+rng.normal(0,np.sqrt(R),120);m,P=0.,10.;est=[];unc=[]
for y in obs:
 P+=Q;K=P/(P+R);m+=K*(y-m);P=(1-K)*P;est.append(m);unc.append(P)
est=np.array(est);sd=np.sqrt(unc);print({'olcum_RMSE':np.sqrt(np.mean((obs-true)**2)),'filtre_RMSE':np.sqrt(np.mean((est-true)**2))})
plt.plot(obs,alpha=.25,label='Ölçüm');plt.plot(true,label='Gerçek seviye');plt.plot(est,label='Filtre');plt.fill_between(range(len(est)),est-1.96*sd,est+1.96*sd,alpha=.15);plt.xlabel('Zaman');plt.ylabel('Seviye');plt.legend()
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

from statsmodels.tsa.api import VAR
x=np.zeros((220,2));A=np.array([[.65,.3],[.1,.55]])
for t in range(1,len(x)):x[t]=A@x[t-1]+rng.normal(size=2)
train,test=x[:180],x[180:];fit=VAR(train).fit(1);pred=fit.forecast(train[-1:],len(test));naive=np.repeat(train[-1:],len(test),axis=0);print({'VAR_MSE':mean_squared_error(test,pred),'son_deger_MSE':mean_squared_error(test,naive),'toplam_MSE':mean_squared_error(test.sum(axis=1),pred.sum(axis=1))})
plt.plot(test.sum(axis=1),label='Gerçek toplam');plt.plot(pred.sum(axis=1),label='Bottom-up VAR toplam');plt.xlabel('Test zamanı');plt.ylabel('İki serinin toplamı');plt.legend()
plt.show()
