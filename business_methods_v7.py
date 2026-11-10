"""Kesit V7. Sabit tohumlu ve yeniden üretilebilir iş analizleri."""
import numpy as np
import pandas as pd
from scipy import stats
from scipy.special import expit
import matplotlib.pyplot as plt

BLUE = '#2457ad'
ORANGE = '#ac452c'
GREEN = '#197254'
GRAY = '#64748b'

def table(frame, title):
    return dict(title=title, columns=frame.columns.tolist(),
                rows=frame.astype(object).where(frame.notna(), None).values.tolist())

def kpi(scenario='default'):
    rows = [
        ['Önce', 'Standart', 900, 882, 0],
        ['Önce', 'Karmaşık', 100, 80, 0],
        ['Sonra', 'Standart', 300, 297, 0],
        ['Sonra', 'Karmaşık', 700, 588, 0],
    ]
    if scenario == 'unknown':
        rows[3][3:] = [552, 48]
    raw = pd.DataFrame(rows, columns=['Dönem', 'İş türü', 'Toplam', 'Zamanında', 'Durumu bilinmiyor'])
    raw['Gecikmiş'] = raw.Toplam - raw.Zamanında - raw['Durumu bilinmiyor']
    assert (raw.Gecikmiş >= 0).all()
    p = raw.iloc[:2]
    q = raw.iloc[2:]
    w = p.Toplam.to_numpy() / p.Toplam.sum()
    before = p.Zamanında.to_numpy() / p.Toplam.to_numpy()
    low = q.Zamanında.to_numpy() / q.Toplam.to_numpy()
    high = (q.Zamanında + q['Durumu bilinmiyor']).to_numpy() / q.Toplam.to_numpy()
    base = w @ before
    crude = [q.Zamanında.sum()/q.Toplam.sum(), (q.Zamanında.sum()+q['Durumu bilinmiyor'].sum())/q.Toplam.sum()]
    fixed = [w @ low, w @ high]
    diff = [(x-base)*100 for x in fixed]
    def display_interval(values, precision, signed=False):
        spec = ('+' if signed else '') + f'.{precision}f'
        text = [format(v, spec).replace('.',',') for v in values]
        return text[0] if np.isclose(values[0], values[1]) else ' ile '.join(text)
    crude_display = display_interval(np.array(crude)*100, 1)
    diff_display = display_interval(diff, 2, signed=True)
    info = raw[['Dönem', 'İş türü', 'Toplam', 'Zamanında', 'Durumu bilinmiyor']].copy()
    info['En düşük oran %'] = raw.Zamanında / raw.Toplam * 100
    info['En yüksek oran %'] = (raw.Zamanında+raw['Durumu bilinmiyor'])/raw.Toplam*100
    fig, ax = plt.subplots(figsize=(8.5, 4.2), layout='constrained')
    labels = ['Standart', 'Karmaşık', 'Tüm işler\nham oran', 'Tüm işler\neski dağılımla']
    old = np.r_[before, base, base]*100
    newlow = np.r_[low, crude[0], fixed[0]]*100
    newhigh = np.r_[high, crude[1], fixed[1]]*100
    x = np.arange(4)
    ax.scatter(x-.11, old, color=BLUE, label='Önce', s=65)
    ax.errorbar(x+.11, (newlow+newhigh)/2, (newhigh-newlow)/2, fmt='s', capsize=5, color=ORANGE,
                label='Sonra' if scenario=='default' else 'Sonra (bilinmeyen durum sınırları)')
    ax.set(xticks=x, xticklabels=labels, ylim=(73,101), ylabel='Zamanında teslim · %',
           title='İş karmasını sabitleyince KPI ne söylüyor?')
    ax.legend(loc='lower right', fontsize=9)
    fig2, ax2 = plt.subplots(figsize=(8.5,3.4),layout='constrained')
    ax2.barh([0,1], [90,30],color=BLUE,label='Standart')
    ax2.barh([0,1], [10,70],left=[90,30],color=ORANGE,label='Karmaşık')
    for y,a,b in [(0,90,10),(1,30,70)]:
        ax2.text(a/2,y,f'%{a}',color='white',ha='center',va='center',weight='bold')
        ax2.text(a+b/2,y,f'%{b}',color='white',ha='center',va='center',weight='bold')
    ax2.set(yticks=[0,1],yticklabels=['Önce','Sonra'],xlabel='Tüm işler içindeki pay · %',title='Sonraki dönemde karmaşık işler daha ağırlıklı')
    ax2.legend(loc='upper center',bbox_to_anchor=(.5,-.18),ncol=2)
    decision = (
        'Ham oran düşerken her iş türünde oran yükseliyor. İş karması eski ağırlıklarla sabitlendiğinde fark +1,30 yüzde puan. Hacim planı için karmaşık iş yükünü, yöntem performansı için tür bazlı oranları incele.'
        if scenario == 'default' else
        'Eski iş karmasına göre toplam farkın alt sınırı pozitif olsa da karmaşık grupta değişimin yönü bilinmiyor. Önce 48 açık teslim durumunu kapat. Sonraki dönemin ham SLA düşüşünü ve standartlaştırılmış kıyası ayrı raporla.'
    )
    return dict(metrics={'Önce · ham %':base*100,'Sonra · ham %':crude_display,
                         'Sabit karma farkı · yp':diff_display,'Bilinmeyen iş':int(raw['Durumu bilinmiyor'].sum())},
        tables=[table(info,'Aynı payda ile tür bazında KPI')], figures=[
          ('Noktalar tür bazlı oranları, dikey çizgiler bilinmeyen teslimlerin yaratabileceği sınırı gösterir. Bu çizgiler güven aralığı değildir.',fig),
          ('Önceki dönemde karmaşık işlerin payı %10, sonraki dönemde %70. Ham toplam bu değişimden etkilenir.',fig2)],
        frames={'kpi_sayimlari':raw},
        steps=['Her dönem ve iş türünde zamanında / tüm uygun iş oranını hesapla. Eksik durumları paydada tut.',
               f'Önceki karışımı referans seç: %90 standart + %10 karmaşık. Sonra sabit karma oranı %{fixed[0]*100:.2f}–%{fixed[1]*100:.2f}.',
               'Bilinmeyenlerin tamamı gecikmiş ve tamamı zamanında varsayımlarını ayrı hesapla. İki sınır arasındaki fark veri riskidir.'],
        decision=decision,limit='Dört hücre iki dönemlik sentetik sayımdır. Ağırlıklar seçilen referansa bağlıdır. Standartlaştırma yalnız gözlenen iş türünü dengeler. Dönem kıyası tek başına süreç değişikliğinin nedensel etkisini göstermez.',
        diagnostics={'crude_before':base,'crude_after':crude,'fixed':fixed,'diff_pp':diff},
        focus=[['Ham hizmet düzeyi',f'%{base*100:.1f} → %{crude[0]*100:.1f}'+(' alt sınır' if scenario=='unknown' else ''),'Müşterinin karşılaştığı toplam düzey'],
               ['Karma etkisi','%10 → %70','Karmaşık iş payı arttı'],
               ['Adil kıyas',f'{diff[0]:+.2f} yp'+(' alt sınır' if scenario=='unknown' else ''),'Eski iş dağılımı ile kıyas']])

