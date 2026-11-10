"""İleri derslerin yürütülebilir, sentetik veri uygulamaları."""
from pathlib import Path
import json,io,contextlib,base64,traceback,zipfile
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).parent; OUT=ROOT/'docs/advanced';OUT.mkdir(exist_ok=True)
COURSE=json.loads((ROOT/'docs/content.js').read_text()[14:-1])
SETUP='''import numpy as np
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
'''
# Her kayıt: iş sorusu / grafik okuması / yorum sınırı / tek değişkenli alıştırma / gerçek analiz kodu.
R={}
def add(i,q,read,limit,task,code):R[i]=dict(question=q,reading=read,limit=limit,task=task,code=code.strip())
add(57,'Bir partiden kontrol örneği kaç farklı biçimde seçilebilir?','Sıralı seçimin neden daha çok sonuç ürettiğini karşılaştır.','Bu sayma modeli yerine koymadan ve eşit olasılıklı seçim içindir.','n=12, k=3 yerine k=5 kullan; kombinasyonun neden monoton artmadığını açıkla.', '''
from math import comb, perm
n,k=12,3
print({'sirasiz':comb(n,k),'sirali':perm(n,k),'oran':perm(n,k)/comb(n,k)})
ks=np.arange(n+1);plt.bar(ks,[comb(n,int(j)) for j in ks]);plt.xlabel('Seçilen birim k');plt.ylabel('Kombinasyon sayısı')
assert perm(n,k)==comb(n,k)*perm(k,k)
''')
add(58,'Hacim bilgisi süre tahminini nasıl günceller?','Noktaların eğimini ve X=1 için koşullu ortalamayı birlikte oku.','İki değişkenli normal modelin koşullu formülü kullanılır; her veri için geçerli değildir.','Korelasyonu .7’den -.4’e değiştir; marjinal ve koşullu ortalamaları ayır.', '''
rho=.7;xy=rng.multivariate_normal([0,0],[[1,rho],[rho,1]],600)
x0=1.;print({'marjinal_EY':0,'kosullu_EY_X1':rho*x0,'kosullu_varyans':1-rho**2})
plt.scatter(*xy.T,s=10,alpha=.35);plt.plot([-3,3],rho*np.array([-3,3]),c='tab:orange',label='E[Y|X]');plt.xlabel('Standart hacim');plt.ylabel('Standart süre');plt.legend()
''')
add(59,'Log dönüşümü ortalama belirsizliğini nasıl değiştirir?','Bootstrap log-ortalama dağılımını delta aralığıyla karşılaştır.','Delta yaklaşımı düzgün dönüşüm ve yeterli örneklem ister; log ortalama ile ortalama log farklıdır.','n=80 yerine n=15 kullan ve yaklaşım farkını yorumla.', '''
x=rng.lognormal(2,.5,80);mu=x.mean();se=x.std(ddof=1)/np.sqrt(len(x));delta=se/mu
boot=np.log(rng.choice(x,(2000,len(x))).mean(axis=1));print({'log_ortalama':np.log(mu),'delta_SE':delta,'bootstrap_SE':boot.std(ddof=1)})
plt.hist(boot,bins=30);plt.axvline(np.log(mu)-1.96*delta,c='tab:orange');plt.axvline(np.log(mu)+1.96*delta,c='tab:orange');plt.xlabel('log(örneklem ortalaması)');plt.ylabel('Tekrar sayısı')
''')
add(60,'Daha çok veri hangi oynaklığı azaltır?','n arttığında sapma olasılığı ile Chebyshev üst sınırını karşılaştır.','Sınır gevşek olabilir; bağımsız sonlu varyanslı üstel veri kullanılır.','Sapma eşiğini .3 yerine .15 yap; gerekli n üzerindeki etkiyi açıkla.', '''
ns=np.array([5,10,20,50,100,200]);eps=.3
observed=[np.mean(np.abs(rng.exponential(1,(3000,int(n))).mean(axis=1)-1)>=eps) for n in ns]
bound=np.minimum(1,1/(ns*eps**2));print(pd.DataFrame({'n':ns,'gozlenen':observed,'Chebyshev':bound}))
plt.plot(ns,observed,'o-',label='Simülasyon');plt.plot(ns,bound,'o-',label='Üst sınır');plt.xlabel('n');plt.ylabel('P(|ortalama−1|≥ε)');plt.legend()
''')
add(61,'Yanlı ama daha kararlı tahmin bazen daha iyi olabilir mi?','Sapma ve varyansın toplamının MSE’ye katkısını oku.','Sonuç seçilmiş simülasyon evrenine aittir; tek kazanan evrensel değildir.','Gerçek ortalamayı 1’den 0’a değiştir; küçültmenin zararını/kazancını yeniden değerlendir.', '''
truth=1.;samples=rng.normal(truth,2,(4000,8));raw=samples.mean(axis=1);shrink=.65*raw
rows=[]
for name,v in [('Ortalama',raw),('0 yönüne küçültme',shrink)]:
 bias=v.mean()-truth;var=v.var();mse=np.mean((v-truth)**2);rows.append([name,bias,var,mse]);assert abs(mse-bias**2-var)<1e-10
print(pd.DataFrame(rows,columns=['tahmin','yanlilik','varyans','MSE']));plt.hist(raw,bins=35,alpha=.5,label='Ortalama');plt.hist(shrink,bins=35,alpha=.5,label='Küçültme');plt.axvline(truth,c='black');plt.legend();plt.xlabel('Tahmin');plt.ylabel('Tekrar sayısı')
''')
add(62,'Sayım verisinde MLE ve momentler nerede buluşur?','Olabilirlik tepesinin örneklem ortalamasıyla çakışmasını izle.','Poisson modeli ortak hız ve uygun maruziyet varsayar; aşırı saçılmayı çözmez.','Üretim hızını 4’ten 9’a değiştir; hız tahminini ve eğriyi yeniden hesapla.', '''
x=rng.poisson(4,80);mle=x.mean();grid=np.linspace(.1,9,180);ll=np.array([stats.poisson.logpmf(x,v).sum() for v in grid])
print({'MLE':mle,'momentler':x.mean(),'n':len(x)})
plt.plot(grid,np.exp(ll-ll.max()));plt.axvline(mle,c='tab:orange');plt.xlabel('Poisson hız λ');plt.ylabel('Göreli olabilirlik')
''')
add(63,'Olabilirlik oranı ile Wald yaklaşımı aynı sonucu verir mi?','İki aralığın özellikle küçük sayımlarda ayrılabildiğini gör.','Wilks χ² ve Wald yaklaşımları sınırda/küçük örneklemde zayıflayabilir.','k=7,n=40 yerine k=1,n=10 kullan; simetrik aralığın sınır sorununu incele.', '''
k,n=7,40;p=k/n;grid=np.linspace(.0001,.9999,1000);ll=stats.binom.logpmf(k,n,grid);best=stats.binom.logpmf(k,n,p);lr=2*(best-ll);ok=grid[lr<=stats.chi2.ppf(.95,1)]
info=n/(p*(1-p));print({'MLE':p,'Fisher_bilgi':info,'Wald':(p-1.96/np.sqrt(info),p+1.96/np.sqrt(info)),'LR_profil':(ok.min(),ok.max())})
plt.plot(grid,lr);plt.axhline(stats.chi2.ppf(.95,1),c='tab:orange');plt.ylim(0,12);plt.xlabel('p');plt.ylabel('2 log olabilirlik farkı')
''')
add(64,'Daha esnek modelin daha iyi uyumu neye mal olur?','AIC/BIC ile ayrı test hatasını aynı dereceler için karşılaştır.','Bilgi kriterleri aynı yanıt/olabilirlik ve uygun parametre sayısıyla karşılaştırılır; test seti model seçmek için tüketilmez.','n=100 yerine n=30 kullan; yüksek derecenin cezasını ve test hatasını karşılaştır.', '''
x=np.linspace(-2,2,100);y=2+x+.7*x*x+rng.normal(0,1,len(x));xt=rng.uniform(-2,2,500);yt=2+xt+.7*xt*xt+rng.normal(0,1,500);rows=[]
for degree in range(1,7):
 model=sm.OLS(y,np.vander(x,degree+1,increasing=True)).fit();pred=model.predict(np.vander(xt,degree+1,increasing=True));rows.append([degree,model.aic,model.bic,mean_squared_error(yt,pred)])
tab=pd.DataFrame(rows,columns=['derece','AIC','BIC','test_MSE']);print(tab);plt.plot(tab.derece,tab.AIC,label='AIC');plt.plot(tab.derece,tab.BIC,label='BIC');plt.xlabel('Derece');plt.ylabel('Bilgi kriteri');plt.legend()
''')
add(65,'Bağımsız vardiya ile aynı kişilerin değişimi neden farklı test ister?','Eşleştirilmiş çizgilerin yönüyle grup histogramını ayır.','Wilcoxon sıfır fark ve simetri koşulları; Mann–Whitney dağılımsal hedefi korunmalı.','Sonra sütununu rastgele karıştır; eşleştirmenin etkisini açıklayarak iki testi yeniden çalıştır.', '''
a=rng.lognormal(2,.35,30);b=a-rng.normal(.8,.6,30);ind=rng.lognormal(2,.35,35)
print({'Wilcoxon_esli':stats.wilcoxon(a,b).pvalue,'Mann_Whitney_bagimsiz':stats.mannwhitneyu(a,ind,method='asymptotic').pvalue})
plt.plot([0,1],np.vstack([a,b]),alpha=.35);plt.xticks([0,1],['Önce','Sonra']);plt.ylabel('Aynı birimde süre')
''')
add(66,'Üç bağımsız grup ile üç tekrarlı ölçümü nasıl ayırırım?','Aynı birimin üç ölçümü arasındaki bağı koru.','Kruskal ve Friedman aynı deney tasarımını test etmez; genel p hangi çiftin farklı olduğunu söylemez.','Birimin ortak etkisini artır; Friedman ile bağımsız yaklaşımın farkını açıkla.', '''
base=rng.normal(10,3,25);a=base+rng.normal(0,1,25);b=base+1+rng.normal(0,1,25);c=base+2+rng.normal(0,1,25)
print({'Friedman_tekrarli':stats.friedmanchisquare(a,b,c).pvalue,'Kruskal_bagimsiz_ornek':stats.kruskal(rng.normal(10,2,25),rng.normal(11,2,25),rng.normal(12,2,25)).pvalue})
plt.boxplot([a,b,c],tick_labels=['A','B','C']);plt.ylabel('Ölçüm');plt.xlabel('Tekrarlı yöntem')
''')
add(67,'Uç süreyi silmeden tipik performansı nasıl raporlarım?','Ortalama, medyan ve kırpılmış ortalamanın aykırılığa tepkisini karşılaştır.','Kırpma önceden belirlenmeli; geçerli kuyruk maliyetini ortadan kaldırdığı varsayılmamalı.','Son 80 dakikalık kaydı 800 yap; her özetin değişimini yaz.', '''
x=np.r_[rng.normal(10,1,39),80];trim=.1;med=np.median(x);mad=stats.median_abs_deviation(x,scale='normal');print({'ortalama':x.mean(),'medyan':med,'kirpilmis':stats.trim_mean(x,trim),'MAD_normal_olcek':mad})
plt.hist(x,bins=25);plt.axvline(x.mean(),label='Ortalama',c='tab:orange');plt.axvline(med,label='Medyan',c='tab:green');plt.xlabel('Süre');plt.ylabel('Kayıt');plt.legend()
''')
add(68,'Fark bulamamak yerine eşdeğerliği nasıl sınarım?','%90 fark aralığının önceden seçilmiş ±Δ sınırları içinde kalıp kalmadığını oku.','İki tek yönlü test α=.05 ile eşdeğerlik sınırı önceden seçilir; aşağı kalmama tek yönlü başka hedeftir.','Eşdeğerlik marjını 1’den .3’e indir ve kararın değişmesini açıkla.', '''
d=rng.normal(.1,1.2,50);delta=1.;se=stats.sem(d);df=len(d)-1
p_lower=stats.t.sf((d.mean()+delta)/se,df);p_upper=stats.t.cdf((d.mean()-delta)/se,df);ci=stats.t.interval(.90,df,loc=d.mean(),scale=se)
print({'fark':d.mean(),'TOST_p':max(p_lower,p_upper),'CI90':ci,'esdeger':bool(max(p_lower,p_upper)<.05),'asagi_kalmama_ust_sinir_p':p_upper})
plt.errorbar([d.mean()],[1],xerr=[[d.mean()-ci[0]],[ci[1]-d.mean()]],fmt='o');plt.axvline(-delta,c='tab:orange');plt.axvline(delta,c='tab:orange');plt.yticks([]);plt.xlabel('Önce−sonra farkı')
''')
add(69,'İş yükü etkisi vardiyaya göre değişiyor mu?','İki vardiya doğrusunun farklı eğimlerini karşılaştır.','Etkileşim koşullu ilişkiyi gösterir; randomizasyon olmadan nedensellik kurulmaz.','Etkileşim katsayısını 1.2’den 0’a indir; modelde ve grafikte ne değiştiğini yaz.', '''
x=rng.uniform(0,5,180);shift=rng.integers(0,2,180);y=3+2*x+2*shift+1.2*x*shift+.2*x*x+rng.normal(0,1,180);d=pd.DataFrame({'x':x,'vardiya':shift,'y':y});fit=smf.ols('y ~ x * vardiya + I(x**2)',d).fit();print(fit.params.round(3));print('Etkileşim CI:',fit.conf_int().loc['x:vardiya'].round(3).tolist())
for g in [0,1]:
 xx=np.linspace(0,5,80);plt.scatter(x[shift==g],y[shift==g],s=10,alpha=.25);plt.plot(xx,fit.predict(pd.DataFrame({'x':xx,'vardiya':g})),label=f'Vardiya {g}')
plt.xlabel('Hacim');plt.ylabel('Süre');plt.legend()
''')
add(70,'Daha uzun maruziyet daha çok hatayı açıklıyor mu?','Aynı x için sayım yerine maruziyet başına oranı karşılaştır.','Offset log(maruziyet) katsayısı 1’e sabittir. Negatif binom modeli aşırı saçılma için ayrıca gerekçelendirilir.','Maruziyetleri iki katına çıkar; oran ile beklenen sayımı ayır.', '''
x=rng.normal(size=250);exposure=rng.uniform(.5,3,250);mu=exposure*np.exp(.5+.6*x);y=rng.negative_binomial(3,3/(3+mu));X=sm.add_constant(x)
pois=sm.GLM(y,X,family=sm.families.Poisson(),offset=np.log(exposure)).fit();nb=sm.NegativeBinomial(y,X,offset=np.log(exposure)).fit(disp=False)
print({'Poisson_beta':pois.params.tolist(),'NB_beta_ve_alpha':nb.params.tolist(),'Poisson_Pearson_dispersion':pois.pearson_chi2/pois.df_resid})
order=np.argsort(x);plt.scatter(x,y/exposure,s=12,alpha=.25,label='Gözlenen oran');plt.plot(x[order],np.exp(X@pois.params)[order],label='Poisson');plt.plot(x[order],np.exp(X@nb.params[:2])[order],label='NB');plt.xlabel('x');plt.ylabel('Olay / maruziyet');plt.legend()
''')
add(71,'Az kayıtlı deponun ortalamasına ne kadar güvenmeliyim?','Ham grup ortalamalarıyla karma model tahminlerini karşılaştır.','Rastgele kesişim modeli grupların ortak dağılımını varsayar; ML/REML ve grup tasarımı önemlidir.','İlk deponun n değerini 5’ten 50’ye çıkar; küçültmenin nasıl değiştiğini incele.', '''
rows=[]
for g,n in enumerate([5,8,12,16,20,24,30,40]):
 u=rng.normal(0,2)
 for j in range(n):rows.append([str(g),10+u+rng.normal(0,3)])
d=pd.DataFrame(rows,columns=['depo','sure']);fit=smf.mixedlm('sure ~ 1',d,groups=d.depo).fit(reml=True,method='powell',disp=False);raw=d.groupby('depo').sure.mean();pooled=np.array([fit.fe_params.iloc[0]+float(fit.random_effects[g].iloc[0]) for g in raw.index]);print({'genel_ortalama':float(fit.fe_params.iloc[0]),'grup_varyansi':float(fit.cov_re.iloc[0,0]),'hata_varyansi':float(fit.scale)})
plt.plot(raw.index,raw,'o',label='Ham');plt.plot(raw.index,pooled,'o',label='Kısmi havuzlama');plt.xlabel('Depo');plt.ylabel('Beklenen süre');plt.legend()
''')
add(72,'Ortalama süre iyi görünürken üst hizmet kuyruğu ne oluyor?','Koşullu medyan ve .9 kantil çizgisini aynı noktalarda oku.','Kantil katsayısı koşullu kantile aittir; nedensellik veya tekil tahmin garantisi değildir.','Hata ölçeğinin x ile artışını kaldır; kantil eğimlerinin değişimini açıkla.', '''
x=rng.uniform(0,8,250);y=5+2*x+rng.normal(size=len(x))*(1+.5*x);X=sm.add_constant(x);grid=np.linspace(0,8,100)
for q in [.5,.9]:
 fit=sm.QuantReg(y,X).fit(q=q,max_iter=3000);print('Kantil',q,'katsayılar',fit.params.round(3));plt.plot(grid,fit.predict(sm.add_constant(grid)),label=f'q={q}')
plt.scatter(x,y,s=10,alpha=.2);plt.xlabel('Hacim');plt.ylabel('Süre');plt.legend()
''')
add(73,'Az gözlemli grubun oranını ortak önselle nasıl güncellerim?','Beta sonsallarının genişliği ile örneklem büyüklüğünü eşleştir.','Burada üst düzey Beta parametreleri sabittir; onların belirsizliğini öğrenen tam hiyerarşik model değildir.','Önseli Beta(2,18) yerine Beta(1,1) yap; küçük grupta etkiyi açıkla.', '''
a,b=2,18;groups=[(1,8),(10,80),(30,200)];p=np.linspace(.001,.999,400)
for k,n in groups:
 post=stats.beta(a+k,b+n-k);print({'k':k,'n':n,'ham':k/n,'sonsal':post.mean(),'CI95':post.ppf([.025,.975]).tolist()});plt.plot(p,post.pdf(p),label=f'{k}/{n}')
plt.xlabel('Grup olay olasılığı');plt.ylabel('Sonsal yoğunluk');plt.legend()
''')
add(74,'Yüksek kabul oranı iyi karışma anlamına gelir mi?','İzleri ve klasik split R-hat değerini adım boyuna göre karşılaştır.','Random-walk öğretim uygulaması modern rank-normalize R-hat ve HMC tanılarının yerine geçmez.','step=.12 yerine .005 kullan; kabul ve zincirler arası farkı birlikte yorumla.', '''
a,b,step=5,9,.12;chains=[];accepted=0
for start in [.1,.35,.65,.9]:
 z=start;out=[]
 for i in range(2400):
  proposal=z+rng.normal(0,step)
  if 0<proposal<1 and np.log(rng.uniform())<stats.beta.logpdf(proposal,a,b)-stats.beta.logpdf(z,a,b):z=proposal;accepted+=1
  if i>=800:out.append(z)
 chains.append(out)
c=np.array(chains);split=c.reshape(8,800);W=split.var(axis=1,ddof=1).mean();B=800*split.mean(axis=1).var(ddof=1);rhat=np.sqrt(((799/800)*W+B/800)/W)
print({'kabul':accepted/9600,'klasik_split_Rhat':rhat,'cekim_ortalama':c.mean(),'analitik':a/(a+b)})
plt.plot(c.T[::8],alpha=.65);plt.xlabel('Saklanan çekim / 8');plt.ylabel('p')
''')
add(75,'Model gözlenen hata sayısını yeniden üretebiliyor mu?','Gözlenen istatistiği sonsal öngörü histogramıyla karşılaştır.','Sonsal öngörü kontrolü model uygunluğuna bakar; kullanılan veriden bağımsız doğrulama değildir.','n=100,k=12 değerini değiştir; öngörü ile parametre aralığını ayır.', '''
k,n=12,100;p=rng.beta(2+k,18+n-k,4000);rep=rng.binomial(n,p);print({'yeni_sayim_ortalama':rep.mean(),'ongoru_95':np.quantile(rep,[.025,.975]).tolist(),'gozlenen':k,'parametre_95':np.quantile(p,[.025,.975]).tolist()})
plt.hist(rep,bins=np.arange(rep.max()+2)-.5);plt.axvline(k,c='tab:orange',label='Gözlenen');plt.xlabel('Yeni 100 kayıtta hata sayısı');plt.ylabel('Tekrar');plt.legend()
''')
add(76,'Önsel ve hata maliyeti kararı nasıl değiştirir?','Farklı önsellerde sonsal ve BF10 değerini karşılaştır.','Bayes faktörü belirtilen nokta H0 ile Beta alternatifini karşılaştırır; önsele duyarlıdır.','H0 oranını .1’den .2’ye değiştir; maliyet eşiğini ayrı değerlendir.', '''
k,n,p0=18,100,.1;rows=[]
for a,b in [(1,1),(2,18),(10,90)]:
 logBF=special.betaln(a+k,b+n-k)-special.betaln(a,b)-k*np.log(p0)-(n-k)*np.log1p(-p0);prob=stats.beta.sf(p0,a+k,b+n-k);rows.append([f'{a},{b}',prob,np.exp(logBF)])
print(pd.DataFrame(rows,columns=['Beta_onsel','P_p_buyuk_H0','BF10']));C_FP,C_FN=2,10;print('Pozitif karar eşiği:',C_FP/(C_FP+C_FN))
plt.bar([r[0] for r in rows],[r[1] for r in rows]);plt.ylim(0,1);plt.xlabel('Önsel');plt.ylabel('P(p > H0 | veri)')
''')
add(77,'Tahmin artıklarında zaman bağımlılığı kaldı mı?','AR(1) serisinin ACF ve PACF desenini incele.','Gecikme bantları yaklaşık ve çoklu bakış içerir; beyaz gürültü testi model doğruluğunu kanıtlamaz.','AR katsayısını .7’den 0’a değiştir; Ljung–Box ve grafiği birlikte oku.', '''
from statsmodels.tsa.stattools import acf,pacf
from statsmodels.stats.diagnostic import acorr_ljungbox
x=np.zeros(240)
for t in range(1,len(x)):x[t]=.7*x[t-1]+rng.normal()
a=acf(x,nlags=16);p=pacf(x,nlags=16);print(acorr_ljungbox(x,lags=[8,16],return_df=True));plt.plot(range(1,17),a[1:],'o-',label='ACF');plt.plot(range(1,17),p[1:],'o-',label='PACF');plt.axhline(0,c='black',lw=.7);plt.xlabel('Gecikme');plt.ylabel('Korelasyon');plt.legend()
''')
add(78,'Süreçte kalıcı seviye değişimini nasıl ararım?','Tek kırılmalı en küçük kareler taramasını zaman serisinde oku.','Bu eğitim taraması bir kırılma varsayar; taranmış en iyi tarih için saf p hesaplamak geçersizdir.','Değişim büyüklüğünü 3’ten .5’e indir; seçilen tarihin kararlılığını tartış.', '''
x=np.r_[rng.normal(10,1,80),rng.normal(13,1,80)];candidates=np.arange(20,len(x)-20);loss=np.array([((x[:k]-x[:k].mean())**2).sum()+((x[k:]-x[k:].mean())**2).sum() for k in candidates]);best=int(candidates[loss.argmin()]);print({'secilen_kirilma':best,'once':x[:best].mean(),'sonra':x[best:].mean()})
plt.plot(x,label='Ölçüm');plt.axvline(best,c='tab:orange',label='Tarama minimumu');plt.xlabel('Zaman');plt.ylabel('Süreç seviyesi');plt.legend()
''')
add(79,'Gürültülü ölçümde gizli seviyeyi nasıl izlerim?','Ölçüm, gerçek simülasyon seviyesi ve filtre tahminini ayır.','Yerel seviye Kalman modeli Q/R sabit kabul eder; geleceği kullanan smoother uygulanmaz.','Q=.08 yerine .8 kullan; tepki hızı ile oynaklık dengesini açıkla.', '''
Q,R=.08,1.;true=np.cumsum(rng.normal(0,np.sqrt(Q),120));obs=true+rng.normal(0,np.sqrt(R),120);m,P=0.,10.;est=[];unc=[]
for y in obs:
 P+=Q;K=P/(P+R);m+=K*(y-m);P=(1-K)*P;est.append(m);unc.append(P)
est=np.array(est);sd=np.sqrt(unc);print({'olcum_RMSE':np.sqrt(np.mean((obs-true)**2)),'filtre_RMSE':np.sqrt(np.mean((est-true)**2))})
plt.plot(obs,alpha=.25,label='Ölçüm');plt.plot(true,label='Gerçek seviye');plt.plot(est,label='Filtre');plt.fill_between(range(len(est)),est-1.96*sd,est+1.96*sd,alpha=.15);plt.xlabel('Zaman');plt.ylabel('Seviye');plt.legend()
''')
add(80,'Bağlı serileri ve toplamı tutarlı nasıl tahmin ederim?','VAR tahminlerini aynı test döneminde son değer tabanıyla karşılaştır.','VAR(1) ve bottom-up toplam örneği; genel hiyerarşi uzlaştırması veya nedensel yön çıkarımı değildir.','Çapraz etkiyi .3’ten 0’a indir; taban modeline göre kazancı incele.', '''
from statsmodels.tsa.api import VAR
x=np.zeros((220,2));A=np.array([[.65,.3],[.1,.55]])
for t in range(1,len(x)):x[t]=A@x[t-1]+rng.normal(size=2)
train,test=x[:180],x[180:];fit=VAR(train).fit(1);pred=fit.forecast(train[-1:],len(test));naive=np.repeat(train[-1:],len(test),axis=0);print({'VAR_MSE':mean_squared_error(test,pred),'son_deger_MSE':mean_squared_error(test,naive),'toplam_MSE':mean_squared_error(test.sum(axis=1),pred.sum(axis=1))})
plt.plot(test.sum(axis=1),label='Gerçek toplam');plt.plot(pred.sum(axis=1),label='Bottom-up VAR toplam');plt.xlabel('Test zamanı');plt.ylabel('İki serinin toplamı');plt.legend()
''')
add(81,'Bir durumdan diğerine geçiş uzun dönemi nasıl belirler?','Başlangıç etkisinin durağan dağılıma yaklaşmasını izle.','Sabit geçiş matrisi ve uygun ergodiklik gerekir; her Markov zinciri tek durağan limite gitmez.','İlk satırı [.9,.1] yap; uzun dönem ve yakınsama hızını karşılaştır.', '''
P=np.array([[.8,.2],[.3,.7]]);dist=np.array([1.,0.]);history=[dist.copy()]
for t in range(35):dist=dist@P;history.append(dist.copy())
A=np.vstack([P.T-np.eye(2),np.ones(2)]);stationary=np.linalg.lstsq(A,[0,0,1],rcond=None)[0];assert np.allclose(stationary@P,stationary)
print({'duragan':stationary.tolist(),'35_adim':dist.tolist()});plt.plot(history);plt.xlabel('Adım');plt.ylabel('Durum olasılığı');plt.legend(['Normal','Yoğun'])
''')
add(82,'Kullanımı yükseltmek beklemeyi ne kadar artırır?','M/M/1 eğrisindeki doğrusal olmayan artışı oku.','Poisson geliş, üstel hizmet, tek sunucu ve λ<μ varsayılır; W saat birimindedir.','Hizmet hızını 10’dan 12’ye çıkar; aynı gelişte bekleme kazancını hesapla.', '''
mu=10.;lam=np.linspace(1,9.8,150);W=1/(mu-lam);Wq=lam/(mu*(mu-lam));l=8.;print({'rho':l/mu,'W_dakika':60/(mu-l),'L':l/(mu-l),'Little_kontrol':l*1/(mu-l)})
plt.plot(lam/mu,60*W,label='Sistemde');plt.plot(lam/mu,60*Wq,label='Kuyrukta');plt.xlabel('Kullanım ρ');plt.ylabel('Bekleme · dakika');plt.legend()
''')
add(83,'Ortalama kayıp yerine kuyruk riskini nasıl raporlarım?','VaR eşiği ile eşiği aşan kayıpların ortalamasını ayır.','Tarihsel/sentetik örneklem kuyruğu gelecekte garanti değildir; küçük kuyruk örneklemi kararsızdır.','α=.95 yerine .99 kullan; kuyruktaki kayıt sayısını mutlaka raporla.', '''
loss=rng.lognormal(2,1,4000);alpha=.95;var=np.quantile(loss,alpha);tail=loss[loss>=var];es=tail.mean();print({'VaR':var,'ES':es,'kuyruk_n':len(tail)})
plt.hist(loss,bins=80);plt.axvline(var,c='tab:orange',label='VaR');plt.axvline(es,c='tab:red',label='ES');plt.xlim(0,np.quantile(loss,.997));plt.xlabel('Kayıp');plt.ylabel('Kayıt');plt.legend()
''')
add(84,'Dağılım kaymasını tek bir ortalamayla görebilir miyim?','P ve Q kategorilerinin paylarını KL yönüyle birlikte oku.','KL asimetriktir ve Q sıfırken P pozitifse sonsuzdur; kategoriler aynı tanımlanmalı.','Q’nun ilk payını .2’den .05’e indirip normalize et; iki KL yönünü karşılaştır.', '''
p=np.array([.6,.3,.1]);q=np.array([.2,.4,.4]);print({'H_P_bit':stats.entropy(p,base=2),'KL_P_Q_bit':stats.entropy(p,q,base=2),'KL_Q_P_bit':stats.entropy(q,p,base=2)})
x=np.arange(3);plt.bar(x-.18,p,.36,label='P');plt.bar(x+.18,q,.36,label='Q');plt.xticks(x,['A','B','C']);plt.ylabel('Pay');plt.legend()
''')
add(85,'Tek atama belirsizliği neden eksik gösterir?','Ayrı sonsal çekimlerle tamamlanmış veri setlerinin eğimlerini karşılaştır.','IterativeImputer+BayesianRidge sayısal MAR örneğidir; MNAR ve kategorik alanlar ayrıca modellenmeli.','Eksik payını %25’ten %50’ye çıkar; Rubin toplam varyansındaki payları karşılaştır.', '''
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
x=rng.normal(size=250);z=.6*x+rng.normal(size=250);y=1+2*x+z+rng.normal(size=250);data=np.c_[x,z,y];mask=rng.uniform(size=250)<.25;data[mask,0]=np.nan;est=[];vars=[]
for seed in range(10):
 complete=IterativeImputer(estimator=BayesianRidge(),sample_posterior=True,random_state=seed,max_iter=10).fit_transform(data);fit=sm.OLS(complete[:,2],sm.add_constant(complete[:,:2])).fit();est.append(fit.params[1]);vars.append(fit.cov_params()[1,1])
within=np.mean(vars);between=np.var(est,ddof=1);total=within+1.1*between;print({'havuz_egim':np.mean(est),'ic_varyans':within,'arasi_varyans':between,'Rubin_SE':np.sqrt(total)})
plt.plot(range(1,11),est,'o');plt.axhline(np.mean(est),c='tab:orange');plt.xlabel('Atama');plt.ylabel('Tamamlanmış veri eğimi')
''')
add(86,'Ağırlıklı anketin 100 kaydı gerçekten 100 birim bilgi mi?','Ağırlık yoğunlaştıkça Kish etkin örneklemin düşmesini izle.','Kish ESS tek başına tasarım varyansı değildir; küme/katman/FPC için tam anket tasarımı gerekir.','Son ağırlığı 15’ten 50’ye çıkar; ağırlıklı ortalama ve ESS’yi birlikte raporla.', '''
y=rng.normal(10,2,100);w=np.r_[np.ones(99),15.];estimate=np.average(y,weights=w);ess=w.sum()**2/(w@w);print({'agirlikli_ortalama':estimate,'ham_n':len(y),'Kish_ESS':ess,'yalniz_agirlik_DEFF':len(y)/ess})
plt.plot(w,'o');plt.xlabel('Yanıtlayan');plt.ylabel('Anket ağırlığı')
''')
add(87,'Gürültülü ölçüm ilişkiyi nasıl zayıflatır?','Aynı yanıt için gerçek ve hatalı x eğimlerini karşılaştır.','Klasik bağımsız ölçüm hatası senaryosu; gerçek hayatta hata yapısı ve tekrar ölçümler ayrıca gerekir.','Ölçüm hata sapmasını 1.5’ten .2’ye indir; zayıflamayı incele.', '''
x=rng.normal(size=1000);y=3*x+rng.normal(size=1000);xm=x+rng.normal(0,1.5,len(x));btrue=stats.linregress(x,y).slope;bmeas=stats.linregress(xm,y).slope
baseline=rng.normal(size=1000);first=baseline+rng.normal(size=1000);second=baseline+rng.normal(size=1000);selected=first>np.quantile(first,.9)
print({'gercek_x_egim':btrue,'hata_x_egim':bmeas,'secili_ilk_ortalama':first[selected].mean(),'secili_tekrar_ortalama':second[selected].mean()})
plt.scatter(xm,y,s=8,alpha=.2);grid=np.linspace(-5,5,50);plt.plot(grid,bmeas*grid,c='tab:orange');plt.xlabel('Hatalı x');plt.ylabel('y')
''')
add(88,'Varsayım değişince kararım ayakta kalıyor mu?','Eksiklerin gözlenenlerden farklı olabileceği senaryoları karşılaştır.','Bu delta duyarlılığı MNAR’ı teşhis etmez; makul aralığı alan bilgisi belirler.','Delta aralığını ±2 yerine ±5 yap; karar eşiği 10’a göre sonucu yaz.', '''
import hashlib
observed=rng.normal(10,2,80);missing_n=20;deltas=np.linspace(-2,2,9);means=[(observed.sum()+missing_n*(observed.mean()+d))/(len(observed)+missing_n) for d in deltas]
print(pd.DataFrame({'delta':deltas,'tam_ortalama':means}));print('Veri SHA256:',hashlib.sha256(observed.tobytes()).hexdigest());plt.plot(deltas,means,'o-');plt.axhline(10,c='tab:orange');plt.xlabel('Eksik ortalaması − gözlenen ortalama');plt.ylabel('Duyarlılık ortalaması')
''')
add(89,'Eğitim başarısı yeni veride ne kadar korunur?','Aynı derecelerde eğitim ve bağımsız test hatasını karşılaştır.','Tek simülasyon genelleme dağılımını göstermez; test üzerinde derece seçilmez.','Gürültüyü .3’ten .7’ye çıkar; eğitim ve test farkını açıkla.', '''
x=rng.uniform(-1,1,40);y=np.sin(3*x)+rng.normal(0,.3,40);xt=rng.uniform(-1,1,500);yt=np.sin(3*xt)+rng.normal(0,.3,500);rows=[]
for d in [1,2,4,8,12]:
 m=make_pipeline(PolynomialFeatures(d),Ridge(alpha=.001));m.fit(x[:,None],y);rows.append([d,mean_squared_error(y,m.predict(x[:,None])),mean_squared_error(yt,m.predict(xt[:,None]))])
t=pd.DataFrame(rows,columns=['derece','egitim','test']);print(t);plt.plot(t.derece,t.egitim,'o-',label='Eğitim');plt.plot(t.derece,t.test,'o-',label='Test');plt.xlabel('Derece');plt.ylabel('MSE');plt.legend()
''')
add(90,'Yanlılık ve varyansı tek eğitimden ayırabilir miyim?','Aynı evrenden yeniden eğitilmiş modellerin varyansını ölç.','Bileşenler gerçek f bilindiği için simülasyonda ayrılır; gerçek veride doğrudan gözlenmez.','n=30 yerine n=100 yap; model varyansını karşılaştır.', '''
grid=np.linspace(-1,1,150);truth=np.sin(3*grid);sigma=.3;rows=[]
for d in [1,3,8]:
 predictions=[]
 for repeat in range(60):
  x=rng.uniform(-1,1,30);y=np.sin(3*x)+rng.normal(0,sigma,30);m=make_pipeline(PolynomialFeatures(d),Ridge(alpha=.001));m.fit(x[:,None],y);predictions.append(m.predict(grid[:,None]))
 p=np.array(predictions);bias2=np.mean((p.mean(axis=0)-truth)**2);variance=p.var(axis=0).mean();rows.append([d,bias2,variance,sigma**2])
t=pd.DataFrame(rows,columns=['derece','yanlilik2','varyans','gurultu']);print(t);plt.bar(t.derece,t.yanlilik2,label='Yanlılık²');plt.bar(t.derece,t.varyans,bottom=t.yanlilik2,label='Varyans');plt.bar(t.derece,t.gurultu,bottom=t.yanlilik2+t.varyans,label='Gürültü');plt.xlabel('Derece');plt.ylabel('Beklenen hata bileşenleri');plt.legend()
''')
add(91,'Kaçırma maliyeti artarsa eşik ne olmalı?','Maliyet eğrisinin minimumunu precision/recall hedefinden ayır.','Teorik eşik kalibre olasılık ve sabit maliyet varsayar; burada sentetik olasılıklar üretici modelden bilinir.','FN maliyetini 10’dan 2’ye indir; teorik ve gözlenen eşikleri karşılaştır.', '''
p=rng.beta(2,6,2000);y=rng.binomial(1,p);fp_cost,fn_cost=2,10;thresholds=np.linspace(0,1,101);cost=[]
for t in thresholds:
 pred=p>=t;cost.append((fp_cost*np.sum(pred&(y==0))+fn_cost*np.sum((~pred)&(y==1)))/len(y))
print({'teorik_esik':fp_cost/(fp_cost+fn_cost),'orneklem_min':thresholds[np.argmin(cost)],'min_ortalama_maliyet':min(cost)})
plt.plot(thresholds,cost);plt.axvline(fp_cost/(fp_cost+fn_cost),c='tab:orange');plt.xlabel('Eşik');plt.ylabel('Kayıt başına maliyet')
''')
add(92,'Daha çok veri mi daha iyi model mi gerekir?','Eğitim büyüklüğüne göre tekrarlı doğrulama hatasını oku.','Bağımsız test aynı kalır; simülasyon eğrisi başka evrene otomatik taşınmaz.','Polinom derecesini 3’ten 1’e düşür; doygunlaşan hatayı yorumla.', '''
xt=rng.uniform(-1,1,500);yt=np.sin(3*xt)+rng.normal(0,.3,500);sizes=[20,40,80,160,320];errors=[]
for n in sizes:
 vals=[]
 for rep in range(15):
  x=rng.uniform(-1,1,n);y=np.sin(3*x)+rng.normal(0,.3,n);m=make_pipeline(PolynomialFeatures(3),Ridge(alpha=.01));m.fit(x[:,None],y);vals.append(mean_squared_error(yt,m.predict(xt[:,None])))
 errors.append([np.mean(vals),np.std(vals)])
errors=np.array(errors);print(pd.DataFrame({'n':sizes,'ortalama_test_MSE':errors[:,0],'tekrar_SD':errors[:,1]}));plt.errorbar(sizes,errors[:,0],yerr=errors[:,1],fmt='o-');plt.axhline(.3**2,c='tab:orange');plt.xlabel('Eğitim n');plt.ylabel('Test MSE ± tekrar SD')
''')
add(93,'Aynı doğrulukta daha emin yanlış karar neden daha pahalı?','İki olasılık tahmininin log kaybını ve Brier’ını karşılaştır.','Kayıplar olasılık kalitesini ölçer; sıralama kalitesi veya eşik maliyetiyle aynı değildir.','Yanlış kayda verilen .99 olasılığını .7 yap; doğruluk değişmeden kaybı izle.', '''
y=np.array([1,0,1,0]);p1=np.array([.7,.2,.6,.6]);p2=np.array([.99,.01,.99,.99]);print(pd.DataFrame([{'model':name,'log_kayip':log_loss(y,p),'Brier':brier_score_loss(y,p),'dogruluk':np.mean((p>=.5)==y)} for name,p in [('Ilımlı',p1),('Aşırı emin',p2)]]))
plt.plot(range(1,5),-(y*np.log(p1)+(1-y)*np.log1p(-p1)),'o-',label='Ilımlı');plt.plot(range(1,5),-(y*np.log(p2)+(1-y)*np.log1p(-p2)),'o-',label='Aşırı emin');plt.xlabel('Kayıt');plt.ylabel('Negatif log olabilirlik');plt.legend()
''')
add(94,'Adım boyu optimizasyonu nasıl bozabilir?','Kayıp izlerini küçük, uygun ve büyük adım için karşılaştır.','Konveks tek parametreli kare kayıp örneği; derin ağların tüm davranışını temsil etmez.','Öğrenme hızına 1.1 ekle; taşma yerine ilk 20 adımda yükselen kaybı gözle.', '''
x=rng.normal(size=100);y=2*x+rng.normal(0,.3,100)
for rate in [.01,.1,.8]:
 b=0.;history=[]
 for step in range(60):
  pred=b*x;history.append(np.mean((pred-y)**2));grad=2*np.mean(x*(pred-y));b-=rate*grad
 print({'adim':rate,'son_beta':b,'son_kayip':history[-1]});plt.semilogy(history,label=f'η={rate}')
plt.xlabel('Gradyan adımı');plt.ylabel('MSE · log ölçek');plt.legend()
''')
add(95,'Gradyanı sayısal farkla doğrulayabilir miyim?','Analitik ve sonlu fark gradyanlarının eşleşmesini denetle.','Kovaryans özdeğerleri ölçekteki değişime duyarlıdır; merkezleme ve n−1 tanımı korunur.','İkinci sütunu 100 ile çarp; kovaryans ve gradyan ölçeğinin etkisini yaz.', '''
X=rng.normal(size=(80,2));X[:,1]=.7*X[:,0]+.5*X[:,1];y=X@np.array([2.,-1.])+rng.normal(0,.3,80);b=np.array([.5,.5]);loss=lambda v:np.mean((X@v-y)**2);g=2*X.T@(X@b-y)/len(y);eps=1e-6;numeric=np.array([(loss(b+eps*np.eye(2)[j])-loss(b-eps*np.eye(2)[j]))/(2*eps) for j in range(2)])
print({'gradyan':g.tolist(),'sonlu_fark':numeric.tolist(),'kovaryans':np.cov(X,rowvar=False).tolist()});assert np.allclose(g,numeric,atol=1e-7)
plt.scatter(*X.T,s=15);plt.axis('equal');plt.xlabel('x1');plt.ylabel('x2')
''')
add(96,'Nokta tahminine hangi aralığı ekleyebilirim?','Kalibrasyon ve testteki kapsama ile aralık genişliğini birlikte oku.','Split konformal marjinal kapsama verir; değiştirilebilirlik ve eğitimden ayrı kalibrasyon gerekir.','α=.1 yerine .05 yap; sonlu sıra düzeltmesini ve genişliği raporla.', '''
x=rng.uniform(-2,2,(450,1));y=2*x[:,0]+rng.normal(size=450);model=LinearRegression().fit(x[:200],y[:200]);cal=np.abs(y[200:325]-model.predict(x[200:325]));alpha=.1;rank=int(np.ceil((len(cal)+1)*(1-alpha)));q=np.sort(cal)[rank-1];pred=model.predict(x[325:]);covered=np.abs(y[325:]-pred)<=q
print({'kalibrasyon_n':len(cal),'sira':rank,'q':q,'test_kapsama':covered.mean(),'genislik':2*q});order=np.argsort(x[325:,0]);xx=x[325:,0][order];pp=pred[order];plt.scatter(xx,y[325:][order],s=12);plt.plot(xx,pp,c='tab:orange');plt.fill_between(xx,pp-q,pp+q,alpha=.2);plt.xlabel('x');plt.ylabel('Yeni y ve tahmin aralığı')
''')
add(97,'Sınıfların kovaryansı farklıysa doğrusal sınır yeterli mi?','LDA ve QDA’nın aynı testteki olasılık kaybını karşılaştır.','QDA daha çok parametre tahmin eder; az veriyle yüksek varyans yaratabilir.','Her sınıfın n değerini 200’den 30’a indir; test sonuçlarının kararlılığını tartış.', '''
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
X=np.r_[rng.multivariate_normal([-1,0],[[1,.7],[.7,1]],200),rng.multivariate_normal([1,0],[[1,-.6],[-.6,.5]],200)];y=np.repeat([0,1],200);a,b,c,d=train_test_split(X,y,test_size=.35,stratify=y,random_state=7)
for model in [LinearDiscriminantAnalysis(),QuadraticDiscriminantAnalysis()]:
 model.fit(a,c);p=model.predict_proba(b)[:,1];print(type(model).__name__,{'logloss':log_loss(d,p),'AUC':roc_auc_score(d,p)})
plt.scatter(*b.T,c=d,s=18,cmap='coolwarm');plt.xlabel('x1 · test');plt.ylabel('x2 · test')
''')
add(98,'Bağımsızlık varsayımı olasılık güvenini nasıl etkiler?','Aynı sinyalin kopyalarını ekleyerek NB ile lojistiği karşılaştır.','Naive Bayes’in koşullu bağımsızlığı sınıf koşulundadır; iyi doğruluk iyi kalibrasyon garantisi değildir.','Gürültülü kopya sayısını 1’den 5’e çıkar; log kaybını izle.', '''
from sklearn.naive_bayes import GaussianNB
X,y=make_classification(n_samples=600,n_features=4,n_informative=2,n_redundant=0,random_state=7);X=np.c_[X,X[:,0]+rng.normal(0,.05,len(X))];a,b,c,d=train_test_split(X,y,test_size=.35,stratify=y,random_state=7);names=[];loss=[]
for name,model in [('Gaussian NB',GaussianNB()),('Lojistik',make_pipeline(StandardScaler(),LogisticRegression()))]:
 model.fit(a,c);p=model.predict_proba(b)[:,1];names.append(name);loss.append(log_loss(d,p));print(name,{'logloss':loss[-1],'Brier':brier_score_loss(d,p)})
plt.bar(names,loss);plt.ylabel('Bağımsız test log kaybı')
''')
add(99,'İlgisiz boyutlar yakın komşuyu neden bozar?','Eklenen gürültü boyutlarıyla test doğruluğunu karşılaştır.','Ölçekleme eğitim içinde öğrenilir; tek bölme boyut etkisinin kesin büyüklüğü değildir.','Komşu sayısını 7’den 25’e çıkar; boyut etkisini yeniden değerlendir.', '''
from sklearn.neighbors import KNeighborsClassifier
X,y=make_moons(n_samples=600,noise=.2,random_state=7);dims=[0,5,20,60];scores=[]
for extra in dims:
 xx=np.c_[X,rng.normal(size=(len(X),extra))];a,b,c,d=train_test_split(xx,y,test_size=.35,stratify=y,random_state=7);m=make_pipeline(StandardScaler(),KNeighborsClassifier(7));m.fit(a,c);scores.append(m.score(b,d))
print(pd.DataFrame({'ek_gurultu_boyutu':dims,'test_dogruluk':scores}));plt.plot(dims,scores,'o-');plt.xlabel('Ek gürültü boyutu');plt.ylabel('Test doğruluğu')
''')
add(100,'Doğrusal sınır yerine çekirdek ne kazandırır?','Aynı test noktalarında doğrusal ve RBF kararını karşılaştır.','C/gamma testten seçilmez; burada sabit eğitim ayarlarıdır. SVM decision_function kalibre olasılık değildir.','gamma=1 yerine 20 kullan; eğitim/test farkını incele.', '''
from sklearn.svm import SVC
X,y=make_moons(n_samples=400,noise=.22,random_state=7);a,b,c,d=train_test_split(X,y,test_size=.35,stratify=y,random_state=7)
for kernel in ['linear','rbf']:
 m=make_pipeline(StandardScaler(),SVC(C=1,kernel=kernel,gamma=1));m.fit(a,c);print(kernel,{'egitim':m.score(a,c),'test':m.score(b,d)})
plt.scatter(*b.T,c=d,s=20,cmap='coolwarm');plt.xlabel('Test x1');plt.ylabel('Test x2')
''')
add(101,'Daha derin ağaç neden daha iyi test sonucu vermeyebilir?','Derinliğe göre eğitim/test kaybını karşılaştır.','Ağaç parametreleri testten seçilmez; tek bölme genelleme belirsizliğini özetlemez.','min_samples_leaf değerini 1’den 10’a çıkar; aşırı uyumu incele.', '''
from sklearn.tree import DecisionTreeClassifier
X,y=make_classification(n_samples=600,n_features=6,n_informative=3,flip_y=.1,random_state=7);a,b,c,d=train_test_split(X,y,test_size=.35,stratify=y,random_state=7);rows=[]
for depth in [1,2,3,5,9,None]:
 m=DecisionTreeClassifier(max_depth=depth,random_state=7);m.fit(a,c);rows.append([str(depth),1-m.score(a,c),1-m.score(b,d)])
t=pd.DataFrame(rows,columns=['derinlik','egitim_hata','test_hata']);print(t);plt.plot(t.derinlik,t.egitim_hata,'o-',label='Eğitim');plt.plot(t.derinlik,t.test_hata,'o-',label='Test');plt.xlabel('Maksimum derinlik');plt.ylabel('Hata payı');plt.legend()
''')
add(102,'Toplulukta ağaç sayısı kadar korelasyon neden önemli?','max_features değişince tek ağaç tahminlerinin korelasyonunu ve orman başarısını birlikte oku.','Korelasyon aynı test noktalarında tanımlıdır; hata korelasyonu ve tahmin korelasyonu farklıdır.','Ağaç sayısını 80’den 10’a indir; korelasyonun tek açıklayıcı olmadığını göster.', '''
from sklearn.ensemble import RandomForestClassifier
X,y=make_classification(n_samples=700,n_features=12,n_informative=4,random_state=7);a,b,c,d=train_test_split(X,y,test_size=.35,stratify=y,random_state=7);rows=[]
for features in ['sqrt',1.0]:
 m=RandomForestClassifier(n_estimators=80,max_features=features,min_samples_leaf=3,random_state=7,n_jobs=1);m.fit(a,c);p=np.array([tree.predict_proba(b)[:,1] for tree in m.estimators_]);corr=np.corrcoef(p);off=corr[np.triu_indices_from(corr,1)];rows.append([str(features),np.nanmean(off),m.score(b,d)])
print(pd.DataFrame(rows,columns=['max_features','tahmin_korelasyonu','test_dogruluk']));plt.bar([r[0] for r in rows],[r[2] for r in rows]);plt.ylim(.5,1);plt.ylabel('Test doğruluğu')
''')
add(103,'Boosting adımları ne zaman aşırı uyuma döner?','Sabit ayarda adım sayısı boyunca eğitim ve test log kaybını izle.','Test eğrisi öğretim gözlemidir; üretimde erken durdurma ayrı doğrulama verisinden seçilir.','Öğrenme hızını .1’den .03’e düşür; aynı adım sayısının anlamını tartış.', '''
from sklearn.ensemble import GradientBoostingClassifier
X,y=make_classification(n_samples=600,n_features=8,n_informative=4,flip_y=.1,random_state=7);a,b,c,d=train_test_split(X,y,test_size=.35,stratify=y,random_state=7);m=GradientBoostingClassifier(n_estimators=150,learning_rate=.1,max_depth=2,random_state=7);m.fit(a,c);train=[log_loss(c,p) for p in m.staged_predict_proba(a)];test=[log_loss(d,p) for p in m.staged_predict_proba(b)];print({'son_egitim':train[-1],'son_test':test[-1]});plt.plot(train,label='Eğitim');plt.plot(test,label='Test');plt.xlabel('Eklenen ağaç');plt.ylabel('Log kaybı');plt.legend()
''')
add(104,'Ağ kapasitesi ve ceza birlikte nasıl değerlendirilir?','Aynı testte farklı ağların kaybını eğitim kaybıyla karşılaştır.','Küçük MLP öğretim modelidir; derin öğrenmenin bütün mimarilerini temsil etmez. Yakınsama uyarısı model tanısıdır.','alpha=.01 yerine 1 kullan; model karmaşıklığı ve kaybı karşılaştır.', '''
from sklearn.neural_network import MLPClassifier
X,y=make_moons(n_samples=500,noise=.25,random_state=7);a,b,c,d=train_test_split(X,y,test_size=.35,stratify=y,random_state=7);rows=[]
for width in [4,16,48]:
 m=make_pipeline(StandardScaler(),MLPClassifier(hidden_layer_sizes=(width,),alpha=.01,max_iter=1200,early_stopping=True,n_iter_no_change=30,random_state=7));m.fit(a,c);rows.append([width,log_loss(c,m.predict_proba(a)),log_loss(d,m.predict_proba(b))])
t=pd.DataFrame(rows,columns=['gizli_birim','egitim_logloss','test_logloss']);print(t);plt.plot(t.gizli_birim,t.egitim_logloss,'o-',label='Eğitim');plt.plot(t.gizli_birim,t.test_logloss,'o-',label='Test');plt.xlabel('Gizli birim');plt.ylabel('Log kaybı');plt.legend()
''')
add(105,'Seçtiğim en iyi doğrulama skoru neden iyimser olabilir?','İç seçim skoruyla dış kat sonuçlarını ayır.','Ölçekleme pipeline içindedir. İç içe CV belirlenen arama prosedürünü değerlendirir, her veri sorununu çözmez.','C adaylarına 10 ve 100 ekle; seçim skorunu dış sonuçla karşılaştır.', '''
from sklearn.svm import SVC
X,y=make_classification(n_samples=240,n_features=8,n_informative=4,random_state=7);outer=StratifiedKFold(4,shuffle=True,random_state=7);rows=[]
for fold,(tr,te) in enumerate(outer.split(X,y),1):
 search=GridSearchCV(make_pipeline(StandardScaler(),SVC(kernel='rbf')),{'svc__C':[.1,1,10],'svc__gamma':[.01,.1,1]},cv=3,scoring='accuracy');search.fit(X[tr],y[tr]);rows.append([fold,search.best_score_,search.score(X[te],y[te])])
t=pd.DataFrame(rows,columns=['dis_kat','ic_secim_skoru','dis_test_skoru']);print(t);print('Dış ortalama:',t.dis_test_skoru.mean());plt.plot(t.dis_kat,t.ic_secim_skoru,'o-',label='İç seçim');plt.plot(t.dis_kat,t.dis_test_skoru,'o-',label='Dış test');plt.xlabel('Dış kat');plt.ylabel('Doğruluk');plt.legend()
''')
add(106,'Nadir olayda ROC iyi görünürken alarm yükü nasıl olabilir?','ROC-AUC yanında PR ve taban oranını raporla.','Average precision bir eşikte precision değildir; değerlendirme bağımsız testte yapılır.','Pozitif payını .1’den .02’ye indir; ROC ve AP değişimini incele.', '''
from sklearn.metrics import RocCurveDisplay, PrecisionRecallDisplay
X,y=make_classification(n_samples=1500,n_features=6,n_informative=3,weights=[.9,.1],random_state=7);a,b,c,d=train_test_split(X,y,test_size=.4,stratify=y,random_state=7);m=make_pipeline(StandardScaler(),LogisticRegression());m.fit(a,c);p=m.predict_proba(b)[:,1];print({'taban':d.mean(),'ROC_AUC':roc_auc_score(d,p),'AP':average_precision_score(d,p)})
PrecisionRecallDisplay.from_predictions(d,p,ax=plt.gca());plt.axhline(d.mean(),c='tab:orange',label='Taban oranı');plt.legend()
''')
add(107,'Kalibratörü test verisinden öğrenmeden nasıl sınarım?','Kalibrasyon eğrilerini ve Brier’ı aynı bağımsız testte kıyasla.','CalibratedClassifierCV eğitim içinde CV kullanır; final test ayarlamada kullanılmaz.','Kalibrasyon yöntemini sigmoid yerine isotonic yap; veri ihtiyacını tartış.', '''
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.ensemble import RandomForestClassifier
X,y=make_classification(n_samples=1200,n_features=8,n_informative=4,random_state=7);a,b,c,d=train_test_split(X,y,test_size=.35,stratify=y,random_state=7);base=RandomForestClassifier(n_estimators=60,min_samples_leaf=8,random_state=7,n_jobs=1);cal=CalibratedClassifierCV(base,method='sigmoid',cv=3);base.fit(a,c);cal.fit(a,c)
for name,m in [('Ham',base),('Sigmoid',cal)]:
 p=m.predict_proba(b)[:,1];print(name,'Brier',brier_score_loss(d,p));obs,mean=calibration_curve(d,p,n_bins=6);plt.plot(mean,obs,'o-',label=name)
plt.plot([0,1],[0,1],'--',c='gray');plt.xlabel('Ortalama tahmin');plt.ylabel('Gözlenen pay');plt.legend()
''')
add(108,'İki model aynı kayıtlarda nasıl karşılaştırılır?','Satırları çift olarak yeniden çekerek kayıp farkı aralığını kur.','Bağımsız test kayıtları varsayılır; zaman veya müşteri kümelerinde blok/küme bootstrap gerekir.','İki modelin aynı satırlardaki korelasyonunu artır; bağımsız çekimin neden yanlış olduğunu açıkla.', '''
y=rng.normal(size=250);pA=y+rng.normal(0,1,250);pB=y+rng.normal(0,.9,250);diff=(pA-y)**2-(pB-y)**2;draws=rng.choice(diff,(2000,len(diff))).mean(axis=1);print({'MSE_A_eksi_B':diff.mean(),'esli_bootstrap_CI95':np.quantile(draws,[.025,.975]).tolist()})
plt.hist(draws,bins=35);plt.axvline(0,c='tab:orange');plt.xlabel('Ortalama eşleştirilmiş kayıp farkı');plt.ylabel('Tekrar')
''')
add(109,'Korelasyonlu iki ölçümde uzaklığı nasıl değerlendiririm?','Aynı Öklid uzaklığında noktaların Mahalanobis farkını gör.','Kovaryans tahmini bağımsız referanstan gelir; yüksek boyut/az örneklemde regularizasyon gerekir.','Korelasyonu .85’ten 0’a indir; eliptik uzaklığın değişimini incele.', '''
X=rng.multivariate_normal([0,0],[[1,.85],[.85,1]],400);cov=np.cov(X,rowvar=False);center=X.mean(axis=0);points=np.array([[2,2],[2,-2]]);delta=points-center;dist2=np.einsum('ij,jk,ik->i',delta,np.linalg.inv(cov),delta);print({'noktalar':points.tolist(),'Mahalanobis_kare':dist2.tolist(),'chi2_95':stats.chi2.ppf(.95,2)})
plt.scatter(*X.T,s=10,alpha=.3);plt.scatter(*points.T,s=80,c=['tab:green','tab:red']);plt.axis('equal');plt.xlabel('x1');plt.ylabel('x2')
''')
add(110,'EM ile yumuşak küme üyeliğini nasıl öğrenirim?','Sert etiket yerine üyelik olasılığı ve BIC’yi birlikte incele.','Karışım etiketleri yer değiştirebilir; yerel optimum ve normal bileşen varsayımı kontrol edilir.','Bileşen ortalamalarını yaklaştır; üyelik belirsizliğini gör.', '''
from sklearn.mixture import GaussianMixture
X=np.r_[rng.normal(-1.5,.7,(180,1)),rng.normal(1.5,1,(220,1))];rows=[];models=[]
for k in [1,2,3,4]:
 m=GaussianMixture(k,n_init=5,random_state=7).fit(X);models.append(m);rows.append([k,m.bic(X),m.converged_])
print(pd.DataFrame(rows,columns=['bilesen','BIC','yakinsadi']));m=models[1];print('Ortalama:',m.means_.ravel(),'Ağırlık:',m.weights_);grid=np.linspace(-5,5,300)[:,None];plt.hist(X.ravel(),bins=35,density=True,alpha=.4);plt.plot(grid[:,0],np.exp(m.score_samples(grid)));plt.xlabel('Ölçüm');plt.ylabel('Yoğunluk')
''')
add(111,'Ortak faktör ile toplam varyans aynı hedef mi?','Faktör yükleri ve özgül hata varyanslarını ayır.','Faktörün işareti/rotasyonu tanımlanabilirlik sınırı taşır; faktörler kendiliğinden gerçek neden değildir.','Son ölçümün hata sapmasını artır; özgül varyansı incele.', '''
from sklearn.decomposition import FactorAnalysis
latent=rng.normal(size=(400,1));load=np.array([[1,.8,.6,1.2]]);X=latent@load+rng.normal(size=(400,4))*np.array([.3,.5,1.,.4]);m=FactorAnalysis(1,random_state=7).fit(X);print({'yukler':m.components_.tolist(),'ozgul_varyans':m.noise_variance_.tolist()});plt.bar(np.arange(4)-.18,m.components_[0],.36,label='Yük');plt.bar(np.arange(4)+.18,m.noise_variance_,.36,label='Özgül varyans');plt.xlabel('Ölçüm');plt.legend()
''')
add(112,'İki boyutlu adalar doğal sınıf kanıtı mı?','Aynı noktaların farklı perplexity değerlerinde yerleşimini karşılaştır.','t-SNE eksenleri ve küme arası uzaklık global geometri değildir; UMAP burada eğitilmez, ayrı algoritmadır.','Perplexity=10 yerine 50 kullan; etiketlerin değişmediğini, yerleşimin değiştiğini göster.', '''
from sklearn.manifold import TSNE
X,y=make_classification(n_samples=180,n_features=6,n_informative=3,n_classes=3,n_clusters_per_class=1,random_state=7);X=StandardScaler().fit_transform(X);m=TSNE(perplexity=20,max_iter=500,init='pca',random_state=7);z=m.fit_transform(X);print({'KL_objektif':m.kl_divergence_,'n':len(X),'perplexity':20});plt.scatter(*z.T,c=y,s=20,cmap='viridis');plt.xlabel('t-SNE 1 · keyfi eksen');plt.ylabel('t-SNE 2 · keyfi eksen')
''')
add(113,'Tedavi seçimiyle müdahale etkisini nasıl ayırırım?','Ham farkı IPW ve bilinen simülasyon etkisiyle karşılaştır.','IPW gözlenen karıştırıcılar, doğru eğilim modeli, tutarlılık ve pozitiflik ister; gizli karıştırıcıyı çözmez.','Seçilim katsayısını 1’den 2’ye çıkar; uç ağırlık ve ESS’yi incele.', '''
x=rng.normal(size=1000);prop=special.expit(x);t=rng.binomial(1,prop);y=2*t+3*x+rng.normal(size=1000);m=LogisticRegression(C=1e5).fit(x[:,None],t);e=m.predict_proba(x[:,None])[:,1]
if np.min(e)<.01 or np.max(e)>.99:print('UYARI: zayıf destek / uç ağırlık')
w1=t/e;w0=(1-t)/(1-e);effect=np.sum(w1*y)/w1.sum()-np.sum(w0*y)/w0.sum();ess=lambda w:w.sum()**2/(w@w)
print({'ham_fark':y[t==1].mean()-y[t==0].mean(),'Hajek_IPW':effect,'gercek_etki':2,'tedavi_ESS':ess(w1),'kontrol_ESS':ess(w0)})
plt.hist(e[t==0],bins=20,alpha=.5,label='Kontrol');plt.hist(e[t==1],bins=20,alpha=.5,label='Tedavi');plt.xlabel('Tahmin edilen eğilim');plt.ylabel('Kayıt');plt.legend()
''')
add(114,'Dışsal araç endojenlik sorununu nasıl değiştirebilir?','OLS, 2SLS ve bilinen üretim etkisini karşılaştır.','Araç dışsallığı ve dışlama veriyle tek başına kanıtlanmaz; ikinci aşama saf OLS standart hatası geçerli değildir.','Araç katsayısını 1’den .1’e indir; ilk aşama F ve tahmini incele.', '''
n=1200;z=rng.normal(size=n);u=rng.normal(size=n);t=z+.8*u+rng.normal(size=n);y=2*t+u+rng.normal(size=n);first=sm.OLS(t,sm.add_constant(z)).fit();that=first.fittedvalues;beta_iv=sm.OLS(y,sm.add_constant(that)).fit().params[1];ols=sm.OLS(y,sm.add_constant(t)).fit().params[1]
print({'OLS':ols,'2SLS_nokta':beta_iv,'gercek':2,'ilk_asama_F':float(first.fvalue),'CI':'Bu örnekte IV güven aralığı hesaplanmadı'})
plt.bar(['OLS','2SLS','Gerçek'],[ols,beta_iv,2]);plt.ylabel('Etki tahmini')
''')
add(115,'Bir eşik çevresinde yerel etkiyi nasıl kurarım?','İki taraftaki yerel doğruların eşikteki sıçramasını oku.','Süreklilik, manipülasyon olmaması ve uygun bant gerekir; etki eşik çevresine aittir.','Bant genişliğini .6’dan .3’e indir; n ve aralığın değişimini karşılaştır.', '''
x=rng.uniform(-2,2,800);t=(x>=0).astype(int);y=5+2*x+1.5*t+.4*x*t+rng.normal(size=len(x));band=.6;keep=np.abs(x)<=band;df=pd.DataFrame({'x':x[keep],'t':t[keep],'y':y[keep]});fit=smf.ols('y ~ x * t',df).fit(cov_type='HC1');print({'yerel_n':int(keep.sum()),'sicrama':fit.params['t'],'HC1_CI':fit.conf_int().loc['t'].tolist(),'gercek':1.5})
plt.scatter(df.x,df.y,s=10,alpha=.25)
for g in [0,1]:
 grid=np.linspace(-band,0,60) if g==0 else np.linspace(0,band,60);plt.plot(grid,fit.predict(pd.DataFrame({'x':grid,'t':g})))
plt.axvline(0,c='gray');plt.xlabel('Eşiğe uzaklık');plt.ylabel('Sonuç')
''')
add(116,'Tekrarlı bakış ve ön dönem bilgisi deneyi nasıl etkiler?','Önceden planlı dört bakışı Bonferroni eşiğiyle oku; CUPED varyansını ayrı karşılaştır.','Bu basit dört bakış düzeltmesi always-valid veya genel grup sıralı tasarım değildir. CUPED kovaryatı tedavi öncesi olmalı.','Etkiyi .15’ten 0’a indir; tek simülasyondan tip I hata oranı çıkarmamaya dikkat et.', '''
n=800;pre=rng.normal(size=n);t=rng.binomial(1,.5,n);y=.15*t+.8*pre+rng.normal(size=n);theta=np.cov(y,pre,ddof=1)[0,1]/np.var(pre,ddof=1);adjusted=y-theta*(pre-pre.mean());looks=[200,400,600,800];p=[]
for k in looks:p.append(stats.ttest_ind(y[:k][t[:k]==1],y[:k][t[:k]==0],equal_var=False).pvalue)
print({'bakis_p':p,'planli_esik':.05/len(looks),'ham_varyans':np.var(y),'CUPED_varyans':np.var(adjusted),'theta':theta});plt.plot(looks,p,'o-');plt.axhline(.05/len(looks),c='tab:orange');plt.xlabel('Planlı bakış n');plt.ylabel('İki yönlü p')
''')
add(117,'Sonlu partiden yerine koymadan seçince hata olasılığı nedir?','Hipergeometrik dağılımı aynı oranlı binom yaklaşımıyla karşılaştır.','Multinomial sabit n ve toplamı 1 olan kategoriler içindir; bağımsız ayrı binomların toplamı sabit değildir.','Örnekleme payını 10/100’den 60/100’e çıkar; sonlu evren farkını gör.', '''
N,K,n=100,15,20;k=np.arange(n+1);hyper=stats.hypergeom(N,K,n).pmf(k);binom=stats.binom(n,K/N).pmf(k);counts=np.array([5,9,6]);p=np.array([.2,.5,.3]);print({'hiper_P_en_az_1':stats.hypergeom.sf(0,N,K,n),'multinomial_P_5_9_6':stats.multinomial.pmf(counts,n=20,p=p)})
assert np.isclose(hyper.sum(),1);plt.plot(k,hyper,'o-',label='Hipergeometrik');plt.plot(k,binom,'o-',label='Binom yaklaşımı');plt.xlabel('Hata sayısı');plt.ylabel('P(X=k)');plt.legend()
''')
add(118,'Gamma hız ve ölçek tanımlarını karıştırırsam ne olur?','Aynı şekil için scale=1/rate ilişkisini açık tut.','Beta 0–1 parametrelerini, gamma pozitif büyüklükleri modeller; tek bir şekil tüm veri için yeterli değildir.','Gamma hızını 2’den 4’e çıkar; ortalama ve varyansın nasıl değiştiğini hesapla.', '''
shape,rate=3.,2.;scale=1/rate;g=stats.gamma(a=shape,scale=scale);b=stats.beta(2,5);print({'gamma_ortalama':g.mean(),'gamma_varyans':g.var(),'gamma_P_X_2_alti':g.cdf(2),'beta_ortalama':b.mean()});x=np.linspace(.001,5,300);plt.plot(x,g.pdf(x),label='Gamma');xx=np.linspace(.001,.999,200);plt.plot(xx,b.pdf(xx),label='Beta');plt.xlabel('Değer');plt.ylabel('Yoğunluk');plt.legend()
''')
add(119,'Henüz arızalanmamış birimi Weibull uyumuna nasıl dahil ederim?','Sabit sansür zamanı altında yaşam eğrisiyle hazard biçimini ayır.','Parametrik Weibull ve bağımsız sansür varsayılır; sansürü arıza saymak yanlıdır.','Sansür zamanını 18’den 10’a indir; tahmin ve gözlenen olay sayısını karşılaştır.', '''
shape,scale=1.8,20.;life=stats.weibull_min.rvs(shape,scale=scale,size=300,random_state=rng);censor=18.;event=life<=censor;obs=np.minimum(life,censor);data=stats.CensoredData(uncensored=obs[event],right=obs[~event]);c,loc,s=stats.weibull_min.fit(data,floc=0);print({'olay_n':int(event.sum()),'sansur_n':int((~event).sum()),'uyum_sekil':c,'uyum_olcek':s,'gercek_sekil':shape,'gercek_olcek':scale})
x=np.linspace(.01,40,200);plt.plot(x,stats.weibull_min.sf(x,c,scale=s),label='Uyum yaşam');plt.plot(x,stats.weibull_min.sf(x,shape,scale=scale),'--',label='Gerçek yaşam');plt.xlabel('Gün');plt.ylabel('S(t)');plt.legend()
''')
add(120,'ECDF ile yoğunluk tahmini neden farklı çizilir?','ECDF birikimli payı, KDE alanı 1 olan yoğunluğu gösterir.','KDE bant genişliğine ve sınır yanlılığına duyarlıdır; negatif alana sızma pozitif süre modeliyle çelişebilir.','bw_method=.2 yerine .6 yap; küçük tepelerin kaybolmasını yorumla.', '''
x=rng.lognormal(1,.6,160);grid=np.linspace(0,15,300);kde=stats.gaussian_kde(x,bw_method=.2);sorted_x=np.sort(x);ecdf=np.arange(1,len(x)+1)/len(x);print({'n':len(x),'F_5':np.mean(x<=5),'KDE_P_0_5':kde.integrate_box_1d(0,5),'negatif_sizma':kde.integrate_box_1d(-np.inf,0)})
fig,axes=plt.subplots(1,2,figsize=(9,3.5));axes[0].step(sorted_x,ecdf,where='post');axes[0].set(xlabel='Süre',ylabel='ECDF');axes[1].plot(grid,kde(grid));axes[1].set(xlabel='Süre',ylabel='KDE yoğunluğu');fig.tight_layout()
''')
assert set(R)==set(range(57,121))

