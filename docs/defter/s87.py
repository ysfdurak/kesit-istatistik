# S87 · Ölçüm hatası ve regresyona dönüş
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

# %% Görev 1: Ortalamaya dönüş: Q2'de bağlılığı en üst %10'da olanların Q4'teki ortalama değişimi (Q4 − Q2, 3 basamak)
p = survey.pivot_table(index="emp_id", columns="wave", values="engagement").dropna(); t = p[p["2024-Q2"] >= p["2024-Q2"].quantile(.9)]; cevap = (t["2024-Q4"] - t["2024-Q2"]).mean()
assert abs(cevap - -0.643564) <= 0.00321782, cevap
print("Görev 1:", round(cevap, 3), "✓")

# %% Görev 2: Q2'de en alt %10'dakilerin ortalama değişimi (3 basamak)
p = survey.pivot_table(index="emp_id", columns="wave", values="engagement").dropna(); t = p[p["2024-Q2"] <= p["2024-Q2"].quantile(.1)]; cevap = (t["2024-Q4"] - t["2024-Q2"]).mean()
assert abs(cevap - 0.579348) <= 0.00289674, cevap
print("Görev 2:", round(cevap, 3), "✓")

# %% Görev 3: Q4 ~ Q2 regresyon eğimi (1'den küçükse ortalamaya dönüş, 3 basamak)
p = survey.pivot_table(index="emp_id", columns="wave", values="engagement").dropna(); p.columns = ["q2", "q4"]; cevap = smf.ols("q4 ~ q2", p).fit().params["q2"]
assert abs(cevap - 0.243528) <= 0.00121764, cevap
print("Görev 3:", round(cevap, 3), "✓")
