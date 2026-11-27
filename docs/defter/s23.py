# S23 · Etki büyüklüğü ve pratik önem
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

# %% Görev 1: A/B dönüşüm farkının Cohen h etki büyüklüğü (3 basamak)
pa, pb = ab.groupby("variant").converted.mean(); cevap = 2 * np.arcsin(np.sqrt(pb)) - 2 * np.arcsin(np.sqrt(pa))
assert abs(cevap - 0.113078) <= 0.00056539, cevap
print("Görev 1:", round(cevap, 3), "✓")

# %% Görev 2: Göreli artış: (pB − pA) / pA × 100 (yüzde, 1 basamak)
pa, pb = ab.groupby("variant").converted.mean(); cevap = 100 * (pb - pa) / pa
assert abs(cevap - 34.606535) <= 0.173032675, cevap
print("Görev 2:", round(cevap, 1), "✓")

# %% Görev 3: Hibrit ve ofis çalışanlarının bağlılık puanı farkının Cohen d'si (birleşik std, 3 basamak; anketi emp ile birleştir)
d = survey.merge(emp[["emp_id", "work_mode"]], on="emp_id").dropna(subset=["engagement"]); a = d[d.work_mode == "hibrit"].engagement; b = d[d.work_mode == "ofis"].engagement; sp = np.sqrt(((len(a) - 1) * a.var() + (len(b) - 1) * b.var()) / (len(a) + len(b) - 2)); cevap = (a.mean() - b.mean()) / sp
assert abs(cevap - -0.087376) <= 0.0005, cevap
print("Görev 3:", round(cevap, 3), "✓")