def inventory_audit(scenario='default'):
    rng = np.random.default_rng(72101)
    configs = [('Hızlı dönen',8000,0.035,100),('Orta dönen',3000,0.075,100),('Yavaş dönen',1000,0.17,100)]
    selections = []
    rows = []
    for label,N,p,n in configs:
        error = rng.binomial(1,p,N)
        idx = rng.choice(N,n,replace=False)
        sampled = error[idx]
        draw = rng.random(n)
        lost = (draw < np.where(sampled==1,.54,.09)) if scenario == 'nonresponse' else np.zeros(n,dtype=bool)
        visible = np.where(lost,np.nan,sampled)
        observed = np.nansum(visible)
        missing = lost.sum()
        lower = observed/n
        upper = (observed+missing)/n
        rows.append([label,N,n,int(observed),int(missing),lower,upper,N/12000])
        selections.extend([[label,int(i+1),None if m else int(v)] for i,m,v in zip(idx,lost,sampled)])
    detail = pd.DataFrame(rows,columns=['Tabaka','Evren N','Çekilen n','Bulunan hata','Eksik denetim','Alt oran','Üst oran','Evren ağırlığı'])
    raw = pd.DataFrame(selections,columns=['Tabaka','Adres no (tabaka içi)','Sayım farkı · 0/1'])
    w = detail['Evren ağırlığı'].to_numpy()
    lows = detail['Alt oran'].to_numpy()
    highs = detail['Üst oran'].to_numpy()
    low,high = w @ lows,w @ highs
    n = detail['Çekilen n'].to_numpy()
    N = detail['Evren N'].to_numpy()
    var = np.sum(w**2*(1-n/N)*lows*(1-lows)/(n-1))
    ci = [max(0,low-1.96*np.sqrt(var)),min(1,low+1.96*np.sqrt(var))]
    complete = scenario=='default'
    crude = raw['Sayım farkı · 0/1'].mean()
    target = .06
    fig, ax = plt.subplots(figsize=(8.6,4.4),layout='constrained')
    x = np.arange(3)
    ax.errorbar(x,(lows+highs)*50,(highs-lows)*50,fmt='o',capsize=7,color=BLUE,label='Örneklem durumu sınırları')
    ax.set(xticks=x,xticklabels=detail.Tabaka,ylabel='Sayım farkı · %',title='Her tabakada örneklem ve bilinmeyen denetimler')
    for i,a in enumerate(w):
        ax.annotate(f'Evren payı %{a*100:.1f}',(i,highs[i]*100),xytext=(0,10),textcoords='offset points',ha='center')
    ax.set_ylim(0,max(highs)*100+6)
    fig2, ax2 = plt.subplots(figsize=(8.6,3.25),layout='constrained')
    bounds = ci if complete else [low,high]
    ax2.errorbar([(bounds[0]+bounds[1])*50],[1],xerr=[(bounds[1]-bounds[0])*50],fmt='o',capsize=6,color=BLUE)
    ax2.axvline(target*100,color=ORANGE,ls='--',label='%6 işletme inceleme eşiği')
    ax2.set(yticks=[],xlabel='Ağırlıklı hata oranı · %',
            title='Tasarım temelli yaklaşık %95 aralık' if complete else 'Cevapsız adresler için duyarlılık sınırı')
    ax2.legend(loc='upper right',fontsize=9)
    decision = (
        f'Adres ağırlığıyla tahmin %{low*100:.2f}. Yaklaşık aralık %{ci[0]*100:.2f}–%{ci[1]*100:.2f}. %6 eşiğine ilişkin kesin karar için aralığın konumunu ve tabaka risklerini birlikte oku.'
        if complete else
        f'Kayıp denetimler için ağırlıklı örneklem oranı %{low*100:.2f}–%{high*100:.2f} arasında. Bu sınırlar örnekleme hatasını içermez. Cevapsız adresleri takip et ve nedenlerini kaydet.'
    )
    return dict(metrics={'Çekilen adres':int(len(raw)),'Evren adresi':12000,'Tamamlananların basit oranı · %':crude*100,
                         'Ağırlıklı tahmin · %':low*100 if complete else 'Cevap eksik',
                         'Aralık türü':'%95 yaklaşık örnekleme' if complete else 'Eksik veri duyarlılığı',
                         'Alt–üst · %':f'{bounds[0]*100:.2f}–{bounds[1]*100:.2f}'},
        tables=[table(detail,'Örneklem hacmi ve evren ağırlığı')],figures=[
          ('Üç tabakanın her birinden 100 adres çekilir, ama evren payları farklıdır.',fig),
          ('İş eşiği aynı kalır. Eksik veri senaryosundaki çizgi güven aralığı değildir.',fig2)],
        frames={'adres_denetimi':raw,'tabaka_ozeti':detail},
        steps=['Adresleri hareket hızına göre birbirini dışlayan üç tabakaya ayır. Her tabakadan yerine koymadan rastgele çek.',
               'Tabaka oranını evren ağırlığı Nₕ/N ile çarp ve topla. Örnekteki eşit n, evrenin üçte birini temsil etmez.',
               'Tam cevapta varyansa sonlu evren düzeltmesi 1−nₕ/Nₕ ekle. Eksik cevapta yalnız tamamlananların oranına güvenme.'],
        decision=decision,limit='Evren çerçevesinin tam ve tabakaların doğru olduğu varsayılır. Yaklaşık normal aralık çok seyrek hata veya küçük tabaka n değerinde zayıf olabilir. Eksik senaryosunda sonuçla ilişkili kayıp simüle edilir, güven aralığı üretilmez.',
        diagnostics={'weight_sum':w.sum(),'weighted_bounds':[low,high],'ci':ci if complete else None,'crude':crude},
        focus=[['Seçim','3 × 100 adres','Her tabakada rastgele'],['Ağırlık','8.000 / 3.000 / 1.000','Evren büyüklüğüne göre'],['Karar',f'%{bounds[0]*100:.2f}–{bounds[1]*100:.2f}','%6 iş eşiğiyle karşılaştır']])

