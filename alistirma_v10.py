"""Kesit İstatistik V10: ders içi uygulamalı alıştırmalar (Kesit verisiyle), ders defterleri ve Excel çalışma kitapları.

Kullanım:  python alistirma_v10.py ../kesit-python/data
Üretir:
  docs/data/kesit/*.csv, docs/data/kesit-veri.zip     alıştırmaların kullandığı Kesit verisi (kardeş Kesit Python deposundan)
  docs/ders-alistirma.js                              window.KESIT_DERS_ALISTIRMA: her derse 3 görev (soru, cevap, tolerans, ipucu, Python kodu)
  docs/defter/sNN.ipynb, sNN.py, kesit-defterler.zip  her ders için çalışma defteri (aynı kod, cevabı assert ile denetler)
  docs/excel/modul-NN.xlsx                           her modül için Excel kitabı (veri sayfaları + Görevler sayfası, kontrol formülü; NN = ekrandaki modül no)
Tek doğruluk kaynağı: her görevin `kod` metni burada çalıştırılır, cevap ondan hesaplanır; defterdeki kod aynı metindir.
"""
import sys, os, json, math, zipfile, io, re
import numpy as np, pandas as pd
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf

KAYNAK = sys.argv[1] if len(sys.argv) > 1 else '../kesit-python/data'
KOK = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(KOK, 'docs')
VERI = os.path.join(DOCS, 'data', 'kesit')
os.makedirs(VERI, exist_ok=True)

# ---------------------------------------------------------------- veri: kaynak CSV'ler + türetilmiş günlük bisiklet tablosu
DOSYA = {
    'orders': 'anadolu_market/orders.csv', 'order_items': 'anadolu_market/order_items.csv', 'products': 'anadolu_market/products.csv',
    'customers': 'anadolu_market/customers.csv', 'ab_test': 'anadolu_market/ab_test.csv', 'web_events': 'anadolu_market/web_events.csv',
    'hv_flights': 'kanat_havayollari/hv_flights.csv', 'hv_delays': 'kanat_havayollari/hv_delays.csv', 'hv_bookings': 'kanat_havayollari/hv_bookings.csv',
    'lk_orders': 'lezzet_kurye/lk_orders.csv', 'lk_ratings': 'lezzet_kurye/lk_ratings.csv', 'lk_couriers': 'lezzet_kurye/lk_couriers.csv',
    'ik_employees': 'pusula_ik/ik_employees.csv', 'ik_survey': 'pusula_ik/ik_survey.csv',
    'bank_txns': 'ilgaz_bank/bank_txns.csv', 'bank_customers': 'ilgaz_bank/bank_customers.csv', 'bk_weather': 'pedal_izmir/bk_weather.csv',
}
for ad, yol in DOSYA.items():
    df = pd.read_csv(os.path.join(KAYNAK, yol))
    df.to_csv(os.path.join(VERI, ad + '.csv'), index=False, lineterminator='\n')
tr = pd.read_csv(os.path.join(KAYNAK, 'pedal_izmir/bk_trips.csv'), parse_dates=['started_at'])
wt = pd.read_csv(os.path.join(KAYNAK, 'pedal_izmir/bk_weather.csv'), parse_dates=['obs_hour'])
g = tr.groupby(tr.started_at.dt.date).agg(yolculuk=('trip_id', 'count'), ort_km=('distance_km', 'mean')).reset_index().rename(columns={'started_at': 'tarih'})
w = wt.groupby(wt.obs_hour.dt.date).agg(sicaklik=('temp_c', 'mean'), yagis=('rain_mm', 'sum')).reset_index().rename(columns={'obs_hour': 'tarih'})
gun = g.merge(w, on='tarih', how='left'); gun['ort_km'] = gun.ort_km.round(3); gun['sicaklik'] = gun.sicaklik.round(2); gun['yagis'] = gun.yagis.round(2)
gun.to_csv(os.path.join(VERI, 'bk_gunluk.csv'), index=False, lineterminator='\n')

HAZIRLIK = '''import math
import numpy as np, pandas as pd
from scipy import stats
import statsmodels.formula.api as smf
V = "kesit/"   # veri paketinin (kesit-veri.zip) açıldığı klasör
orders = pd.read_csv(V + "orders.csv", parse_dates=["order_date"])
items = pd.read_csv(V + "order_items.csv"); items["tutar"] = items.quantity * items.unit_price * (1 - items.discount)
products = pd.read_csv(V + "products.csv")
customers = pd.read_csv(V + "customers.csv")
ab = pd.read_csv(V + "ab_test.csv")
web = pd.read_csv(V + "web_events.csv", parse_dates=["event_time"])
flights = pd.read_csv(V + "hv_flights.csv", parse_dates=["sched_dep", "sched_arr", "actual_dep", "actual_arr"])
flights["gecikme"] = (flights.actual_dep - flights.sched_dep).dt.total_seconds() / 60   # kalkış gecikmesi, dakika
delays = pd.read_csv(V + "hv_delays.csv")
bookings = pd.read_csv(V + "hv_bookings.csv")
lk = pd.read_csv(V + "lk_orders.csv", parse_dates=["placed_at", "picked_at", "delivered_at"])
lk["sure"] = (lk.delivered_at - lk.placed_at).dt.total_seconds() / 60   # teslim süresi, dakika
ratings = pd.read_csv(V + "lk_ratings.csv")
couriers = pd.read_csv(V + "lk_couriers.csv")
emp = pd.read_csv(V + "ik_employees.csv", parse_dates=["hire_date", "term_date"])
survey = pd.read_csv(V + "ik_survey.csv")
txns = pd.read_csv(V + "bank_txns.csv", parse_dates=["txn_time"])
bcust = pd.read_csv(V + "bank_customers.csv")
gunluk = pd.read_csv(V + "bk_gunluk.csv", parse_dates=["tarih"])
teslim = lk[lk.status == "teslim"]            # teslim edilen siparişler
inen = flights[flights.status == "landed"]     # inen uçuşlar
'''
ORTAM = {}
exec(HAZIRLIK.replace('V = "kesit/"', 'V = ' + json.dumps(VERI + '/')), ORTAM)

# ---------------------------------------------------------------- görevler: (ders, soru, kod, ondalık, ipucu)  kod `cevap = ...` atar
T = []
def G(ders, soru, kod, d=2, ipucu='', tol=None):
    T.append(dict(ders=ders, soru=soru, kod=kod.strip(), d=d, ipucu=ipucu, tol=tol))

# 0 · temel kavramlar
G('s01', 'Anadolu Market sipariş tablosunda <b>analiz birimi</b> siparişse kaç birim var? (orders satır sayısı)', 'cevap = len(orders)', 0, 'len(orders)')
G('s01', 'Sipariş veren <b>farklı müşteri</b> sayısı kaç? Analiz birimi müşteri olursa n budur.', 'cevap = orders.customer_id.nunique()', 0, 'nunique()')
G('s01', 'Müşteri tablosundaki 150 müşterinin yüzde kaçı en az bir sipariş vermiş? (yüzde, 1 basamak)', 'cevap = 100 * customers.customer_id.isin(orders.customer_id).mean()', 1, 'isin(...).mean()')
G('s02', 'Lezzet Kurye siparişlerinde ödeme yöntemi <b>nominal</b> bir değişkendir. Kaç farklı ödeme yöntemi var?', 'cevap = lk.payment.nunique()', 0)
G('s02', 'Yemek puanı (food_score) sıralı bir ölçektir. Puanların <b>medyanı</b> kaç?', 'cevap = ratings.food_score.median()', 1, 'Sıralı ölçekte ortalama yerine medyan')
G('s02', 'Yemek puanı 4 ve üstü olanların oranı (yüzde, 1 basamak)', 'cevap = 100 * (ratings.food_score >= 4).mean()', 1)
G('s03', 'Uçuş tablosunda gerçek kalkış zamanı (actual_dep) <b>eksik</b> olan kaç uçuş var?', 'cevap = flights.actual_dep.isna().sum()', 0, 'isna().sum()')
G('s03', 'Pusula İK anketinde eNPS sorusu boş bırakılan cevapların oranı (yüzde, 1 basamak)', 'cevap = 100 * survey.enps.isna().mean()', 1)
G('s03', 'Lezzet Kurye siparişlerinden kaçının değerlendirme (lk_ratings) kaydı var? Oranı yüzde olarak ver (1 basamak); düşükse yanıt yanlılığına dikkat.', 'cevap = 100 * lk.order_id.isin(ratings.order_id).mean()', 1)
G('s04', 'İnen uçuşlarda kalkış gecikmesinin <b>medyanı</b> kaç dakika? (1 basamak)', 'cevap = inen.gecikme.median()', 1, 'Çarpık dağılımda medyan')
G('s04', 'İnen uçuşlarda gecikmenin ortalaması medyanından kaç dakika büyük? (1 basamak)', 'cevap = inen.gecikme.mean() - inen.gecikme.median()', 1, 'Fark büyükse sağa çarpık')
G('s04', 'Teslim edilen siparişlerde teslim süresi 60 dakikayı aşanların sayısı', 'cevap = (teslim.sure > 60).sum()', 0)

# 1 · betimsel
G('s05', 'Teslim edilen siparişlerde teslim süresinin ortalaması (dakika, 2 basamak)', 'cevap = teslim.sure.mean()', 2)
G('s05', 'Teslim süresinin medyanı (dakika, 2 basamak)', 'cevap = teslim.sure.median()', 2)
G('s05', 'Bahşiş bırakılan siparişlerde (tip > 0) bahşişin <b>modu</b> (en sık değer) kaç TL? (Tüm siparişlerde mod 0: çoğu kişi bahşiş vermez.)', 'cevap = lk[lk.tip > 0].tip.mode().iloc[0]', 1)
G('s06', 'Teslim süresinin örneklem standart sapması (ddof = 1, 2 basamak)', 'cevap = teslim.sure.std()', 2, 'pandas std() varsayılan ddof=1')
G('s06', 'Teslim süresinin değişim katsayısı (std / ortalama × 100, 1 basamak)', 'cevap = 100 * teslim.sure.std() / teslim.sure.mean()', 1)
G('s06', 'İnen uçuşlarda yolcu sayısının (pax) varyansı (ddof = 1, tam sayıya yuvarla)', 'cevap = inen.pax.var()', 0)
G('s07', 'Teslim süresinin IQR\'ı (Q3 − Q1, dakika, 2 basamak; pandas quantile varsayılanı)', 'cevap = teslim.sure.quantile(.75) - teslim.sure.quantile(.25)', 2)
G('s07', 'Tukey üst çitinin (Q3 + 1,5·IQR) üstünde kalan teslim sayısı', 'q1, q3 = teslim.sure.quantile([.25, .75]); cevap = (teslim.sure > q3 + 1.5 * (q3 - q1)).sum()', 0)
G('s07', 'Kart harcamalarında tutarın (mutlak değer) 95. yüzdeliği (TL, 2 basamak)', 'cevap = txns[txns.txn_type == "kart_harcama"].amount.abs().quantile(.95)', 2)
G('s08', 'Yemek siparişlerinde ortalama bahşiş: önce ödeme yöntemine göre ortalama al, sonra bu ortalamaları <b>sipariş sayısıyla ağırlıklandır</b>. Sonuç genel ortalamaya eşit olmalı (TL, 3 basamak).', 'o = lk.groupby("payment").tip.agg(["mean", "count"]); cevap = (o["mean"] * o["count"]).sum() / o["count"].sum()', 3)
G('s08', 'Ödeme yöntemlerinin bahşiş ortalamalarının <b>ağırlıksız</b> ortalaması (TL, 3 basamak). Ağırlıklıdan farkı neden?', 'cevap = lk.groupby("payment").tip.mean().mean()', 3)
G('s08', 'Pusula İK\'da gönüllü ayrılma oranı (term_type = "gönüllü" olanların tüm çalışanlara oranı, yüzde, 1 basamak)', 'cevap = 100 * (emp.term_type == "gönüllü").mean()', 1)

# 2 · olasılık
G('s09', 'Rastgele seçilen bir yemek siparişinin <b>iptal ya da iade</b> olma olasılığı (4 basamak)', 'cevap = lk.status.isin(["iptal", "iade"]).mean()', 4)
G('s09', 'Bir siparişin nakit ödenmiş <b>ve</b> iptal edilmiş olma olasılığı (4 basamak)', 'cevap = ((lk.payment == "nakit") & (lk.status == "iptal")).mean()', 4)
G('s09', 'Nakit ödenmiş <b>ya da</b> iptal edilmiş olma olasılığı (birleşim kuralı, 4 basamak)', 'cevap = ((lk.payment == "nakit") | (lk.status == "iptal")).mean()', 4)
G('s10', 'P(iptal | nakit): nakit ödenen siparişlerde iptal oranı (4 basamak)', 'cevap = (lk[lk.payment == "nakit"].status == "iptal").mean()', 4)
G('s10', 'P(iptal | kart) (4 basamak)', 'cevap = (lk[lk.payment == "kart"].status == "iptal").mean()', 4)
G('s10', 'P(iptal | nakit) / P(iptal): bağımsızlık olsaydı 1 olurdu (3 basamak)', 'cevap = (lk[lk.payment == "nakit"].status == "iptal").mean() / (lk.status == "iptal").mean()', 3)
G('s11', 'Bayes: iptal edilen bir siparişin nakit ödenmiş olma olasılığı P(nakit | iptal) (4 basamak)', 'cevap = (lk[lk.status == "iptal"].payment == "nakit").mean()', 4)
G('s11', 'Taban oran: tüm siparişlerde nakit payı P(nakit) (4 basamak)', 'cevap = (lk.payment == "nakit").mean()', 4)
G('s11', 'P(nakit | iptal)\'i Bayes kuralıyla P(iptal | nakit)·P(nakit) / P(iptal) olarak hesapla; doğrudan oranla aynı çıkmalı (4 basamak)', 'cevap = (lk[lk.payment == "nakit"].status == "iptal").mean() * (lk.payment == "nakit").mean() / (lk.status == "iptal").mean()', 4)
G('s12', 'Bahşişin beklenen değeri: sipariş başına ortalama bahşiş (TL, 3 basamak)', 'cevap = lk.tip.mean()', 3)
G('s12', 'Bahşiş dağılımının varyansı (ddof = 0, popülasyon varyansı, 2 basamak)', 'cevap = lk.tip.var(ddof=0)', 2)
G('s12', 'Bir siparişte bahşiş verilme olasılığı (tip > 0, 4 basamak)', 'cevap = (lk.tip > 0).mean()', 4)

# 3 · dağılımlar
G('s13', 'A/B testinde A grubunun dönüşüm oranı p ile, 20 kullanıcıdan <b>en az 3\'ünün</b> dönüşme olasılığı (binom, 4 basamak)', 'p = ab[ab.variant == "A"].converted.mean(); cevap = 1 - stats.binom.cdf(2, 20, p)', 4)
G('s13', 'Rötar nedeni kayıtları 4 ayda: günlük ortalama "teknik" rötar sayısı λ = teknik kayıt / 122 gün. Bir günde <b>hiç</b> teknik rötar olmaması olasılığı (Poisson, 4 basamak)', 'lam = (delays.reason == "teknik").sum() / 122; cevap = stats.poisson.pmf(0, lam)', 4)
G('s13', 'Aynı λ ile bir günde 3 ya da daha fazla teknik rötar olasılığı (4 basamak)', 'lam = (delays.reason == "teknik").sum() / 122; cevap = 1 - stats.poisson.cdf(2, lam)', 4)
G('s14', 'Çalışan bağlılık puanının (engagement) z puanı 4,5 için kaç? (ortalama ve std ddof = 1 anketin tamamından, boşlar hariç; 3 basamak)', 'e = survey.engagement.dropna(); cevap = (4.5 - e.mean()) / e.std()', 3)
G('s14', 'Bağlılık normal dağılsaydı puanın 3\'ün altında olma olasılığı (aynı ortalama ve std, 4 basamak)', 'e = survey.engagement.dropna(); cevap = stats.norm.cdf(3, e.mean(), e.std())', 4)
G('s14', 'Gerçekte 3\'ün altındaki oran (4 basamak); normal yaklaşımla karşılaştır.', 'cevap = (survey.engagement.dropna() < 3).mean()', 4)
G('s15', 'Teslim edilen siparişlerde ardışık iki sipariş arasındaki süre (dakika) üstel kabul edilirse ortalaması kaç? (placed_at sıralı, farkların ortalaması, 3 basamak)', 's = lk.placed_at.sort_values().diff().dt.total_seconds().dropna() / 60; cevap = s.mean()', 3)
G('s15', 'Kart harcama tutarlarının (mutlak) log ortalaması (doğal log, 3 basamak): lognormal parametresi μ', 'cevap = np.log(txns[txns.txn_type == "kart_harcama"].amount.abs()).mean()', 3)
G('s15', 'Aynı log değerlerin standart sapması σ (ddof = 1, 3 basamak)', 'cevap = np.log(txns[txns.txn_type == "kart_harcama"].amount.abs()).std()', 3)
G('s16', 'Serbestlik derecesi 24 olan t dağılımında %95 iki yönlü kritik değer (3 basamak)', 'cevap = stats.t.ppf(.975, 24)', 3)
G('s16', 'Serbestlik derecesi 4 olan ki-kare dağılımında %95 kritik değer (3 basamak)', 'cevap = stats.chi2.ppf(.95, 4)', 3)
G('s16', 'F(2, 60) dağılımında %95 kritik değer (3 basamak)', 'cevap = stats.f.ppf(.95, 2, 60)', 3)

