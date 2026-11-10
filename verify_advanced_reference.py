import json,numpy as np
from sklearn.mixture import GaussianMixture
x=np.array([-2.2,-1.8,-1.5,-1.2,-1,-.8,.5,.9,1.2,1.5,1.8,2.2])
g=GaussianMixture(2,means_init=np.quantile(x,[.25,.75])[:,None],weights_init=np.array([.5,.5]),precisions_init=np.full((2,1,1),1/np.var(x)),reg_covar=0,tol=1e-12,max_iter=1000,random_state=7).fit(x[:,None])
a=np.array([10,11,9,10,12,11,14,13,15,14,16,15]);Q=.2;R=1.;m=float(a[0]);P=10.;est=[];var=[]
for y in a:
 Pminus=P+Q;K=Pminus/(Pminus+R);m=m+K*(y-m);P=(1-K)*Pminus;est.append(m);var.append(P)
json.dump({'gmm_mu':sorted(g.means_.ravel().tolist()),'gmm_ll':float(g.score(x[:,None])*len(x)),'kalman_mean':m,'kalman_var':P,'weighted_mean':np.average([8,10,11,9,12,15,10,9],weights=[1,1,1,1,1,8,1,1]),'weighted_ess':15**2/71},open('advancedrefs.json','w'))
