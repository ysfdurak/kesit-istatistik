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

from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
X=np.r_[rng.multivariate_normal([-1,0],[[1,.7],[.7,1]],200),rng.multivariate_normal([1,0],[[1,-.6],[-.6,.5]],200)];y=np.repeat([0,1],200);a,b,c,d=train_test_split(X,y,test_size=.35,stratify=y,random_state=7)
for model in [LinearDiscriminantAnalysis(),QuadraticDiscriminantAnalysis()]:
 model.fit(a,c);p=model.predict_proba(b)[:,1];print(type(model).__name__,{'logloss':log_loss(d,p),'AUC':roc_auc_score(d,p)})
plt.scatter(*b.T,c=d,s=18,cmap='coolwarm');plt.xlabel('x1 · test');plt.ylabel('x2 · test')
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

from sklearn.naive_bayes import GaussianNB
X,y=make_classification(n_samples=600,n_features=4,n_informative=2,n_redundant=0,random_state=7);X=np.c_[X,X[:,0]+rng.normal(0,.05,len(X))];a,b,c,d=train_test_split(X,y,test_size=.35,stratify=y,random_state=7);names=[];loss=[]
for name,model in [('Gaussian NB',GaussianNB()),('Lojistik',make_pipeline(StandardScaler(),LogisticRegression()))]:
 model.fit(a,c);p=model.predict_proba(b)[:,1];names.append(name);loss.append(log_loss(d,p));print(name,{'logloss':loss[-1],'Brier':brier_score_loss(d,p)})
plt.bar(names,loss);plt.ylabel('Bağımsız test log kaybı')
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

from sklearn.neighbors import KNeighborsClassifier
X,y=make_moons(n_samples=600,noise=.2,random_state=7);dims=[0,5,20,60];scores=[]
for extra in dims:
 xx=np.c_[X,rng.normal(size=(len(X),extra))];a,b,c,d=train_test_split(xx,y,test_size=.35,stratify=y,random_state=7);m=make_pipeline(StandardScaler(),KNeighborsClassifier(7));m.fit(a,c);scores.append(m.score(b,d))
print(pd.DataFrame({'ek_gurultu_boyutu':dims,'test_dogruluk':scores}));plt.plot(dims,scores,'o-');plt.xlabel('Ek gürültü boyutu');plt.ylabel('Test doğruluğu')
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

from sklearn.svm import SVC
X,y=make_moons(n_samples=400,noise=.22,random_state=7);a,b,c,d=train_test_split(X,y,test_size=.35,stratify=y,random_state=7)
for kernel in ['linear','rbf']:
 m=make_pipeline(StandardScaler(),SVC(C=1,kernel=kernel,gamma=1));m.fit(a,c);print(kernel,{'egitim':m.score(a,c),'test':m.score(b,d)})
plt.scatter(*b.T,c=d,s=20,cmap='coolwarm');plt.xlabel('Test x1');plt.ylabel('Test x2')
plt.show()
