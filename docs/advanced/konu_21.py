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

P=np.array([[.8,.2],[.3,.7]]);dist=np.array([1.,0.]);history=[dist.copy()]
for t in range(35):dist=dist@P;history.append(dist.copy())
A=np.vstack([P.T-np.eye(2),np.ones(2)]);stationary=np.linalg.lstsq(A,[0,0,1],rcond=None)[0];assert np.allclose(stationary@P,stationary)
print({'duragan':stationary.tolist(),'35_adim':dist.tolist()});plt.plot(history);plt.xlabel('Adım');plt.ylabel('Durum olasılığı');plt.legend(['Normal','Yoğun'])
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

mu=10.;lam=np.linspace(1,9.8,150);W=1/(mu-lam);Wq=lam/(mu*(mu-lam));l=8.;print({'rho':l/mu,'W_dakika':60/(mu-l),'L':l/(mu-l),'Little_kontrol':l*1/(mu-l)})
plt.plot(lam/mu,60*W,label='Sistemde');plt.plot(lam/mu,60*Wq,label='Kuyrukta');plt.xlabel('Kullanım ρ');plt.ylabel('Bekleme · dakika');plt.legend()
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

loss=rng.lognormal(2,1,4000);alpha=.95;var=np.quantile(loss,alpha);tail=loss[loss>=var];es=tail.mean();print({'VaR':var,'ES':es,'kuyruk_n':len(tail)})
plt.hist(loss,bins=80);plt.axvline(var,c='tab:orange',label='VaR');plt.axvline(es,c='tab:red',label='ES');plt.xlim(0,np.quantile(loss,.997));plt.xlabel('Kayıp');plt.ylabel('Kayıt');plt.legend()
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

p=np.array([.6,.3,.1]);q=np.array([.2,.4,.4]);print({'H_P_bit':stats.entropy(p,base=2),'KL_P_Q_bit':stats.entropy(p,q,base=2),'KL_Q_P_bit':stats.entropy(q,p,base=2)})
x=np.arange(3);plt.bar(x-.18,p,.36,label='P');plt.bar(x+.18,q,.36,label='Q');plt.xticks(x,['A','B','C']);plt.ylabel('Pay');plt.legend()
plt.show()
