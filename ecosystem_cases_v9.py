"""Kesit İstatistik V9 · Kesit veri setleriyle istatistik vakaları.

Kesit SQL, Kesit Power BI ve Kesit Python'da kullanılan ortak kurgusal veri
setlerinden 13 istatistik vakası üretir. Bütün sayılar bu betikle gerçek
CSV'lerden hesaplanır ve docs/ecosystem-data-v9.js dosyasına yazılır.

Kullanım:
    python ecosystem_cases_v9.py ../kesit-python/data

Gerekenler: pandas, numpy, scipy, statsmodels.
"""
import json
import re
import pathlib
import sys

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats

if len(sys.argv) < 2:
    sys.exit("Kullanım: python ecosystem_cases_v9.py <kesit-python/data klasörü>")
DATA = pathlib.Path(sys.argv[1])
OUT = pathlib.Path(__file__).resolve().parent / "docs" / "ecosystem-data-v9.js"
RAW = "https://raw.githubusercontent.com/ysfdurak/kesit-python/main/data/"
RNG = np.random.default_rng(20261110)


def r(x, d=3):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), d)


def wilson(k, n, z=1.959964):
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return c - h, c + h


def boot(fn, *arrays, b=4000):
    vals = []
    for _ in range(b):
        vals.append(fn(*[a[RNG.integers(0, len(a), len(a))] for a in arrays]))
    return np.percentile(vals, [2.5, 97.5])


def pct(x):
    return ("−" if x < 0 else "") + f"%{abs(x)*100:.1f}"


def csv(path, **kw):
    return pd.read_csv(DATA / path, **kw)


NICE = {"ulasim": "ulaşım", "akaryakit": "akaryakıt", "saglik": "sağlık", "e_ticaret": "e-ticaret", "egitim": "eğitim", "elektronik": "elektronik", "giyim": "giyim", "market": "market", "restoran": "restoran"}
NUM = re.compile(r"(?<![A-Za-z_])\d[\d,]*(?:\.\d+)?(?:e[-+]?\d+)?")


def trnum(text):
    """1,234.5 → 1.234,5 (Türkçe sayı yazımı)."""
    return NUM.sub(lambda m: m.group(0).translate(str.maketrans({",": ".", ".": ","})), str(text))


cases = []

# 1 ─ Anadolu Market A/B dönüşüm
ab = csv("anadolu_market/ab_test.csv")
g = ab.groupby("variant").converted.agg(["size", "sum", "mean"])
nA, kA, pA = int(g.loc["A", "size"]), int(g.loc["A", "sum"]), g.loc["A", "mean"]
nB, kB, pB = int(g.loc["B", "size"]), int(g.loc["B", "sum"]), g.loc["B", "mean"]
pp = (kA + kB) / (nA + nB)
z = (pB - pA) / np.sqrt(pp * (1 - pp) * (1 / nA + 1 / nB))
se = np.sqrt(pA * (1 - pA) / nA + pB * (1 - pB) / nB)
lo, hi = (pB - pA) - 1.959964 * se, (pB - pA) + 1.959964 * se
cases.append(dict(
    id="am-ab-donusum", dataset="Anadolu Market", app="sql", tables=["ab_test"],
    title="Yeni tasarım dönüşümü artırdı mı?",
    question="A (kontrol) ve B (yeni tasarım) gruplarında satın alma oranı farklı mı, fark ne kadar?",
    unit="Kullanıcı (her satır bir kullanıcı; her kullanıcı tek gruba atanmış).",
    predict=dict(q="B'nin oranı A'dan yaklaşık 3,8 puan yüksek. Her grupta yaklaşık 1.000 kullanıcı var. Fark rastlantı olabilir mi?",
                 options=["Evet, 1.000 kişi azdır; 3,8 puan kesinlikle gürültüdür", "Standart hatayla karşılaştırmadan karar verilemez; burada SE ≈ 1,5 puan, fark yaklaşık 2,5 SE", "Hayır, her fark gerçektir"], correct=1,
                 why="Farkın büyüklüğü tek başına yetmez. Önemli olan farkın standart hataya oranıdır. 2,5 SE'lik fark, gerçek etki sıfırken nadir görülür."),
    method="İki bağımsız oran için z testi ve Wald güven aralığı",
    why="Sonuç 0/1, gruplar rastgele atanmış ve bağımsız; her grupta başarı ve başarısızlık sayısı 10'dan çok büyük.",
    sql="SELECT variant,\n       COUNT(*)            AS n,\n       SUM(converted)      AS donusen,\n       AVG(converted*1.0)  AS oran\nFROM ab_test\nGROUP BY variant;",
    python=f"import pandas as pd\nfrom statsmodels.stats.proportion import proportions_ztest, confint_proportions_2indep\n\nab = pd.read_csv('{RAW}anadolu_market/ab_test.csv')\ng = ab.groupby('variant').converted.agg(['sum', 'size'])\nz, p = proportions_ztest(g['sum'][['B', 'A']], g['size'][['B', 'A']])\nlo, hi = confint_proportions_2indep(g.loc['B','sum'], g.loc['B','size'],\n                                    g.loc['A','sum'], g.loc['A','size'], method='wald')\nprint(z, p, lo, hi)",
    dax="Dönüşüm Oranı =\nDIVIDE ( SUM ( ab_test[converted] ), COUNTROWS ( ab_test ) )\n\nFark (B − A) =\nCALCULATE ( [Dönüşüm Oranı], ab_test[variant] = \"B\" )\n  - CALCULATE ( [Dönüşüm Oranı], ab_test[variant] = \"A\" )",
    results=[["A dönüşüm", f"{kA}/{nA} = %{pA*100:.1f}"], ["B dönüşüm", f"{kB}/{nB} = %{pB*100:.1f}"],
             ["Fark (B − A)", f"{(pB-pA)*100:.2f} puan"], ["%95 aralık", f"[{lo*100:.2f}; {hi*100:.2f}] puan"],
             ["z / iki yönlü p", f"{z:.2f} / {2*stats.norm.sf(abs(z)):.4f}"], ["Göreli artış", f"%{(pB/pA-1)*100:.0f}"]],
    chart=dict(kind="bars", unit="%", labels=["A", "B"], values=[r(pA * 100, 2), r(pB * 100, 2)],
               lo=[r(wilson(kA, nA)[0] * 100, 2), r(wilson(kB, nB)[0] * 100, 2)], hi=[r(wilson(kA, nA)[1] * 100, 2), r(wilson(kB, nB)[1] * 100, 2)],
               caption="Dönüşüm oranı ve Wilson %95 aralığı"),
    read="Fark sıfırı dışlayan bir aralıkla pozitif. Ancak aralığın alt ucu 1 puanın altına yakın: etki küçük de olabilir. Karar, alt uçtaki etkinin bile tasarım maliyetini karşılayıp karşılamadığına göre verilir.",
    limits="Deney süresi, yenilik etkisi ve kullanıcı başına birden çok ziyaret bu tabloda yok. Tek metrik bakıldı; ikinci bir metrik eklenirse çoklu karşılaştırma planlanmalıdır.",
    lessons=["s33", "s19", "s21", "s23"]))