def experiment(scenario='default'):
    rng = np.random.default_rng(72102)
    n = 4000
    z = stats.norm.ppf(.975)
    p0, p1 = .10,.13
    pbar = (p0+p1)/2
    planned = int(np.ceil((z*np.sqrt(2*pbar*(1-pbar)) + stats.norm.ppf(.8)*np.sqrt(p0*(1-p0)+p1*(1-p1)))**2/(p1-p0)**2))
    assignment = np.repeat(['A','B'],n)
    rng.shuffle(assignment)
    is_b = assignment=='B'
    conversion = (rng.random(2*n) < np.where(is_b,.146,.10)).astype(int)
    complaint = (rng.random(2*n) < np.where(is_b,.045 if scenario=='complaints' else .020,.019)).astype(int)
    raw = pd.DataFrame({'Müşteri':np.arange(1,2*n+1),'Kol':assignment,'Dönüşüm':conversion,'Şikayet':complaint})
    def wilson(k,n):
        p = k/n
        denom=1+z*z/n
        mid=(p+z*z/(2*n))/denom
        radius=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/denom
        return mid-radius,mid+radius
    rows=[]
    for name,th in [('Dönüşüm',.02),('Şikayet',.015)]:
        a,b = [int(raw.loc[raw.Kol==g,name].sum()) for g in ['A','B']]
        pa,pb = a/n,b/n
        la,ua = wilson(a,n)
        lb,ub = wilson(b,n)
        d=pb-pa
        lo = d-np.hypot(pb-lb,ua-pa)
        hi = d+np.hypot(ub-pb,pa-la)
        rows.append([name,a,b,pa*100,pb*100,d*100,lo*100,hi*100,th*100])
    detail=pd.DataFrame(rows,columns=['Ölçü','A olay','B olay','A %','B %','Fark · yp','Alt · yp','Üst · yp','İş eşiği · yp'])
    fig,axes=plt.subplots(2,1,figsize=(8.6,5.1),layout='constrained')
    for i,(ax,row) in enumerate(zip(axes,rows)):
        name,_,_,_,_,d,lo,hi,th=row
        ax.errorbar([d],[0],xerr=[[d-lo],[hi-d]],fmt='o',capsize=6,color=BLUE)
        ax.axvline(0,color=GRAY,ls=':',label='Fark 0')
        ax.axvline(th,color=ORANGE,ls='--',label='İş eşiği')
        ax.set(yticks=[],xlabel='B−A · yüzde puan',title=f'{name}: '+('alt sınır ≥ +2 yp' if i==0 else 'üst sınır ≤ +1,5 yp'))
        ax.legend(loc='upper right',fontsize=8)
    pass_lift=rows[0][6]>=2
    pass_guard=rows[1][7]<=1.5
    eligible=pass_lift and pass_guard
    return dict(metrics={'Müşteri / kol':n,'Yaklaşık güç planı / kol':planned,'Dönüşüm farkı · yp':rows[0][5],
                         'Şikayet farkı · yp':rows[1][5],'İki karar koşulu':'Sağlandı' if eligible else 'Sağlanmadı'},
        tables=[table(detail,'Ayrı ölçütler için Newcombe %95 fark aralıkları')],
        figures=[('Üst grafikte aralığın tamamının kazanım eşiğini aşması, alt grafikte aralığın üst ucunun zarar sınırını geçmemesi aranır.',fig)],
        frames={'deney_musteri_sonuclari':raw,'karar_tablosu':detail},
        steps=[f'%10’dan %13’e farkı sıfıra karşı %80 güçle saptamak için yaklaşık {planned} müşteri/kol gerekir. Bu hesap iş eşiğini ve şikayet koşulunu birlikte geçme gücü değildir.',
               'Sabit hacim 4.000/kol; analiz ilk atamaya göre, tüm müşterilerde aynı takip penceresiyle yapılır. Ortada tekrar tekrar test edip erken durma yok.',
               'Bağımsız oran farkı için Wilson uçlarını Newcombe ile birleştir. Son kararda dönüşüm alt ucu ve şikayet üst ucunu ayrı iş eşikleriyle karşılaştır.'],
        decision='İki koşul da sağlandı. Sınırlı yaygınlaştırma ve aynı şikayet takibi düşünülebilir.' if eligible else 'Bir karar koşulu sağlanmadı. Artan dönüşüm tek başına yaygınlaştırma için yeterli kanıt değil. Şikayet nedenlerini ve etki aralığını incele.',
        limit='Bir müşteri bir atama, bağımsız birimler ve tam takip varsayılır. Sonuçlar önceden belirlenen tek final analizine aittir. Alt gruplarda sonradan aranan farklar doğrulama gerektirir.',
        diagnostics={'n_arm':n,'planned':planned,'rows':rows,'pass_lift':pass_lift,'pass_guard':pass_guard},
        focus=[['Tasarım','4.000 + 4.000','Müşteri düzeyinde rastgele atama'],['Kazanım',f'{rows[0][6]:+.2f} yp alt uç','En az +2 yp koşulu'],['Koruma',f'{rows[1][7]:+.2f} yp üst uç','En çok +1,5 yp şikayet']])

