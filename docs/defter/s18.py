# S18 · Merkezî limit teoremi ve standart hata
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

# %% Görev 1: Teslim süresi ortalamasının standart hatası (std / √n, ddof = 1, 4 basamak)
cevap = teslim.sure.std() / np.sqrt(len(teslim))
assert abs(cevap - 0.132121) <= 0.000660605, cevap
print("Görev 1:", round(cevap, 4), "✓")

# %% Görev 2: A grubundaki dönüşüm oranının standart hatası √(p(1−p)/n) (5 basamak)
a = ab[ab.variant == "A"].converted; p = a.mean(); cevap = np.sqrt(p * (1 - p) / len(a))
assert abs(cevap - 0.0099691) <= 4.98455e-05, cevap
print("Görev 2:", round(cevap, 5), "✓")

# %% Görev 3: Örneklem 4 katına çıksa teslim süresi ortalamasının standart hatası (aynı std ile, 4 basamak)
cevap = teslim.sure.std() / np.sqrt(4 * len(teslim))
assert abs(cevap - 0.06606) <= 0.00033029999999999995, cevap
print("Görev 3:", round(cevap, 4), "✓")
