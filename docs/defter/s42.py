# S42 · Güvenilir aralık ve Bayesçi karar
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

# %% Görev 1: B grubu için %95 güvenilir aralığın alt sınırı (Beta(1, 1) önsel, eşit kuyruk, 4 basamak)
b = ab[ab.variant == "B"].converted; cevap = stats.beta.ppf(.025, 1 + b.sum(), 1 + len(b) - b.sum())
assert abs(cevap - 0.126045) <= 0.000630225, cevap
print("Görev 1:", round(cevap, 4), "✓")

# %% Görev 2: Aynı aralığın üst sınırı (4 basamak)
b = ab[ab.variant == "B"].converted; cevap = stats.beta.ppf(.975, 1 + b.sum(), 1 + len(b) - b.sum())
assert abs(cevap - 0.169318) <= 0.00084659, cevap
print("Görev 2:", round(cevap, 4), "✓")

# %% Görev 3: P(pB > pA): sonsallardan 200.000 çekiliş (tohum 42, önce A sonra B), oran (3 basamak)
rng = np.random.default_rng(42); a = ab[ab.variant == "A"].converted; b = ab[ab.variant == "B"].converted; xa = rng.beta(1 + a.sum(), 1 + len(a) - a.sum(), 200000); xb = rng.beta(1 + b.sum(), 1 + len(b) - b.sum(), 200000); cevap = (xb > xa).mean()
assert abs(cevap - 0.993895) <= 0.005, cevap
print("Görev 3:", round(cevap, 3), "✓")