# 4 · örnekleme ve tahmin
G('s17', 'Tabakalı örnekleme: 2.200 çalışandan 200 kişilik orantılı örneklemde "hibrit" tabakasından kaç kişi seçilir? (yuvarla)', 'cevap = round(200 * (emp.work_mode == "hibrit").mean())', 0)
G('s17', 'Aynı örneklemde "uzaktan" tabakasından kaç kişi seçilir?', 'cevap = round(200 * (emp.work_mode == "uzaktan").mean())', 0)
G('s17', 'Sistematik örneklem: 3.173 uçuştan her 25\'inci (1., 26., 51., ...) seçilirse kaç uçuş seçilir?', 'cevap = len(flights.iloc[::25])', 0)
G('s18', 'Teslim süresi ortalamasının standart hatası (std / √n, ddof = 1, 4 basamak)', 'cevap = teslim.sure.std() / np.sqrt(len(teslim))', 4)
G('s18', 'A grubundaki dönüşüm oranının standart hatası √(p(1−p)/n) (5 basamak)', 'a = ab[ab.variant == "A"].converted; p = a.mean(); cevap = np.sqrt(p * (1 - p) / len(a))', 5)
G('s18', 'Örneklem 4 katına çıksa teslim süresi ortalamasının standart hatası (aynı std ile, 4 basamak)', 'cevap = teslim.sure.std() / np.sqrt(4 * len(teslim))', 4)
G('s19', 'Teslim süresi ortalaması için %95 güven aralığının <b>alt</b> sınırı (t dağılımı, 3 basamak)', 's = teslim.sure; cevap = stats.t.interval(.95, len(s) - 1, s.mean(), s.std() / np.sqrt(len(s)))[0]', 3)
G('s19', 'Aynı aralığın üst sınırı (3 basamak)', 's = teslim.sure; cevap = stats.t.interval(.95, len(s) - 1, s.mean(), s.std() / np.sqrt(len(s)))[1]', 3)
G('s19', 'B grubunun dönüşüm oranı için %95 Wald hata payı (1,96·SE, yüzde puan, 2 basamak)', 'b = ab[ab.variant == "B"].converted; p = b.mean(); cevap = 100 * 1.96 * np.sqrt(p * (1 - p) / len(b))', 2)
G('s20', 'Dönüşüm oranını ±2 puan hata payıyla (%95) ölçmek için gereken örneklem: p = A grubunun oranı (yukarı yuvarla)', 'p = ab[ab.variant == "A"].converted.mean(); cevap = math.ceil(1.96 ** 2 * p * (1 - p) / 0.02 ** 2)', 0)
G('s20', 'Teslim süresi ortalamasını ±1 dakika hata payıyla (%95) tahmin etmek için gereken n (std teslim süresinden, yukarı yuvarla)', 'cevap = math.ceil((1.96 * teslim.sure.std() / 1) ** 2)', 0)
G('s20', 'A ve B oranları arasındaki farkı %80 güç, %5 anlamlılıkla saptamak için grup başına gereken n (Cohen h ile; yukarı yuvarla)', 'from statsmodels.stats.power import NormalIndPower; pa, pb = ab.groupby("variant").converted.mean(); h = 2 * np.arcsin(np.sqrt(pb)) - 2 * np.arcsin(np.sqrt(pa)); cevap = math.ceil(NormalIndPower().solve_power(h, alpha=.05, power=.8))', 0, tol=2)

# 5 · hipotez testi
G('s21', 'A/B: B ile A dönüşüm oranı farkının iki oran z testi istatistiği (birleşik oranla, 3 basamak)', 'x = ab.groupby("variant").converted.agg(["sum", "count"]); p = x["sum"].sum() / x["count"].sum(); se = np.sqrt(p * (1 - p) * (1 / x.loc["A", "count"] + 1 / x.loc["B", "count"])); cevap = (x.loc["B", "sum"] / x.loc["B", "count"] - x.loc["A", "sum"] / x.loc["A", "count"]) / se', 3)
G('s21', 'Aynı testin iki yönlü p değeri (4 basamak)', 'x = ab.groupby("variant").converted.agg(["sum", "count"]); p = x["sum"].sum() / x["count"].sum(); se = np.sqrt(p * (1 - p) * (1 / x.loc["A", "count"] + 1 / x.loc["B", "count"])); z = (x.loc["B", "sum"] / x.loc["B", "count"] - x.loc["A", "sum"] / x.loc["A", "count"]) / se; cevap = 2 * stats.norm.sf(abs(z))', 4)
G('s21', 'Teslim süresi ortalaması 30 dakikadan farklı mı? Tek örneklem t istatistiği (3 basamak)', 'cevap = stats.ttest_1samp(teslim.sure, 30).statistic', 3)
G('s22', 'Beş rötar nedeni için ayrı ayrı test yapılırsa Bonferroni ile her testin anlamlılık eşiği (α = 0,05, 3 basamak)', 'cevap = 0.05 / delays.reason.nunique()', 3)
G('s22', 'Beş bağımsız testte en az bir yanlış pozitif olasılığı (aile boyu hata, α = 0,05, 4 basamak)', 'k = delays.reason.nunique(); cevap = 1 - 0.95 ** k', 4)
G('s22', 'A/B z testinde gücü yaklaşık hesapla: gözlenen etki gerçek olsaydı %5 iki yönlü testte güç (Cohen h, A ve B gerçek n, 3 basamak)', 'from statsmodels.stats.power import NormalIndPower; pa, pb = ab.groupby("variant").converted.mean(); na, nb = ab.variant.value_counts()[["A", "B"]]; h = 2 * np.arcsin(np.sqrt(pb)) - 2 * np.arcsin(np.sqrt(pa)); cevap = NormalIndPower().power(h, nobs1=na, alpha=.05, ratio=nb / na)', 3)
G('s23', 'A/B dönüşüm farkının Cohen h etki büyüklüğü (3 basamak)', 'pa, pb = ab.groupby("variant").converted.mean(); cevap = 2 * np.arcsin(np.sqrt(pb)) - 2 * np.arcsin(np.sqrt(pa))', 3)
G('s23', 'Göreli artış: (pB − pA) / pA × 100 (yüzde, 1 basamak)', 'pa, pb = ab.groupby("variant").converted.mean(); cevap = 100 * (pb - pa) / pa', 1)
G('s23', 'Hibrit ve ofis çalışanlarının bağlılık puanı farkının Cohen d\'si (birleşik std, 3 basamak; anketi emp ile birleştir)', 'd = survey.merge(emp[["emp_id", "work_mode"]], on="emp_id").dropna(subset=["engagement"]); a = d[d.work_mode == "hibrit"].engagement; b = d[d.work_mode == "ofis"].engagement; sp = np.sqrt(((len(a) - 1) * a.var() + (len(b) - 1) * b.var()) / (len(a) + len(b) - 2)); cevap = (a.mean() - b.mean()) / sp', 3)
G('s24', 'Teslim süresinin çarpıklık katsayısı (scipy skew, yanlılık düzeltmesiz, 3 basamak)', 'cevap = stats.skew(teslim.sure)', 3)
G('s24', 'Teslim süresinin basıklığı (fazlalık, scipy kurtosis, 3 basamak)', 'cevap = stats.kurtosis(teslim.sure)', 3)
G('s24', 'Levene testi: kart ve nakit ödemeli teslimlerde süre varyansları eşit mi? p değeri (4 basamak)', 'cevap = stats.levene(teslim[teslim.payment == "kart"].sure, teslim[teslim.payment == "nakit"].sure).pvalue', 4)

# 6 · klasik testler
G('s25', 'Eşleştirilmiş t testi: anketin iki dalgasına (Q2, Q4) da katılan çalışanlarda bağlılık değişiminin (Q4 − Q2) ortalaması (3 basamak)', 'p = survey.pivot_table(index="emp_id", columns="wave", values="engagement").dropna(); cevap = (p["2024-Q4"] - p["2024-Q2"]).mean()', 3)
G('s25', 'Aynı eşleştirilmiş t testinin istatistiği (3 basamak)', 'p = survey.pivot_table(index="emp_id", columns="wave", values="engagement").dropna(); cevap = stats.ttest_rel(p["2024-Q4"], p["2024-Q2"]).statistic', 3)
G('s25', 'Kaç çalışan iki dalgada da bağlılık sorusunu yanıtlamış?', 'p = survey.pivot_table(index="emp_id", columns="wave", values="engagement").dropna(); cevap = len(p)', 0)
G('s26', 'Welch t testi: B grubunda geliri olanlar ile A grubunda geliri olanların ortalama geliri (revenue > 0) farklı mı? t istatistiği (B − A, 3 basamak)', 'a = ab[(ab.variant == "A") & (ab.revenue > 0)].revenue; b = ab[(ab.variant == "B") & (ab.revenue > 0)].revenue; cevap = stats.ttest_ind(b, a, equal_var=False).statistic', 3)
G('s26', 'Aynı testin p değeri (4 basamak)', 'a = ab[(ab.variant == "A") & (ab.revenue > 0)].revenue; b = ab[(ab.variant == "B") & (ab.revenue > 0)].revenue; cevap = stats.ttest_ind(b, a, equal_var=False).pvalue', 4)
G('s26', 'Kart ve nakit ödemeli teslimlerin süre ortalaması farkı (kart − nakit, dakika, 3 basamak)', 'cevap = teslim[teslim.payment == "kart"].sure.mean() - teslim[teslim.payment == "nakit"].sure.mean()', 3)
G('s27', 'Tek yönlü ANOVA: üç ödeme yöntemine göre teslim süresi; F istatistiği (3 basamak)', 'cevap = stats.f_oneway(*[g.sure for _, g in teslim.groupby("payment")]).statistic', 3)
G('s27', 'Aynı ANOVA\'nın p değeri (4 basamak)', 'cevap = stats.f_oneway(*[g.sure for _, g in teslim.groupby("payment")]).pvalue', 4)
G('s27', 'Rötar nedenlerine göre rötar dakikası ANOVA F istatistiği (3 basamak)', 'cevap = stats.f_oneway(*[g.minutes for _, g in delays.groupby("reason")]).statistic', 3)
G('s28', 'Ki-kare bağımsızlık: ödeme yöntemi × durum (teslim/iptal/iade) tablosunun ki-kare istatistiği (3 basamak)', 'cevap = stats.chi2_contingency(pd.crosstab(lk.payment, lk.status)).statistic', 3)
G('s28', 'Aynı testin serbestlik derecesi', 'cevap = stats.chi2_contingency(pd.crosstab(lk.payment, lk.status)).dof', 0)
G('s28', 'Bilet sınıfı × durum (flown/cancelled/no_show) ki-kare p değeri (4 basamak)', 'cevap = stats.chi2_contingency(pd.crosstab(bookings.fare_class, bookings.status)).pvalue', 4)

# 7 · ilişki ve regresyon
G('s29', 'Günlük bisiklet yolculuğu ile günlük ortalama sıcaklık arasındaki Pearson r (3 basamak)', 'cevap = gunluk.yolculuk.corr(gunluk.sicaklik)', 3)
G('s29', 'Aynı ilişkinin Spearman ρ değeri (3 basamak)', 'cevap = gunluk.yolculuk.corr(gunluk.sicaklik, method="spearman")', 3)
G('s29', 'Teslim süresi ile kurye puanı (courier_score) arasındaki Spearman ρ (değerlendirilen teslimler, 3 basamak)', 'd = teslim.merge(ratings, on="order_id"); cevap = d.sure.corr(d.courier_score, method="spearman")', 3)
G('s30', 'Basit regresyon: günlük yolculuk = a + b·sıcaklık. Eğim b (1 °C başına yolculuk, 3 basamak)', 'cevap = smf.ols("yolculuk ~ sicaklik", gunluk).fit().params["sicaklik"]', 3)
G('s30', 'Aynı modelin R² değeri (4 basamak)', 'cevap = smf.ols("yolculuk ~ sicaklik", gunluk).fit().rsquared', 4)
G('s30', 'Modelle 30 °C\'lik bir gün için tahmini yolculuk (1 basamak)', 'm = smf.ols("yolculuk ~ sicaklik", gunluk).fit(); cevap = m.params["Intercept"] + 30 * m.params["sicaklik"]', 1)
G('s31', 'Çoklu regresyon: yolculuk ~ sıcaklık + yağış. Yağış katsayısı (mm başına, 3 basamak)', 'cevap = smf.ols("yolculuk ~ sicaklik + yagis", gunluk).fit().params["yagis"]', 3)
G('s31', 'Aynı modelde sıcaklık katsayısı (3 basamak); basit modeldekinden ne kadar değişti?', 'cevap = smf.ols("yolculuk ~ sicaklik + yagis", gunluk).fit().params["sicaklik"]', 3)
G('s31', 'Aynı modelin düzeltilmiş R² değeri (4 basamak)', 'cevap = smf.ols("yolculuk ~ sicaklik + yagis", gunluk).fit().rsquared_adj', 4)
G('s32', 'Lojistik regresyon: converted ~ variant. B değişkeninin katsayısı (log odds, 4 basamak)', 'cevap = smf.logit("converted ~ C(variant)", ab).fit(disp=0).params["C(variant)[T.B]"]', 4)
G('s32', 'Aynı katsayının odds oranı (exp, 3 basamak)', 'cevap = np.exp(smf.logit("converted ~ C(variant)", ab).fit(disp=0).params["C(variant)[T.B]"])', 3)
G('s32', 'Odds oranını çapraz tablodan elle hesapla: (B dönüşen/B dönüşmeyen) / (A dönüşen/A dönüşmeyen) (3 basamak)', 't = pd.crosstab(ab.variant, ab.converted); cevap = (t.loc["B", 1] / t.loc["B", 0]) / (t.loc["A", 1] / t.loc["A", 0])', 3)