# 2 ─ Anadolu Market A/B gelir
a = ab[ab.variant == "A"].revenue.to_numpy()
b = ab[ab.variant == "B"].revenue.to_numpy()
wt = stats.ttest_ind(b, a, equal_var=False)
bci = boot(lambda x, y: x.mean() - y.mean(), b, a)
zeroA, zeroB = (a == 0).mean(), (b == 0).mean()
ca, cb = a[a > 0], b[b > 0]
wc = stats.ttest_ind(cb, ca, equal_var=False)
cases.append(dict(
    id="am-ab-gelir", dataset="Anadolu Market", app="sql", tables=["ab_test"],
    title="Kullanıcı başına gelir: sıfırlarla dolu bir ortalama",
    question="B tasarımı kullanıcı başına geliri artırdı mı? Artış dönüşümden mi, sepet tutarından mı geliyor?",
    unit="Kullanıcı. Gelir satın almayanlarda 0'dır.",
    predict=dict(q=f"Kullanıcıların yaklaşık %{zeroA*100:.0f}'inin geliri 0. Ortalama gelir farkını test etmek için ne yaparsın?",
                 options=["Sıfırları atarım, yalnızca alıcıları karşılaştırırım", "Kullanıcı başına ortalamayı Welch ve bootstrap ile karşılaştırır, sonra farkı dönüşüm ve sepet bileşenlerine ayırırım", "Medyanları karşılaştırırım; ikisi de 0 olduğu için fark yoktur"], correct=1,
                 why="Sıfırları atmak soruyu değiştirir (alıcı başına gelir olur). Medyan iki grupta da 0'dır ve etkiyi göstermez. Ortalama doğru hedeftir; dağılım çarpık olduğu için bootstrap ile çapraz kontrol edilir."),
    method="Welch t testi + yüzdelik bootstrap (4.000 tekrar), ardından bileşen ayrıştırma",
    why="Gelir sıfır yığılmalı ve sağa çarpık. Örneklem büyük olduğu için ortalama farkına Welch yaklaşımı çalışır; bootstrap bu varsayımı kontrol eder.",
    sql="SELECT variant,\n       AVG(revenue)                         AS kullanici_basi_gelir,\n       AVG(CASE WHEN converted = 1 THEN revenue END) AS alici_basi_gelir,\n       AVG(converted * 1.0)                 AS donusum\nFROM ab_test\nGROUP BY variant;",
    python=f"import numpy as np, pandas as pd\nfrom scipy import stats\n\nab = pd.read_csv('{RAW}anadolu_market/ab_test.csv')\na = ab.query(\"variant=='A'\").revenue.to_numpy()\nb = ab.query(\"variant=='B'\").revenue.to_numpy()\nprint(stats.ttest_ind(b, a, equal_var=False))\nrng = np.random.default_rng(1)\nfark = [rng.choice(b, len(b)).mean() - rng.choice(a, len(a)).mean() for _ in range(4000)]\nprint(np.percentile(fark, [2.5, 97.5]))",
    dax="Kullanıcı Başı Gelir =\nDIVIDE ( SUM ( ab_test[revenue] ), COUNTROWS ( ab_test ) )\n\nAlıcı Başı Gelir =\nCALCULATE ( AVERAGE ( ab_test[revenue] ), ab_test[converted] = 1 )",
    results=[["A kullanıcı başı", f"{a.mean():.2f} TL"], ["B kullanıcı başı", f"{b.mean():.2f} TL"],
             ["Fark", f"{b.mean()-a.mean():.2f} TL"], ["Welch %95 aralık", f"[{wt.confidence_interval().low:.2f}; {wt.confidence_interval().high:.2f}] TL"],
             ["Bootstrap %95 aralık", f"[{bci[0]:.2f}; {bci[1]:.2f}] TL"], ["Welch p", f"{wt.pvalue:.4f}"],
             ["Alıcı başı gelir A / B", f"{ca.mean():.0f} / {cb.mean():.0f} TL (p = {wc.pvalue:.3f})"]],
    chart=dict(kind="bars", unit="TL", labels=["A kullanıcı", "B kullanıcı", "A alıcı", "B alıcı"],
               values=[r(a.mean(), 1), r(b.mean(), 1), r(ca.mean(), 1), r(cb.mean(), 1)], caption="Kullanıcı başı ve alıcı başı ortalama gelir"),
    read="Kullanıcı başı gelir artışının çoğu daha fazla kişinin satın almasından gelir. Alıcı başı tutardaki fark daha belirsizdir. İki aralık yöntemi birbirine yakın: büyük örneklemde çarpıklık Welch'i bozmamış.",
    limits="Alıcı başı karşılaştırma randomizasyonu korumaz: B daha farklı kişileri alıcıya dönüştürmüş olabilir. Bu yüzden bileşenler nedensel değil, betimsel ayrıştırmadır.",
    lessons=["s26", "s43", "s05", "s33"]))

# 3 ─ Lezzet Kurye teslim süresi dağılımı
o = csv("lezzet_kurye/lk_orders.csv", parse_dates=["placed_at", "picked_at", "delivered_at"])
t = o[o.status == "teslim"].copy()
t["dk"] = (t.delivered_at - t.placed_at).dt.total_seconds() / 60
d = t.dk
q1, q3 = d.quantile([.25, .75])
fence = q3 + 1.5 * (q3 - q1)
hist, edges = np.histogram(d, bins=np.arange(10, 95, 5))
cases.append(dict(
    id="lk-teslim-dagilim", dataset="Lezzet Kurye", app="python", tables=["lk_orders"],
    title="Teslim süresi: hangi sayıyı söz verirsin?",
    question="Müşteriye uygulamada hangi teslim süresini göstermelisin? Ortalama mı, medyan mı, yüksek bir yüzdelik mi?",
    unit="Teslim edilmiş sipariş (iptal ve iadeler süre taşımaz).",
    predict=dict(q="Dağılım hafif sağa çarpık. 'Siparişlerin %90'ı bu sürede gelir' sözü için hangi özet gerekir?",
                 options=["Ortalama", "Medyan", "90. yüzdelik"], correct=2,
                 why="Söz bir olasılık içerir. Ortalama ve medyan merkezi anlatır. Verilecek süre sözü, dağılımın kuyruğunu gösteren yüzdelikten okunur."),
    method="Betimsel özet, yüzdelikler, IQR ve çarpıklık",
    why="Karar sorusu bir hizmet sözü olduğu için merkez değil, dağılımın üst kısmı gerekir.",
    sql="SELECT COUNT(*) AS n,\n       AVG((julianday(delivered_at) - julianday(placed_at)) * 1440) AS ort_dk\nFROM lk_orders\nWHERE status = 'teslim';\n-- Yüzdelik için: SQL Server/PostgreSQL'de PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY ...)",
    python=f"import pandas as pd\n\no = pd.read_csv('{RAW}lezzet_kurye/lk_orders.csv', parse_dates=['placed_at','delivered_at'])\nt = o[o.status == 'teslim']\ndk = (t.delivered_at - t.placed_at).dt.total_seconds() / 60\nprint(dk.describe(percentiles=[.5, .9, .95]))\nprint('çarpıklık', dk.skew())",
    dax="Teslim Dk = \n  DATEDIFF ( lk_orders[placed_at], lk_orders[delivered_at], MINUTE )   -- hesaplanmış sütun\n\nP90 Teslim =\nCALCULATE ( PERCENTILEX.INC ( lk_orders, lk_orders[Teslim Dk], 0.9 ),\n            lk_orders[status] = \"teslim\" )",
    results=[["Teslim edilen", f"{len(d):,}"], ["Ortalama / medyan", f"{d.mean():.1f} / {d.median():.1f} dk"],
             ["Standart sapma", f"{d.std():.1f} dk"], ["90. / 95. yüzdelik", f"{d.quantile(.9):.1f} / {d.quantile(.95):.1f} dk"],
             ["IQR", f"{q1:.1f} – {q3:.1f} dk"], ["Üst çit (Q3+1,5·IQR)", f"{fence:.1f} dk · üstünde kalan %{(d>fence).mean()*100:.1f}"],
             ["Çarpıklık", f"{d.skew():.2f}"]],
    chart=dict(kind="hist", unit="sipariş", labels=[f"{int(e)}" for e in edges[:-1]], values=[int(v) for v in hist],
               marks=[["medyan", r(d.median(), 1)], ["P90", r(d.quantile(.9), 1)]], step=5, start=10, caption="5 dakikalık aralıklarla teslim süresi"),
    read=f"Medyan {d.median():.0f} dk; ama her dört siparişten biri {q3:.0f} dakikayı, her on siparişten biri {d.quantile(.9):.0f} dakikayı aşar. Uygulamada '30–40 dk' yazmak her dört müşteriden birine tutulmayan bir söz verir.",
    limits="Süreler restoran, mesafe ve saat karışımıdır. Tek bir genel yüzdelik, uzak ilçeler için iyimser kalır; söz koşullu yüzdeliklerle (restoran × saat) verilmelidir.",
    lessons=["s05", "s07", "s06", "s04"]))

