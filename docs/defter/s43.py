# S43 · Bootstrap ve belirsizlik tahmini
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

# %% Görev 1: Bootstrap: teslim süresi medyanının 2.000 tekrarlı bootstrap standart hatası (tohum 7, 2 basamak)
rng = np.random.default_rng(7); s = teslim.sure.to_numpy(); cevap = np.std([np.median(rng.choice(s, len(s))) for _ in range(2000)], ddof=1)
assert abs(cevap - 0.15026) <= 0.03, cevap
print("Görev 1:", round(cevap, 2), "✓")

# %% Görev 2: Aynı bootstrap dağılımından medyan için %95 yüzdelik aralığın alt sınırı (2 basamak)
rng = np.random.default_rng(7); s = teslim.sure.to_numpy(); b = [np.median(rng.choice(s, len(s))) for _ in range(2000)]; cevap = np.percentile(b, 2.5)
assert abs(cevap - 36.508333) <= 0.182541665, cevap
print("Görev 2:", round(cevap, 2), "✓")

# %% Görev 3: Bootstrap ile A/B dönüşüm farkının standart hatası (3.000 tekrar, tohum 11, yüzde puan, 2 basamak)
rng = np.random.default_rng(11); a = ab[ab.variant == "A"].converted.to_numpy(); b = ab[ab.variant == "B"].converted.to_numpy(); d = [rng.choice(b, len(b)).mean() - rng.choice(a, len(a)).mean() for _ in range(3000)]; cevap = 100 * np.std(d, ddof=1)
assert abs(cevap - 1.430974) <= 0.05, cevap
print("Görev 3:", round(cevap, 2), "✓")