# 8 · deney ve nedensellik
G('s33', 'A/B: dönüşüm farkı (B − A) için %95 Wald güven aralığının alt sınırı (yüzde puan, 2 basamak)', 'x = ab.groupby("variant").converted.agg(["mean", "count"]); pa, na = x.loc["A"]; pb, nb = x.loc["B"]; se = np.sqrt(pa * (1 - pa) / na + pb * (1 - pb) / nb); cevap = 100 * (pb - pa - 1.96 * se)', 2)
G('s33', 'Aynı aralığın üst sınırı (yüzde puan, 2 basamak)', 'x = ab.groupby("variant").converted.agg(["mean", "count"]); pa, na = x.loc["A"]; pb, nb = x.loc["B"]; se = np.sqrt(pa * (1 - pa) / na + pb * (1 - pb) / nb); cevap = 100 * (pb - pa + 1.96 * se)', 2)
G('s33', 'Örneklem oranı uyumsuzluğu (SRM) denetimi: 50/50 beklenen bölünmede ki-kare uygunluk p değeri (4 basamak)', 'n = ab.variant.value_counts(); cevap = stats.chisquare([n["A"], n["B"]]).pvalue', 4)
G('s34', 'Bloklama: kalkış saatini sabah (< 12) ve öğleden sonra (≥ 12) bloklarına ayır; sabah bloğundaki inen uçuşların ortalama gecikmesi (dakika, 2 basamak)', 'cevap = inen[inen.sched_dep.dt.hour < 12].gecikme.mean()', 2)
G('s34', 'Öğleden sonra bloğunun ortalama gecikmesi (dakika, 2 basamak)', 'cevap = inen[inen.sched_dep.dt.hour >= 12].gecikme.mean()', 2)
G('s34', 'İki yönlü ANOVA benzeri etkileşim: gecikme ~ blok × hafta sonu modelinde etkileşim katsayısı (3 basamak)', 'd = inen.assign(blok=(inen.sched_dep.dt.hour >= 12).astype(int), hs=(inen.sched_dep.dt.dayofweek >= 5).astype(int)); cevap = smf.ols("gecikme ~ blok * hs", d).fit().params["blok:hs"]', 3)
G('s35', 'Farkların farkı: sipariş kanalı mobil ve web için 2023 ve 2024 sipariş sayıları. (mobil 2024 − mobil 2023) − (web 2024 − web 2023)', 'c = orders.assign(y=orders.order_date.dt.year).pivot_table(index="channel", columns="y", values="order_id", aggfunc="count"); cevap = (c.loc["mobile", 2024] - c.loc["mobile", 2023]) - (c.loc["web", 2024] - c.loc["web", 2023])', 0)
G('s35', 'Mobil kanalın 2023 → 2024 sipariş artışı (adet)', 'c = orders.assign(y=orders.order_date.dt.year).pivot_table(index="channel", columns="y", values="order_id", aggfunc="count"); cevap = c.loc["mobile", 2024] - c.loc["mobile", 2023]', 0)
G('s35', 'Web kanalının 2023 → 2024 sipariş artışı (adet)', 'c = orders.assign(y=orders.order_date.dt.year).pivot_table(index="channel", columns="y", values="order_id", aggfunc="count"); cevap = c.loc["web", 2024] - c.loc["web", 2023]', 0)
G('s36', 'Seçilim yanlılığı: yalnız değerlendirme bırakan teslimlerde ortalama teslim süresi (dakika, 2 basamak)', 'cevap = teslim[teslim.order_id.isin(ratings.order_id)].sure.mean()', 2)
G('s36', 'Değerlendirme bırakmayan teslimlerde ortalama teslim süresi (dakika, 2 basamak)', 'cevap = teslim[~teslim.order_id.isin(ratings.order_id)].sure.mean()', 2)
G('s36', 'Değerlendirme bırakma oranı: 45 dakikadan uzun teslimlerde (yüzde, 1 basamak)', 'cevap = 100 * teslim[teslim.sure > 45].order_id.isin(ratings.order_id).mean()', 1)

# 9 · zaman serisi
G('s37', 'Günlük bisiklet yolculuğu serisinin gecikme 1 otokorelasyonu (pandas autocorr, 3 basamak)', 'cevap = gunluk.yolculuk.autocorr(1)', 3)
G('s37', 'Gecikme 7 otokorelasyonu (haftalık desen, 3 basamak)', 'cevap = gunluk.yolculuk.autocorr(7)', 3)
G('s37', 'Haftanın gününe göre ortalama yolculuk: en yüksek gün ile en düşük gün ortalaması farkı (1 basamak)', 'm = gunluk.groupby(gunluk.tarih.dt.dayofweek).yolculuk.mean(); cevap = m.max() - m.min()', 1)
G('s38', 'Naif tahmin: yarın = bugün. Günlük yolculuk serisinde naif tahminin ortalama mutlak hatası (MAE, 2 basamak)', 'cevap = gunluk.yolculuk.diff().abs().mean()', 2)
G('s38', 'Mevsimsel naif tahmin (geçen haftanın aynı günü) MAE (2 basamak)', 'cevap = gunluk.yolculuk.diff(7).abs().mean()', 2)
G('s38', 'Basit üstel düzeltme (α = 0,3, ilk değer ilk gözlem): son gün için düzeltilmiş değer (2 basamak)', 's = gunluk.yolculuk.astype(float); cevap = s.ewm(alpha=0.3, adjust=False).mean().iloc[-1]', 2)
G('s39', 'Yolculuk serisinin birinci farkının standart sapması (ddof = 1, 2 basamak)', 'cevap = gunluk.yolculuk.diff().std()', 2)
G('s39', 'ADF durağanlık testi istatistiği (statsmodels adfuller varsayılan, 3 basamak); %5 kritik değerden küçükse durağan', 'from statsmodels.tsa.stattools import adfuller; cevap = adfuller(gunluk.yolculuk)[0]', 3)
G('s39', 'AR(1) modeli: yolculuk ~ dünkü yolculuk regresyonunda eğim (3 basamak)', 'd = gunluk.assign(dun=gunluk.yolculuk.shift(1)).dropna(); cevap = smf.ols("yolculuk ~ dun", d).fit().params["dun"]', 3)
G('s40', 'Son 14 günü test olarak ayır: eğitim ortalamasıyla tahminin test MAE değeri (2 basamak)', 'tr, te = gunluk.yolculuk[:-14], gunluk.yolculuk[-14:]; cevap = (te - tr.mean()).abs().mean()', 2)
G('s40', 'Aynı test döneminde mevsimsel naif tahmin MAE (2 basamak)', 's = gunluk.yolculuk; cevap = (s - s.shift(7))[-14:].abs().mean()', 2)
G('s40', 'Mevsimsel naif tahminin MAPE değeri, son 14 gün (yüzde, 2 basamak)', 's = gunluk.yolculuk; e = (s - s.shift(7))[-14:]; cevap = 100 * (e.abs() / s[-14:]).mean()', 2)

# 10 · Bayes ve yeniden örnekleme
G('s41', 'Beta(1, 1) önsel ile A grubunun dönüşüm oranı için sonsal Beta(a, b): sonsal ortalama (4 basamak)', 'a = ab[ab.variant == "A"].converted; cevap = (1 + a.sum()) / (2 + len(a))', 4)
G('s41', 'B grubunun sonsal ortalaması (Beta(1, 1) önsel, 4 basamak)', 'b = ab[ab.variant == "B"].converted; cevap = (1 + b.sum()) / (2 + len(b))', 4)
G('s41', 'Beta(10, 90) önsel (önceki kampanya: %10) ile A grubunun sonsal ortalaması (4 basamak)', 'a = ab[ab.variant == "A"].converted; cevap = (10 + a.sum()) / (100 + len(a))', 4)
G('s42', 'B grubu için %95 güvenilir aralığın alt sınırı (Beta(1, 1) önsel, eşit kuyruk, 4 basamak)', 'b = ab[ab.variant == "B"].converted; cevap = stats.beta.ppf(.025, 1 + b.sum(), 1 + len(b) - b.sum())', 4)
G('s42', 'Aynı aralığın üst sınırı (4 basamak)', 'b = ab[ab.variant == "B"].converted; cevap = stats.beta.ppf(.975, 1 + b.sum(), 1 + len(b) - b.sum())', 4)
G('s42', 'P(pB > pA): sonsallardan 200.000 çekiliş (tohum 42, önce A sonra B), oran (3 basamak)', 'rng = np.random.default_rng(42); a = ab[ab.variant == "A"].converted; b = ab[ab.variant == "B"].converted; xa = rng.beta(1 + a.sum(), 1 + len(a) - a.sum(), 200000); xb = rng.beta(1 + b.sum(), 1 + len(b) - b.sum(), 200000); cevap = (xb > xa).mean()', 3, tol=0.005)
G('s43', 'Bootstrap: teslim süresi medyanının 2.000 tekrarlı bootstrap standart hatası (tohum 7, 2 basamak)', 'rng = np.random.default_rng(7); s = teslim.sure.to_numpy(); cevap = np.std([np.median(rng.choice(s, len(s))) for _ in range(2000)], ddof=1)', 2, tol=0.03)
G('s43', 'Aynı bootstrap dağılımından medyan için %95 yüzdelik aralığın alt sınırı (2 basamak)', 'rng = np.random.default_rng(7); s = teslim.sure.to_numpy(); b = [np.median(rng.choice(s, len(s))) for _ in range(2000)]; cevap = np.percentile(b, 2.5)', 2, tol=0.1)
G('s43', 'Bootstrap ile A/B dönüşüm farkının standart hatası (3.000 tekrar, tohum 11, yüzde puan, 2 basamak)', 'rng = np.random.default_rng(11); a = ab[ab.variant == "A"].converted.to_numpy(); b = ab[ab.variant == "B"].converted.to_numpy(); d = [rng.choice(b, len(b)).mean() - rng.choice(a, len(a)).mean() for _ in range(3000)]; cevap = 100 * np.std(d, ddof=1)', 2, tol=0.05)
G('s44', 'Permütasyon testi: A/B dönüşüm farkı için 5.000 karıştırma (tohum 3); |fark| ≥ gözlenen oranı (p değeri, 3 basamak)', 'rng = np.random.default_rng(3); y = ab.converted.to_numpy(); g = (ab.variant == "B").to_numpy(); obs = y[g].mean() - y[~g].mean(); cnt = 0\nfor _ in range(5000):\n    p = rng.permutation(g); cnt += abs(y[p].mean() - y[~p].mean()) >= abs(obs)\ncevap = cnt / 5000', 3, tol=0.004)
G('s44', 'Gözlenen dönüşüm farkı (B − A, yüzde puan, 2 basamak)', 'pa, pb = ab.groupby("variant").converted.mean(); cevap = 100 * (pb - pa)', 2)
G('s44', 'Monte Carlo: günlük teknik rötar Poisson(λ) ise 30 günde toplamın 60\'ı aşma olasılığı (λ s13\'teki gibi, kesin hesap: Poisson(30λ), 4 basamak)', 'lam = (delays.reason == "teknik").sum() / 122; cevap = stats.poisson.sf(60, 30 * lam)', 4)

# 11 · çok değişkenli ve öğrenme
G('s45', 'Ölçekleme: günlük tablo (yolculuk, ort_km, sicaklik, yagis) standartlaştırılırsa (z, ddof = 0) PCA\'da birinci bileşenin açıkladığı varyans oranı (3 basamak)', 'from sklearn.decomposition import PCA; X = gunluk[["yolculuk", "ort_km", "sicaklik", "yagis"]]; Z = (X - X.mean()) / X.std(ddof=0); cevap = PCA().fit(Z).explained_variance_ratio_[0]', 3)
G('s45', 'Aynı PCA\'da ilk iki bileşenin toplam açıkladığı varyans oranı (3 basamak)', 'from sklearn.decomposition import PCA; X = gunluk[["yolculuk", "ort_km", "sicaklik", "yagis"]]; Z = (X - X.mean()) / X.std(ddof=0); cevap = PCA().fit(Z).explained_variance_ratio_[:2].sum()', 3)
G('s45', 'Ölçeklemeden PCA: birinci bileşenin açıkladığı oran (3 basamak). Neden bu kadar yüksek?', 'from sklearn.decomposition import PCA; X = gunluk[["yolculuk", "ort_km", "sicaklik", "yagis"]]; cevap = PCA().fit(X - X.mean()).explained_variance_ratio_[0]', 3)
G('s46', 'k-ortalamalar (k = 3, random_state = 0, n_init = 10): standartlaştırılmış (yolculuk, sicaklik) ile en büyük kümenin gün sayısı', 'from sklearn.cluster import KMeans; X = gunluk[["yolculuk", "sicaklik"]]; Z = (X - X.mean()) / X.std(ddof=0); cevap = np.bincount(KMeans(3, random_state=0, n_init=10).fit_predict(Z)).max()', 0, tol=3)
G('s46', 'İki gün arasındaki Öklit uzaklığı: ilk iki günün standartlaştırılmış (yolculuk, sicaklik) değerleri (3 basamak)', 'X = gunluk[["yolculuk", "sicaklik"]]; Z = (X - X.mean()) / X.std(ddof=0); cevap = np.sqrt(((Z.iloc[0] - Z.iloc[1]) ** 2).sum())', 3)
G('s46', 'Aynı iki gün ölçeklenmeden Öklit uzaklığı (2 basamak). Hangi değişken baskın?', 'X = gunluk[["yolculuk", "sicaklik"]]; cevap = np.sqrt(((X.iloc[0] - X.iloc[1]) ** 2).sum())', 2)
G('s47', 'Ridge (alpha = 10) ile standartlaştırılmış sıcaklık ve yağıştan yolculuk tahmini: sıcaklık katsayısı (2 basamak)', 'from sklearn.linear_model import Ridge; X = gunluk[["sicaklik", "yagis"]]; Z = (X - X.mean()) / X.std(ddof=0); cevap = Ridge(alpha=10).fit(Z, gunluk.yolculuk).coef_[0]', 2)
G('s47', 'Aynı modelde alpha = 0 (sıradan en küçük kareler) sıcaklık katsayısı (2 basamak)', 'from sklearn.linear_model import LinearRegression; X = gunluk[["sicaklik", "yagis"]]; Z = (X - X.mean()) / X.std(ddof=0); cevap = LinearRegression().fit(Z, gunluk.yolculuk).coef_[0]', 2)
G('s47', 'Lasso (alpha = 50) ile yağış katsayısı (2 basamak; sıfıra iner mi?)', 'from sklearn.linear_model import Lasso; X = gunluk[["sicaklik", "yagis"]]; Z = (X - X.mean()) / X.std(ddof=0); cevap = Lasso(alpha=50).fit(Z, gunluk.yolculuk).coef_[1]', 2)
G('s48', 'Hotelling yerine basit kontrol: hibrit ve ofis çalışanlarının (engagement, manager_score) ortalama vektörleri arasındaki Öklit farkı (3 basamak)', 'd = survey.merge(emp[["emp_id", "work_mode"]], on="emp_id").dropna(subset=["engagement", "manager_score"]); m = d.groupby("work_mode")[["engagement", "manager_score"]].mean(); cevap = np.sqrt(((m.loc["hibrit"] - m.loc["ofis"]) ** 2).sum())', 3)
G('s48', 'Hiyerarşik özet: çalışma modeline göre bağlılık ortalamalarının ağırlıksız ortalaması (3 basamak)', 'd = survey.merge(emp[["emp_id", "work_mode"]], on="emp_id"); cevap = d.groupby("work_mode").engagement.mean().mean()', 3)
G('s48', 'engagement ile manager_score arasındaki korelasyon (3 basamak)', 'cevap = survey.engagement.corr(survey.manager_score)', 3)