# 4 ─ Lezzet Kurye puan eşiği
c = csv("lezzet_kurye/lk_couriers.csv")
rt = csv("lezzet_kurye/lk_ratings.csv")
tr = t.merge(rt, on="order_id")
sp = stats.spearmanr(tr.dk, tr.courier_score)
pe = stats.pearsonr(tr.dk, tr.courier_score)
tr["kova"] = pd.cut(tr.dk, [0, 30, 40, 50, 60, 999], labels=["≤30", "30–40", "40–50", "50–60", ">60"])
bk = tr.groupby("kova", observed=True).courier_score.agg(["size", "mean", lambda s: (s <= 2).mean()])
bk.columns = ["n", "ort", "dusuk"]
cases.append(dict(
    id="lk-puan-esik", dataset="Lezzet Kurye", app="python", tables=["lk_orders", "lk_ratings"],
    title="Gecikme puanı nasıl düşürüyor: doğru mu, eşik mi?",
    question="Teslim süresi uzadıkça kurye puanı düzenli mi düşüyor, yoksa belli bir süreden sonra mı çöküyor?",
    unit="Puanlanmış teslim siparişi. Puan vermeyen siparişler dışarıda kalır.",
    predict=dict(q=f"Spearman korelasyonu {sp.statistic:.2f}. Bu, ilişkinin zayıf olduğu anlamına mı gelir?",
                 options=["Evet; korelasyon küçükse etki de küçüktür", "Hayır; korelasyon tek sayıya indirger. Eşik biçimindeki güçlü bir etki düşük korelasyon üretebilir", "Korelasyon negatif olduğu için ilişki ters yöndedir ve önemsizdir"], correct=1,
                 why="Korelasyon tüm aralıktaki ortalama tekdüze eğilimi ölçer. Puan 50 dakikaya kadar neredeyse sabitse ve sonra düşüyorsa, tek katsayı bunu gizler. Kovalara bölünmüş grafik zorunludur."),
    method="Spearman ve Pearson korelasyonu + süre kovalarına göre puan ortalaması",
    why="Puan 1–5 sıralı ve sınırlı; ilişkinin biçimini görmek için kovalı özet gerekir.",
    sql="SELECT CASE WHEN dk <= 30 THEN '≤30' WHEN dk <= 40 THEN '30–40'\n            WHEN dk <= 50 THEN '40–50' WHEN dk <= 60 THEN '50–60' ELSE '>60' END AS kova,\n       COUNT(*) AS n, AVG(courier_score) AS ort_puan,\n       AVG(CASE WHEN courier_score <= 2 THEN 1.0 ELSE 0 END) AS dusuk_oran\nFROM (SELECT o.order_id, (julianday(delivered_at)-julianday(placed_at))*1440 AS dk, r.courier_score\n      FROM lk_orders o JOIN lk_ratings r ON r.order_id = o.order_id\n      WHERE o.status = 'teslim') x\nGROUP BY kova;",
    python=f"import pandas as pd\nfrom scipy import stats\n\no = pd.read_csv('{RAW}lezzet_kurye/lk_orders.csv', parse_dates=['placed_at','delivered_at'])\nr = pd.read_csv('{RAW}lezzet_kurye/lk_ratings.csv')\nt = o[o.status=='teslim'].merge(r, on='order_id')\nt['dk'] = (t.delivered_at - t.placed_at).dt.total_seconds()/60\nprint(stats.spearmanr(t.dk, t.courier_score))\nt['kova'] = pd.cut(t.dk, [0,30,40,50,60,999])\nprint(t.groupby('kova').courier_score.agg(['size','mean']))",
    dax="Ort Kurye Puanı = AVERAGE ( lk_ratings[courier_score] )\n\nDüşük Puan Oranı =\nDIVIDE ( CALCULATE ( COUNTROWS ( lk_ratings ), lk_ratings[courier_score] <= 2 ),\n         COUNTROWS ( lk_ratings ) )\n-- Süre kovasını hesaplanmış sütun olarak ekleyip eksene koy.",
    results=[["Puanlı sipariş", f"{len(tr):,}"], ["Spearman ρ", f"{sp.statistic:.3f} (p < 0.001)"], ["Pearson r", f"{pe.statistic:.3f}"]]
    + [[f"{k} dk", f"n={int(v.n)} · ort {v.ort:.2f} · ≤2 puan %{v.dusuk*100:.1f}"] for k, v in bk.iterrows()],
    chart=dict(kind="bars", unit="puan", labels=[str(k) for k in bk.index], values=[r(v, 2) for v in bk.ort], min=1, max=5, caption="Süre kovasına göre ortalama kurye puanı"),
    read="50 dakikaya kadar puan neredeyse sabit; sonra belirgin bir kırılma var. İşletme kararı 'ortalama süreyi biraz kısalt' değil, '50 dakikayı aşan siparişleri önle' olmalıdır.",
    limits="Puan vermek gönüllü: gecikmede kızgın müşterinin puan verme olasılığı farklı olabilir (seçilim). Uzun teslimler uzak adreslerde toplandığı için mesafe karıştırıcıdır.",
    lessons=["s29", "s04", "s36", "s72"]))

# 5 ─ Lezzet Kurye araç türü
tv = t.merge(c[["courier_id", "vehicle"]], on="courier_id")
grp = [tv[tv.vehicle == v].dk.to_numpy() for v in ["motosiklet", "araba", "bisiklet"]]
kw = stats.kruskal(*grp)
an = stats.f_oneway(*grp)
sizes = [len(x) for x in grp]
cases.append(dict(
    id="lk-arac", dataset="Lezzet Kurye", app="sql", tables=["lk_orders", "lk_couriers"],
    title="Bisikletli kuryeler gerçekten yavaş mı?",
    question="Teslim süresi kuryenin aracına göre değişiyor mu? Bu fark aracın kendisinden mi kaynaklanıyor?",
    unit="Teslim siparişi; ama siparişler kurye içinde kümelenir (60 kurye).",
    predict=dict(q=f"Bisikletli siparişler ortalama {grp[2].mean()-grp[0].mean():.0f} dk daha uzun. 'Bisikleti kaldıralım' demek için en büyük eksik nedir?",
                 options=["Örneklem çok küçük", "Bisikletlilerin hangi bölgelere ve mesafelere atandığı bilinmiyor; karıştırıcı kontrol edilmedi", "Ki-kare testi yapılmadı"], correct=1,
                 why="Fark istatistiksel olarak güçlü olabilir; ama atama rastgele değil. Bisikletliler kısa mesafeli merkez bölgelere ya da yoğun saatlere verilmiş olabilir. Bu tablo nedensellik göstermez."),
    method="Kruskal–Wallis ve tek yönlü ANOVA (çapraz kontrol)",
    why="Üç bağımsız grup, çarpık dağılım ve çok farklı grup büyüklükleri. Sıralama testi ortalamaya duyarlı ANOVA'yı kontrol eder.",
    sql="SELECT c.vehicle, COUNT(*) AS n,\n       AVG((julianday(o.delivered_at)-julianday(o.placed_at))*1440) AS ort_dk,\n       COUNT(DISTINCT c.courier_id) AS kurye\nFROM lk_orders o JOIN lk_couriers c ON c.courier_id = o.courier_id\nWHERE o.status = 'teslim'\nGROUP BY c.vehicle;",
    python=f"import pandas as pd\nfrom scipy import stats\n\no = pd.read_csv('{RAW}lezzet_kurye/lk_orders.csv', parse_dates=['placed_at','delivered_at'])\nc = pd.read_csv('{RAW}lezzet_kurye/lk_couriers.csv')\nt = o[o.status=='teslim'].merge(c, on='courier_id')\nt['dk'] = (t.delivered_at - t.placed_at).dt.total_seconds()/60\nprint(stats.kruskal(*[g.dk for _, g in t.groupby('vehicle')]))",
    dax="Ort Teslim Dk = AVERAGE ( lk_orders[Teslim Dk] )\n-- lk_couriers[vehicle] eksende, lk_couriers → lk_orders ilişkisiyle",
    results=[[v, f"n={n:,} · ort {x.mean():.1f} · medyan {np.median(x):.1f} dk"] for v, n, x in zip(["Motosiklet", "Araba", "Bisiklet"], sizes, grp)]
    + [["Kruskal–Wallis H / p", f"{kw.statistic:.1f} / {kw.pvalue:.1e}"], ["ANOVA F / p", f"{an.statistic:.1f} / {an.pvalue:.1e}"],
       ["Kurye sayısı", ", ".join(f"{v} {n}" for v, n in c.vehicle.value_counts().items())]],
    chart=dict(kind="bars", unit="dk", labels=["Motosiklet", "Araba", "Bisiklet"], values=[r(np.median(x), 1) for x in grp], caption="Araç türüne göre medyan teslim süresi"),
    read=f"Fark var ve rastlantı ile açıklanamaz. Ancak gözlem birimi sipariş, atama birimi kurye: bisiklet grubu yalnızca {int((c.vehicle=='bisiklet').sum())} kuryeden oluşuyor. Bu iki kişinin bireysel performansı ile aracın etkisi bu veride ayrılamaz.",
    limits="Mesafe, restoran ve saat kontrol edilmedi. Etkin örneklem kurye sayısına yakındır; sipariş sayısı p değerini olduğundan küçük gösterebilir (karma model gerekir).",
    lessons=["s27", "s66", "s31", "s71"]))