def run():
 manifest={};chapters={};failed=[]
 for i,r in R.items():
  lesson=COURSE['lessons'][i-1];lid=lesson['id'];ns={};buf=io.StringIO();plt.close('all')
  try:
   with contextlib.redirect_stdout(buf),contextlib.redirect_stderr(buf):exec(SETUP+'\n'+r['code'],ns)
   assert plt.get_fignums(),f'{lid}: grafik yok'
   fig=plt.gcf();fig.savefig(OUT/f'{lid}.png',dpi=130,bbox_inches='tight',facecolor='white');output=buf.getvalue();assert output.strip(),f'{lid}: çıktı yok'
  except Exception:
   failed.append(lid);traceback.print_exc();continue
  png=base64.b64encode((OUT/f'{lid}.png').read_bytes()).decode()
  intro=f"## {lesson['title']}\n\n{r['question']}\n\n**Veri:** Kod içindeki sabit tohumlu sentetik veri. Gerçek şirket verisi içermez.\n\n**Grafiği oku:** {r['reading']}\n\n**Yorum sınırı:** {r['limit']}\n\n**Alıştırma:** {r['task']}\n\n**Kabul ölçütü:** İlk çıktıyı, tek değişiklikten sonraki çıktıyı, grafikteki farkı ve yorum sınırını dört cümlede kaydet.\n"
  cell={'cell_type':'code','execution_count':i,'metadata':{},'source':r['code'].splitlines(keepends=True),'outputs':[{'output_type':'stream','name':'stdout','text':output.splitlines(keepends=True)},{'output_type':'display_data','metadata':{},'data':{'image/png':png}}]}
  chapters.setdefault(lesson['module'],[]).extend([{'cell_type':'markdown','metadata':{},'source':intro.splitlines(keepends=True)},cell])
  manifest[lid]={**r,'id':lid,'module':lesson['module'],'title':lesson['title'],'output':output,'image':f'advanced/{lid}.png','notebook':f"advanced/konu_{lesson['module']+1:02}.ipynb",'script':f"advanced/konu_{lesson['module']+1:02}.py"}
  print('PASS',lid,lesson['title'],flush=True)
 assert not failed,failed
 for m,cells in chapters.items():
  title=COURSE['modules'][m]['title'];header=f'# Kesit İstatistik — {title}\n\nKurulum: `python -m pip install -r requirements.txt`\n\nPython 3.11+ ve Jupyter/VS Code ile aç. Önce kurulum hücresini, sonra ders hücrelerini çalıştır. Hazır çıktılar doğrulanan çalıştırmadan alınmıştır; kodu değiştirdiğinde hücreyi yeniden çalıştır. Her ders kendi sentetik verisini üretir. İnternet/API/şirket verisi gerektirmez.\n'
  # Every exercise resets RNG independently exactly as verified.
  for j in range(1,len(cells),2):cells[j]['source']=(SETUP+'\n'+''.join(cells[j]['source'])).splitlines(keepends=True)
  nb={'nbformat':4,'nbformat_minor':5,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.11'}},'cells':[{'cell_type':'markdown','metadata':{},'source':header.splitlines(keepends=True)}]+cells}
  for j,cell in enumerate(nb['cells']):cell['id']=f'kesit-{m}-{j}'
  (OUT/f'konu_{m+1:02}.ipynb').write_text(json.dumps(nb,ensure_ascii=False),encoding='utf-8')
  script='# -*- coding: utf-8 -*-\n'+''.join('\n# %%\n'+''.join(cell['source'])+'\nplt.show()\n' for cell in cells if cell['cell_type']=='code')
  (OUT/f'konu_{m+1:02}.py').write_text(script,encoding='utf-8')
 import importlib.metadata
 versions={p:importlib.metadata.version(p) for p in ['numpy','scipy','pandas','matplotlib','scikit-learn','statsmodels']}
 (OUT/'requirements.txt').write_text('\n'.join(p+'=='+v for p,v in versions.items())+'\n',encoding='utf-8')
 (OUT/'README.txt').write_text('Kesit İstatistik ileri uygulamalar\nPython 3.11+ kur. Bu klasörde: python -m pip install -r requirements.txt\nJupyter veya VS Code ile .ipynb aç; alternatif olarak python konu_15.py çalıştır.\nHer ders sabit tohumlu bağımsız sentetik veri üretir. Çıktı ve yorum sınırları defterdedir.\nBu paket 64 ileri ders için 16 defter ve 16 Python betiği içerir.\n',encoding='utf-8')
 (ROOT/'docs/advanced-content.js').write_text('window.ADVANCED='+json.dumps(manifest,ensure_ascii=False)+';',encoding='utf-8')
 with zipfile.ZipFile(OUT/'Kesit_Ileri_Uygulamalar.zip','w',zipfile.ZIP_DEFLATED) as z:
  for f in OUT.iterdir():
   if f.suffix in ['.ipynb','.py','.txt']:z.write(f,f.name)
 print('DONE:',len(manifest),'ders;',len(chapters),'defter;',versions)
if __name__=='__main__':run()