# 12 · kalite
G('s49', 'I-MR kontrol grafiği: günlük yolculuk için ortalama hareketli aralık (MR̄, 2 basamak)', 'cevap = gunluk.yolculuk.diff().abs().mean()', 2)
G('s49', 'Bireysel değer grafiğinin üst kontrol sınırı UCL = x̄ + 2,66·MR̄ (1 basamak)', 's = gunluk.yolculuk; cevap = s.mean() + 2.66 * s.diff().abs().mean()', 1)
G('s49', 'Alt kontrol sınırının (x̄ − 2,66·MR̄) altında kalan gün sayısı', 's = gunluk.yolculuk; cevap = (s < s.mean() - 2.66 * s.diff().abs().mean()).sum()', 0)
G('s50', 'Teslim süresi için üst spesifikasyon 60 dk: Cpk = (USL − x̄) / (3s) (tek taraflı, 3 basamak)', 'cevap = (60 - teslim.sure.mean()) / (3 * teslim.sure.std())', 3)
G('s50', 'Spesifikasyon dışı (60 dk üstü) teslim oranı (ppm, tam sayı)', 'cevap = 1e6 * (teslim.sure > 60).mean()', 0)
G('s50', 'Normal varsayımla Cpk\'dan beklenen spesifikasyon dışı oranı (ppm, tam sayı); gerçek oranla karşılaştır.', 'cpk = (60 - teslim.sure.mean()) / (3 * teslim.sure.std()); cevap = 1e6 * stats.norm.sf(3 * cpk)', 0)
G('s51', 'Ölçüm tekrarlanabilirliği: iki dalgaya da yanıt veren çalışanlarda bağlılık puanı farklarının standart sapması / √2 (3 basamak)', 'p = survey.pivot_table(index="emp_id", columns="wave", values="engagement").dropna(); cevap = (p["2024-Q4"] - p["2024-Q2"]).std() / np.sqrt(2)', 3)
G('s51', 'Kişiler arası standart sapma (iki dalganın ortalamasının std, 3 basamak)', 'p = survey.pivot_table(index="emp_id", columns="wave", values="engagement").dropna(); cevap = p.mean(axis=1).std()', 3)
G('s51', 'İki dalga arasındaki korelasyon (test-yeniden test güvenirliği, 3 basamak)', 'p = survey.pivot_table(index="emp_id", columns="wave", values="engagement").dropna(); cevap = p["2024-Q2"].corr(p["2024-Q4"])', 3)
G('s52', 'Sağkalım: Pusula İK\'da ayrılan çalışanların hizmet süresi (gün) medyanı (tam sayı)', 'a = emp.dropna(subset=["term_date"]); cevap = (a.term_date - a.hire_date).dt.days.median()', 0)
G('s52', 'Kaplan–Meier: 365. günde hâlâ çalışıyor olma olasılığı (sansür: ayrılmamış, son tarih 2024-12-31; 3 basamak)', 'son = pd.Timestamp("2024-12-31"); t = ((emp.term_date.fillna(son) - emp.hire_date).dt.days).to_numpy(); e = emp.term_date.notna().to_numpy(); S = 1.0\nfor u in np.sort(np.unique(t[e & (t <= 365)])):\n    S *= 1 - ((t == u) & e).sum() / (t >= u).sum()\ncevap = S', 3)
G('s52', 'Sansürlü (hâlâ çalışan) gözlem oranı (yüzde, 1 basamak)', 'cevap = 100 * emp.term_date.isna().mean()', 1)

# 13 · modelleme pratiği
G('s53', 'Sızıntı denetimi: revenue > 0 olan satır sayısı kaç? converted toplamıyla aynıysa revenue hedefin kopyasıdır, özellik olarak kullanılamaz.', 'cevap = (ab.revenue > 0).sum()', 0)
G('s53', '5 katlı çapraz doğrulama (KFold, shuffle, random_state = 0): yolculuk ~ sıcaklık doğrusal modelinin ortalama R² değeri (3 basamak)', 'from sklearn.model_selection import cross_val_score, KFold; from sklearn.linear_model import LinearRegression; cevap = cross_val_score(LinearRegression(), gunluk[["sicaklik"]], gunluk.yolculuk, cv=KFold(5, shuffle=True, random_state=0), scoring="r2").mean()', 3)
G('s53', 'Zaman sırasını koruyan TimeSeriesSplit (5 bölme) ile aynı modelin ortalama R² değeri (3 basamak)', 'from sklearn.model_selection import cross_val_score, TimeSeriesSplit; from sklearn.linear_model import LinearRegression; cevap = cross_val_score(LinearRegression(), gunluk[["sicaklik"]], gunluk.yolculuk, cv=TimeSeriesSplit(5), scoring="r2").mean()', 3)
G('s54', 'Eşik: lojistik model converted ~ variant olasılıklarıyla 0,13 eşiğinde pozitif tahmin oranı (yüzde, 1 basamak)', 'p = smf.logit("converted ~ C(variant)", ab).fit(disp=0).predict(ab); cevap = 100 * (p > 0.13).mean()', 1)
G('s54', 'Aynı eşikte duyarlılık (recall, yüzde, 1 basamak)', 'p = smf.logit("converted ~ C(variant)", ab).fit(disp=0).predict(ab); y = ab.converted; cevap = 100 * ((p > 0.13) & (y == 1)).sum() / (y == 1).sum()', 1)
G('s54', 'Aynı modelin Brier skoru (tahmin olasılığı ile 0/1 sonuç farkının karesinin ortalaması, 5 basamak)', 'p = smf.logit("converted ~ C(variant)", ab).fit(disp=0).predict(ab); cevap = ((p - ab.converted) ** 2).mean()', 5)
G('s55', 'Dağılım kayması: Haziran ve Ağustos günlük yolculuk ortalamaları farkı (Ağustos − Haziran, 1 basamak)', 'm = gunluk.groupby(gunluk.tarih.dt.month).yolculuk.mean(); cevap = m[8] - m[6]', 1)
G('s55', 'İki ayın günlük yolculuk dağılımı için Kolmogorov–Smirnov istatistiği (3 basamak)', 'a = gunluk[gunluk.tarih.dt.month == 6].yolculuk; b = gunluk[gunluk.tarih.dt.month == 8].yolculuk; cevap = stats.ks_2samp(a, b).statistic', 3)
G('s55', 'Adalet denetimi: kadın ve erkek çalışanların gönüllü ayrılma oranı farkı (K − E, yüzde puan, 2 basamak)', 'r = emp.assign(g=(emp.term_type == "gönüllü")).groupby("gender").g.mean(); cevap = 100 * (r["K"] - r["E"])', 2)
G('s56', 'Karar notu sayısı 1: A/B dönüşüm farkı (yüzde puan, 2 basamak)', 'pa, pb = ab.groupby("variant").converted.mean(); cevap = 100 * (pb - pa)', 2)
G('s56', 'Karar notu sayısı 2: kullanıcı başına gelir farkı (B − A, tüm kullanıcılar, TL, 2 basamak)', 'cevap = ab[ab.variant == "B"].revenue.mean() - ab[ab.variant == "A"].revenue.mean()', 2)
G('s56', 'Karar notu sayısı 3: B\'ye geçilirse 10.000 kullanıcıda beklenen ek dönüşüm (tam sayı)', 'pa, pb = ab.groupby("variant").converted.mean(); cevap = round(10000 * (pb - pa))', 0)

# 14 · olasılık ileri
G('s57', '5 rötar nedeninden 2\'sini öncelik listesine almanın sırasız yol sayısı', 'cevap = math.comb(delays.reason.nunique(), 2)', 0)
G('s57', 'Aynı 5 nedenden ilk 3 sırayı dizmenin (sıralı) yol sayısı', 'cevap = math.perm(delays.reason.nunique(), 3)', 0)
G('s57', '60 kuryeden 3 kişilik ekip kaç farklı şekilde seçilir?', 'cevap = math.comb(len(couriers), 3)', 0)
G('s58', 'Ortak dağılım: bilet sınıfı × durum tablosunda P(Business ve no_show) (4 basamak)', 'cevap = ((bookings.fare_class == "Business") & (bookings.status == "no_show")).mean()', 4)
G('s58', 'Marjinal: P(no_show) (4 basamak)', 'cevap = (bookings.status == "no_show").mean()', 4)
G('s58', 'Koşullu: P(no_show | Eko) (4 basamak)', 'cevap = (bookings[bookings.fare_class == "Eko"].status == "no_show").mean()', 4)
G('s59', 'Log dönüşümü: kart harcama tutarlarının geometrik ortalaması (exp(log ortalaması), TL, 2 basamak)', 'cevap = np.exp(np.log(txns[txns.txn_type == "kart_harcama"].amount.abs()).mean())', 2)
G('s59', 'Aynı tutarların aritmetik ortalaması (TL, 2 basamak)', 'cevap = txns[txns.txn_type == "kart_harcama"].amount.abs().mean()', 2)
G('s59', 'Delta yöntemi: A grubunda log odds\'un standart hatası 1/√(n·p(1−p)) (4 basamak)', 'a = ab[ab.variant == "A"].converted; p = a.mean(); cevap = 1 / np.sqrt(len(a) * p * (1 - p))', 4)
G('s60', 'Büyük sayılar: ilk 100 teslimin süre ortalaması ile tüm teslimlerin ortalaması farkının mutlak değeri (dakika, 3 basamak)', 'cevap = abs(teslim.sure.iloc[:100].mean() - teslim.sure.mean())', 3)
G('s60', 'Chebyshev: teslim süresinin ortalamadan 2 standart sapma uzakta olma oranının üst sınırı (yüzde)', 'cevap = 100 / 2 ** 2', 0)
G('s60', 'Gerçekte ortalamadan 2 std\'den uzak teslimlerin oranı (yüzde, 2 basamak)', 's = teslim.sure; cevap = 100 * ((s - s.mean()).abs() > 2 * s.std()).mean()', 2)

# 15 · çıkarım teorisi
G('s61', 'Yanlılık: teslim süresi varyansının ddof = 0 ile ddof = 1 tahminleri farkı (3 basamak)', 's = teslim.sure; cevap = s.var(ddof=1) - s.var(ddof=0)', 3)
G('s61', 'İlk 30 teslimin örneklem ortalamasının ortalama kare hatası (tüm teslim ortalaması doğru değer kabul edilirse, 3 basamak)', 'cevap = (teslim.sure.iloc[:30].mean() - teslim.sure.mean()) ** 2', 3)
G('s61', 'n = 30 için ortalamanın teorik varyansı σ²/n (σ tüm teslimlerden, ddof = 0, 3 basamak)', 'cevap = teslim.sure.var(ddof=0) / 30', 3)
G('s62', 'En çok olabilirlik: rötar dakikasına üstel dağılım uydurulursa λ̂ = 1 / ortalama (4 basamak)', 'cevap = 1 / delays.minutes.mean()', 4)
G('s62', 'Momentler yöntemi: Poisson λ, günlük teknik rötar sayısının ortalaması (122 gün, 4 basamak)', 'cevap = (delays.reason == "teknik").sum() / 122', 4)
G('s62', 'Kart harcama tutarlarına (mutlak) lognormal uydurmada σ̂ (MLE, ddof = 0, 4 basamak)', 'cevap = np.log(txns[txns.txn_type == "kart_harcama"].amount.abs()).std(ddof=0)', 4)
G('s63', 'Bernoulli Fisher bilgisi: A grubunda n / (p(1−p)) (1 basamak)', 'a = ab[ab.variant == "A"].converted; p = a.mean(); cevap = len(a) / (p * (1 - p))', 1)
G('s63', 'Olabilirlik oranı testi: converted ~ variant lojistik modelinin LR istatistiği (3 basamak)', 'cevap = smf.logit("converted ~ C(variant)", ab).fit(disp=0).llr', 3)
G('s63', 'Aynı LR testinin p değeri (4 basamak)', 'cevap = smf.logit("converted ~ C(variant)", ab).fit(disp=0).llr_pvalue', 4)
G('s64', 'AIC: yolculuk ~ sıcaklık modeli (statsmodels, 2 basamak)', 'cevap = smf.ols("yolculuk ~ sicaklik", gunluk).fit().aic', 2)
G('s64', 'AIC: yolculuk ~ sıcaklık + yağış modeli (2 basamak); hangisi seçilir?', 'cevap = smf.ols("yolculuk ~ sicaklik + yagis", gunluk).fit().aic', 2)
G('s64', 'BIC: yolculuk ~ sıcaklık + yağış modeli (2 basamak)', 'cevap = smf.ols("yolculuk ~ sicaklik + yagis", gunluk).fit().bic', 2)

# 16 · parametrik olmayan
G('s65', 'Mann–Whitney U: kart ve nakit ödemeli teslimlerin süreleri; iki yönlü p değeri (4 basamak)', 'cevap = stats.mannwhitneyu(teslim[teslim.payment == "kart"].sure, teslim[teslim.payment == "nakit"].sure).pvalue', 4)
G('s65', 'Wilcoxon işaretli sıralar: iki dalgadaki bağlılık değişimi; p değeri (4 basamak)', 'p = survey.pivot_table(index="emp_id", columns="wave", values="engagement").dropna(); cevap = stats.wilcoxon(p["2024-Q4"], p["2024-Q2"]).pvalue', 4)
G('s65', 'Kart − nakit teslim süresi medyanları farkı (dakika, 2 basamak)', 'cevap = teslim[teslim.payment == "kart"].sure.median() - teslim[teslim.payment == "nakit"].sure.median()', 2)
G('s66', 'Kruskal–Wallis: rötar nedenlerine göre dakika; H istatistiği (3 basamak)', 'cevap = stats.kruskal(*[g.minutes for _, g in delays.groupby("reason")]).statistic', 3)
G('s66', 'Aynı testin p değeri (4 basamak)', 'cevap = stats.kruskal(*[g.minutes for _, g in delays.groupby("reason")]).pvalue', 4)
G('s66', 'Medyan rötar dakikası en yüksek nedenin medyanı (dakika, 1 basamak)', 'cevap = delays.groupby("reason").minutes.median().max()', 1)
G('s67', '%10 kırpılmış ortalama: teslim süresi (her uçtan %10, 3 basamak)', 'cevap = stats.trim_mean(teslim.sure, 0.1)', 3)
G('s67', 'Medyan mutlak sapma (MAD, ölçeklemesiz, 3 basamak)', 's = teslim.sure; cevap = (s - s.median()).abs().median()', 3)
G('s67', 'Rötar dakikasında ortalama ile %20 kırpılmış ortalama farkı (2 basamak)', 'cevap = delays.minutes.mean() - stats.trim_mean(delays.minutes, 0.2)', 2)
G('s68', 'Eşdeğerlik (TOST): kart ve cüzdan teslim süreleri ±0,5 dakika içinde eşdeğer mi? İki tek yönlü testten büyük olan p değeri (4 basamak)', 'from statsmodels.stats.weightstats import ttost_ind; cevap = ttost_ind(teslim[teslim.payment == "kart"].sure, teslim[teslim.payment == "cüzdan"].sure, -0.5, 0.5, usevar="unequal")[0]', 4)
G('s68', 'Kart − cüzdan ortalama teslim süresi farkı (dakika, 3 basamak)', 'cevap = teslim[teslim.payment == "kart"].sure.mean() - teslim[teslim.payment == "cüzdan"].sure.mean()', 3)
G('s68', 'Aşağı kalmama: B grubu dönüşümü A\'dan en fazla 2 puan kötü olabilir. (pB − pA + 0,02) / SE z istatistiği (3 basamak)', 'x = ab.groupby("variant").converted.agg(["mean", "count"]); pa, na = x.loc["A"]; pb, nb = x.loc["B"]; se = np.sqrt(pa * (1 - pa) / na + pb * (1 - pb) / nb); cevap = (pb - pa + 0.02) / se', 3)