# 6 ─ Kanat Havayolları rötar kuyruğu
f = csv("kanat_havayollari/hv_flights.csv", parse_dates=["sched_dep", "actual_dep"])
fl = f[f.status != "cancelled"].copy()
fl["d"] = (fl.actual_dep - fl.sched_dep).dt.total_seconds() / 60
n_f, k15 = len(fl), int((fl.d >= 15).sum())
w_lo, w_hi = wilson(n_f - k15, n_f)
hb = [-5, 0, 5, 15, 30, 60, 120, 300]
hh, _ = np.histogram(fl.d, bins=hb)
cases.append(dict(
    id="hv-rotar-kuyruk", dataset="Kanat Havayolları", app="powerbi", tables=["hv_flights"],
    title="Zamanında kalkış oranı ve uzun rötar kuyruğu",
    question="Uçuşların ne kadarı zamanında kalkıyor (15 dk kuralı)? Ortalama rötar bu soruya cevap verir mi?",
    unit="Kalkış yapan uçuş (iptaller süresiz olduğu için ayrı raporlanır).",
    predict=dict(q=f"Ortalama rötar {fl.d.mean():.0f} dk, medyan {fl.d.median():.0f} dk. Bu fark ne söyler?",
                 options=["Veri hatalıdır", "Az sayıdaki çok uzun rötar ortalamayı yukarı çeker; tipik uçuş ortalamadan çok daha az gecikir", "Uçuşların yarısı 25 dk geç kalkar"], correct=1,
                 why="Ortalama, kuyruktaki 2–4 saatlik rötarlara duyarlıdır. Yolcuya tipik deneyimi medyan ve oran anlatır; maliyet ve tazminat için kuyruk ayrıca izlenir."),
    method="Oran için Wilson %95 aralığı + dağılım özeti",
    why="Zamanında kalkış 0/1 bir olaydır; oran ve belirsizliği raporlanır. Uzun kuyruk nedeniyle ortalama tek başına yanıltıcıdır.",
    sql="SELECT COUNT(*) AS kalkan,\n       AVG(CASE WHEN (julianday(actual_dep)-julianday(sched_dep))*1440 < 15 THEN 1.0 ELSE 0 END) AS zamaninda\nFROM hv_flights\nWHERE status <> 'cancelled';",
    python=f"import pandas as pd\nfrom statsmodels.stats.proportion import proportion_confint\n\nf = pd.read_csv('{RAW}kanat_havayollari/hv_flights.csv', parse_dates=['sched_dep','actual_dep'])\nf = f[f.status != 'cancelled']\nd = (f.actual_dep - f.sched_dep).dt.total_seconds()/60\nk = (d < 15).sum()\nprint(k/len(d), proportion_confint(k, len(d), method='wilson'))\nprint(d.describe(percentiles=[.5,.9,.99]))",
    dax="Kalkış Rötarı Dk = DATEDIFF ( hv_flights[sched_dep], hv_flights[actual_dep], MINUTE )\n\nZamanında Kalkış % =\nDIVIDE ( CALCULATE ( COUNTROWS ( hv_flights ), hv_flights[Kalkış Rötarı Dk] < 15,\n                     hv_flights[status] <> \"cancelled\" ),\n         CALCULATE ( COUNTROWS ( hv_flights ), hv_flights[status] <> \"cancelled\" ) )",
    results=[["Kalkan uçuş", f"{n_f:,}"], ["Zamanında (<15 dk)", f"%{(1-k15/n_f)*100:.1f} · Wilson [%{w_lo*100:.1f}; %{w_hi*100:.1f}]"],
             ["Ortalama / medyan rötar", f"{fl.d.mean():.1f} / {fl.d.median():.0f} dk"], ["90. / 99. yüzdelik", f"{fl.d.quantile(.9):.0f} / {fl.d.quantile(.99):.0f} dk"],
             ["İptal", f"{int((f.status=='cancelled').sum())} uçuş"], ["60 dk üzeri rötar", f"%{(fl.d>=60).mean()*100:.1f}"]],
    chart=dict(kind="bars", unit="uçuş", labels=["−5–0", "0–5", "5–15", "15–30", "30–60", "60–120", "120+"], values=[int(v) for v in hh], caption="Kalkış rötarı dağılımı (dakika aralıkları)"),
    read="Tipik uçuş birkaç dakika gecikir; ama her on uçuştan biri bir saati aşar. Zamanında kalkış KPI'ı ile ortalama rötar farklı soruları cevaplar ve ikisi birlikte raporlanmalıdır.",
    limits="Eylül–Aralık dönemi; mevsim etkisi tek dönemle ayrılamaz. İptaller orana dahil edilmedi; iptali 'sonsuz rötar' gibi raporlayan tanımlar farklı sonuç verir.",
    lessons=["s19", "s07", "s05", "s13"]))

# 7 ─ Kanat akşam yayılımı
fl["dilim"] = pd.cut(fl.sched_dep.dt.hour, [0, 9, 13, 17, 24], right=False, labels=["00–09", "09–13", "13–17", "17–24"])
tab = pd.crosstab(fl.dilim, fl.d >= 15)
chi = stats.chi2_contingency(tab)
dl = csv("kanat_havayollari/hv_delays.csv")
share = dl.groupby("reason").minutes.sum() / dl.minutes.sum()
rate = (fl.groupby("dilim", observed=True).d.apply(lambda s: (s >= 15).mean()))
dlj = dl.merge(f[["flight_id", "sched_dep"]], on="flight_id")
dlj["aksam"] = dlj.sched_dep.dt.hour >= 17
shr = dlj.groupby("aksam").apply(lambda g: g.groupby("reason").minutes.sum() / g.minutes.sum(), include_groups=False)
cv = np.sqrt(chi[0] / (tab.values.sum() * (min(tab.shape) - 1)))
cases.append(dict(
    id="hv-aksam", dataset="Kanat Havayolları", app="sql", tables=["hv_flights", "hv_delays"],
    title="Rötar gün içinde birikiyor mu?",
    question="Akşam uçuşlarında rötar oranı neden yükseliyor? Hava mı, uçak rotasyonu mu?",
    unit="Kalkış yapan uçuş; rötar nedenleri dakika üzerinden paylaştırılır.",
    predict=dict(q="Rötar oranı sabah %32, akşam %49. 'Sabahki gecikme uçak rotasyonuyla akşama taşınıyor' hipotezini nasıl sınarsın?",
                 options=["Akşam uçuşlarını azaltırım; oran düşerse hipotez doğrudur", "Neden kodlarını akşam ve gündüz için ayrı ayrı karşılaştırırım: rotasyon akşam fazlasını açıklıyorsa akşam 'geç gelen uçak' payı belirgin biçimde artmalı", "Ki-kare p değeri küçükse hipotez doğrulanmış olur"], correct=1,
                 why="p değeri yalnızca dilimler arasında fark olduğunu söyler, nedenini söylemez. Bir mekanizma iddiası, o mekanizmanın veride bırakması gereken izle sınanır."),
    method="Ki-kare bağımsızlık testi + Cramér V + neden payları",
    why="İki kategorik değişken (saat dilimi × rötar var/yok); etki büyüklüğü için Cramér V raporlanır.",
    sql="SELECT reason, SUM(minutes) AS dk,\n       ROUND(100.0 * SUM(minutes) / (SELECT SUM(minutes) FROM hv_delays), 1) AS pay\nFROM hv_delays\nGROUP BY reason\nORDER BY dk DESC;",
    python=f"import pandas as pd\nfrom scipy import stats\n\nf = pd.read_csv('{RAW}kanat_havayollari/hv_flights.csv', parse_dates=['sched_dep','actual_dep'])\nf = f[f.status != 'cancelled']\nf['rotar'] = (f.actual_dep - f.sched_dep).dt.total_seconds()/60 >= 15\nf['dilim'] = pd.cut(f.sched_dep.dt.hour, [0,9,13,17,24], right=False)\nprint(stats.chi2_contingency(pd.crosstab(f.dilim, f.rotar)))",
    dax="Rötar Dakika Payı =\nDIVIDE ( SUM ( hv_delays[minutes] ),\n         CALCULATE ( SUM ( hv_delays[minutes] ), ALL ( hv_delays[reason] ) ) )",
    results=[[f"{k} rötar oranı", f"%{v*100:.1f}"] for k, v in rate.items()]
    + [["χ² / sd / p", f"{chi[0]:.1f} / {chi[2]} / {chi[1]:.1e}"], ["Cramér V", f"{cv:.3f}"]]
    + [[f"Neden: {k}", f"dakika payı %{v*100:.1f} · gündüz %{shr.loc[False, k]*100:.1f} / akşam %{shr.loc[True, k]*100:.1f}"] for k, v in share.sort_values(ascending=False).items()],
    chart=dict(kind="bars", unit="%", labels=[str(k) for k in rate.index], values=[r(v * 100, 1) for v in rate], caption="Saat dilimine göre ≥15 dk rötar oranı"),
    read=f"Akşam dilimi belirgin biçimde daha kötü (Cramér V ≈ {cv:.2f}: küçük–orta etki). Ama neden payları akşam ve gündüz neredeyse aynı: geç gelen uçak payı akşam artmıyor. Rotasyon hipotezi bu veriyle desteklenmedi; akşam fazlası bütün nedenlerde orantılı artıyor. Sıradaki adım, saat dilimine göre trafik yoğunluğu ve slot verisidir.",
    limits="Cramér V gücü sınırlı bir özettir; rotalar ve uçak tipleri dilimlere eşit dağılmıyor olabilir. Neden kodlaması operasyon ekibinin beyanıdır.",
    lessons=["s28", "s23", "s37", "s36"]))

