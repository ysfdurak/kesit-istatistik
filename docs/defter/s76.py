# S76 · Duyarlılık, karar eşiği ve Bayes faktörü
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

# %% Görev 1: Duyarlılık: Beta(50, 450) güçlü önselle B'nin sonsal ortalaması (4 basamak)
b = ab[ab.variant == "B"].converted; cevap = (50 + b.sum()) / (500 + len(b))
assert abs(cevap - 0.131148) <= 0.0006557399999999999, cevap
print("Görev 1:", round(cevap, 4), "✓")

# %% Görev 2: Bayes faktörü (B grubu): p = 0,15 ile p = 0,10 hipotezlerinin olabilirlik oranı (log10, 3 basamak)
b = ab[ab.variant == "B"].converted; k, n = b.sum(), len(b); cevap = (stats.binom.logpmf(k, n, .15) - stats.binom.logpmf(k, n, .10)) / np.log(10)
assert abs(cevap - 4.693053) <= 0.023465265, cevap
print("Görev 2:", round(cevap, 3), "✓")

# %% Görev 3: Karar eşiği: P(pB > 0,13) (Beta(1, 1) sonsal, 4 basamak)
b = ab[ab.variant == "B"].converted; cevap = stats.beta.sf(0.13, 1 + b.sum(), 1 + len(b) - b.sum())
assert abs(cevap - 0.942144) <= 0.00471072, cevap
print("Görev 3:", round(cevap, 4), "✓")