# 17 · ileri regresyon
G('s69', 'Etkileşim: yolculuk ~ sıcaklık × yağış (yağış > 0 göstergesi) modelinde etkileşim katsayısı (3 basamak)', 'd = gunluk.assign(yg=(gunluk.yagis > 0).astype(int)); cevap = smf.ols("yolculuk ~ sicaklik * yg", d).fit().params["sicaklik:yg"]', 3)
G('s69', 'Polinom: yolculuk ~ sıcaklık + sıcaklık² modelinde kare terimin katsayısı (3 basamak)', 'cevap = smf.ols("yolculuk ~ sicaklik + I(sicaklik ** 2)", gunluk).fit().params["I(sicaklik ** 2)"]', 3)
G('s69', 'Polinom modelin R² değeri (4 basamak)', 'cevap = smf.ols("yolculuk ~ sicaklik + I(sicaklik ** 2)", gunluk).fit().rsquared', 4)
G('s70', 'Poisson regresyon: günlük yolculuk ~ sıcaklık; sıcaklık katsayısı (log ölçek, 5 basamak)', 'import statsmodels.api as sm; cevap = smf.glm("yolculuk ~ sicaklik", gunluk, family=sm.families.Poisson()).fit().params["sicaklik"]', 5)
G('s70', 'Aşırı yayılım: aynı modelin Pearson χ² / serbestlik derecesi (2 basamak)', 'import statsmodels.api as sm; m = smf.glm("yolculuk ~ sicaklik", gunluk, family=sm.families.Poisson()).fit(); cevap = m.pearson_chi2 / m.df_resid', 2)
G('s70', 'Sıcaklık 1 °C artınca beklenen yolculuk yüzde kaç değişir? (exp(β) − 1, yüzde, 3 basamak)', 'import statsmodels.api as sm; b = smf.glm("yolculuk ~ sicaklik", gunluk, family=sm.families.Poisson()).fit().params["sicaklik"]; cevap = 100 * (np.exp(b) - 1)', 3)
G('s71', 'Kısmi havuzlama sezgisi: kurye başına ortalama teslim süresinin kuryeler arası standart sapması (en az 1 teslim, 3 basamak)', 'cevap = teslim.groupby("courier_id").sure.mean().std()', 3)
G('s71', 'Karma model: sure ~ 1 + (1 | kurye) rastgele kesişim varyansı (statsmodels MixedLM, 3 basamak)', 'd = teslim.dropna(subset=["courier_id"]); cevap = smf.mixedlm("sure ~ 1", d, groups=d.courier_id).fit().cov_re.iloc[0, 0]', 3, tol=0.05)
G('s71', 'En az teslimi olan kuryenin teslim sayısı (küçük grup = daha çok büzülme)', 'cevap = teslim.groupby("courier_id").size().min()', 0)
G('s72', 'Kantil regresyon: teslim süresinin 0,9 kantili ~ ödeme kart göstergesi; kart katsayısı (3 basamak)', 'd = teslim.assign(kart=(teslim.payment == "kart").astype(int)); cevap = smf.quantreg("sure ~ kart", d).fit(q=0.9).params["kart"]', 3, tol=0.05)
G('s72', 'Teslim süresinin 0,9 kantili (tüm teslimler, 2 basamak)', 'cevap = teslim.sure.quantile(0.9)', 2)
G('s72', 'Medyan regresyon (q = 0,5) kesişimi: nakit ve cüzdan teslimlerinin medyanına yakın (3 basamak)', 'd = teslim.assign(kart=(teslim.payment == "kart").astype(int)); cevap = smf.quantreg("sure ~ kart", d).fit(q=0.5).params["Intercept"]', 3, tol=0.05)

# 18 · Bayes ileri
G('s73', 'Eşlenik Gamma(2, 1) önsel ile günlük teknik rötar oranının sonsal ortalaması (122 gün, (2 + toplam) / (1 + 122), 4 basamak)', 'k = (delays.reason == "teknik").sum(); cevap = (2 + k) / (1 + 122)', 4)
G('s73', 'Hiyerarşik büzülme: Beta(1, 1) ile her ödeme yönteminin iptal oranı sonsal ortalaması; nakit için (4 basamak)', 'n = lk[lk.payment == "nakit"]; cevap = (1 + (n.status == "iptal").sum()) / (2 + len(n))', 4)
G('s73', 'Ödeme yöntemleri arasında ham iptal oranlarının standart sapması (ddof = 1, 4 basamak)', 'cevap = lk.assign(i=lk.status == "iptal").groupby("payment").i.mean().std()', 4)
G('s74', 'MCMC sezgisi: B grubunun dönüşüm oranı için Metropolis (10.000 adım, adım std 0,02, tohum 1, ilk 2.000 atılır) zincir ortalaması (3 basamak)', 'rng = np.random.default_rng(1); b = ab[ab.variant == "B"].converted; k, n = b.sum(), len(b)\nll = lambda p: k * np.log(p) + (n - k) * np.log(1 - p) if 0 < p < 1 else -np.inf\np, z = 0.5, []\nfor _ in range(10000):\n    q = p + rng.normal(0, 0.02)\n    if np.log(rng.random()) < ll(q) - ll(p): p = q\n    z.append(p)\ncevap = np.mean(z[2000:])', 3, tol=0.003)
G('s74', 'Aynı problemin kesin sonsal ortalaması (Beta(1, 1), 4 basamak)', 'b = ab[ab.variant == "B"].converted; cevap = (1 + b.sum()) / (2 + len(b))', 4)
G('s74', 'Kesin sonsal standart sapması (4 basamak)', 'b = ab[ab.variant == "B"].converted; cevap = stats.beta.std(1 + b.sum(), 1 + len(b) - b.sum())', 4)
G('s75', 'Sonsal öngörü: B grubunda 1.000 yeni kullanıcıda beklenen dönüşen sayısı (sonsal ortalama × 1.000, 1 basamak)', 'b = ab[ab.variant == "B"].converted; cevap = 1000 * (1 + b.sum()) / (2 + len(b))', 1)
G('s75', 'Beta-binom öngörü dağılımında 1.000 kullanıcıdan 130\'dan az dönüşme olasılığı (4 basamak)', 'b = ab[ab.variant == "B"].converted; cevap = stats.betabinom.cdf(129, 1000, 1 + b.sum(), 1 + len(b) - b.sum())', 4)
G('s75', 'Gözlenen B dönüşen sayısı', 'cevap = ab[ab.variant == "B"].converted.sum()', 0)
G('s76', 'Duyarlılık: Beta(50, 450) güçlü önselle B\'nin sonsal ortalaması (4 basamak)', 'b = ab[ab.variant == "B"].converted; cevap = (50 + b.sum()) / (500 + len(b))', 4)
G('s76', 'Bayes faktörü (B grubu): p = 0,15 ile p = 0,10 hipotezlerinin olabilirlik oranı (log10, 3 basamak)', 'b = ab[ab.variant == "B"].converted; k, n = b.sum(), len(b); cevap = (stats.binom.logpmf(k, n, .15) - stats.binom.logpmf(k, n, .10)) / np.log(10)', 3)
G('s76', 'Karar eşiği: P(pB > 0,13) (Beta(1, 1) sonsal, 4 basamak)', 'b = ab[ab.variant == "B"].converted; cevap = stats.beta.sf(0.13, 1 + b.sum(), 1 + len(b) - b.sum())', 4)

# 19 · zaman serisi ileri
G('s77', 'Ljung–Box: günlük yolculuk serisinin 7 gecikmeli Q istatistiği (3 basamak)', 'from statsmodels.stats.diagnostic import acorr_ljungbox; cevap = acorr_ljungbox(gunluk.yolculuk, lags=[7]).lb_stat.iloc[0]', 3)
G('s77', 'PACF: gecikme 1 kısmi otokorelasyon (statsmodels pacf, 3 basamak)', 'from statsmodels.tsa.stattools import pacf; cevap = pacf(gunluk.yolculuk, nlags=7)[1]', 3)
G('s77', 'AR(1) regresyonunun artıklarının gecikme 1 otokorelasyonu (3 basamak)', 'd = gunluk.assign(dun=gunluk.yolculuk.shift(1)).dropna(); r = smf.ols("yolculuk ~ dun", d).fit().resid; cevap = r.autocorr(1)', 3)
G('s78', 'Değişim noktası sezgisi: Temmuz öncesi (Haziran) ve sonrası (Temmuz–Ağustos) ortalama yolculuk farkı (1 basamak)', 'a = gunluk[gunluk.tarih.dt.month == 6].yolculuk.mean(); b = gunluk[gunluk.tarih.dt.month > 6].yolculuk.mean(); cevap = b - a', 1)
G('s78', 'CUSUM: ortalamadan sapmaların birikimli toplamının en büyük mutlak değeri (1 basamak)', 's = gunluk.yolculuk; cevap = (s - s.mean()).cumsum().abs().max()', 1)
G('s78', 'CUSUM\'un en büyük olduğu gün (ayın günü, tarih.day)', 's = gunluk.yolculuk; cevap = gunluk.tarih.iloc[(s - s.mean()).cumsum().abs().idxmax()].day', 0)
G('s79', 'Yerel düzey (rastgele yürüyüş + gürültü) için basit Kalman: Q = 100, R = 2.500, ilk durum ilk gözlem, P0 = 2.500. Son günün filtrelenmiş düzeyi (1 basamak)', 'y = gunluk.yolculuk.to_numpy(float); x, P = y[0], 2500.0\nfor z in y[1:]:\n    P += 100; K = P / (P + 2500); x += K * (z - x); P *= 1 - K\ncevap = x', 1)
G('s79', 'Aynı filtrenin son Kalman kazancı K (4 basamak)', 'y = gunluk.yolculuk.to_numpy(float); x, P = y[0], 2500.0\nfor z in y[1:]:\n    P += 100; K = P / (P + 2500); x += K * (z - x); P *= 1 - K\ncevap = K', 4)
G('s79', 'Son 7 günün basit ortalaması (karşılaştırma için, 1 basamak)', 'cevap = gunluk.yolculuk.iloc[-7:].mean()', 1)
G('s80', 'Hiyerarşik tutarlılık: aylık yolculuk toplamlarının toplamı günlük toplama eşit mi? Aylık toplamların toplamı', 'cevap = gunluk.groupby(gunluk.tarih.dt.month).yolculuk.sum().sum()', 0)
G('s80', 'Temmuz ayının toplam içindeki payı (yüzde, 2 basamak)', 'm = gunluk.groupby(gunluk.tarih.dt.month).yolculuk.sum(); cevap = 100 * m[7] / m.sum()', 2)
G('s80', 'Yukarıdan aşağı dağıtım: Ağustos tahmini 40.000 ise Ağustos\'un haftaiçi günlerine düşen pay (Haziran–Temmuz haftaiçi payıyla, yuvarla)', 'h = gunluk[gunluk.tarih.dt.month < 8]; pay = h[h.tarih.dt.dayofweek < 5].yolculuk.sum() / h.yolculuk.sum(); cevap = round(40000 * pay)', 0)

# 20 · stokastik süreçler ve risk
G('s81', 'Markov: bir çalışanın anket dalgaları arasında "yüksek bağlılık" (≥ 3,6) durumunda kalma olasılığı P(yüksek→yüksek) (4 basamak)', 'p = survey.pivot_table(index="emp_id", columns="wave", values="engagement").dropna() >= 3.6; cevap = (p["2024-Q2"] & p["2024-Q4"]).sum() / p["2024-Q2"].sum()', 4)
G('s81', 'P(düşük→yüksek) (4 basamak)', 'p = survey.pivot_table(index="emp_id", columns="wave", values="engagement").dropna() >= 3.6; cevap = (~p["2024-Q2"] & p["2024-Q4"]).sum() / (~p["2024-Q2"]).sum()', 4)
G('s81', 'Bu iki olasılıkla durağan dağılımda "yüksek" payı a / (a + 1 − b) (a = P(düşük→yüksek), b = P(yüksek→yüksek), 4 basamak)', 'p = survey.pivot_table(index="emp_id", columns="wave", values="engagement").dropna() >= 3.6; b = (p["2024-Q2"] & p["2024-Q4"]).sum() / p["2024-Q2"].sum(); a = (~p["2024-Q2"] & p["2024-Q4"]).sum() / (~p["2024-Q2"]).sum(); cevap = a / (a + 1 - b)', 4)
G('s82', 'Little yasası: Lezzet Kurye\'de saatlik ortalama sipariş geliş hızı λ (tüm siparişler / toplam saat; ilk ve son sipariş arası, 3 basamak)', 'h = (lk.placed_at.max() - lk.placed_at.min()).total_seconds() / 3600; cevap = len(lk) / h', 3)
G('s82', 'Teslim edilen siparişlerde ortalama sistemde kalma süresi W (saat, 4 basamak)', 'cevap = teslim.sure.mean() / 60', 4)
G('s82', 'L = λ·W: aynı anda yolda olan ortalama sipariş sayısı (λ yalnız teslim edilenler için, 3 basamak)', 'h = (lk.placed_at.max() - lk.placed_at.min()).total_seconds() / 3600; cevap = len(teslim) / h * teslim.sure.mean() / 60', 3)
G('s83', 'Tarihsel VaR: kart harcamalarında (mutlak) %99 yüzdelik (TL, 2 basamak)', 'cevap = txns[txns.txn_type == "kart_harcama"].amount.abs().quantile(.99)', 2)
G('s83', 'Beklenen kuyruk kaybı (ES): %99 yüzdeliğin üstündeki harcamaların ortalaması (TL, 2 basamak)', 'x = txns[txns.txn_type == "kart_harcama"].amount.abs(); cevap = x[x > x.quantile(.99)].mean()', 2)
G('s83', 'Rötarda kuyruk: 120 dakikayı aşan rötar kayıtlarının oranı (yüzde, 2 basamak)', 'cevap = 100 * (delays.minutes > 120).mean()', 2)
G('s84', 'Entropi: rötar nedeni dağılımının Shannon entropisi (bit, 4 basamak)', 'p = delays.reason.value_counts(normalize=True); cevap = -(p * np.log2(p)).sum()', 4)
G('s84', 'En yüksek olası entropi (5 neden, bit, 4 basamak)', 'cevap = np.log2(delays.reason.nunique())', 4)
G('s84', 'KL ıraksaması: kart ile nakit ödemelerin durum dağılımı arasında D(kart || nakit) (nat, 4 basamak)', 'c = pd.crosstab(lk.payment, lk.status, normalize="index"); cevap = stats.entropy(c.loc["kart"], c.loc["nakit"])', 4)

# 21 · veri sorunları
G('s85', 'Eksik veri: anket bağlılık puanını boşları ortalamayla doldurunca std (ddof = 1, 4 basamak) — gerçek std\'den küçük çıkar', 'e = survey.engagement; cevap = e.fillna(e.mean()).std()', 4)
G('s85', 'Yalnız gözlenen değerlerin std\'si (4 basamak)', 'cevap = survey.engagement.std()', 4)
G('s85', 'Boş bağlılık puanı sayısı', 'cevap = survey.engagement.isna().sum()', 0)
G('s86', 'Anket ağırlığı: çalışma modelinin anket içindeki payı ile çalışan tablosundaki payı oranı; "uzaktan" ağırlığı (popülasyon payı / örneklem payı, 4 basamak)', 'd = survey[survey.wave == "2024-Q4"].merge(emp[["emp_id", "work_mode"]], on="emp_id"); cevap = (emp.work_mode == "uzaktan").mean() / (d.work_mode == "uzaktan").mean()', 4)
G('s86', 'Kish etkin örneklem: ağırlıklar w (her yanıtlayana kendi modelinin ağırlığı), n_eff = (Σw)² / Σw² (Q4 dalgası, 1 basamak)', 'd = survey[survey.wave == "2024-Q4"].merge(emp[["emp_id", "work_mode"]], on="emp_id"); w = d.work_mode.map(emp.work_mode.value_counts(normalize=True) / d.work_mode.value_counts(normalize=True)); cevap = w.sum() ** 2 / (w ** 2).sum()', 1)
G('s86', 'Ağırlıklı ortalama bağlılık (Q4, aynı ağırlıklar, boşlar hariç, 4 basamak)', 'd = survey[survey.wave == "2024-Q4"].merge(emp[["emp_id", "work_mode"]], on="emp_id").dropna(subset=["engagement"]); w = d.work_mode.map(emp.work_mode.value_counts(normalize=True) / d.work_mode.value_counts(normalize=True)); cevap = (w * d.engagement).sum() / w.sum()', 4)
G('s87', 'Ortalamaya dönüş: Q2\'de bağlılığı en üst %10\'da olanların Q4\'teki ortalama değişimi (Q4 − Q2, 3 basamak)', 'p = survey.pivot_table(index="emp_id", columns="wave", values="engagement").dropna(); t = p[p["2024-Q2"] >= p["2024-Q2"].quantile(.9)]; cevap = (t["2024-Q4"] - t["2024-Q2"]).mean()', 3)
G('s87', 'Q2\'de en alt %10\'dakilerin ortalama değişimi (3 basamak)', 'p = survey.pivot_table(index="emp_id", columns="wave", values="engagement").dropna(); t = p[p["2024-Q2"] <= p["2024-Q2"].quantile(.1)]; cevap = (t["2024-Q4"] - t["2024-Q2"]).mean()', 3)
G('s87', 'Q4 ~ Q2 regresyon eğimi (1\'den küçükse ortalamaya dönüş, 3 basamak)', 'p = survey.pivot_table(index="emp_id", columns="wave", values="engagement").dropna(); p.columns = ["q2", "q4"]; cevap = smf.ols("q4 ~ q2", p).fit().params["q2"]', 3)
G('s88', 'Duyarlılık: teslim süresi eşiğini 45 yerine 50 dakika alınca "geç teslim" oranı kaç puan değişir? (yüzde puan, 2 basamak)', 'cevap = 100 * ((teslim.sure > 45).mean() - (teslim.sure > 50).mean())', 2)
G('s88', 'Aynı soru: iptalleri dahil etmeyen ortalama teslim süresi ile iade dahil (teslim + iade) ortalama farkı (dakika, 3 basamak)', 'cevap = lk[lk.status.isin(["teslim", "iade"])].sure.mean() - teslim.sure.mean()', 3)
G('s88', 'Yeniden üretilebilirlik: tohum 2024 ile teslimlerden 500 örneklemin ortalama süresi (pandas sample, random_state = 2024, 3 basamak)', 'cevap = teslim.sure.sample(500, random_state=2024).mean()', 3)

