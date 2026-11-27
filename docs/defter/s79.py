# S79 · Durum uzayı ve Kalman filtresi
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

# %% Görev 1: Yerel düzey (rastgele yürüyüş + gürültü) için basit Kalman: Q = 100, R = 2.500, ilk durum ilk gözlem, P0 = 2.500. Son günün filtrelenmiş düzeyi (1 basamak)
y = gunluk.yolculuk.to_numpy(float); x, P = y[0], 2500.0
for z in y[1:]:
    P += 100; K = P / (P + 2500); x += K * (z - x); P *= 1 - K
cevap = x
assert abs(cevap - 1347.956942) <= 6.73978471, cevap
print("Görev 1:", round(cevap, 1), "✓")

# %% Görev 2: Aynı filtrenin son Kalman kazancı K (4 basamak)
y = gunluk.yolculuk.to_numpy(float); x, P = y[0], 2500.0
for z in y[1:]:
    P += 100; K = P / (P + 2500); x += K * (z - x); P *= 1 - K
cevap = K
assert abs(cevap - 0.180998) <= 0.0009049899999999999, cevap
print("Görev 2:", round(cevap, 4), "✓")

# %% Görev 3: Son 7 günün basit ortalaması (karşılaştırma için, 1 basamak)
cevap = gunluk.yolculuk.iloc[-7:].mean()
assert abs(cevap - 1319.428571) <= 6.5971428549999995, cevap
print("Görev 3:", round(cevap, 1), "✓")
