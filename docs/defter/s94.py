# S94 · Gradyan inişi ve stokastik optimizasyon
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

# %% Görev 1: Gradyan inişi: yolculuk ~ standartlaştırılmış sıcaklık, öğrenme oranı 0,1, 200 adım, başlangıç (0, 0). Son eğim (2 basamak)
x = ((gunluk.sicaklik - gunluk.sicaklik.mean()) / gunluk.sicaklik.std(ddof=0)).to_numpy(); y = gunluk.yolculuk.to_numpy(float); a = b = 0.0
for _ in range(200):
    e = a + b * x - y; a -= 0.1 * 2 * e.mean(); b -= 0.1 * 2 * (e * x).mean()
cevap = b
assert abs(cevap - -23.871918) <= 0.11935959, cevap
print("Görev 1:", round(cevap, 2), "✓")

# %% Görev 2: Kapalı çözümdeki eğim (aynı ölçekleme, 2 basamak)
x = (gunluk.sicaklik - gunluk.sicaklik.mean()) / gunluk.sicaklik.std(ddof=0); cevap = np.cov(x, gunluk.yolculuk, ddof=0)[0, 1]
assert abs(cevap - -23.871918) <= 0.11935959, cevap
print("Görev 2:", round(cevap, 2), "✓")

# %% Görev 3: Gradyan inişinde son kesişim (2 basamak); y ortalamasına yakın mı?
x = ((gunluk.sicaklik - gunluk.sicaklik.mean()) / gunluk.sicaklik.std(ddof=0)).to_numpy(); y = gunluk.yolculuk.to_numpy(float); a = b = 0.0
for _ in range(200):
    e = a + b * x - y; a -= 0.1 * 2 * e.mean(); b -= 0.1 * 2 * (e * x).mean()
cevap = a
assert abs(cevap - 1266.48913) <= 6.3324456499999995, cevap
print("Görev 3:", round(cevap, 2), "✓")