# 22 · öğrenme teorisi
G('s89', 'Ampirik risk: yolculuk ~ sıcaklık modelinin eğitim MSE değeri (1 basamak)', 'cevap = smf.ols("yolculuk ~ sicaklik", gunluk).fit().mse_resid * (len(gunluk) - 2) / len(gunluk)', 1)
G('s89', 'İlk 70 gün eğitim, kalanı test: test MSE (1 basamak)', 'tr, te = gunluk.iloc[:70], gunluk.iloc[70:]; m = smf.ols("yolculuk ~ sicaklik", tr).fit(); cevap = ((te.yolculuk - m.predict(te)) ** 2).mean()', 1)
G('s89', 'Aynı bölmede eğitim MSE (1 basamak); test ile farkı genelleme açığıdır.', 'tr = gunluk.iloc[:70]; m = smf.ols("yolculuk ~ sicaklik", tr).fit(); cevap = (m.resid ** 2).mean()', 1)
G('s90', 'Yanlılık–varyans: sabit model (eğitim ortalaması) ile ilk 70 / kalan bölmede test MSE (1 basamak)', 'tr, te = gunluk.iloc[:70], gunluk.iloc[70:]; cevap = ((te.yolculuk - tr.yolculuk.mean()) ** 2).mean()', 1)
G('s90', 'Aynı bölmede 5. derece polinom (sıcaklık) test MSE (numpy polyfit, 1 basamak)', 'tr, te = gunluk.iloc[:70], gunluk.iloc[70:]; c = np.polyfit(tr.sicaklik, tr.yolculuk, 5); cevap = ((te.yolculuk - np.polyval(c, te.sicaklik)) ** 2).mean()', 1, tol=0.01)
G('s90', 'Test döneminde yolculuğun varyansı (ddof = 0): yaklaşık indirgenemez hata ölçeği (1 basamak)', 'cevap = gunluk.iloc[70:].yolculuk.var(ddof=0)', 1)
G('s91', 'Hata maliyeti: dönüşüm tahmininde yanlış negatif 50 TL, yanlış pozitif 5 TL. Bayes karar eşiği 5 / (5 + 50) (4 basamak)', 'cevap = 5 / (5 + 50)', 4)
G('s91', 'Bu eşikle lojistik (converted ~ variant) modelin pozitif tahmin oranı (yüzde, 1 basamak)', 'p = smf.logit("converted ~ C(variant)", ab).fit(disp=0).predict(ab); cevap = 100 * (p > 5 / 55).mean()', 1)
G('s91', 'Herkes pozitif tahmin edilirse toplam maliyet (yanlış pozitif × 5 TL)', 'cevap = 5 * (ab.converted == 0).sum()', 0)
G('s92', 'Öğrenme eğrisi: ilk 30 günle eğitilen yolculuk ~ sıcaklık modelinin son 22 günde test MSE değeri (1 basamak)', 'tr, te = gunluk.iloc[:30], gunluk.iloc[70:]; m = smf.ols("yolculuk ~ sicaklik", tr).fit(); cevap = ((te.yolculuk - m.predict(te)) ** 2).mean()', 1)
G('s92', 'İlk 70 günle eğitilince aynı test MSE (1 basamak)', 'tr, te = gunluk.iloc[:70], gunluk.iloc[70:]; m = smf.ols("yolculuk ~ sicaklik", tr).fit(); cevap = ((te.yolculuk - m.predict(te)) ** 2).mean()', 1)
G('s92', 'Verinin değeri: iki MSE farkı (30 gün − 70 gün, 1 basamak)', 'te = gunluk.iloc[70:]; f = lambda k: ((te.yolculuk - smf.ols("yolculuk ~ sicaklik", gunluk.iloc[:k]).fit().predict(te)) ** 2).mean(); cevap = f(30) - f(70)', 1)

# 23 · optimizasyon temelleri
G('s93', 'Log kayıp: herkese B grubunun dönüşüm oranını tahmin eden modelin B grubu üzerindeki ortalama log kaybı (nat, 4 basamak)', 'b = ab[ab.variant == "B"].converted; p = b.mean(); cevap = -(b * np.log(p) + (1 - b) * np.log(1 - p)).mean()', 4)
G('s93', 'Aynı grupta herkese 0,5 tahmin eden modelin log kaybı (4 basamak)', 'cevap = np.log(2)', 4)
G('s93', 'Lojistik modelin (converted ~ variant) toplam log olabilirliği (2 basamak)', 'cevap = smf.logit("converted ~ C(variant)", ab).fit(disp=0).llf', 2)
G('s94', 'Gradyan inişi: yolculuk ~ standartlaştırılmış sıcaklık, öğrenme oranı 0,1, 200 adım, başlangıç (0, 0). Son eğim (2 basamak)', 'x = ((gunluk.sicaklik - gunluk.sicaklik.mean()) / gunluk.sicaklik.std(ddof=0)).to_numpy(); y = gunluk.yolculuk.to_numpy(float); a = b = 0.0\nfor _ in range(200):\n    e = a + b * x - y; a -= 0.1 * 2 * e.mean(); b -= 0.1 * 2 * (e * x).mean()\ncevap = b', 2)
G('s94', 'Kapalı çözümdeki eğim (aynı ölçekleme, 2 basamak)', 'x = (gunluk.sicaklik - gunluk.sicaklik.mean()) / gunluk.sicaklik.std(ddof=0); cevap = np.cov(x, gunluk.yolculuk, ddof=0)[0, 1]', 2)
G('s94', 'Gradyan inişinde son kesişim (2 basamak); y ortalamasına yakın mı?', 'x = ((gunluk.sicaklik - gunluk.sicaklik.mean()) / gunluk.sicaklik.std(ddof=0)).to_numpy(); y = gunluk.yolculuk.to_numpy(float); a = b = 0.0\nfor _ in range(200):\n    e = a + b * x - y; a -= 0.1 * 2 * e.mean(); b -= 0.1 * 2 * (e * x).mean()\ncevap = a', 2)
G('s95', 'Kovaryans matrisi: günlük (sıcaklık, yolculuk) kovaryansı (ddof = 1, 2 basamak)', 'cevap = gunluk[["sicaklik", "yolculuk"]].cov().iloc[0, 1]', 2)
G('s95', 'Aynı matrisin determinantı (ddof = 1, 1 basamak)', 'cevap = np.linalg.det(gunluk[["sicaklik", "yolculuk"]].cov())', 1, tol=0.001)
G('s95', 'Sıcaklık varyansı (ddof = 1, 4 basamak)', 'cevap = gunluk.sicaklik.var()', 4)
G('s96', 'Konformal aralık: ilk 70 günle yolculuk ~ sıcaklık; 70–80. günlerin mutlak artıklarının 0,9 kantili (kalibrasyon, numpy "higher", 1 basamak)', 'm = smf.ols("yolculuk ~ sicaklik", gunluk.iloc[:70]).fit(); c = gunluk.iloc[70:80]; cevap = np.quantile((c.yolculuk - m.predict(c)).abs(), 0.9, method="higher")', 1)
G('s96', 'Bu genişlikle son 12 günde aralığın kapsama oranı (yüzde, 1 basamak)', 'm = smf.ols("yolculuk ~ sicaklik", gunluk.iloc[:70]).fit(); c = gunluk.iloc[70:80]; q = np.quantile((c.yolculuk - m.predict(c)).abs(), 0.9, method="higher"); t = gunluk.iloc[80:]; cevap = 100 * ((t.yolculuk - m.predict(t)).abs() <= q).mean()', 1)
G('s96', 'Modelin klasik %95 tahmin aralığının yarı genişliği, ilk test günü için (1 basamak)', 'm = smf.ols("yolculuk ~ sicaklik", gunluk.iloc[:70]).fit(); f = m.get_prediction(gunluk.iloc[[70]]).summary_frame(alpha=.05); cevap = (f.obs_ci_upper - f["mean"]).iloc[0]', 1)

# 24–26 · sınıflandırma: ortak örnek (A/B + cihaz)
CLS = 'from sklearn.model_selection import train_test_split\nd = ab.merge(web.groupby("user_id").agg(olay=("event_id", "count"), mobil=("device", lambda s: (s == "mobile").mean())).reset_index(), on="user_id", how="left").fillna(0)\nd["B"] = (d.variant == "B").astype(int)\nX, y = d[["B", "olay", "mobil"]], d.converted\nXtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)\n'
G('s97', 'LDA: (B, olay, mobil) özellikleriyle dönüşüm; test doğruluğu (yüzde, 1 basamak). Ortak hazırlık kodu görevde.', CLS + 'from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA; cevap = 100 * LDA().fit(Xtr, ytr).score(Xte, yte)', 1)
G('s97', 'Test kümesinde herkesi "dönüşmez" tahmin etmenin doğruluğu (yüzde, 1 basamak)', CLS + 'cevap = 100 * (yte == 0).mean()', 1)
G('s97', 'Eğitim kümesinin boyutu', CLS + 'cevap = len(Xtr)', 0)
G('s98', 'Naive Bayes (Gaussian): aynı özelliklerle test AUC (4 basamak)', CLS + 'from sklearn.naive_bayes import GaussianNB; from sklearn.metrics import roc_auc_score; cevap = roc_auc_score(yte, GaussianNB().fit(Xtr, ytr).predict_proba(Xte)[:, 1])', 4)
G('s98', 'Koşullu bağımsızlık denetimi: dönüşenlerde olay sayısı ile mobil payı korelasyonu (3 basamak)', CLS + 'cevap = d[d.converted == 1].olay.corr(d[d.converted == 1].mobil)', 3)
G('s98', 'Dönüşenlerin ortalama olay sayısı (3 basamak)', CLS + 'cevap = d[d.converted == 1].olay.mean()', 3)
G('s99', 'k-NN (k = 15): test AUC (4 basamak)', CLS + 'from sklearn.neighbors import KNeighborsClassifier; from sklearn.metrics import roc_auc_score; cevap = roc_auc_score(yte, KNeighborsClassifier(15).fit(Xtr, ytr).predict_proba(Xte)[:, 1])', 4)
G('s99', 'Aynı model özellikler standartlaştırılarak (StandardScaler) test AUC (4 basamak)', CLS + 'from sklearn.neighbors import KNeighborsClassifier; from sklearn.preprocessing import StandardScaler; from sklearn.pipeline import make_pipeline; from sklearn.metrics import roc_auc_score; cevap = roc_auc_score(yte, make_pipeline(StandardScaler(), KNeighborsClassifier(15)).fit(Xtr, ytr).predict_proba(Xte)[:, 1])', 4)
G('s99', 'Olay sayısının standart sapması (ölçek farkını gör, 3 basamak)', CLS + 'cevap = d.olay.std()', 3)
G('s100', 'Doğrusal SVM (LinearSVC, C = 1, dual = "auto", random_state = 0, standartlaştırılmış): test doğruluğu (yüzde, 1 basamak)', CLS + 'from sklearn.svm import LinearSVC; from sklearn.preprocessing import StandardScaler; from sklearn.pipeline import make_pipeline; cevap = 100 * make_pipeline(StandardScaler(), LinearSVC(C=1, dual="auto", random_state=0)).fit(Xtr, ytr).score(Xte, yte)', 1)
G('s100', 'Dengesiz sınıfta SVM: class_weight = "balanced" ile test duyarlılığı (recall, yüzde, 1 basamak)', CLS + 'from sklearn.svm import LinearSVC; from sklearn.preprocessing import StandardScaler; from sklearn.pipeline import make_pipeline; from sklearn.metrics import recall_score; cevap = 100 * recall_score(yte, make_pipeline(StandardScaler(), LinearSVC(C=1, dual="auto", random_state=0, class_weight="balanced")).fit(Xtr, ytr).predict(Xte))', 1)
G('s100', 'Testteki pozitif sınıf sayısı', CLS + 'cevap = int(yte.sum())', 0)
G('s101', 'Gini safsızlığı: tüm A/B kullanıcılarında dönüşüm için Gini 1 − Σp² (4 basamak)', 'p = ab.converted.mean(); cevap = 1 - p ** 2 - (1 - p) ** 2', 4)
G('s101', 'variant ile bölünce ağırlıklı Gini (4 basamak)', 'g = ab.groupby("variant").converted.agg(["mean", "count"]); gi = 1 - g["mean"] ** 2 - (1 - g["mean"]) ** 2; cevap = (gi * g["count"]).sum() / g["count"].sum()', 4)
G('s101', 'Karar ağacı (max_depth = 3, random_state = 0): test AUC (4 basamak)', CLS + 'from sklearn.tree import DecisionTreeClassifier; from sklearn.metrics import roc_auc_score; cevap = roc_auc_score(yte, DecisionTreeClassifier(max_depth=3, random_state=0).fit(Xtr, ytr).predict_proba(Xte)[:, 1])', 4)
G('s102', 'Rastgele orman (200 ağaç, max_depth = 4, random_state = 0): test AUC (4 basamak)', CLS + 'from sklearn.ensemble import RandomForestClassifier; from sklearn.metrics import roc_auc_score; cevap = roc_auc_score(yte, RandomForestClassifier(200, max_depth=4, random_state=0).fit(Xtr, ytr).predict_proba(Xte)[:, 1])', 4, tol=0.005)
G('s102', 'Aynı ormanda "olay" özelliğinin önemi (feature_importances_, 3 basamak)', CLS + 'from sklearn.ensemble import RandomForestClassifier; cevap = RandomForestClassifier(200, max_depth=4, random_state=0).fit(Xtr, ytr).feature_importances_[1]', 3, tol=0.01)
G('s102', 'Bagging sezgisi: tek ağacın (max_depth = 4) test AUC (4 basamak)', CLS + 'from sklearn.tree import DecisionTreeClassifier; from sklearn.metrics import roc_auc_score; cevap = roc_auc_score(yte, DecisionTreeClassifier(max_depth=4, random_state=0).fit(Xtr, ytr).predict_proba(Xte)[:, 1])', 4)
G('s103', 'Gradient boosting (100 ağaç, max_depth = 2, random_state = 0): test AUC (4 basamak)', CLS + 'from sklearn.ensemble import GradientBoostingClassifier; from sklearn.metrics import roc_auc_score; cevap = roc_auc_score(yte, GradientBoostingClassifier(n_estimators=100, max_depth=2, random_state=0).fit(Xtr, ytr).predict_proba(Xte)[:, 1])', 4, tol=0.005)
G('s103', 'Aynı modelin test log kaybı (4 basamak)', CLS + 'from sklearn.ensemble import GradientBoostingClassifier; from sklearn.metrics import log_loss; cevap = log_loss(yte, GradientBoostingClassifier(n_estimators=100, max_depth=2, random_state=0).fit(Xtr, ytr).predict_proba(Xte)[:, 1])', 4, tol=0.005)
G('s103', 'Başlangıç tahmini: boosting\'in ilk adımdaki log odds (eğitim dönüşüm oranından, 4 basamak)', CLS + 'p = ytr.mean(); cevap = np.log(p / (1 - p))', 4)
G('s104', 'Tek nöron = lojistik regresyon: sklearn LogisticRegression (standartlaştırılmış, varsayılan) test AUC (4 basamak)', CLS + 'from sklearn.linear_model import LogisticRegression; from sklearn.preprocessing import StandardScaler; from sklearn.pipeline import make_pipeline; from sklearn.metrics import roc_auc_score; cevap = roc_auc_score(yte, make_pipeline(StandardScaler(), LogisticRegression()).fit(Xtr, ytr).predict_proba(Xte)[:, 1])', 4)
G('s104', 'Sigmoid(0,5) değeri (4 basamak)', 'cevap = 1 / (1 + np.exp(-0.5))', 4)
G('s104', 'Küçük ağ: MLPClassifier(hidden_layer_sizes = (8,), max_iter = 2000, random_state = 0, standartlaştırılmış) test AUC (4 basamak)', CLS + 'from sklearn.neural_network import MLPClassifier; from sklearn.preprocessing import StandardScaler; from sklearn.pipeline import make_pipeline; from sklearn.metrics import roc_auc_score; cevap = roc_auc_score(yte, make_pipeline(StandardScaler(), MLPClassifier((8,), max_iter=2000, random_state=0)).fit(Xtr, ytr).predict_proba(Xte)[:, 1])', 4, tol=0.01)
G('s105', 'İç içe çapraz doğrulama: lojistik regresyonda C ∈ {0,01; 0,1; 1; 10} için GridSearchCV (iç 3 kat) + dış 5 kat (StratifiedKFold, shuffle, random_state = 0) ortalama AUC (4 basamak)', CLS + 'from sklearn.model_selection import GridSearchCV, cross_val_score, StratifiedKFold; from sklearn.linear_model import LogisticRegression; from sklearn.preprocessing import StandardScaler; from sklearn.pipeline import make_pipeline; gs = GridSearchCV(make_pipeline(StandardScaler(), LogisticRegression()), {"logisticregression__C": [.01, .1, 1, 10]}, cv=3, scoring="roc_auc"); cevap = cross_val_score(gs, X, y, cv=StratifiedKFold(5, shuffle=True, random_state=0), scoring="roc_auc").mean()', 4, tol=0.005)
G('s105', 'Seçim yanlılığı: aynı ızgarada yalnız GridSearchCV (5 kat) en iyi skoru (4 basamak); iç içe sonuçtan iyimser mi?', CLS + 'from sklearn.model_selection import GridSearchCV, StratifiedKFold; from sklearn.linear_model import LogisticRegression; from sklearn.preprocessing import StandardScaler; from sklearn.pipeline import make_pipeline; cevap = GridSearchCV(make_pipeline(StandardScaler(), LogisticRegression()), {"logisticregression__C": [.01, .1, 1, 10]}, cv=StratifiedKFold(5, shuffle=True, random_state=0), scoring="roc_auc").fit(X, y).best_score_', 4, tol=0.005)
G('s105', 'Toplam örnek sayısı', CLS + 'cevap = len(X)', 0)
G('s106', 'Dengesizlik: dönüşüm (pozitif sınıf) oranı (yüzde, 2 basamak)', 'cevap = 100 * ab.converted.mean()', 2)
G('s106', 'Lojistik regresyon (standartlaştırılmış) test ortalama kesinlik (average precision, 4 basamak)', CLS + 'from sklearn.linear_model import LogisticRegression; from sklearn.preprocessing import StandardScaler; from sklearn.pipeline import make_pipeline; from sklearn.metrics import average_precision_score; cevap = average_precision_score(yte, make_pipeline(StandardScaler(), LogisticRegression()).fit(Xtr, ytr).predict_proba(Xte)[:, 1])', 4)
G('s106', 'Rastgele sınıflandırıcının beklenen ortalama kesinliği = test pozitif oranı (4 basamak)', CLS + 'cevap = yte.mean()', 4)
G('s107', 'Brier skoru: lojistik regresyon (standartlaştırılmış) test kümesinde (4 basamak)', CLS + 'from sklearn.linear_model import LogisticRegression; from sklearn.preprocessing import StandardScaler; from sklearn.pipeline import make_pipeline; from sklearn.metrics import brier_score_loss; cevap = brier_score_loss(yte, make_pipeline(StandardScaler(), LogisticRegression()).fit(Xtr, ytr).predict_proba(Xte)[:, 1])', 4)
G('s107', 'Herkese eğitim oranını veren modelin Brier skoru (4 basamak)', CLS + 'from sklearn.metrics import brier_score_loss; cevap = brier_score_loss(yte, np.full(len(yte), ytr.mean()))', 4)
G('s107', 'Test kümesinde ortalama tahmin olasılığı ile gerçek oran farkı (yüzde puan, 3 basamak)', CLS + 'from sklearn.linear_model import LogisticRegression; from sklearn.preprocessing import StandardScaler; from sklearn.pipeline import make_pipeline; p = make_pipeline(StandardScaler(), LogisticRegression()).fit(Xtr, ytr).predict_proba(Xte)[:, 1]; cevap = 100 * (p.mean() - yte.mean())', 3)
G('s108', 'Model karşılaştırması: 10 katlı CV (StratifiedKFold, shuffle, random_state = 0) AUC farkları (lojistik − karar ağacı max_depth 3) ortalaması (4 basamak)', CLS + 'from sklearn.model_selection import cross_val_score, StratifiedKFold; from sklearn.linear_model import LogisticRegression; from sklearn.tree import DecisionTreeClassifier; from sklearn.preprocessing import StandardScaler; from sklearn.pipeline import make_pipeline; cv = StratifiedKFold(10, shuffle=True, random_state=0); a = cross_val_score(make_pipeline(StandardScaler(), LogisticRegression()), X, y, cv=cv, scoring="roc_auc"); b = cross_val_score(DecisionTreeClassifier(max_depth=3, random_state=0), X, y, cv=cv, scoring="roc_auc"); cevap = (a - b).mean()', 4, tol=0.005)
G('s108', 'Aynı farkların eşleştirilmiş t testi p değeri (4 basamak)', CLS + 'from sklearn.model_selection import cross_val_score, StratifiedKFold; from sklearn.linear_model import LogisticRegression; from sklearn.tree import DecisionTreeClassifier; from sklearn.preprocessing import StandardScaler; from sklearn.pipeline import make_pipeline; cv = StratifiedKFold(10, shuffle=True, random_state=0); a = cross_val_score(make_pipeline(StandardScaler(), LogisticRegression()), X, y, cv=cv, scoring="roc_auc"); b = cross_val_score(DecisionTreeClassifier(max_depth=3, random_state=0), X, y, cv=cv, scoring="roc_auc"); cevap = stats.ttest_rel(a, b).pvalue', 4, tol=0.02)
G('s108', 'Lojistik regresyonun 10 kat AUC standart sapması (4 basamak)', CLS + 'from sklearn.model_selection import cross_val_score, StratifiedKFold; from sklearn.linear_model import LogisticRegression; from sklearn.preprocessing import StandardScaler; from sklearn.pipeline import make_pipeline; cevap = cross_val_score(make_pipeline(StandardScaler(), LogisticRegression()), X, y, cv=StratifiedKFold(10, shuffle=True, random_state=0), scoring="roc_auc").std(ddof=1)', 4, tol=0.005)