# 8 ─ Kanat no-show
bkg = csv("kanat_havayollari/hv_bookings.csv")
bf = bkg[bkg.status != "cancelled"]
ns = bf.groupby("fare_class").status.apply(lambda s: (s == "no_show").mean())
nn = bf.groupby("fare_class").size()
nk = bf.groupby("fare_class").status.apply(lambda s: int((s == "no_show").sum()))
ct2 = pd.crosstab(bf.fare_class, bf.status == "no_show")
chi2 = stats.chi2_contingency(ct2)
order = ["Eko", "EkoFlex", "Business"]
cases.append(dict(
    id="hv-noshow", dataset="Kanat Havayolları", app="powerbi", tables=["hv_bookings"],
    title="Gelmeyen yolcu oranı fiyat sınıfına göre değişiyor mu?",
    question="Fazla satış (overbooking) kararı için her fiyat sınıfında kaç yolcunun gelmediğini ve bu oranın belirsizliğini bil.",
    unit="İptal edilmemiş rezervasyon (uçan veya gelmeyen).",
    predict=dict(q="Business sınıfında rezervasyon sayısı az. Oranı tek sayı olarak vermek neden riskli?",
                 options=["Business yolcular hep gelir", "Küçük n'de oranın aralığı geniştir; fazla satışı nokta tahmine göre yapmak koltuk riskini gizler", "Oranlar sınıflar arasında karşılaştırılamaz"], correct=1,
                 why="Fazla satış kararı belirsizliğe duyarlıdır: aralığın üst ucu kullanılırsa daha az koltuk satılır, alt ucu kullanılırsa yolcu geri çevrilir."),
    method="Sınıf bazında Wilson aralıkları + ki-kare bağımsızlık testi",
    why="Oranlar küçük ve gruplar dengesiz; Wilson aralığı küçük n'de Wald'dan güvenilirdir.",
    sql="SELECT fare_class, COUNT(*) AS n,\n       SUM(CASE WHEN status = 'no_show' THEN 1 ELSE 0 END) AS gelmeyen,\n       AVG(CASE WHEN status = 'no_show' THEN 1.0 ELSE 0 END) AS oran\nFROM hv_bookings\nWHERE status <> 'cancelled'\nGROUP BY fare_class;",
    python=f"import pandas as pd\nfrom statsmodels.stats.proportion import proportion_confint\n\nb = pd.read_csv('{RAW}kanat_havayollari/hv_bookings.csv')\nb = b[b.status != 'cancelled']\ng = b.groupby('fare_class').status.agg(n='size', k=lambda s: (s=='no_show').sum())\ng['alt'], g['ust'] = proportion_confint(g.k, g.n, method='wilson')\nprint(g)",
    dax="No-show % =\nDIVIDE ( CALCULATE ( COUNTROWS ( hv_bookings ), hv_bookings[status] = \"no_show\" ),\n         CALCULATE ( COUNTROWS ( hv_bookings ), hv_bookings[status] <> \"cancelled\" ) )",
    results=[[k, f"{nk[k]}/{nn[k]} = %{ns[k]*100:.1f} · Wilson [%{wilson(nk[k], nn[k])[0]*100:.1f}; %{wilson(nk[k], nn[k])[1]*100:.1f}]"] for k in order if k in ns.index]
    + [["χ² / sd / p", f"{chi2[0]:.1f} / {chi2[2]} / {chi2[1]:.2g}"]],
    chart=dict(kind="bars", unit="%", labels=[k for k in order if k in ns.index], values=[r(ns[k] * 100, 2) for k in order if k in ns.index],
               lo=[r(wilson(nk[k], nn[k])[0] * 100, 2) for k in order if k in ns.index], hi=[r(wilson(nk[k], nn[k])[1] * 100, 2) for k in order if k in ns.index], caption="Gelmeyen yolcu oranı ve Wilson %95 aralığı"),
    read=f"Sınıflar arasında anlamlı bir fark yok (p = {chi2[1]:.2f}); oranların hepsi %3–4 civarında. Business için tek başına oran yerine havuzlanmış oran (%{bf.status.eq('no_show').mean()*100:.1f}) daha kararlı bir tahmindir. Business aralığının üst ucu %6'ya çıkıyor: fazla satış o sınıfta temkinli tutulmalıdır.",
    limits="Rezervasyonlar yalnızca sadakat üyelerine ait; tüm yolcuları temsil etmeyebilir. Aynı yolcunun birden çok rezervasyonu bağımsız değildir.",
    lessons=["s19", "s28", "s13", "s12"]))

# 9 ─ Pusula İK çalışma modeli ve ayrılma (anlamsız sonuç)
e = csv("pusula_ik/ik_employees.csv", parse_dates=["hire_date", "term_date"])
act0 = e[(e.hire_date < "2024-01-01") & (e.term_date.isna() | (e.term_date >= "2024-01-01"))].copy()
act0["ayrildi"] = (act0.term_type == "gönüllü") & (act0.term_date < "2025-01-01")
wm = act0.groupby("work_mode").ayrildi.agg(["size", "sum", "mean"])
chi3 = stats.chi2_contingency(pd.crosstab(act0.work_mode, act0.ayrildi))
pu, nu = wm.loc["uzaktan", "mean"], wm.loc["uzaktan", "size"]
po, no = wm.loc["ofis", "mean"], wm.loc["ofis", "size"]
sed = np.sqrt(pu * (1 - pu) / nu + po * (1 - po) / no)
dlo, dhi = (pu - po) - 1.96 * sed, (pu - po) + 1.96 * sed
cases.append(dict(
    id="ik-calisma-modeli", dataset="Pusula İK", app="sql", tables=["ik_employees"],
    title="Uzaktan çalışanlar daha mı çok ayrılıyor?",
    question="2024'te gönüllü ayrılma oranı ofis, hibrit ve uzaktan çalışanlar arasında farklı mı?",
    unit="1 Ocak 2024'te şirkette olan çalışan; olay 2024 içinde gönüllü ayrılma.",
    predict=dict(q=f"p = {chi3[1]:.2f} çıktı. 'Çalışma modeli ayrılmayı etkilemiyor' diyebilir misin?",
                 options=["Evet, p > 0,05 olduğuna göre etki sıfırdır", "Hayır; anlamlı olmamak etkinin olmadığını kanıtlamaz. Farkın güven aralığına bakıp hangi büyüklükteki etkileri dışlayabildiğini söylersin", "Hayır; p değeri yanlış hesaplanmıştır"], correct=1,
                 why="Anlamsız sonuç, veri ile uyumlu etki aralığını raporlayarak yorumlanır. Uzaktan grubu küçük olduğu için aralık geniştir; birkaç puanlık bir etki hâlâ mümkündür."),
    method="Ki-kare bağımsızlık testi + oran farkı için %95 aralık",
    why="Kategorik maruziyet ve 0/1 sonuç. Dönem başında var olan çalışanlarla kohort tanımı, işe yeni girenlerin kısa maruziyetini dışarıda bırakır.",
    sql="SELECT work_mode, COUNT(*) AS n,\n       SUM(CASE WHEN term_type = 'gönüllü' AND term_date < '2025-01-01' THEN 1 ELSE 0 END) AS ayrilan\nFROM ik_employees\nWHERE hire_date < '2024-01-01'\n  AND (term_date IS NULL OR term_date >= '2024-01-01')\nGROUP BY work_mode;",
    python=f"import pandas as pd\nfrom scipy import stats\n\ne = pd.read_csv('{RAW}pusula_ik/ik_employees.csv', parse_dates=['hire_date','term_date'])\nk = e[(e.hire_date < '2024-01-01') & (e.term_date.isna() | (e.term_date >= '2024-01-01'))].copy()\nk['ayrildi'] = (k.term_type == 'gönüllü') & (k.term_date < '2025-01-01')\nprint(k.groupby('work_mode').ayrildi.agg(['size','mean']))\nprint(stats.chi2_contingency(pd.crosstab(k.work_mode, k.ayrildi)))",
    dax="Gönüllü Ayrılma % (2024) =\nVAR Kohort = FILTER ( ik_employees, ik_employees[hire_date] < DATE(2024,1,1)\n    && ( ISBLANK ( ik_employees[term_date] ) || ik_employees[term_date] >= DATE(2024,1,1) ) )\nRETURN DIVIDE (\n    COUNTROWS ( FILTER ( Kohort, ik_employees[term_type] = \"gönüllü\"\n                         && ik_employees[term_date] < DATE(2025,1,1) ) ),\n    COUNTROWS ( Kohort ) )",
    results=[[k.capitalize(), f"{int(v['sum'])}/{int(v['size'])} = %{v['mean']*100:.1f}"] for k, v in wm.iterrows()]
    + [["χ² / sd / p", f"{chi3[0]:.2f} / {chi3[2]} / {chi3[1]:.2f}"], ["Uzaktan − ofis farkı", f"{(pu-po)*100:.1f} puan · %95 [{dlo*100:.1f}; {dhi*100:.1f}]"]],
    chart=dict(kind="bars", unit="%", labels=[k for k in wm.index], values=[r(v * 100, 2) for v in wm["mean"]],
               lo=[r(wilson(int(v['sum']), int(v['size']))[0] * 100, 2) for _, v in wm.iterrows()], hi=[r(wilson(int(v['sum']), int(v['size']))[1] * 100, 2) for _, v in wm.iterrows()], caption="2024 gönüllü ayrılma oranı ve Wilson %95 aralığı"),
    read=f"Bu veride çalışma modeline göre belirgin bir fark yok. Doğru cümle: 'Uzaktan çalışanların ayrılma oranı ofistekinden {abs(dlo)*100:.1f} puan düşük ile {dhi*100:.1f} puan yüksek arasında olabilir; daha büyük farkları dışlıyoruz.' 'Fark yoktur' cümlesi veriyle kanıtlanmış değildir.",
    limits="work_mode güncel/son değerdir; yıl içinde model değiştirenler bilinmiyor. Yaş, kıdem ve bölüm karışımı kontrol edilmedi. Süre-olay yapısı için sağkalım analizi daha uygundur.",
    lessons=["s22", "s20", "s28", "s52"]))

