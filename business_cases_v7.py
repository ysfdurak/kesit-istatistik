"""V7 vakalarını yürütür ve tarayıcı, CSV ve yerel Python çıktılarını oluşturur."""
from pathlib import Path
import base64
import inspect
import json
import zipfile
import os

os.environ.setdefault('MPLBACKEND', 'Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from business_methods_v7 import table
from business_briefs_v7 import CASES

ROOT = Path(__file__).resolve().parent
DIST = ROOT / 'docs'
OUT = DIST / 'business-v7'
OUT.mkdir(exist_ok=True)
PREFIX = 'business-v7/'
SETUP = '''import numpy as np
import pandas as pd
from scipy import stats
from scipy.special import expit
import matplotlib.pyplot as plt

BLUE, ORANGE, GREEN, GRAY = '#2457ad', '#ac452c', '#197254', '#64748b'
plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.grid': True, 'axes.axisbelow': True, 'grid.alpha': .19})
'''
CALL = '''
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
'''
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,
                     'axes.grid':True,'axes.axisbelow':True,'grid.alpha':.19})

def exercise(key, r):
    d = r['diagnostics']
    if key == 'sla-mix':
        rows = r['frames']['kpi_sayimlari']
        a,b = rows.Zamanında.iloc[2:]
        return dict(prompt=f'Sonraki dönemde zamanında teslimler {a}/300 standart ve {b}/700 karmaşık. Eski ağırlıklar %90 ve %10. Bilinmeyenleri zamanında saymadan, sabit karma oranı önceki %96,2’ye göre kaç yüzde puan değişti?',
                    answer=d['diff_pp'][0], unit='yüzde puan', why='100 × (0,90 × standart oranı + 0,10 × karmaşık oranı) − 96,2.')
    if key == 'audit-sample':
        n=r['frames']['tabaka_ozeti']['Bulunan hata'].tolist()
        return dict(prompt=f'100’er adreste {n[0]}, {n[1]} ve {n[2]} kesin fark bulundu. Evren büyüklükleri 8.000, 3.000 ve 1.000 adres. Eksikleri fark saymadan ağırlıklı hata oranı yüzde kaç?',
                    answer=d['weighted_bounds'][0]*100,unit='%',why='Her tabakanın bulunan hata / 100 oranını tabakanın 12.000 adres içindeki payıyla çarp ve topla.')
    if key == 'experiment-guardrail':
        _,a,b,*_=d['rows'][1]
        return dict(prompt=f'A kolunda {a}, B kolunda {b} şikayet var. Her kolda 4.000 müşteri. B−A şikayet farkı kaç yüzde puan?',
                    answer=d['rows'][1][5],unit='yüzde puan',why='İki kolun oranını ayrı hesapla. (B/4.000 − A/4.000) × 100. Yaygınlaştırma için ayrıca üst aralık ucuna bak.')
    if key == 'capacity-fit':
        row=r['frames']['final_tahminler'].iloc[0]
        point=round(row.Tahmin,2)
        margin=round(d['prediction_half'],2)
        return dict(prompt=f'151. gün için model tahmini {point:.2f} adam-saat, tek günün aralık marjı {margin:.2f} adam-saat. Üst uç kaç adam-saat?',
                    answer=point+margin,unit='adam-saat',why='Nokta tahminine tek gözlem marjını ekle. Bu marj, günün kendi artık değişkenliğini içerir.')
    if key == 'wms-impact':
        a,b=[round(row[-1],3) for row in r['tables'][0]['rows']]
        return dict(prompt=f'Pilot depolarda değişim {a:+.3f} dk, kıyas depolarında {b:+.3f} dk. Pilot değişimi eksi kıyas değişimi kaç dakika?',
                    answer=a-b,unit='dakika',why='Pilot ve kıyas grubunda değişimi aynı yönde hesapla. Sonra pilot değişiminden kıyas değişimini çıkar.')
    if key == 'risk-monitor':
        raw=r['frames']['izleme_skorlari']
        count=int((raw.loc[raw.Pencere=='Yeni','Sabit risk skoru']>=.30).sum())
        return dict(prompt=f'Yeni dönemde {count} alarm var. 2.400 kaydın 1.800 etiketi olgun. Operasyonun toplam yeni alarm yükü yüzde kaç?',
                    answer=count/2400*100,unit='%',why='Alarm için sonuç etiketini beklemek gerekmez. Payda bütün 2.400 yeni kayıttır.')
    return dict(prompt='Eksik stok 9, fazla stok 3 kayıp puanı. Tek dönem maliyet dengesinin hedef kantili yüzde kaç?',
                answer=d['fractile']*100,unit='%',why='Eksik kaybı / (eksik + fazla kaybı) = 9 / 12. Kantil, karşılanan birim oranıyla aynı ölçü değildir.')

def serial(value):
    if isinstance(value,np.generic):
        return value.item()
    if isinstance(value,np.ndarray):
        return value.tolist()
    raise TypeError(type(value).__name__)

def write_notebook(path, cells, key):
    for i,c in enumerate(cells):
        c['id']=f'{key}-{i}'
    data=dict(nbformat=4,nbformat_minor=5,cells=cells,metadata={
        'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},
        'language_info':{'name':'python','version':'3.11'}})
    path.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')