def capacity(scenario='default'):
    rng=np.random.default_rng(72103)
    n=180
    volume=rng.integers(800,2200,n)
    complex_share=rng.uniform(.12,.64,n)
    noise=rng.normal(0,3,n)
    if scenario=='peak':
        volume[150:]=rng.integers(2200,2800,n-150)
        complex_share[150:]=rng.uniform(.49,.73,n-150)
    hours=7 + .022*volume + 27*complex_share + noise
    if scenario=='peak':
        hours[150:] += .025*np.maximum(volume[150:]-2200,0)
    raw=pd.DataFrame({'Gün':np.arange(1,n+1),'Sipariş':volume,'Karmaşık payı':complex_share,'Adam-saat':hours,
                      'Bölüm':np.where(np.arange(n)<150,'Eğitim','Final')})
    X=np.column_stack([np.ones(n),volume,complex_share])
    train=X[:150]
    y=hours[:150]
    coef=np.linalg.lstsq(train,y,rcond=None)[0]
    fit=train@coef
    resid=y-fit
    df=len(y)-len(coef)
    rmse=np.sqrt((resid@resid)/df)
    inv=np.linalg.inv(train.T@train)
    pred=X[150:]@coef
    leverage=np.einsum('ij,jk,ik->i',X[150:],inv,X[150:])
    half=stats.t.ppf(.975,df)*rmse*np.sqrt(1+leverage)
    cover=np.mean(np.abs(hours[150:]-pred)<=half)
    ood=(volume[150:]<volume[:150].min())|(volume[150:]>volume[:150].max())|(complex_share[150:]<complex_share[:150].min())|(complex_share[150:]>complex_share[:150].max())
    base=np.mean(y)
    final=raw.iloc[150:].copy()
    final['Tahmin']=pred
    final['Alt %95']=pred-half
    final['Üst %95']=pred+half
    final['Eğitim aralığı dışında']=ood
    fig,ax=plt.subplots(figsize=(8.8,4.3),layout='constrained')
    ax.plot(final.Gün,hours[150:],'.-',color=ORANGE,label='Gerçekleşen')
    ax.plot(final.Gün,pred,color=BLUE,label='Tahmin')
    ax.fill_between(final.Gün,pred-half,pred+half,color=BLUE,alpha=.13,label='Tek gün için model aralığı')
    if np.any(ood):
        ax.scatter(final.Gün[ood],pred[ood],marker='x',color=GRAY,label='Eğitim aralığı dışında')
    ax.set(xlabel='Final günleri',ylabel='Adam-saat',title='Kapasite tahmini son 30 günde nasıl çalışıyor?')
    ax.legend(fontsize=8)
    fig2,ax2=plt.subplots(figsize=(8.8,3.7),layout='constrained')
    ax2.scatter(fit,resid,c=complex_share[:150],cmap='viridis',alpha=.7)
    ax2.axhline(0,ls='--',color=GRAY)
    ax2.set(xlabel='Eğitim tahmini · adam-saat',ylabel='Gerçekleşen − tahmin',title='Artıkların şekli, yayılımı ve uç noktaları')
    t=X[150]
    h0=t@inv@t
    c=stats.t.ppf(.975,df)*rmse
    detail=pd.DataFrame([['Bir günün ortalama yükü',pred[0],pred[0]-c*np.sqrt(h0),pred[0]+c*np.sqrt(h0)],
                         ['Tek bir günün yükü',pred[0],pred[0]-half[0],pred[0]+half[0]]],
                        columns=['151. gün için hedef','Tahmin','Alt %95','Üst %95'])
    mae=np.mean(np.abs(hours[150:]-pred))
    return dict(metrics={'Final MAE · adam-saat':mae,'Ortalama taban MAE':np.mean(np.abs(hours[150:]-base)),
                         'Final kapsama · %':cover*100,'Destek dışında gün':int(ood.sum()),'1.000 sipariş farkı · adam-saat':coef[1]*1000},
        tables=[table(detail,'Ortalama güven aralığı ve tek gözlem tahmin aralığı'),table(final.head(8),'Final dönemin ilk 8 günü')],
        figures=[('Son 30 gün eğitimde kullanılmaz. Pik yükte aralığın dışına çıkan ve geçmişte görülmeyen günleri ayır.',fig),
                 ('Eğitim artıkları sıfır çevresinde sistematik şekil gösteriyorsa formülü ve değişen yayılımı sorgula.',fig2)],
        frames={'kapasite_180_gun':raw,'final_tahminler':final},
        steps=['Önce ilk 150 güne OLS uydur. Sipariş sayısı ve karmaşık iş payını tahmin anında erişilebilir girdiler olarak kullan.',
               'Ortalama için SE = s√h. Tek yeni gözlem için SE = s√(1+h). Artı bir, günün kendi oynaklığıdır.',
               'Son 30 günü zaman sırasıyla test et. Eğitim aralığı dışında iş yükü varsa model aralığına karar garantisi yükleme.'],
        decision='Geçmiş yük aralığını aşan günler için ayrı pik pilotu veya kapasite senaryosu gerekir.' if np.any(ood) else 'Son dönemde model taban tahmini iyileştiriyor. Vardiya kararında tahmin aralığı ve hizmet hedefi için rezervi ayrıca planla.',
        limit='Klasik tahmin aralığı doğrusal ortalama, sabit varyans ve yaklaşık bağımsız normal artık varsayar. Kapsama yalnız 30 sentetik günde ölçülür. Hacim katsayısı nedensel personel etkisi değildir.',
        diagnostics={'coef':coef,'rmse':rmse,'cover':cover,'mae':mae,'ood':ood.sum(),'train_n':150,'test_n':30,'mean_half':c*np.sqrt(h0),'prediction_half':half[0]},
        focus=[['Eğitim','Gün 1–150','Model yalnız geçmişten öğrenir'],['Final','Gün 151–180','İlk kez değerlendirilen dönem'],['Karar',f'{int(ood.sum())} gün','Geçmiş yük aralığının dışında']])