# 10 ─ Pusula İK maaş farkı (ham ve düzeltilmiş)
s = csv("pusula_ik/ik_salaries.csv", parse_dates=["effective_date"])
cur = s.sort_values("effective_date").groupby("emp_id").tail(1)
pos = csv("pusula_ik/ik_positions.csv")
act = e[e.term_date.isna()].merge(cur, on="emp_id").merge(pos, on="position_id")
act["lw"] = np.log(act.monthly_gross)
m0 = smf.ols("lw ~ C(gender, Treatment('E'))", act).fit()
m1 = smf.ols("lw ~ C(gender, Treatment('E')) + C(level) + C(dept_id)", act).fit()
kname = "C(gender, Treatment('E'))[T.K]"
raw_gap = np.exp(m0.params[kname]) - 1
adj_gap = np.exp(m1.params[kname]) - 1
ci = np.exp(m1.conf_int().loc[kname]) - 1
lv = act.groupby(["level", "gender"]).monthly_gross.median().unstack()
share_k = act.groupby("level").gender.apply(lambda x: (x == "K").mean())
cases.append(dict(
    id="ik-maas-farki", dataset="Pusula İK", app="python", tables=["ik_employees", "ik_salaries", "ik_positions"],
    title="Maaş farkı: ham fark ile aynı işteki fark",
    question="Kadın ve erkek çalışanların güncel maaşları ne kadar farklı? Fark aynı seviye ve bölümde de sürüyor mu?",
    unit="Hâlen çalışan kişi; maaş, en son geçerli maaş kaydı.",
    predict=dict(q="Regresyona seviye ve bölüm eklenince fark küçülürse ne söylenebilir?",
                 options=["Ayrımcılık yoktur", "Ham farkın bir kısmı seviye ve bölüm dağılımından gelir; kalan fark aynı seviye ve bölümdeki farktır. Seviyeye erişimin kendisi de ayrıca incelenmelidir", "Ham fark yanlıştır"], correct=1,
                 why="Kontrol değişkenleri soruyu değiştirir. Seviye kendi başına eşitsizliğin bir sonucu olabilir; bu durumda onu kontrol etmek etkinin bir kısmını gizler (aracı değişken)."),
    method="Log maaş üzerinde çoklu doğrusal regresyon (ham ve düzeltilmiş model)",
    why="Maaş çarpık ve etkiler oransal; log ölçeğinde katsayı yaklaşık yüzde farkı verir. Seviye ve bölüm sabit etkileri 'aynı iş' karşılaştırmasını yaklaşıklar.",
    sql="WITH son AS (\n  SELECT s.*, ROW_NUMBER() OVER (PARTITION BY emp_id ORDER BY effective_date DESC) AS rn\n  FROM ik_salaries s)\nSELECT p.level, e.gender, COUNT(*) AS n, AVG(son.monthly_gross) AS ort\nFROM ik_employees e\nJOIN son ON son.emp_id = e.emp_id AND son.rn = 1\nJOIN ik_positions p ON p.position_id = e.position_id\nWHERE e.term_date IS NULL\nGROUP BY p.level, e.gender\nORDER BY p.level, e.gender;",
    python=f"import numpy as np, pandas as pd\nimport statsmodels.formula.api as smf\n\nU = '{RAW}pusula_ik/'\ne = pd.read_csv(U+'ik_employees.csv'); p = pd.read_csv(U+'ik_positions.csv')\ns = pd.read_csv(U+'ik_salaries.csv').sort_values('effective_date').groupby('emp_id').tail(1)\nd = e[e.term_date.isna()].merge(s, on='emp_id').merge(p, on='position_id')\nd['lw'] = np.log(d.monthly_gross)\nham = smf.ols(\"lw ~ C(gender, Treatment('E'))\", d).fit()\nduz = smf.ols(\"lw ~ C(gender, Treatment('E')) + C(level) + C(dept_id)\", d).fit()\nprint(np.exp(ham.params.iloc[1])-1, np.exp(duz.params.iloc[1])-1)",
    dax="Medyan Maaş =\nMEDIANX ( VALUES ( ik_employees[emp_id] ), [Güncel Maaş] )\n\nKadın/Erkek Oranı =\nDIVIDE ( CALCULATE ( [Medyan Maaş], ik_employees[gender] = \"K\" ),\n         CALCULATE ( [Medyan Maaş], ik_employees[gender] = \"E\" ) ) - 1\n-- Seviye eksene konunca 'aynı seviyede' oran görünür.",
    results=[["Çalışan (E / K)", f"{int((act.gender=='E').sum())} / {int((act.gender=='K').sum())}"],
             ["Ham fark (K / E)", pct(raw_gap)], ["Seviye + bölüm düzeltilmiş", f"{pct(adj_gap)} · %95 [{pct(ci.iloc[0])}; {pct(ci.iloc[1])}]"],
             ["Düzeltilmiş model R²", f"{m1.rsquared:.3f}"]]
    + [[f"Seviye {int(k)} · kadın payı", f"%{v*100:.0f}"] for k, v in share_k.items()],
    chart=dict(kind="bars", unit="%", labels=["Ham fark", "Aynı seviye+bölüm"], values=[r(raw_gap * 100, 2), r(adj_gap * 100, 2)],
               lo=[None, r(ci.iloc[0] * 100, 2)], hi=[None, r(ci.iloc[1] * 100, 2)], caption="Kadınların maaşı, erkeklere göre % fark"),
    read="Ham farkın büyük bölümü kadın ve erkeklerin farklı seviye ve bölümlerde bulunmasından gelir. Aynı seviye ve bölümde de küçük ama sıfırı dışlayan bir fark kalır. İki sayı farklı soruların cevabıdır; ikisi birlikte raporlanır.",
    limits="Kıdem, performans ve işe giriş maaşı modelde yok. Seviye bir aracı değişken olabilir: terfi süreçleri ayrı bir analizle (ör. terfi oranları) incelenmelidir. Kurgusal veridir.",
    lessons=["s31", "s08", "s30", "s36"]))

# 11 ─ Pusula İK eNPS değişimi
sv = csv("pusula_ik/ik_survey.csv")


def enps(x):
    x = x[~np.isnan(x)]
    return ((x >= 9).mean() - (x <= 6).mean()) * 100


q2 = sv[sv.wave == "2024-Q2"].enps.to_numpy(float)
q4 = sv[sv.wave == "2024-Q4"].enps.to_numpy(float)
both = sv.pivot_table(index="emp_id", columns="wave", values="enps").dropna()
pair_d = enps(both["2024-Q4"].to_numpy()) - enps(both["2024-Q2"].to_numpy())
pb = []
idx = np.arange(len(both))
for _ in range(4000):
    sm_ = both.iloc[RNG.integers(0, len(both), len(both))]
    pb.append(enps(sm_["2024-Q4"].to_numpy()) - enps(sm_["2024-Q2"].to_numpy()))
