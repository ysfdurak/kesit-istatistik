# S44 · Permütasyon testleri ve Monte Carlo
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

# %% Görev 1: Permütasyon testi: A/B dönüşüm farkı için 5.000 karıştırma (tohum 3); |fark| ≥ gözlenen oranı (p değeri, 3 basamak)
rng = np.random.default_rng(3); y = ab.converted.to_numpy(); g = (ab.variant == "B").to_numpy(); obs = y[g].mean() - y[~g].mean(); cnt = 0
for _ in range(5000):
    p = rng.permutation(g); cnt += abs(y[p].mean() - y[~p].mean()) >= abs(obs)
cevap = cnt / 5000
assert abs(cevap - 0.0144) <= 0.004, cevap
print("Görev 1:", round(cevap, 3), "✓")

# %% Görev 2: Gözlenen dönüşüm farkı (B − A, yüzde puan, 2 basamak)
pa, pb = ab.groupby("variant").converted.mean(); cevap = 100 * (pb - pa)
assert abs(cevap - 3.762351) <= 0.018811755, cevap
print("Görev 2:", round(cevap, 2), "✓")

# %% Görev 3: Monte Carlo: günlük teknik rötar Poisson(λ) ise 30 günde toplamın 60'ı aşma olasılığı (λ s13'teki gibi, kesin hesap: Poisson(30λ), 4 basamak)
lam = (delays.reason == "teknik").sum() / 122; cevap = stats.poisson.sf(60, 30 * lam)
assert abs(cevap - 0.181299) <= 0.000906495, cevap
print("Görev 3:", round(cevap, 4), "✓")
