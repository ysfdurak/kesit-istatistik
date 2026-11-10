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

truth=1.;samples=rng.normal(truth,2,(4000,8));raw=samples.mean(axis=1);shrink=.65*raw
rows=[]
for name,v in [('Ortalama',raw),('0 yönüne küçültme',shrink)]:
 bias=v.mean()-truth;var=v.var();mse=np.mean((v-truth)**2);rows.append([name,bias,var,mse]);assert abs(mse-bias**2-var)<1e-10
print(pd.DataFrame(rows,columns=['tahmin','yanlilik','varyans','MSE']));plt.hist(raw,bins=35,alpha=.5,label='Ortalama');plt.hist(shrink,bins=35,alpha=.5,label='Küçültme');plt.axvline(truth,c='black');plt.legend();plt.xlabel('Tahmin');plt.ylabel('Tekrar sayısı')
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

x=rng.poisson(4,80);mle=x.mean();grid=np.linspace(.1,9,180);ll=np.array([stats.poisson.logpmf(x,v).sum() for v in grid])
print({'MLE':mle,'momentler':x.mean(),'n':len(x)})
plt.plot(grid,np.exp(ll-ll.max()));plt.axvline(mle,c='tab:orange');plt.xlabel('Poisson hız λ');plt.ylabel('Göreli olabilirlik')
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

k,n=7,40;p=k/n;grid=np.linspace(.0001,.9999,1000);ll=stats.binom.logpmf(k,n,grid);best=stats.binom.logpmf(k,n,p);lr=2*(best-ll);ok=grid[lr<=stats.chi2.ppf(.95,1)]
info=n/(p*(1-p));print({'MLE':p,'Fisher_bilgi':info,'Wald':(p-1.96/np.sqrt(info),p+1.96/np.sqrt(info)),'LR_profil':(ok.min(),ok.max())})
plt.plot(grid,lr);plt.axhline(stats.chi2.ppf(.95,1),c='tab:orange');plt.ylim(0,12);plt.xlabel('p');plt.ylabel('2 log olabilirlik farkı')
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

x=np.linspace(-2,2,100);y=2+x+.7*x*x+rng.normal(0,1,len(x));xt=rng.uniform(-2,2,500);yt=2+xt+.7*xt*xt+rng.normal(0,1,500);rows=[]
for degree in range(1,7):
 model=sm.OLS(y,np.vander(x,degree+1,increasing=True)).fit();pred=model.predict(np.vander(xt,degree+1,increasing=True));rows.append([degree,model.aic,model.bic,mean_squared_error(yt,pred)])
tab=pd.DataFrame(rows,columns=['derece','AIC','BIC','test_MSE']);print(tab);plt.plot(tab.derece,tab.AIC,label='AIC');plt.plot(tab.derece,tab.BIC,label='BIC');plt.xlabel('Derece');plt.ylabel('Bilgi kriteri');plt.legend()
plt.show()
