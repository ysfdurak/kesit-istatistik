# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats, special
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.contingency_tables import mcnemar
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from statsmodels.stats.oneway import anova_oneway
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.statespace.sarimax import SARIMAX
plt.rcParams.update({'figure.figsize':(8.8,4.3),'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':.15})

def tbl(df,title):return {'title':title,'columns':[str(c) for c in df.columns],'rows':df.where(pd.notnull(df),None).values.tolist()}

def posthoc(scenario='default'):
 rng=np.random.default_rng(260803);names=['A','B','C'];ns=[24,30,36];means=[20,18.5,17.5];scales=[1.5]*3 if scenario=='default' else [1.,2.5,4.];groups=[rng.normal(mu,sd,n) for mu,sd,n in zip(means,scales,ns)];raw=pd.DataFrame([(name,float(v))for name,g in zip(names,groups)for v in g],columns=['method','seconds']);welch=anova_oneway(groups,use_var='unequal');classic=stats.f_oneway(*groups);tukey=pairwise_tukeyhsd(raw.seconds,raw.method,alpha=.05);gh=[]
 for i in range(3):
  for j in range(i+1,3):
   gi,gj=groups[i],groups[j];vi,vj=np.var(gi,ddof=1)/len(gi),np.var(gj,ddof=1)/len(gj);se=np.sqrt(vi+vj);df=(vi+vj)**2/(vi**2/(len(gi)-1)+vj**2/(len(gj)-1));difference=gi.mean()-gj.mean();q=np.sqrt(2)*abs(difference)/se;critical=stats.studentized_range.ppf(.95,3,df)/np.sqrt(2);p=stats.studentized_range.sf(q,3,df);gh.append([names[i]+'−'+names[j],difference,df,p,difference-critical*se,difference+critical*se])
 ghdf=pd.DataFrame(gh,columns=['pair','difference','df','p_adjusted','lower','upper']);summary=raw.groupby('method').seconds.agg(['count','mean','std']).reset_index();fig,ax=plt.subplots();
 for i,g in enumerate(groups):ax.scatter(np.full(len(g),i)+rng.normal(0,.04,len(g)),g,alpha=.5,s=16,color=['#235ACB','#148774','#D5542B'][i])
 ax.set(xticks=range(3),xticklabels=names,ylabel='Paketleme süresi · saniye',title='Ham noktalar: grup ortalamasının yanında yayılımı gör')
 fig2,ax2=plt.subplots();ax2.axvline(0,color='gray',ls='--');ax2.errorbar(ghdf.difference,range(3),xerr=np.vstack([ghdf.difference-ghdf.lower,ghdf.upper-ghdf.difference]),fmt='o',capsize=5,color='#235ACB');ax2.set(yticks=range(3),yticklabels=ghdf.pair,xlabel='Ortalama farkı · saniye',title='Games–Howell eşzamanlı %95 aralıklar')
 tdf=pd.DataFrame(tukey._results_table.data[1:],columns=tukey._results_table.data[0]);assert np.all((ghdf.p_adjusted>=0)&(ghdf.p_adjusted<=1));assert np.all(ghdf.lower<=ghdf.upper)
 decision='Eşit varyanslı öğretim senaryosunda klasik ANOVA ve Tukey tutarlı bir aile oluşturur. Eşit olmayan senaryoda Welch + Games–Howell seç; her çifti düzeltilmemiş t testleriyle tarama.'
 return dict(metrics={'Klasik genel ANOVA p':classic.pvalue,'Welch genel p':float(welch.pvalue),'Bağımsız paket':len(raw),'Varyans senaryosu':'Eşit' if scenario=='default' else 'Eşit değil'},tables=[tbl(summary,'Grup hacmi, merkezi ve yayılımı'),tbl(ghdf,'Games–Howell: A−B yönü'),tbl(tdf,'Tukey: tablodaki meandiff = group2−group1')],figures=[('Her nokta bağımsız bir paket ölçümüdür; renk yöntemdir.',fig),('Sıfırı dışlayan eşzamanlı aralık ilgili çiftin farkını destekler; yönleri tablodaki etikete göre oku.',fig2)],frames={'paket_olcumleri':raw},steps=['Üç bağımsız yöntem grubunda n, ortalama, varyans ve ham dağılımı kontrol et.','Genel H0 bütün ortalamalar eşit. Klasik ANOVA ortak varyans, Welch ayrı varyans hedefiyle kurulur.','Tukey ortak hata varyansına; Games–Howell çiftin ayrı varyansına ve Welch df’sine dayanır. Games–Howell q=√2×|fark|/SE; aile büyüklüğü k=3.'],decision=decision,diagnostics={'classic_p':classic.pvalue,'welch_p':float(welch.pvalue),'gh':ghdf.to_dict('records'),'ns':ns,'stds':[np.std(g,ddof=1)for g in groups]},limit='Sentetik bağımsız normal paket ölçümleri; yöntemler uygun paketlere rastgele atanmış varsayılır. Gerçek çalışmada operatör/vardiya ve sıra etkisi blok gerektirebilir. Varyans ailesi yalnız Levene p’sine göre otomatik seçilmez. İstatistiksel fark işte en iyi yöntem demek değildir.')

result=posthoc('default')
print(result['metrics'])
for t in result['tables']: print(t['title']); print(pd.DataFrame(t['rows'],columns=t['columns']).to_string(index=False))
print(result['decision']);print(result['limit'])
for caption,fig in result['figures']: print(caption);plt.show()
