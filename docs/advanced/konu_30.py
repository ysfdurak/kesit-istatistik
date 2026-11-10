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

N,K,n=100,15,20;k=np.arange(n+1);hyper=stats.hypergeom(N,K,n).pmf(k);binom=stats.binom(n,K/N).pmf(k);counts=np.array([5,9,6]);p=np.array([.2,.5,.3]);print({'hiper_P_en_az_1':stats.hypergeom.sf(0,N,K,n),'multinomial_P_5_9_6':stats.multinomial.pmf(counts,n=20,p=p)})
assert np.isclose(hyper.sum(),1);plt.plot(k,hyper,'o-',label='Hipergeometrik');plt.plot(k,binom,'o-',label='Binom yaklaşımı');plt.xlabel('Hata sayısı');plt.ylabel('P(X=k)');plt.legend()
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

shape,rate=3.,2.;scale=1/rate;g=stats.gamma(a=shape,scale=scale);b=stats.beta(2,5);print({'gamma_ortalama':g.mean(),'gamma_varyans':g.var(),'gamma_P_X_2_alti':g.cdf(2),'beta_ortalama':b.mean()});x=np.linspace(.001,5,300);plt.plot(x,g.pdf(x),label='Gamma');xx=np.linspace(.001,.999,200);plt.plot(xx,b.pdf(xx),label='Beta');plt.xlabel('Değer');plt.ylabel('Yoğunluk');plt.legend()
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

shape,scale=1.8,20.;life=stats.weibull_min.rvs(shape,scale=scale,size=300,random_state=rng);censor=18.;event=life<=censor;obs=np.minimum(life,censor);data=stats.CensoredData(uncensored=obs[event],right=obs[~event]);c,loc,s=stats.weibull_min.fit(data,floc=0);print({'olay_n':int(event.sum()),'sansur_n':int((~event).sum()),'uyum_sekil':c,'uyum_olcek':s,'gercek_sekil':shape,'gercek_olcek':scale})
x=np.linspace(.01,40,200);plt.plot(x,stats.weibull_min.sf(x,c,scale=s),label='Uyum yaşam');plt.plot(x,stats.weibull_min.sf(x,shape,scale=scale),'--',label='Gerçek yaşam');plt.xlabel('Gün');plt.ylabel('S(t)');plt.legend()
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

x=rng.lognormal(1,.6,160);grid=np.linspace(0,15,300);kde=stats.gaussian_kde(x,bw_method=.2);sorted_x=np.sort(x);ecdf=np.arange(1,len(x)+1)/len(x);print({'n':len(x),'F_5':np.mean(x<=5),'KDE_P_0_5':kde.integrate_box_1d(0,5),'negatif_sizma':kde.integrate_box_1d(-np.inf,0)})
fig,axes=plt.subplots(1,2,figsize=(9,3.5));axes[0].step(sorted_x,ecdf,where='post');axes[0].set(xlabel='Süre',ylabel='ECDF');axes[1].plot(grid,kde(grid));axes[1].set(xlabel='Süre',ylabel='KDE yoğunluğu');fig.tight_layout()
plt.show()