def rollout(scenario='default'):
    rng=np.random.default_rng(72104)
    weeks=np.arange(-8,8)
    change=np.r_[np.ones(12,dtype=bool),np.zeros(12,dtype=bool)]
    site_base=rng.normal(13,1.15,24)+1.7*change
    stable_site_slope=rng.normal(0,.035,24)
    common=.12*weeks+.25*np.sin(weeks)
    noise=rng.normal(0,.65,(24,16))
    baseline=site_base[:,None]+common+stable_site_slope[:,None]*weeks+noise
    if scenario=='pretrend':
        baseline+=change[:,None]*(-.22*weeks)
    effect=-1.45 if scenario=='default' else 0.
    outcome=baseline+effect*change[:,None]*(weeks>=0)
    raw=pd.DataFrame({'Depo':np.repeat(np.arange(1,25),16),'Hafta':np.tile(weeks,24),
                      'Pilot':np.repeat(change,16),'Toplama süresi · dk':outcome.ravel()})
    delta=outcome[:,8:].mean(axis=1)-outcome[:,:8].mean(axis=1)
    a,b=delta[change],delta[~change]
    d=a.mean()-b.mean()
    va,vb=a.var(ddof=1)/len(a),b.var(ddof=1)/len(b)
    se=np.sqrt(va+vb)
    df=(va+vb)**2/(va**2/(len(a)-1)+vb**2/(len(b)-1))
    bounds=stats.t.interval(.95,df,loc=d,scale=se)
    pre=outcome[:,4:8].mean(axis=1)-outcome[:,:4].mean(axis=1)
    placebo=pre[change].mean()-pre[~change].mean()
    fig,ax=plt.subplots(figsize=(8.8,4.3),layout='constrained')
    ax.plot(weeks,outcome[change].mean(axis=0),'o-',color=BLUE,label='Pilot depolar')
    ax.plot(weeks,outcome[~change].mean(axis=0),'s-',color=ORANGE,label='Kıyas depoları')
    ax.axvline(-.5,color=GRAY,ls='--')
    ax.annotate('WMS pilot başlangıcı',(0,outcome[change,8].mean()),xytext=(12,23),textcoords='offset points',fontsize=9)
    ax.set(xlabel='Başlangıca göre hafta',ylabel='Depo ortalaması · dakika',title='Pilot öncesi eğilimlerin yönünü karşılaştır')
    ax.legend()
    fig2,ax2=plt.subplots(figsize=(8.8,3.5),layout='constrained')
    ax2.errorbar([d],[0],xerr=[[d-bounds[0]],[bounds[1]-d]],fmt='o',color=BLUE,capsize=6,label='Pilot dönemi farkların farkı')
    ax2.scatter([placebo],[1],marker='D',color=ORANGE,label='Pilot öncesi sahte başlangıç')
    ax2.axvline(0,color=GRAY,ls='--')
    ax2.set(yticks=[0,1],yticklabels=['Pilot dönemi','Ön dönem'],xlabel='Pilot değişimi − kıyas değişimi · dakika',
            title='Ön dönem ayrışması nedensel yorumu zayıflatır')
    ax2.legend(loc='lower left',fontsize=8)
    detail=pd.DataFrame([['Pilot',12,outcome[change,:8].mean(),outcome[change,8:].mean(),a.mean()],
                         ['Kıyas',12,outcome[~change,:8].mean(),outcome[~change,8:].mean(),b.mean()]],
                        columns=['Grup','Depo','Önce · dk','Sonra · dk','Değişim · dk'])
    return dict(metrics={'Farkların farkı · dk':d,'Aralık · dk':f'{bounds[0]:+.2f}…{bounds[1]:+.2f}',
                         'Ön dönem sahte etki · dk':placebo,'Bağımsız birim':'24 depo'},
        tables=[table(detail,'Her depo aynı ağırlıkta')],
        figures=[('Dikey çizgi geçişi gösterir. Ön seviyelerin farklı olması tek başına sorun değildir. Karşılaştırılan eğilimdir.',fig),
                 ('Ön dönem göstergesi tek bir tanıdır. Yakın sıfır paralel eğilimi kanıtlamaz.',fig2)],
        frames={'depo_hafta':raw,'depo_degisimleri':pd.DataFrame({'Depo':np.arange(1,25),'Pilot':change,'Sonra − önce · dk':delta})},
        steps=['Pilot ve kıyas depolarını müdahale öncesi koşullara göre tanımla. Hedef her depoya eşit ağırlık veren ortalama değişim.',
               'Her depo için sekiz sonraki haftanın ortalamasından sekiz önceki haftanın ortalamasını çıkar. Pilot ortalama değişiminden kıyas ortalamasını çıkar.',
               'Belirsizliği 384 depo-hafta yerine 24 depo değişimi üzerinden Welch ile hesapla. Ön dönem sahte başlangıcı ve eşzamanlı değişiklikleri ayrıca incele.'],
        decision='Ön eğilimlerde büyük ayrışma görünmüyor. Sonuç pilotla uyumlu bir iyileşme, fakat vardiya/müşteri karması gibi eşzamanlı değişiklikleri saha kayıtlarıyla doğrula.' if scenario=='default' else 'Pilot öncesinde de benzer yönlü fark var. Gözlenen negatif DiD değerini WMS etkisi olarak raporlama. Kıyas grubu ve geçiş takvimini yeniden kur.',
        limit='Atama gözlemsel. Nedensel yorum için koşullu paralel eğilim, müdahale beklentisi ve yayılma olmaması gerekir. Depo bağımsızlığı, ortak bölgesel şoklar ve önceden seçilen pencere ayrıca sorgulanır. Çok zamanlı kademeli geçiş için bu iki dönem özeti yeterli değildir.',
        diagnostics={'did':d,'ci':bounds,'placebo':placebo,'simulated_effect':effect,'sites':24},
        focus=[['Ön dönem','8 hafta','Kıyas eğilimini kontrol et'],['Etki tahmini',f'{d:+.2f} dk','İki değişimin farkı'],['Sahte başlangıç',f'{placebo:+.2f} dk','Geçişten önce benzer fark var mı?']])