# 27 · gizli yapı
G('s109', 'Mahalanobis: günlük (sıcaklık, yolculuk) için en uzak günün Mahalanobis uzaklığı (ddof = 1 kovaryans, 3 basamak)', 'X = gunluk[["sicaklik", "yolculuk"]].to_numpy(float); m = X.mean(0); S = np.linalg.inv(np.cov(X.T)); cevap = np.sqrt(np.einsum("ij,jk,ik->i", X - m, S, X - m)).max()', 3)
G('s109', 'Mahalanobis uzaklığı 2,5\'i aşan gün sayısı', 'X = gunluk[["sicaklik", "yolculuk"]].to_numpy(float); m = X.mean(0); S = np.linalg.inv(np.cov(X.T)); cevap = (np.sqrt(np.einsum("ij,jk,ik->i", X - m, S, X - m)) > 2.5).sum()', 0)
G('s109', 'Ki-kare(2) dağılımında %95 eşiğin karekökü (Mahalanobis için doğal sınır, 3 basamak)', 'cevap = np.sqrt(stats.chi2.ppf(.95, 2))', 3)
G('s110', 'Gaussian karışım (2 bileşen, random_state = 0): teslim süresine uydur; küçük ortalamalı bileşenin ortalaması (dakika, 2 basamak)', 'from sklearn.mixture import GaussianMixture; g = GaussianMixture(2, random_state=0).fit(teslim[["sure"]]); cevap = g.means_.min()', 2, tol=0.01)
G('s110', 'Büyük ortalamalı bileşenin ortalaması (2 basamak)', 'from sklearn.mixture import GaussianMixture; g = GaussianMixture(2, random_state=0).fit(teslim[["sure"]]); cevap = g.means_.max()', 2, tol=0.01)
G('s110', 'Küçük ortalamalı bileşenin ağırlığı (3 basamak)', 'from sklearn.mixture import GaussianMixture; g = GaussianMixture(2, random_state=0).fit(teslim[["sure"]]); cevap = g.weights_[g.means_.ravel().argmin()]', 3, tol=0.01)
G('s111', 'Faktör analizi sezgisi: anket üç maddesinin (enps, engagement, manager_score) korelasyon matrisinin en büyük özdeğeri (boşlar satırca atılır, 3 basamak)', 'R = survey[["enps", "engagement", "manager_score"]].dropna().corr(); cevap = np.linalg.eigvalsh(R).max()', 3)
G('s111', 'Bu özdeğerin toplam varyans içindeki payı (yüzde, 1 basamak)', 'R = survey[["enps", "engagement", "manager_score"]].dropna().corr(); cevap = 100 * np.linalg.eigvalsh(R).max() / 3', 1)
G('s111', 'Cronbach alfa: üç madde standartlaştırılmış (k·r̄ / (1 + (k−1)·r̄), 3 basamak)', 'R = survey[["enps", "engagement", "manager_score"]].dropna().corr().to_numpy(); r = R[np.triu_indices(3, 1)].mean(); cevap = 3 * r / (1 + 2 * r)', 3)
G('s112', 'Boyut indirgeme öncesi: günlük tablonun 4 değişkeninin (standartlaştırılmış) ikili Öklit uzaklıklarının ortalaması (3 basamak)', 'from scipy.spatial.distance import pdist; X = gunluk[["yolculuk", "ort_km", "sicaklik", "yagis"]]; Z = (X - X.mean()) / X.std(ddof=0); cevap = pdist(Z).mean()', 3)
G('s112', 'PCA ile 2 boyuta indirgeyince aynı ortalama uzaklık (3 basamak); ne kadar korunuyor?', 'from scipy.spatial.distance import pdist; from sklearn.decomposition import PCA; X = gunluk[["yolculuk", "ort_km", "sicaklik", "yagis"]]; Z = (X - X.mean()) / X.std(ddof=0); cevap = pdist(PCA(2).fit_transform(Z)).mean()', 3)
G('s112', 'Uzaklıkların Spearman korelasyonu (4 boyut ile 2 boyut, 3 basamak)', 'from scipy.spatial.distance import pdist; from sklearn.decomposition import PCA; X = gunluk[["yolculuk", "ort_km", "sicaklik", "yagis"]]; Z = (X - X.mean()) / X.std(ddof=0); cevap = stats.spearmanr(pdist(Z), pdist(PCA(2).fit_transform(Z))).statistic', 3)

# 28 · nedensel ileri
G('s113', 'Eğilim skoru: hibrit çalışma (tedavi) olasılığı ~ eğitim + şehir İstanbul mu, lojistik; eğitim düzeyi "Lisans" olmayanlar için ortalama eğilim skoru (4 basamak)', 'd = emp.assign(t=(emp.work_mode == "hibrit").astype(int), ist=(emp.city == "İstanbul").astype(int)); ps = smf.logit("t ~ C(education) + ist", d).fit(disp=0).predict(d); cevap = ps[d.education != "Lisans"].mean()', 4, tol=0.002)
G('s113', 'IPW: hibrit ve diğer çalışanların gönüllü ayrılma oranı farkı (hibrit − diğer, eğilim skoru ağırlıklı, yüzde puan, 2 basamak)', 'd = emp.assign(t=(emp.work_mode == "hibrit").astype(int), ist=(emp.city == "İstanbul").astype(int), y=(emp.term_type == "gönüllü").astype(int)); ps = smf.logit("t ~ C(education) + ist", d).fit(disp=0).predict(d); w = np.where(d.t == 1, 1 / ps, 1 / (1 - ps)); cevap = 100 * (np.average(d.y[d.t == 1], weights=w[d.t == 1]) - np.average(d.y[d.t == 0], weights=w[d.t == 0]))', 2, tol=0.05)
G('s113', 'Ham fark: hibrit − diğer gönüllü ayrılma oranı (yüzde puan, 2 basamak)', 'y = emp.term_type == "gönüllü"; h = emp.work_mode == "hibrit"; cevap = 100 * (y[h].mean() - y[~h].mean())', 2)
G('s114', 'Araç değişken sezgisi (Wald oranı): A/B\'de rastgele atama (B) aracı, "en az bir web olayı" aracıcı, dönüşüm sonuç. Atamanın dönüşüme etkisi (yüzde puan, 2 basamak)', 'pa, pb = ab.groupby("variant").converted.mean(); cevap = 100 * (pb - pa)', 2)
G('s114', 'Atamanın "en az bir web olayı" oranına etkisi (B − A, yüzde puan, 2 basamak)', 'w = ab.user_id.isin(web.user_id); cevap = 100 * (w[ab.variant == "B"].mean() - w[ab.variant == "A"].mean())', 2)
G('s114', 'Bu iki sayının neden "Wald oranı" için zayıf araç uyarısı verdiğini görmek için: ilk adım etkisinin standart hatası (yüzde puan, 2 basamak)', 'w = ab.user_id.isin(web.user_id); a, b = w[ab.variant == "A"], w[ab.variant == "B"]; cevap = 100 * np.sqrt(a.mean() * (1 - a.mean()) / len(a) + b.mean() * (1 - b.mean()) / len(b))', 2)
G('s115', 'Regresyon süreksizliği: kurye puanı 4\'te kesilen bir bahşiş kampanyası varsayımıyla, puanı tam 4 ile 3 olan değerlendirmelerde ortalama bahşiş farkı (4 − 3, TL, 3 basamak)', 'd = lk.merge(ratings, on="order_id"); cevap = d[d.courier_score == 4].tip.mean() - d[d.courier_score == 3].tip.mean()', 3)
G('s115', 'Kurye puanı 4 olan değerlendirme sayısı', 'cevap = (ratings.courier_score == 4).sum()', 0)
G('s115', 'Puan 3 olan değerlendirme sayısı', 'cevap = (ratings.courier_score == 3).sum()', 0)
G('s116', 'CUPED: A/B\'de ön dönem değişkeni yok; web olay sayısıyla düzeltme. θ = cov(revenue, olay) / var(olay) (4 basamak)', 'o = web.groupby("user_id").size(); d = ab.assign(olay=ab.user_id.map(o).fillna(0)); cevap = d.revenue.cov(d.olay) / d.olay.var()', 4)
G('s116', 'Düzeltilmiş gelirin varyansının ham varyansa oranı (4 basamak)', 'o = web.groupby("user_id").size(); d = ab.assign(olay=ab.user_id.map(o).fillna(0)); t = d.revenue.cov(d.olay) / d.olay.var(); cevap = (d.revenue - t * (d.olay - d.olay.mean())).var() / d.revenue.var()', 4)
G('s116', 'Sıralı izleme: Pocock benzeri sabit eşikle 5 ara bakışta her bakışın iki yönlü p eşiği yaklaşık 0,0158; z eşiği (3 basamak)', 'cevap = stats.norm.isf(0.0158 / 2)', 3)

