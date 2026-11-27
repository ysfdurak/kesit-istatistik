# S52 · Güvenilirlik, sağkalım ve sansür
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

# %% Görev 1: Sağkalım: Pusula İK'da ayrılan çalışanların hizmet süresi (gün) medyanı (tam sayı)
a = emp.dropna(subset=["term_date"]); cevap = (a.term_date - a.hire_date).dt.days.median()
assert abs(cevap - 923.5) <= 4.6175, cevap
print("Görev 1:", round(cevap, 0), "✓")

# %% Görev 2: Kaplan–Meier: 365. günde hâlâ çalışıyor olma olasılığı (sansür: ayrılmamış, son tarih 2024-12-31; 3 basamak)
son = pd.Timestamp("2024-12-31"); t = ((emp.term_date.fillna(son) - emp.hire_date).dt.days).to_numpy(); e = emp.term_date.notna().to_numpy(); S = 1.0
for u in np.sort(np.unique(t[e & (t <= 365)])):
    S *= 1 - ((t == u) & e).sum() / (t >= u).sum()
cevap = S
assert abs(cevap - 0.894992) <= 0.00447496, cevap
print("Görev 2:", round(cevap, 3), "✓")

# %% Görev 3: Sansürlü (hâlâ çalışan) gözlem oranı (yüzde, 1 basamak)
cevap = 100 * emp.term_date.isna().mean()
assert abs(cevap - 63.983629) <= 0.319918145, cevap
print("Görev 3:", round(cevap, 1), "✓")
