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
    parser = argparse.ArgumentParser(description='Yarın kaç adam-saat kapasite ayırmalıyız?')
    parser.add_argument('--scenario', choices=['default', 'peak'], default='default')
    args = parser.parse_args()
    result = capacity(args.scenario)
    print_result(result)
    plt.show()
