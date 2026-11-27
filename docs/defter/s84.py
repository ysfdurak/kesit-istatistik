# S84 · Entropi, KL ve dağılım karşılaştırması
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

# %% Görev 1: Entropi: rötar nedeni dağılımının Shannon entropisi (bit, 4 basamak)
p = delays.reason.value_counts(normalize=True); cevap = -(p * np.log2(p)).sum()
assert abs(cevap - 2.266527) <= 0.011332635, cevap
print("Görev 1:", round(cevap, 4), "✓")

# %% Görev 2: En yüksek olası entropi (5 neden, bit, 4 basamak)
cevap = np.log2(delays.reason.nunique())
assert abs(cevap - 2.321928) <= 0.011609640000000001, cevap
print("Görev 2:", round(cevap, 4), "✓")

# %% Görev 3: KL ıraksaması: kart ile nakit ödemelerin durum dağılımı arasında D(kart || nakit) (nat, 4 basamak)
c = pd.crosstab(lk.payment, lk.status, normalize="index"); cevap = stats.entropy(c.loc["kart"], c.loc["nakit"])
assert abs(cevap - 0.000581) <= 5e-05, cevap
print("Görev 3:", round(cevap, 4), "✓")
