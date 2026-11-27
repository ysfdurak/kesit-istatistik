# S74 · MCMC ve yakınsama tanıları
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

# %% Görev 1: MCMC sezgisi: B grubunun dönüşüm oranı için Metropolis (10.000 adım, adım std 0,02, tohum 1, ilk 2.000 atılır) zincir ortalaması (3 basamak)
rng = np.random.default_rng(1); b = ab[ab.variant == "B"].converted; k, n = b.sum(), len(b)
ll = lambda p: k * np.log(p) + (n - k) * np.log(1 - p) if 0 < p < 1 else -np.inf
p, z = 0.5, []
for _ in range(10000):
    q = p + rng.normal(0, 0.02)
    if np.log(rng.random()) < ll(q) - ll(p): p = q
    z.append(p)
cevap = np.mean(z[2000:])
assert abs(cevap - 0.147001) <= 0.003, cevap
print("Görev 1:", round(cevap, 3), "✓")

# %% Görev 2: Aynı problemin kesin sonsal ortalaması (Beta(1, 1), 4 basamak)
b = ab[ab.variant == "B"].converted; cevap = (1 + b.sum()) / (2 + len(b))
assert abs(cevap - 0.14703) <= 0.00073515, cevap
print("Görev 2:", round(cevap, 4), "✓")

# %% Görev 3: Kesin sonsal standart sapması (4 basamak)
b = ab[ab.variant == "B"].converted; cevap = stats.beta.std(1 + b.sum(), 1 + len(b) - b.sum())
assert abs(cevap - 0.011045) <= 5.5225e-05, cevap
print("Görev 3:", round(cevap, 4), "✓")
