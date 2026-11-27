# S116 · Sıralı deneyler ve varyans azaltma
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

# %% Görev 1: CUPED: A/B'de ön dönem değişkeni yok; web olay sayısıyla düzeltme. θ = cov(revenue, olay) / var(olay) (4 basamak)
o = web.groupby("user_id").size(); d = ab.assign(olay=ab.user_id.map(o).fillna(0)); cevap = d.revenue.cov(d.olay) / d.olay.var()
assert abs(cevap - 0.535825) <= 0.002679125, cevap
print("Görev 1:", round(cevap, 4), "✓")

# %% Görev 2: Düzeltilmiş gelirin varyansının ham varyansa oranı (4 basamak)
o = web.groupby("user_id").size(); d = ab.assign(olay=ab.user_id.map(o).fillna(0)); t = d.revenue.cov(d.olay) / d.olay.var(); cevap = (d.revenue - t * (d.olay - d.olay.mean())).var() / d.revenue.var()
assert abs(cevap - 0.999911) <= 0.004999555, cevap
print("Görev 2:", round(cevap, 4), "✓")

# %% Görev 3: Sıralı izleme: Pocock benzeri sabit eşikle 5 ara bakışta her bakışın iki yönlü p eşiği yaklaşık 0,0158; z eşiği (3 basamak)
cevap = stats.norm.isf(0.0158 / 2)
assert abs(cevap - 2.413503) <= 0.012067515000000001, cevap
print("Görev 3:", round(cevap, 3), "✓")
