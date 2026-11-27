# S96 · Tahmin belirsizliği ve konformal aralık
# Kesit İstatistik ders defteri (Python betiği). kesit/ klasörü bu dosyanın yanında olmalı.
import math
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

# %% Görev 1: Konformal aralık: ilk 70 günle yolculuk ~ sıcaklık; 70–80. günlerin mutlak artıklarının 0,9 kantili (kalibrasyon, numpy "higher", 1 basamak)
m = smf.ols("yolculuk ~ sicaklik", gunluk.iloc[:70]).fit(); c = gunluk.iloc[70:80]; cevap = np.quantile((c.yolculuk - m.predict(c)).abs(), 0.9, method="higher")
assert abs(cevap - 712.651485) <= 3.5632574249999998, cevap
print("Görev 1:", round(cevap, 1), "✓")

# %% Görev 2: Bu genişlikle son 12 günde aralığın kapsama oranı (yüzde, 1 basamak)
m = smf.ols("yolculuk ~ sicaklik", gunluk.iloc[:70]).fit(); c = gunluk.iloc[70:80]; q = np.quantile((c.yolculuk - m.predict(c)).abs(), 0.9, method="higher"); t = gunluk.iloc[80:]; cevap = 100 * ((t.yolculuk - m.predict(t)).abs() <= q).mean()
assert abs(cevap - 100.0) <= 0.5, cevap
print("Görev 2:", round(cevap, 1), "✓")

# %% Görev 3: Modelin klasik %95 tahmin aralığının yarı genişliği, ilk test günü için (1 basamak)
m = smf.ols("yolculuk ~ sicaklik", gunluk.iloc[:70]).fit(); f = m.get_prediction(gunluk.iloc[[70]]).summary_frame(alpha=.05); cevap = (f.obs_ci_upper - f["mean"]).iloc[0]
assert abs(cevap - 240.239009) <= 1.2011950450000002, cevap
print("Görev 3:", round(cevap, 1), "✓")
