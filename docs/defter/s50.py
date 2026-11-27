# S50 · Süreç yeterliliği: Cp ve Cpk
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

# %% Görev 1: Teslim süresi için üst spesifikasyon 60 dk: Cpk = (USL − x̄) / (3s) (tek taraflı, 3 basamak)
cevap = (60 - teslim.sure.mean()) / (3 * teslim.sure.std())
assert abs(cevap - 0.689404) <= 0.0034470200000000003, cevap
print("Görev 1:", round(cevap, 3), "✓")

# %% Görev 2: Spesifikasyon dışı (60 dk üstü) teslim oranı (ppm, tam sayı)
cevap = 1e6 * (teslim.sure > 60).mean()
assert abs(cevap - 33443.808376) <= 167.21904188000002, cevap
print("Görev 2:", round(cevap, 0), "✓")

# %% Görev 3: Normal varsayımla Cpk'dan beklenen spesifikasyon dışı oranı (ppm, tam sayı); gerçek oranla karşılaştır.
cpk = (60 - teslim.sure.mean()) / (3 * teslim.sure.std()); cevap = 1e6 * stats.norm.sf(3 * cpk)
assert abs(cevap - 19310.011074) <= 96.55005537, cevap
print("Görev 3:", round(cevap, 0), "✓")
