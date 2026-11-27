# S59 · Değişken dönüşümleri ve delta yöntemi
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

# %% Görev 1: Log dönüşümü: kart harcama tutarlarının geometrik ortalaması (exp(log ortalaması), TL, 2 basamak)
cevap = np.exp(np.log(txns[txns.txn_type == "kart_harcama"].amount.abs()).mean())
assert abs(cevap - 1327.861654) <= 6.639308270000001, cevap
print("Görev 1:", round(cevap, 2), "✓")

# %% Görev 2: Aynı tutarların aritmetik ortalaması (TL, 2 basamak)
cevap = txns[txns.txn_type == "kart_harcama"].amount.abs().mean()
assert abs(cevap - 3111.135779) <= 15.555678895000002, cevap
print("Görev 2:", round(cevap, 2), "✓")

# %% Görev 3: Delta yöntemi: A grubunda log odds'un standart hatası 1/√(n·p(1−p)) (4 basamak)
a = ab[ab.variant == "A"].converted; p = a.mean(); cevap = 1 / np.sqrt(len(a) * p * (1 - p))
assert abs(cevap - 0.102882) <= 0.00051441, cevap
print("Görev 3:", round(cevap, 4), "✓")