pci = np.percentile(pb, [2.5, 97.5])
ib = boot(lambda x, y: enps(x) - enps(y), q4, q2)
eng = sv[["engagement", "manager_score"]].dropna()
pr = stats.pearsonr(eng.engagement, eng.manager_score)
cases.append(dict(
    id="ik-enps", dataset="Pusula İK", app="python", tables=["ik_survey"],
    title="eNPS düştü mü? Aynı kişileri izlemek neyi değiştirir?",
    question="Bağlılık anketinde eNPS ikinci dalgada düştü mü? Fark rastlantıyla açıklanabilir mi?",
    unit="Anket yanıtı; iki dalgaya da cevap veren çalışanlar eşli birimdir.",
    predict=dict(q="Aynı çalışanların iki dalgadaki yanıtları var. Bağımsız grup bootstrap'ı yerine eşli bootstrap neden tercih edilir?",
                 options=["Daha çok veri kullanır", "Kişi içi bağımlılığı doğru modeller; iki dalga güçlü ilişkiliyse aralık daralır, zayıf ilişkiliyse daralmayabilir", "Eşli bootstrap her zaman anlamlı sonuç verir"], correct=1,
                 why="Aynı kişinin iki yanıtı bağımsız değildir; eşli yeniden örnekleme kişiyi birim alır. Kazanç, iki dalga arasındaki korelasyona bağlıdır."),
    method="eNPS (%promoter − %detractor) için bootstrap aralığı: bağımsız ve eşli",
    why="eNPS bir fark-oranıdır; standart hatası için basit formül yerine bootstrap pratik ve şeffaftır.",
    sql="SELECT wave, COUNT(enps) AS yanit,\n       100.0 * (AVG(CASE WHEN enps >= 9 THEN 1.0 ELSE 0 END)\n              - AVG(CASE WHEN enps <= 6 THEN 1.0 ELSE 0 END)) AS enps\nFROM ik_survey\nWHERE enps IS NOT NULL\nGROUP BY wave;",
    python=f"import numpy as np, pandas as pd\n\nsv = pd.read_csv('{RAW}pusula_ik/ik_survey.csv')\nenps = lambda x: ((x >= 9).mean() - (x <= 6).mean()) * 100\nw = sv.pivot_table(index='emp_id', columns='wave', values='enps').dropna()\nrng = np.random.default_rng(1)\nb = [enps(s['2024-Q4']) - enps(s['2024-Q2'])\n     for s in (w.sample(len(w), replace=True, random_state=rng) for _ in range(4000))]\nprint(np.percentile(b, [2.5, 97.5]))",
    dax="eNPS =\nVAR n = COUNT ( ik_survey[enps] )\nRETURN 100 * ( DIVIDE ( CALCULATE ( COUNT ( ik_survey[enps] ), ik_survey[enps] >= 9 ), n )\n             - DIVIDE ( CALCULATE ( COUNT ( ik_survey[enps] ), ik_survey[enps] <= 6 ), n ) )",
    results=[["eNPS 2024-Q2", f"{enps(q2):.1f} (n={int((~np.isnan(q2)).sum())})"], ["eNPS 2024-Q4", f"{enps(q4):.1f} (n={int((~np.isnan(q4)).sum())})"],
             ["Bağımsız bootstrap fark", f"{enps(q4)-enps(q2):.1f} · %95 [{ib[0]:.1f}; {ib[1]:.1f}]"],
             ["İki dalgada da yanıtlayan", f"{len(both)} kişi"], ["Eşli bootstrap fark", f"{pair_d:.1f} · %95 [{pci[0]:.1f}; {pci[1]:.1f}]"],
             ["Aynı kişinin iki dalga puan korelasyonu", f"r = {both.corr().iloc[0, 1]:.2f}"], ["Bağlılık × yönetici puanı", f"r = {pr.statistic:.2f}"]],
    chart=dict(kind="bars", unit="puan", labels=["Q2", "Q4"], values=[r(enps(q2), 2), r(enps(q4), 2)], caption="eNPS (−100 ile +100 arası)", zero=True),
    read=f"Düşüş birkaç puan ve iki yöntemde de aralık sıfırı içeriyor. 'eNPS çöktü' başlığı veriyle desteklenmiyor. Eşli aralık bu kez daralmadı: aynı kişinin iki puanı arasındaki korelasyon yalnızca {both.corr().iloc[0, 1]:.2f}. Yönetici puanı ile bağlılık güçlü ilişkili; izlenecek öncü gösterge yönetici deneyimi olabilir.",
    limits="Yanıt vermeyenler ve işten ayrılanlar ikinci dalgaya girmez (yıpranma yanlılığı). Korelasyon yönetici etkisini kanıtlamaz; iyi ekipler yöneticilerini de yüksek puanlayabilir.",
    lessons=["s43", "s25", "s03", "s29"]))

# 12 ─ Pedal İzmir yağmur ve yolculuk sayısı
trips = csv("pedal_izmir/bk_trips.csv", parse_dates=["started_at", "ended_at"])
wth = csv("pedal_izmir/bk_weather.csv", parse_dates=["obs_hour"])
trips["h"] = trips.started_at.dt.floor("h")
hc = trips.groupby("h").size().rename("n")
W = wth.set_index("obs_hour").join(hc).fillna({"n": 0}).reset_index()
W["yagmur"] = (W.rain_mm > 0).astype(int)
W["saat"] = W.obs_hour.dt.hour
pois = smf.glm("n ~ yagmur + C(saat) + temp_c", W, family=sm.families.Poisson()).fit()
disp = pois.pearson_chi2 / pois.df_resid
nb = smf.negativebinomial("n ~ yagmur + C(saat) + temp_c", W).fit(disp=0, maxiter=200)
rr_p = np.exp(pois.params["yagmur"]); ci_p = np.exp(pois.conf_int().loc["yagmur"])
rr_n = np.exp(nb.params["yagmur"]); ci_n = np.exp(nb.conf_int().loc["yagmur"])
mean_by = W.groupby("yagmur").n.mean()
cases.append(dict(
    id="bk-yagmur", dataset="Pedal İzmir", app="sql", tables=["bk_trips", "bk_weather"],
    title="Yağmur saatlik yolculuğu ne kadar azaltıyor?",
    question="Yağmurlu saatlerde yolculuk sayısı ne kadar düşüyor? Saat ve sıcaklık etkisini ayırınca etki ne kalıyor?",
    unit="Saat (Haziran–Ağustos 2024, 2.208 saat); sonuç o saatte başlayan yolculuk sayısı.",
    predict=dict(q=f"Poisson modelinde Pearson χ²/sd ≈ {disp:.1f}. Bu ne demektir?",
                 options=["Model mükemmel uyuyor", "Aşırı yayılım var: varyans ortalamadan çok büyük; Poisson standart hataları fazla dar", "Veri normal dağılıyor"], correct=1,
                 why="Poisson'da varyans ortalamaya eşittir. Oran 1'den çok büyükse aralıklar aşırı iyimserdir; negatif binom veya sağlam standart hata kullanılır."),
    method="Saat ve sıcaklık kontrollü Poisson ve negatif binom regresyonu",
    why="Sonuç bir sayım ve saatten saate yoğunluk değişiyor. Saat sabit etkisi günlük deseni, sıcaklık mevsim içi farkı tutar.",
    sql="SELECT CASE WHEN w.rain_mm > 0 THEN 'yağmurlu' ELSE 'kuru' END AS hava,\n       COUNT(*) AS saat, AVG(x.n) AS ort_yolculuk\nFROM bk_weather w\nLEFT JOIN (SELECT strftime('%Y-%m-%d %H:00:00', started_at) AS h, COUNT(*) AS n\n           FROM bk_trips GROUP BY h) x ON x.h = w.obs_hour\nGROUP BY hava;",
    python=f"import numpy as np, pandas as pd\nimport statsmodels.formula.api as smf\n\nU = '{RAW}pedal_izmir/'\nt = pd.read_csv(U+'bk_trips.csv', parse_dates=['started_at'])\nw = pd.read_csv(U+'bk_weather.csv', parse_dates=['obs_hour'])\nn = t.groupby(t.started_at.dt.floor('h')).size().rename('n')\nw = w.set_index('obs_hour').join(n).fillna({{'n': 0}}).reset_index()\nw['yagmur'] = (w.rain_mm > 0).astype(int); w['saat'] = w.obs_hour.dt.hour\nm = smf.negativebinomial('n ~ yagmur + C(saat) + temp_c', w).fit(disp=0)\nprint(np.exp(m.params['yagmur']), np.exp(m.conf_int().loc['yagmur']))",
    dax="Saatlik Yolculuk = DIVIDE ( COUNTROWS ( bk_trips ), DISTINCTCOUNT ( bk_weather[obs_hour] ) )\n-- bk_trips'e saat başı anahtar (hesaplanmış sütun) ekleyip bk_weather ile ilişkilendir;\n-- 'yağmurlu' dilimleyicisi ile iki ortalamayı karşılaştır.",
    results=[["Yağmurlu saat", f"{int(W.yagmur.sum())} / {len(W)} (%{W.yagmur.mean()*100:.1f})"],
             ["Ham ortalama kuru / yağmurlu", f"{mean_by[0]:.1f} / {mean_by[1]:.1f} yolculuk"],
             ["Poisson oran (RR)", f"{rr_p:.2f} · %95 [{ci_p.iloc[0]:.2f}; {ci_p.iloc[1]:.2f}]"],
             ["Aşırı yayılım (χ²/sd)", f"{disp:.1f}"], ["Negatif binom oran (RR)", f"{rr_n:.2f} · %95 [{ci_n.iloc[0]:.2f}; {ci_n.iloc[1]:.2f}]"],
             ["Yorum", f"Yağmurlu saatte yolculuk yaklaşık %{(1-rr_n)*100:.0f} daha az"]],
    chart=dict(kind="bars", unit="yolculuk/saat", labels=["Kuru saat", "Yağmurlu saat"], values=[r(mean_by[0], 1), r(mean_by[1], 1)], caption="Saat başına ortalama yolculuk (ham)"),
    read="Etki çok büyük ve iki modelde benzer; değişen, belirsizliğin genişliği. Yağmurlu saat sayısı az olduğu için negatif binom aralığı Poisson'dan geniştir ve dürüst olan odur.",
    limits="Yağmur 0/1 alındı; şiddet ve önceki saat etkisi yok. Yağmurlu saatler belirli günlere toplanıyorsa gün içi bağımlılık aralıkları yine dar gösterebilir.",
    lessons=["s70", "s32", "s13", "s24"]))

