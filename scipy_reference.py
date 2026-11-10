import scipy.stats as st,json
A=[12,14,13,15,11,16,14,13,17,12,15,14];B=[11,12,10,13,12,14,11,12,13,10,12,11]
f=[]
def add(expr,value):f.append([expr,float(value)])
for df in [1,2,10,100,499]:
 for p in [.9,.975,.995]:add(f'E.tInv({p},{df})',st.t.ppf(p,df))
for t in [0,.1,2,8,25]:
 for df in [1,10,100]:add(f'E.tP({t},{df})',2*st.t.sf(t,df))
for name,r in [('ttest',st.ttest_ind(A,B,equal_var=False)),('mannWhitney',st.mannwhitneyu(A,B,method='asymptotic'))]:
 add(f'E.{name}({A},{B}).p',r.pvalue)
add(f'E.ttest({A},null,12).p',st.ttest_1samp(A,12).pvalue)
add(f'E.ttest({A},{B},0,true).p',st.ttest_rel(A,B).pvalue)
add('E.categorical([[8,32],[18,22]]).p',st.chi2_contingency([[8,32],[18,22]],correction=False).pvalue)
add('E.categorical([[8,32],[18,22]]).fisher',st.fisher_exact([[8,32],[18,22]]).pvalue)
add('E.anova([[9,10,11,10,12,9],[11,12,14,12,13,11],[14,15,16,15,17,14]]).p',st.f_oneway([9,10,11,10,12,9],[11,12,14,12,13,11],[14,15,16,15,17,14]).pvalue)
add('E.bayes(12,100,2,2).lower',st.beta.ppf(.025,14,90));add('E.bayes(12,100,2,2).upper',st.beta.ppf(.975,14,90))
json.dump(f,open('scipyrefs.json','w'))
