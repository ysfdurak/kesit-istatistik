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

from sklearn.tree import DecisionTreeClassifier
X,y=make_classification(n_samples=600,n_features=6,n_informative=3,flip_y=.1,random_state=7);a,b,c,d=train_test_split(X,y,test_size=.35,stratify=y,random_state=7);rows=[]
for depth in [1,2,3,5,9,None]:
 m=DecisionTreeClassifier(max_depth=depth,random_state=7);m.fit(a,c);rows.append([str(depth),1-m.score(a,c),1-m.score(b,d)])
t=pd.DataFrame(rows,columns=['derinlik','egitim_hata','test_hata']);print(t);plt.plot(t.derinlik,t.egitim_hata,'o-',label='Eğitim');plt.plot(t.derinlik,t.test_hata,'o-',label='Test');plt.xlabel('Maksimum derinlik');plt.ylabel('Hata payı');plt.legend()
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

from sklearn.ensemble import RandomForestClassifier
X,y=make_classification(n_samples=700,n_features=12,n_informative=4,random_state=7);a,b,c,d=train_test_split(X,y,test_size=.35,stratify=y,random_state=7);rows=[]
for features in ['sqrt',1.0]:
 m=RandomForestClassifier(n_estimators=80,max_features=features,min_samples_leaf=3,random_state=7,n_jobs=1);m.fit(a,c);p=np.array([tree.predict_proba(b)[:,1] for tree in m.estimators_]);corr=np.corrcoef(p);off=corr[np.triu_indices_from(corr,1)];rows.append([str(features),np.nanmean(off),m.score(b,d)])
print(pd.DataFrame(rows,columns=['max_features','tahmin_korelasyonu','test_dogruluk']));plt.bar([r[0] for r in rows],[r[2] for r in rows]);plt.ylim(.5,1);plt.ylabel('Test doğruluğu')
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

from sklearn.ensemble import GradientBoostingClassifier
X,y=make_classification(n_samples=600,n_features=8,n_informative=4,flip_y=.1,random_state=7);a,b,c,d=train_test_split(X,y,test_size=.35,stratify=y,random_state=7);m=GradientBoostingClassifier(n_estimators=150,learning_rate=.1,max_depth=2,random_state=7);m.fit(a,c);train=[log_loss(c,p) for p in m.staged_predict_proba(a)];test=[log_loss(d,p) for p in m.staged_predict_proba(b)];print({'son_egitim':train[-1],'son_test':test[-1]});plt.plot(train,label='Eğitim');plt.plot(test,label='Test');plt.xlabel('Eklenen ağaç');plt.ylabel('Log kaybı');plt.legend()
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

from sklearn.neural_network import MLPClassifier
X,y=make_moons(n_samples=500,noise=.25,random_state=7);a,b,c,d=train_test_split(X,y,test_size=.35,stratify=y,random_state=7);rows=[]
for width in [4,16,48]:
 m=make_pipeline(StandardScaler(),MLPClassifier(hidden_layer_sizes=(width,),alpha=.01,max_iter=1200,early_stopping=True,n_iter_no_change=30,random_state=7));m.fit(a,c);rows.append([width,log_loss(c,m.predict_proba(a)),log_loss(d,m.predict_proba(b))])
t=pd.DataFrame(rows,columns=['gizli_birim','egitim_logloss','test_logloss']);print(t);plt.plot(t.gizli_birim,t.egitim_logloss,'o-',label='Eğitim');plt.plot(t.gizli_birim,t.test_logloss,'o-',label='Test');plt.xlabel('Gizli birim');plt.ylabel('Log kaybı');plt.legend()
plt.show()