# 13 ─ Ilgaz Bank harcama kuyruğu
bt = csv("ilgaz_bank/bank_txns.csv")
k = bt[bt.txn_type == "kart_harcama"].copy()
k["tutar"] = -k.amount
q1k, q3k = k.tutar.quantile([.25, .75])
flag = (k.tutar > q3k + 1.5 * (q3k - q1k)).mean()
lg = np.log(k.tutar)
med = k.groupby("merchant_category").tutar.median().sort_values()
madz = (lg - lg.median()).abs() / (1.4826 * stats.median_abs_deviation(lg))
cat_flag = k.groupby("merchant_category").tutar.transform(lambda s: s > s.quantile(.75) + 1.5 * (s.quantile(.75) - s.quantile(.25))).mean()
cases.append(dict(
    id="ib-harcama-kuyruk", dataset="Ilgaz Bank", app="powerbi", tables=["bank_txns"],
    title="Aykırı harcama mı, sadece pahalı kategori mi?",
    question="Kart harcamalarında 'olağandışı tutar' kuralı nasıl kurulmalı? Tüm işlemlere tek IQR kuralı uygulamak işe yarar mı?",
    unit="Kart harcaması işlemi (2024).",
    predict=dict(q=f"Tüm işlemlere tek IQR kuralı uygulanınca işlemlerin %{flag*100:.0f}'si 'aykırı' çıkıyor. Neden?",
                 options=["Sahtecilik çok yaygındır", "Dağılım çok sağa çarpık ve kategoriler karışık; elektronik ve eğitim gibi pahalı kategoriler doğal olarak çitin üstünde kalır", "IQR kuralı hep %10 işaretler"], correct=1,
                 why="IQR çiti simetrik ve tek tip dağılım için sezgiseldir. Lognormal benzeri karışık bir veride kural, kategoriyi işaretler; aykırıyı değil. Önce log ölçeği ve kategori içi kural gerekir."),
    method="Dağılım biçimi (çarpıklık, log dönüşüm), kategori medyanları, log ölçekte robust z (MAD)",
    why="Para tutarları çarpımsal büyür; log ölçeği simetriye yaklaştırır. MAD temelli z, aykırıların kendisinden etkilenmez.",
    sql="SELECT merchant_category, COUNT(*) AS n,\n       AVG(-amount) AS ort, MIN(-amount) AS en_az, MAX(-amount) AS en_cok\nFROM bank_txns\nWHERE txn_type = 'kart_harcama'\nGROUP BY merchant_category\nORDER BY ort;",
    python=f"import numpy as np, pandas as pd\nfrom scipy import stats\n\nb = pd.read_csv('{RAW}ilgaz_bank/bank_txns.csv')\nk = b[b.txn_type == 'kart_harcama'].assign(tutar=lambda d: -d.amount)\nprint(k.tutar.skew(), np.log(k.tutar).skew())\nprint(k.groupby('merchant_category').tutar.median().sort_values())\nlg = np.log(k.tutar)\nk['robust_z'] = (lg - lg.median()) / (1.4826 * stats.median_abs_deviation(lg))",
    dax="Harcama = -SUM ( bank_txns[amount] )\n\nMedyan Harcama =\nCALCULATE ( MEDIAN ( bank_txns[amount] ) * -1, bank_txns[txn_type] = \"kart_harcama\" )",
    results=[["Kart harcaması", f"{len(k):,}"], ["Ortalama / medyan", f"{k.tutar.mean():,.0f} / {k.tutar.median():,.0f} TL"],
             ["Çarpıklık ham / log", f"{k.tutar.skew():.2f} / {lg.skew():.2f}"], ["Tek IQR kuralı işaretlediği", f"%{flag*100:.1f}"],
             ["Kategori içi IQR kuralı", f"%{cat_flag*100:.1f}"], ["Log ölçekte |robust z| > 3,5", f"%{(madz>3.5).mean()*100:.2f}"]]
    + [[f"Medyan · {NICE.get(kk, kk)}", f"{v:,.0f} TL"] for kk, v in med.items()],
    chart=dict(kind="bars", unit="TL", labels=[NICE.get(kk, kk) for kk in med.index], values=[r(v, 0) for v in med], caption="Kategoriye göre medyan kart harcaması", log=True),
    read="Ham ölçekte 'aykırı' etiketi büyük ölçüde pahalı kategorileri yakalıyor. Kategori içi kural ve log ölçeğinde robust z işaretleme oranını neredeyse sıfıra indiriyor: bu kurgusal veride tutarlar kategori içinde düzgün bir lognormal gibi dağılıyor. Gerçek veride eşik, inceleme ekibinin kapasitesine ve müşterinin kendi geçmişine göre seçilir.",
    limits="Kurgusal veride gerçek sahtecilik etiketi yok; kural performansı (precision/recall) ölçülemez. Müşterinin kendi geçmişine göre kural genelde daha güçlüdür.",
    lessons=["s07", "s15", "s67", "s59"]))

datasets = {
    "Anadolu Market": dict(desc="E-ticaret: müşteriler, siparişler, web olayları ve A/B testi. Kesit SQL'in ana veri seti; Power BI modelinin temeli.", apps=["sql", "powerbi", "python"]),
    "Lezzet Kurye": dict(desc="Yemek teslimatı (Ekim–Aralık 2024): siparişler, kuryeler, restoranlar ve puanlar.", apps=["sql", "powerbi", "python"]),
    "Kanat Havayolları": dict(desc="Havayolu (Eylül–Aralık 2024): uçuşlar, rötar nedenleri, rezervasyonlar ve filo.", apps=["sql", "powerbi", "python"]),
    "Pusula İK": dict(desc="İnsan kaynakları (2019–2024): çalışanlar, maaş geçmişi, performans, anket ve ayrılmalar.", apps=["sql", "powerbi", "python"]),
    "Pedal İzmir": dict(desc="Bisiklet paylaşımı (Haziran–Ağustos 2024): 116.517 yolculuk, istasyonlar ve saatlik hava durumu.", apps=["sql", "powerbi", "python"]),
    "Ilgaz Bank": dict(desc="Bankacılık (2024): 500 müşteri, hesaplar ve yaklaşık 42 bin hesap hareketi.", apps=["sql", "powerbi", "python"]),
}
for cs in cases:
    cs["results"] = [[a, trnum(b)] for a, b in cs["results"]]
    cs["read"] = trnum(cs["read"])
payload = dict(version="V9", generated="ecosystem_cases_v9.py", raw=RAW, datasets=datasets, cases=cases)
OUT.write_text("/* Üretildi: ecosystem_cases_v9.py — elle düzenleme. */\nwindow.KESIT_ECOSYSTEM=" + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
print(f"{len(cases)} vaka yazıldı → {OUT}")
for cs in cases:
    print("-", cs["id"], "|", " ; ".join(f"{a}: {b}" for a, b in cs["results"][:4]))
