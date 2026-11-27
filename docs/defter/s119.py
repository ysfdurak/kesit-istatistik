# S119 · Weibull, hazard ve güvenilirlik
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

# %% Görev 1: Weibull: ayrılan çalışanların hizmet süresine (gün) scipy weibull_min.fit (floc = 0) şekil parametresi (3 basamak)
a = emp.dropna(subset=["term_date"]); t = (a.term_date - a.hire_date).dt.days; t = t[t > 0]; cevap = stats.weibull_min.fit(t, floc=0)[0]
assert abs(cevap - 1.044106) <= 0.01, cevap
print("Görev 1:", round(cevap, 3), "✓")

# %% Görev 2: Aynı uydurmanın ölçek parametresi (gün, 1 basamak)
a = emp.dropna(subset=["term_date"]); t = (a.term_date - a.hire_date).dt.days; t = t[t > 0]; cevap = stats.weibull_min.fit(t, floc=0)[2]
assert abs(cevap - 1248.872862) <= 6.24436431, cevap
print("Görev 2:", round(cevap, 1), "✓")

# %% Görev 3: Şekil < 1 ise hazard azalır. Hizmet süresi 365 günün altında olan ayrılanların payı (yüzde, 1 basamak)
a = emp.dropna(subset=["term_date"]); cevap = 100 * ((a.term_date - a.hire_date).dt.days < 365).mean()
assert abs(cevap - 27.90404) <= 0.13952019999999998, cevap
print("Görev 3:", round(cevap, 1), "✓")