# 29 · dağılım aileleri
G('s117', 'Hipergeometrik: 60 kuryeden 2\'si bisikletli; rastgele 10 kurye seçilirse en az birinin bisikletli olma olasılığı (4 basamak)', 'N = len(couriers); K = (couriers.vehicle == "bisiklet").sum(); cevap = 1 - stats.hypergeom.pmf(0, N, K, 10)', 4)
G('s117', 'Multinomial: rötar nedenlerinin gözlenen oranlarıyla 10 rötarda tam 3 "hava", 3 "gec_gelen_ucak", 4 diğer olasılığı (4 basamak)', 'p = delays.reason.value_counts(normalize=True); ph, pg = p["hava"], p["gec_gelen_ucak"]; cevap = stats.multinomial.pmf([3, 3, 4], 10, [ph, pg, 1 - ph - pg])', 4)
G('s117', '"hava" nedeninin oranı (4 basamak)', 'cevap = (delays.reason == "hava").mean()', 4)
G('s118', 'Beta uydurma (momentler): yemek puanı (1–5) [0, 1]\'e ölçeklenince (x − 1) / 4 ortalaması (4 basamak)', 'cevap = ((ratings.food_score - 1) / 4).mean()', 4)
G('s118', 'Aynı ölçekli değişkenin varyansı (ddof = 1, 4 basamak)', 'cevap = ((ratings.food_score - 1) / 4).var()', 4)
G('s118', 'Gamma (momentler): rötar dakikası için şekil k = ortalama² / varyans (ddof = 1, 4 basamak)', 'm = delays.minutes; cevap = m.mean() ** 2 / m.var()', 4)
G('s119', 'Weibull: ayrılan çalışanların hizmet süresine (gün) scipy weibull_min.fit (floc = 0) şekil parametresi (3 basamak)', 'a = emp.dropna(subset=["term_date"]); t = (a.term_date - a.hire_date).dt.days; t = t[t > 0]; cevap = stats.weibull_min.fit(t, floc=0)[0]', 3, tol=0.01)
G('s119', 'Aynı uydurmanın ölçek parametresi (gün, 1 basamak)', 'a = emp.dropna(subset=["term_date"]); t = (a.term_date - a.hire_date).dt.days; t = t[t > 0]; cevap = stats.weibull_min.fit(t, floc=0)[2]', 1, tol=0.01)
G('s119', 'Şekil < 1 ise hazard azalır. Hizmet süresi 365 günün altında olan ayrılanların payı (yüzde, 1 basamak)', 'a = emp.dropna(subset=["term_date"]); cevap = 100 * ((a.term_date - a.hire_date).dt.days < 365).mean()', 1)
G('s120', 'ECDF: teslim süresinin 30 dakika ve altında olma oranı (4 basamak)', 'cevap = (teslim.sure <= 30).mean()', 4)
G('s120', 'Çekirdek yoğunluk (gaussian_kde, varsayılan bant): teslim süresi yoğunluğunun 30 dakikadaki değeri (5 basamak)', 'cevap = stats.gaussian_kde(teslim.sure)(30)[0]', 5, tol=0.002)
G('s120', 'Kolmogorov–Smirnov: teslim süresi normal mi? (ortalama ve std veriden) KS istatistiği (4 basamak)', 's = teslim.sure; cevap = stats.kstest(s, stats.norm(s.mean(), s.std()).cdf).statistic', 4)

# ---------------------------------------------------------------- hesapla
from collections import defaultdict
ders = defaultdict(list)
for i, t in enumerate(T):
    env = dict(ORTAM); env.update(math=math, np=np, pd=pd, stats=stats, sm=sm, smf=smf)
    exec(t['kod'], env)
    v = env['cevap']; v = float(v.item() if hasattr(v, 'item') else v)
    if not math.isfinite(v): raise SystemExit(f'Sonlu değil: {t["ders"]} {t["soru"][:60]}')
    n = len(ders[t['ders']]) + 1
    ders[t['ders']].append(dict(id=f'{t["ders"]}-v{n}', soru=t['soru'], cevap=round(v, max(t['d'] + 2, 6)), d=t['d'], tol=t['tol'], ipucu=t['ipucu'], kod=t['kod']))

eksik = [f's{i:02d}' if i < 100 else f's{i}' for i in range(1, 121) if (f's{i:02d}' if i < 100 else f's{i}') not in ders]
if eksik: raise SystemExit('Görevi olmayan ders: ' + ', '.join(eksik))
az = [k for k, v in ders.items() if len(v) < 3]
if az: raise SystemExit('3\'ten az görevli ders: ' + ', '.join(az))

DSET = sorted(set(re.findall(r'\b(orders|items|products|customers|ab|web|flights|delays|bookings|lk|ratings|couriers|emp|survey|txns|bcust|gunluk|teslim|inen)\b', ' '.join(t['kod'] for t in T))))
CSV_AD = {'orders': 'orders', 'items': 'order_items', 'products': 'products', 'customers': 'customers', 'ab': 'ab_test', 'web': 'web_events', 'flights': 'hv_flights', 'inen': 'hv_flights', 'delays': 'hv_delays', 'bookings': 'hv_bookings', 'lk': 'lk_orders', 'teslim': 'lk_orders', 'ratings': 'lk_ratings', 'couriers': 'lk_couriers', 'emp': 'ik_employees', 'survey': 'ik_survey', 'txns': 'bank_txns', 'bcust': 'bank_customers', 'gunluk': 'bk_gunluk'}
def kullandigi(kod):
    return sorted(set(CSV_AD[x] for x in re.findall(r'\b(orders|items|products|customers|ab|web|flights|delays|bookings|lk|ratings|couriers|emp|survey|txns|bcust|gunluk|teslim|inen)\b', kod)))
for k, v in ders.items():
    for g in v: g['veri'] = kullandigi(g['kod'])

# ---------------------------------------------------------------- docs/ders-alistirma.js
cikti = {'surum': 'V10', 'hazirlik': HAZIRLIK, 'dersler': ders}
open(os.path.join(DOCS, 'ders-alistirma.js'), 'w', encoding='utf-8').write(
    '/* Kesit İstatistik V10: ders içi uygulamalı alıştırmalar. ÜRETİLİR (alistirma_v10.py), elle düzenleme. */\nwindow.KESIT_DERS_ALISTIRMA = ' + json.dumps(cikti, ensure_ascii=False, separators=(',', ':')) + ';\n')

# ---------------------------------------------------------------- veri zip
def zip_yaz(yol, dosyalar):
    with zipfile.ZipFile(yol, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for ad, veri in dosyalar:
            zi = zipfile.ZipInfo(ad, date_time=(2026, 1, 1, 0, 0, 0)); zi.compress_type = zipfile.ZIP_DEFLATED; zi.external_attr = 0o644 << 16
            z.writestr(zi, veri, compresslevel=9)
csvler = sorted(f for f in os.listdir(VERI) if f.endswith('.csv'))
BENIOKU = 'Kesit İstatistik · ders alıştırmaları veri paketi\n\nBu klasördeki CSV dosyaları Kesit uygulamalarının ortak kurgusal veri setlerinden alınmıştır (Anadolu Market, Kanat Havayolları, Lezzet Kurye, Pusula İK, Ilgaz Bank, Pedal İzmir).\nbk_gunluk.csv türetilmiştir: Pedal İzmir yolculuklarının günlük sayısı ve ortalama mesafesi, aynı günün ortalama sıcaklığı ve toplam yağışı.\nDefterler ve Excel kitapları bu klasörü "kesit/" adıyla bekler.\nVeri ve içerik CC BY-NC 4.0 · https://ysfdurak.github.io/kesit-istatistik/\n'
zip_yaz(os.path.join(DOCS, 'data', 'kesit-veri.zip'), [('kesit/' + f, open(os.path.join(VERI, f), 'rb').read()) for f in csvler] + [('kesit/BENIOKU.txt', BENIOKU.encode('utf-8'))])

# ---------------------------------------------------------------- defterler
C = {l['id']: l for l in json.loads(re.search(r'window\.COURSE\s*=\s*(\{.*\});?\s*$', open(os.path.join(DOCS, 'content.js'), encoding='utf-8').read(), re.S).group(1))['lessons']} if False else None
import subprocess
dersbilgi = json.loads(subprocess.run(['node', '-e', 'const fs=require("fs"),vm=require("vm");const c={window:{}};vm.createContext(c);vm.runInContext(fs.readFileSync(process.argv[1],"utf8"),c);process.stdout.write(JSON.stringify(c.window.COURSE.lessons.map(l=>({id:l.id,title:l.title,module:l.module}))))', os.path.join(DOCS, 'content.js')], capture_output=True, text=True, check=True).stdout)
BILGI = {l['id']: l for l in dersbilgi}
DEF = os.path.join(DOCS, 'defter'); os.makedirs(DEF, exist_ok=True)
def hucre(tur, metin):
    satir = metin.split('\n'); src = [s + '\n' for s in satir[:-1]] + [satir[-1]]
    return {'cell_type': tur, 'metadata': {}, 'source': src} | ({'outputs': [], 'execution_count': None} if tur == 'code' else {})
def tolerans(g):
    return max(abs(g['cevap']) * 0.005, 0.5 * 10 ** -g['d'], g['tol'] or 0)   # tol: rastgelelik/sürüm farkı için ek pay
defter_zip = []
for k in sorted(ders, key=lambda x: int(x[1:])):
    b = BILGI.get(k, {'title': k})
    cells = [hucre('markdown', f'# {k.upper()} · {b["title"]}\n\nKesit İstatistik ders defteri. Önce veri paketini (`kesit-veri.zip`) bu defterin yanına aç; `kesit/` klasörü oluşmalı. Her görevde `cevap` değişkenini hesapla; son satır sonucu beklenenle karşılaştırır.\n\nUygulamadaki ders: https://ysfdurak.github.io/kesit-istatistik/docs/#lesson/{k}'),
             hucre('code', HAZIRLIK.strip())]
    py = [f'# {k.upper()} · {b["title"]}\n# Kesit İstatistik ders defteri (Python betiği). kesit/ klasörü bu dosyanın yanında olmalı.\n', HAZIRLIK]
    for i, g in enumerate(ders[k], 1):
        soru = re.sub(r'</?b>', '', g['soru'])
        kontrol = f'assert abs(cevap - {g["cevap"]!r}) <= {tolerans(g)!r}, cevap\nprint("Görev {i}:", round(cevap, {g["d"]}), "✓")'
        cells += [hucre('markdown', f'## Görev {i}\n\n{soru}'), hucre('code', g['kod'] + '\n' + kontrol)]
        py += [f'\n# %% Görev {i}: {soru}\n', g['kod'] + '\n' + kontrol + '\n']
    nb = {'cells': cells, 'metadata': {'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}, 'language_info': {'name': 'python'}}, 'nbformat': 4, 'nbformat_minor': 5}
    s_nb = json.dumps(nb, ensure_ascii=False, indent=1) + '\n'; s_py = ''.join(py)
    open(os.path.join(DEF, k + '.ipynb'), 'w', encoding='utf-8').write(s_nb); open(os.path.join(DEF, k + '.py'), 'w', encoding='utf-8').write(s_py)
    defter_zip += [(k + '.ipynb', s_nb.encode('utf-8')), (k + '.py', s_py.encode('utf-8'))]
req = 'numpy\npandas\nscipy\nstatsmodels\nscikit-learn\n'
zip_yaz(os.path.join(DEF, 'kesit-defterler.zip'), [('kesit-defterler/' + a, v) for a, v in defter_zip] + [('kesit-defterler/requirements.txt', req.encode()), ('kesit-defterler/BENIOKU.txt', ('Kesit İstatistik ders defterleri: her ders için .ipynb ve .py.\npython -m pip install -r requirements.txt\nkesit-veri.zip dosyasını bu klasöre aç (kesit/ klasörü oluşur), sonra defteri Jupyter ya da VS Code ile aç.\n').encode('utf-8'))] + [('kesit-defterler/kesit/' + f, open(os.path.join(VERI, f), 'rb').read()) for f in csvler])

# ---------------------------------------------------------------- Excel kitapları (modül başına)
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
XL = os.path.join(DOCS, 'excel'); os.makedirs(XL, exist_ok=True)
TURET = {'order_items': lambda d: d.assign(tutar=(d.quantity * d.unit_price * (1 - d.discount)).round(4)),
         'hv_flights': lambda d: d.assign(gecikme=((pd.to_datetime(d.actual_dep) - pd.to_datetime(d.sched_dep)).dt.total_seconds() / 60)),
         'lk_orders': lambda d: d.assign(sure=((pd.to_datetime(d.delivered_at) - pd.to_datetime(d.placed_at)).dt.total_seconds() / 60).round(4))}
moduller = defaultdict(list)
for k in ders: moduller[BILGI[k]['module']].append(k)
xl_zip = []
for m, ks in sorted(moduller.items()):
    ks = sorted(ks, key=lambda x: int(x[1:]))
    wb = Workbook(); ws = wb.active; ws.title = 'Görevler'
    import datetime as _dt; wb.properties.created = wb.properties.modified = _dt.datetime(2026, 1, 1); wb.properties.creator = 'Kesit İstatistik'
    ws.append(['Ders', 'Görev', 'Soru', 'Veri sayfası', 'Senin cevabın', 'Kontrol', 'Ondalık']); [setattr(c, 'font', Font(bold=True)) for c in ws[1]]
    sayfalar = set()
    for k in ks:
        for i, g in enumerate(ders[k], 1):
            r = ws.max_row + 1; tol = tolerans(g)
            ws.append([k, i, re.sub(r'</?b>', '', g['soru']), ', '.join(g['veri']), None, None, g['d']])
            ws.cell(r, 6).value = f'=IF(E{r}="","",IF(ABS(E{r}-{g["cevap"]!r})<={tol!r},"Doğru","Tekrar dene"))'
            ws.cell(r, 3).alignment = Alignment(wrap_text=True, vertical='top'); ws.cell(r, 5).fill = PatternFill('solid', fgColor='FFF4CC')
            sayfalar.update(g['veri'])
    for col, w in zip('ABCDEFG', [7, 7, 80, 24, 16, 14, 9]): ws.column_dimensions[col].width = w
    ws.freeze_panes = 'A2'
    bilgi = wb.create_sheet('Nasıl')
    for s in ['Kesit İstatistik · modül çalışma kitabı', '', '1. Görevler sayfasında soruyu oku; veri sayfasında Excel işlevleriyle hesapla (ORTALAMA, ORTANCA, STDSAPMA.S, YÜZDEBİRLİK.DAHİL, ÇOKEĞERSAY, KORELASYON, EĞİM, DOT, BİNOM.DAĞ, POISSON.DAĞ, NORM.DAĞ, T.TERS.2T…).',
              '2. Sonucu sarı "Senin cevabın" hücresine yaz; Kontrol sütunu Doğru ya da Tekrar dene der (tolerans: göreli %0,5 ya da son basamağın yarısı).',
              '3. Bazı görevler (makine öğrenmesi, MCMC, karma model) Excel ile pratik değildir; onları ders defteriyle (Python) çöz.',
              '4. Türetilmiş sütunlar hazır: order_items.tutar, hv_flights.gecikme (dakika), lk_orders.sure (dakika). teslim = lk_orders içinde status = "teslim"; inen = hv_flights içinde status = "landed".',
              '', 'Veri ve içerik CC BY-NC 4.0 · https://ysfdurak.github.io/kesit-istatistik/']:
        bilgi.append([s])
    bilgi.column_dimensions['A'].width = 120
    for ad in sorted(sayfalar):
        d = pd.read_csv(os.path.join(VERI, ad + '.csv'))
        if ad in TURET: d = TURET[ad](d)
        sh = wb.create_sheet(ad[:31]); sh.append(list(d.columns)); [setattr(c, 'font', Font(bold=True)) for c in sh[1]]
        for row in d.itertuples(index=False):
            sh.append([None if (isinstance(v, float) and math.isnan(v)) else v for v in row])
        sh.freeze_panes = 'A2'
    yol = os.path.join(XL, f'modul-{int(m) + 1:02d}.xlsx'); wb.save(yol)
    xl_zip.append((f'kesit-excel/modul-{int(m) + 1:02d}.xlsx', open(yol, 'rb').read()))

print(json.dumps({'ders': len(ders), 'gorev': sum(len(v) for v in ders.values()), 'csv': len(csvler), 'defter': len(ders), 'excel': len(moduller),
                  'veri_zip_MB': round(os.path.getsize(os.path.join(DOCS, 'data', 'kesit-veri.zip')) / 1e6, 2),
                  'excel_MB': round(sum(len(v) for _, v in xl_zip) / 1e6, 2),
                  'js_KB': round(os.path.getsize(os.path.join(DOCS, 'ders-alistirma.js')) / 1024)}, ensure_ascii=False))