def monitoring(scenario='default'):
    rng=np.random.default_rng(72105)
    n=2400
    group_old=(rng.random(n)<.25).astype(int)
    group_new=(rng.random(n)<(.60 if scenario=='shift' else .25)).astype(int)
    x_old=rng.normal(0,1,n)
    x_new=rng.normal(0,1,n)
    p_old=expit(-2.40+1.15*group_old+.85*x_old)
    p_new=expit(-2.40+1.15*group_new+.85*x_new)
    true_new=expit(-2.40+1.15*group_new+.85*x_new+(.7*group_new if scenario=='shift' else 0))
    y_old=(rng.random(n)<p_old).astype(int)
    y_new=(rng.random(n)<true_new).astype(int)
    mature=np.arange(n)<1800
    threshold=.30
    raw=pd.DataFrame({'Pencere':np.repeat(['Referans','Yeni'],n),'Gözlem':np.tile(np.arange(1,n+1),2),
                      'Yoğun vardiya':np.r_[group_old,group_new],'Sabit risk skoru':np.r_[p_old,p_new],
                      'Etiket olgun':np.r_[np.ones(n,dtype=bool),mature],
                      'Gecikme':np.r_[y_old,np.where(mature,y_new,np.nan)]})
    summary=[]
    calibration=[]
    for label,frame in raw.groupby('Pencere',sort=False):
        observed=frame[frame['Etiket olgun']]
        for group in ['Tümü',0,1]:
            f=observed if group=='Tümü' else observed[observed['Yoğun vardiya']==group]
            s=f['Sabit risk skoru'].to_numpy()
            y=f.Gecikme.to_numpy()
            a=s>=threshold
            fp=int(np.sum(a & (y==0)))
            fn=int(np.sum(~a & (y==1)))
            summary.append([label,'Tümü' if group=='Tümü' else ('Yoğun' if group==1 else 'Normal'),len(f),
                            s.mean(),y.mean(),np.mean((s-y)**2),int(a.sum()),fp,fn,(fp+8*fn)*1000/len(f)])
        s=observed['Sabit risk skoru'].to_numpy()
        y=observed.Gecikme.to_numpy()
        boundaries=[0,.1,.2,.3,.5,1.01]
        for low,high in zip(boundaries[:-1],boundaries[1:]):
            member=(s>=low)&(s<high)
            if member.sum()>0:
                calibration.append([label,low,high,int(member.sum()),s[member].mean(),y[member].mean()])
    summary=pd.DataFrame(summary,columns=['Pencere','Vardiya','Etiketli n','Ortalama skor','Gözlenen oran','Brier','Alarm','Yanlış alarm','Kaçırma','Kayıp puanı / 1.000'])
    calibration=pd.DataFrame(calibration,columns=['Pencere','Skor altı','Skor üstü','n','Ortalama skor','Gözlenen oran'])
    fig,ax=plt.subplots(figsize=(7.2,4.4),layout='constrained')
    ax.plot([0,.8],[0,.8],'--',color=GRAY,label='Skor = gerçekleşme')
    for (label,frame),color in zip(calibration.groupby('Pencere',sort=False),[BLUE,ORANGE]):
        ax.plot(frame['Ortalama skor'],frame['Gözlenen oran'],'o-',color=color,label=label)
    ax.set(xlim=(0,.8),ylim=(0,.8),xlabel='Ortalama tahmin',ylabel='Gerçek gecikme oranı',
           title='Sabit skorun anlamı değişti mi?')
    ax.legend(fontsize=9)
    fig2,ax2=plt.subplots(figsize=(8.6,3.7),layout='constrained')
    latest=summary[(summary.Pencere=='Yeni') & (summary.Vardiya!='Tümü')]
    x=np.arange(len(latest))
    ax2.bar(x-.17,latest['Ortalama skor']*100,.34,color=BLUE,label='Tahmin ortalaması')
    ax2.bar(x+.17,latest['Gözlenen oran']*100,.34,color=ORANGE,label='Gerçekleşen')
    ax2.set(xticks=x,xticklabels=latest.Vardiya,ylabel='Gecikme · %',title='Yeni dönemin olgun etiketleri, vardiyaya göre')
    ax2.legend()
    alert_load=(p_new>=threshold).mean()
    current=summary[(summary.Pencere=='Yeni') & (summary.Vardiya=='Tümü')].iloc[0]
    return dict(metrics={'Yeni kayıt':n,'Olgun etiket':int(mature.sum()),'Bekleyen etiket':int((~mature).sum()),
                         'Tüm yeni kayıt · alarm %':alert_load*100,'Olgun etiket · Brier':current.Brier},
        tables=[table(summary,'Sabit 0,30 eşik: olgun kayıtlar ve vardiyalar'),table(calibration,'Güvenilirlik grafiğinin sayı tablosu')],
        figures=[('Her nokta sabit skor aralığındaki ortalama risk ve gerçekleşme oranıdır. Kutuların n değerlerini birlikte oku.',fig),
                 ('Ortalama uyum toplamda iyi görünse bile yoğun vardiyada gecikme riski düşük tahmin edilebilir.',fig2)],
        frames={'izleme_skorlari':raw,'vardiya_izleme':summary},
        steps=['Etiketi olgunlaşmamış 600 kaydı gecikmedi diye yazma. Veri karması ve alarm hacmini tüm yeni kayıtlarda ölç; doğruluğu yalnız ortak takip süresi tamamlananlarda değerlendir.',
               'Tahmin ve gerçekleşmeyi aynı sabit skor kutularında ve aynı vardiya kırılımında karşılaştır. Brier ortalama (skor−sonuç)² değeridir.',
               'Sabit eşikte 1 yanlış alarm ve 8 kaçırma puanı varsay. İş yükü, hata maliyeti ve veri kaymasını ayrı ayrı araştır.'],
        decision='Yoğun vardiyada hem pay değişimi hem risk artışı var. İlk adım etiket ve vardiya kaydını doğrulamak, ardından ayrı bir zaman kesiminde kalibrasyon ve eşik seçimini sınamak.' if scenario=='shift' else 'Bu öğretim örneğinde yeni pencere aynı mekanizmayla üretilir. Örneklem dalgalanması nedeniyle küçük farklar olabilir. Etiket olgunluğunu ve alarm yükünü izlemeye devam et.',
        limit='Skorlar sentetik ve donmuş. Vardiya karşılaştırması açıklayıcıdır, ayrımcılık ya da nedensellik testi değildir. Tüm pencere için performans, son 600 etiket tamamlanmadan bilinmez. Kayıp puanları örnek varsayımdır, para değildir.',
        diagnostics={'mature':mature.sum(),'total':n,'threshold':threshold,'share_old':group_old.mean(),'share_new':group_new.mean(),
                     'late_n':current['Etiketli n'],'fp':current['Yanlış alarm'],'fn':current['Kaçırma']},
        focus=[['Olgunluk','1.800 / 2.400','600 etiket bekliyor'],['Yoğun vardiya',f'%{group_old.mean()*100:.1f} → %{group_new.mean()*100:.1f}','Karma değişimi'],['Operasyon',f'%{alert_load*100:.1f} alarm','Kapasiteyle karşılaştır']])

