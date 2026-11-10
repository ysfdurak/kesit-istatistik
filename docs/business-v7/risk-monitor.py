import numpy as np
import pandas as pd
from scipy import stats
from scipy.special import expit
import matplotlib.pyplot as plt

BLUE, ORANGE, GREEN, GRAY = '#2457ad', '#ac452c', '#197254', '#64748b'
plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.grid': True, 'axes.axisbelow': True, 'grid.alpha': .19})

def table(frame, title):
    return dict(title=title, columns=frame.columns.tolist(),
                rows=frame.astype(object).where(frame.notna(), None).values.tolist())

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


def print_result(result):
    for name, value in result['metrics'].items():
        print(f"{name}: {value}")
    print()
    for t in result['tables']:
        print(t['title'])
        print(pd.DataFrame(t['rows'], columns=t['columns']).to_string(index=False))
        print()
    print('Karar:', result['decision'])
    print('Koşullar:', result['limit'])

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Gecikme modeli canlıda hâlâ aynı riski mi ölçüyor?')
    parser.add_argument('--scenario', choices=['default', 'shift'], default='default')
    args = parser.parse_args()
    result = monitoring(args.scenario)
    print_result(result)
    plt.show()