def build():
    output={}
    for key, meta in CASES.items():
        fn=meta['function']
        src=SETUP+'\n'+inspect.getsource(table)+'\n'+inspect.getsource(fn)+'\n'+CALL
        # Her indirilebilir defterin dış yardımcı dosya olmadan çalıştığını denetle.
        scope={}
        exec(compile(src,f'{key}.py','exec'),scope)
        case={k:v for k,v in meta.items() if k!='function'}
        case.update(id=key,scenes={},script=f'{PREFIX}{key}.py',notebook=f'{PREFIX}{key}.ipynb',
                    requirements=f'{PREFIX}requirements.txt')
        cells=[{'cell_type':'markdown','metadata':{},'source':[
            f"# {case['title']}\n\n{case['story']}\n\nKarar: {case['decision']}\n\n"
            "Veriler sentetiktir. Her senaryo sabit tohumla aynı veriyi yeniden oluşturur. "
            "CSV dosyaları örnek çıktıdır. Bir CSV’yi değiştirmen bu defterin verisini otomatik değiştirmez.\n"
        ]},{'cell_type':'code','metadata':{},'source':src.splitlines(keepends=True),
             'execution_count':1,'outputs':[]}]
        for i,(scenario,label) in enumerate(meta['scenarios'],start=2):
            result=scope[fn.__name__](scenario)
            scene={k:result[k] for k in ['metrics','tables','steps','decision','limit','diagnostics','focus']}
            scene.update(id=scenario,label=label,datasets=[],plots=[],exercise=exercise(key,result))
            for name, df in result['frames'].items():
                filename=f'{key}_{scenario}_{name}.csv'
                df.to_csv(OUT/filename,index=False)
                scene['datasets'].append(dict(name=name.replace('_',' ').capitalize(),file=PREFIX+filename,
                                               rows=len(df),preview=table(df.head(8),'İlk 8 kayıt')))
            captured=[]
            for j,(caption,fig) in enumerate(result['figures'],start=1):
                filename=f'{key}_{scenario}_{j}.png'
                fig.savefig(OUT/filename,dpi=145,bbox_inches='tight',facecolor='white')
                scene['plots'].append(dict(file=PREFIX+filename,caption=caption))
                captured.append(dict(output_type='display_data',metadata={},data={
                    'image/png':base64.b64encode((OUT/filename).read_bytes()).decode()}))
                plt.close(fig)
            import contextlib
            import io
            buf=io.StringIO()
            with contextlib.redirect_stdout(buf):
                scope['print_result'](result)
            cells.append({'cell_type':'markdown','metadata':{},'source':[f'## {label}\n\n{scene["exercise"]["prompt"]}\n']})
            cells.append({'cell_type':'code','metadata':{},'execution_count':i,'source':[
                f"result = {fn.__name__}({scenario!r})\n","print_result(result)\n","plt.show()\n"],
                'outputs':[dict(output_type='stream',name='stdout',text=buf.getvalue().splitlines(keepends=True)),*captured]})
            case['scenes'][scenario]=scene
            print('PASS',key,scenario,flush=True)
        cells.append({'cell_type':'markdown','metadata':{},'source':[
            f"## Karar notu\n\n{case['task']}\n\n"+'\n'.join('- '+x for x in case['rubric'])]})
        write_notebook(OUT/f'{key}.ipynb',cells,key)
        (OUT/f'{key}.py').write_text(src+f"""
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description={case['title']!r})
    parser.add_argument('--scenario', choices={list(case['scenes'])!r}, default='default')
    args = parser.parse_args()
    result = {fn.__name__}(args.scenario)
    print_result(result)
    plt.show()
""",encoding='utf-8')
        output[key]=case
    js=json.dumps(output,ensure_ascii=False,default=serial,allow_nan=False)
    (DIST/'business-content-v7.js').write_text('Object.assign(window.BUSINESS_DATA,'+js+');',encoding='utf-8')
    (OUT/'requirements.txt').write_text('numpy==2.3.5\nscipy==1.17.0\npandas==2.2.3\nmatplotlib==3.10.8\n',encoding='utf-8')
    (OUT/'README.txt').write_text(
        'Kesit İstatistik V7 iş vakaları\nPython 3.11+ ile python -m pip install -r requirements.txt\n'
        'Her .py dosyası bağımsız çalışır. Örnek: python sla-mix.py --scenario unknown\n'
        'Jupyter defterleri önceden çalıştırılmış sonuçları ve grafikleri içerir.\n'
        'Veriler sentetiktir. CSV dosyaları aynı örneklerden üretilmiştir.\n',encoding='utf-8')
    with zipfile.ZipFile(OUT/'Kesit_Is_Vakalari_V7.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(OUT.iterdir()):
            if p.suffix in {'.csv','.py','.ipynb','.txt'}:
                z.write(p,p.name)
    print(f'Tamamlandı: {len(output)} yeni vaka, {sum(len(c["scenes"]) for c in output.values())} senaryo',flush=True)

if __name__=='__main__':
    build()