def stock(scenario='default'):
    rng=np.random.default_rng(72106)
    history=rng.poisson(80,180)+rng.binomial(1,.22,180)*rng.poisson(34,180)
    actual=rng.poisson(80,60)+rng.binomial(1,.22,60)*rng.poisson(34,60)
    if scenario=='surge':
        actual=actual+25
    short,extra=9,3
    q=short/(short+extra)
    stock=int(np.quantile(history,q,method='inverted_cdf'))
    mean=int(np.round(np.mean(history)))
    high=int(np.quantile(history,.95,method='inverted_cdf'))
    rows=[]
    def measure(demand,available):
        shortage=np.maximum(demand-available,0)
        excess=np.maximum(available-demand,0)
        return [np.mean(demand<=available),1-shortage.sum()/demand.sum(),np.mean(short*shortage+extra*excess)]
    for label,s in [('Yuvarlanmış ortalama',mean),('Maliyet dengesi P75',stock),('Yüksek hizmet P95',high)]:
        rows.append([label,s,*measure(history,s),*measure(actual,s)])
    detail=pd.DataFrame(rows,columns=['Politika','Stok · adet','Geçmiş tam karşılama','Geçmiş birim doluluk','Geçmiş kayıp',
                                    'Final tam karşılama','Final birim doluluk','Final kayıp'])
    grid=np.arange(55,165)
    loss=np.array([measure(history,s)[2] for s in grid])
    assert np.isclose(measure(history,stock)[2],loss.min())
    fig,ax=plt.subplots(figsize=(8.7,4.3),layout='constrained')
    for x,color,label in [(history,BLUE,'Geçmiş'),(actual,ORANGE,'Final')]:
        xs=np.sort(x)
        ax.step(xs,np.arange(1,len(xs)+1)/len(xs),where='post',color=color,label=label)
    ax.axvline(stock,color=GREEN,ls='--',label=f'Donmuş P75: {stock} adet')
    ax.set(xlabel='Tedarik süresi boyunca talep · adet',ylabel='Talebin bu değeri aşmama payı',title='Aynı stok düzeyi, değişen talep')
    ax.legend()
    fig2,ax2=plt.subplots(figsize=(8.7,3.7),layout='constrained')
    ax2.plot(grid,loss,color=BLUE,label='Geçmiş kayıp')
    ax2.plot(grid,[measure(actual,s)[2] for s in grid],color=ORANGE,label='Final kayıp, yalnız değerlendirme')
    ax2.axvline(stock,color=GREEN,ls='--',label='Geçmişten seçilen miktar')
    ax2.set(xlabel='Elde hazır stok · adet',ylabel='Döngü başına kayıp puanı',title='Eksik ve fazla stok maliyetinin dengesi')
    ax2.legend(fontsize=8)
    m=rows[1]
    raw=pd.DataFrame({'Tedarik döngüsü':np.arange(1,241),'Kesit':np.repeat(['Geçmiş','Final'],[180,60]),'Talep · adet':np.r_[history,actual]})
    return dict(metrics={'Eksik / fazla puan':'9 / 3','Geçmiş maliyet kantili':'P75','Donmuş stok · adet':stock,
                         'Final tam karşılama · %':100*m[5],'Final birim doluluk · %':100*m[6],'Final ortalama kayıp':m[7]},
        tables=[table(detail,'Üç önceden belirlenmiş stok politikasının kıyası')],
        figures=[('Yatay eksende stok miktarını bul. Eğri yüksekliği, tüm döngü talebinin karşılanma payını verir.',fig),
                 ('Politika geçmişte seçilir. Final kayıp eğrisi sonucu açıklamak içindir, aynı finalden yeni başarı seçilmez.',fig2)],
        frames={'tedarik_dongusu':raw,'stok_politikalari':detail},
        steps=['Bir satır tedarik süresince oluşan talebi gösterir. Fazla birime 3, eksik birime 9 kayıp puanı ata.',
               'Tek dönem doğrusal kayıp modelinde hedef kantil 9/(9+3)=0,75. İlk 180 döngünün ampirik P75 değerini dondur.',
               'Son 60 döngüde tam karşılama payı, karşılanan birim payı ve kaybı ayrı raporla. Aynı stok değişen dağılımda farklı sonuç verir.'],
        decision='Geçmişten seçilmiş miktar ani talep artışında güvenilir hizmet sağlamıyor. Satış ve tedarik ekipleriyle artışın kaynağını doğrula, yeni dönem için önceden belirlenen yeniden hesaplama sürecini başlat.' if scenario=='surge' else 'Maliyet ve hizmet hedefleri farklı. P75 maliyet puanına, P95 tam karşılama hedeflerine aday olabilir. Fazla stok riskini ve kapasite kısıtını kararla birlikte değerlendir.',
        limit='Tek dönem, sabit eksik/fazla puanı, bir ürün ve bağımsız döngüler varsayılır. Teslim süresi belirsizliği talep penceresine dahil edilmelidir. Bu çözüm çok ürünlü sipariş politikası veya sürekli stok optimizasyonu değildir.',
        diagnostics={'stock':stock,'fractile':q,'history_n':180,'test_n':60,'test_fill':m[6],'test_cycle':m[5],'test_loss':m[7]},
        focus=[['Geçmiş','180 döngü','Miktarı burada seç'],['Maliyet dengesi',f'P75 → {stock} adet','9 eksik / 3 fazla puan'],['Final',f'%{m[5]*100:.1f} tam karşılama','60 ayrı döngüde değerlendir']])
