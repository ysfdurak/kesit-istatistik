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

y=np.array([1,0,1,0]);p1=np.array([.7,.2,.6,.6]);p2=np.array([.99,.01,.99,.99]);print(pd.DataFrame([{'model':name,'log_kayip':log_loss(y,p),'Brier':brier_score_loss(y,p),'dogruluk':np.mean((p>=.5)==y)} for name,p in [('Ilımlı',p1),('Aşırı emin',p2)]]))
plt.plot(range(1,5),-(y*np.log(p1)+(1-y)*np.log1p(-p1)),'o-',label='Ilımlı');plt.plot(range(1,5),-(y*np.log(p2)+(1-y)*np.log1p(-p2)),'o-',label='Aşırı emin');plt.xlabel('Kayıt');plt.ylabel('Negatif log olabilirlik');plt.legend()
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

x=rng.normal(size=100);y=2*x+rng.normal(0,.3,100)
for rate in [.01,.1,.8]:
 b=0.;history=[]
 for step in range(60):
  pred=b*x;history.append(np.mean((pred-y)**2));grad=2*np.mean(x*(pred-y));b-=rate*grad
 print({'adim':rate,'son_beta':b,'son_kayip':history[-1]});plt.semilogy(history,label=f'η={rate}')
plt.xlabel('Gradyan adımı');plt.ylabel('MSE · log ölçek');plt.legend()
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

X=rng.normal(size=(80,2));X[:,1]=.7*X[:,0]+.5*X[:,1];y=X@np.array([2.,-1.])+rng.normal(0,.3,80);b=np.array([.5,.5]);loss=lambda v:np.mean((X@v-y)**2);g=2*X.T@(X@b-y)/len(y);eps=1e-6;numeric=np.array([(loss(b+eps*np.eye(2)[j])-loss(b-eps*np.eye(2)[j]))/(2*eps) for j in range(2)])
print({'gradyan':g.tolist(),'sonlu_fark':numeric.tolist(),'kovaryans':np.cov(X,rowvar=False).tolist()});assert np.allclose(g,numeric,atol=1e-7)
plt.scatter(*X.T,s=15);plt.axis('equal');plt.xlabel('x1');plt.ylabel('x2')
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

x=rng.uniform(-2,2,(450,1));y=2*x[:,0]+rng.normal(size=450);model=LinearRegression().fit(x[:200],y[:200]);cal=np.abs(y[200:325]-model.predict(x[200:325]));alpha=.1;rank=int(np.ceil((len(cal)+1)*(1-alpha)));q=np.sort(cal)[rank-1];pred=model.predict(x[325:]);covered=np.abs(y[325:]-pred)<=q
print({'kalibrasyon_n':len(cal),'sira':rank,'q':q,'test_kapsama':covered.mean(),'genislik':2*q});order=np.argsort(x[325:,0]);xx=x[325:,0][order];pp=pred[order];plt.scatter(xx,y[325:][order],s=12);plt.plot(xx,pp,c='tab:orange');plt.fill_between(xx,pp-q,pp+q,alpha=.2);plt.xlabel('x');plt.ylabel('Yeni y ve tahmin aralığı')
plt.show()
