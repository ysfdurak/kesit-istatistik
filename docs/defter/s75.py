# S75 · Sonsal öngörü kontrolü
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

# %% Görev 1: Sonsal öngörü: B grubunda 1.000 yeni kullanıcıda beklenen dönüşen sayısı (sonsal ortalama × 1.000, 1 basamak)
b = ab[ab.variant == "B"].converted; cevap = 1000 * (1 + b.sum()) / (2 + len(b))
assert abs(cevap - 147.030185) <= 0.735150925, cevap
print("Görev 1:", round(cevap, 1), "✓")

# %% Görev 2: Beta-binom öngörü dağılımında 1.000 kullanıcıdan 130'dan az dönüşme olasılığı (4 basamak)
b = ab[ab.variant == "B"].converted; cevap = stats.betabinom.cdf(129, 1000, 1 + b.sum(), 1 + len(b) - b.sum())
assert abs(cevap - 0.131194) <= 0.0006559700000000001, cevap
print("Görev 2:", round(cevap, 4), "✓")

# %% Görev 3: Gözlenen B dönüşen sayısı
cevap = ab[ab.variant == "B"].converted.sum()
assert abs(cevap - 150.0) <= 0.75, cevap
print("Görev 3:", round(cevap, 0), "✓")
