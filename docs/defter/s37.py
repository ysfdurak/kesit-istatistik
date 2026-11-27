# S37 · Trend, mevsimsellik ve otokorelasyon
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

# %% Görev 1: Günlük bisiklet yolculuğu serisinin gecikme 1 otokorelasyonu (pandas autocorr, 3 basamak)
cevap = gunluk.yolculuk.autocorr(1)
assert abs(cevap - 0.295181) <= 0.0014759050000000002, cevap
print("Görev 1:", round(cevap, 3), "✓")

# %% Görev 2: Gecikme 7 otokorelasyonu (haftalık desen, 3 basamak)
cevap = gunluk.yolculuk.autocorr(7)
assert abs(cevap - 0.19362) <= 0.0009681, cevap
print("Görev 2:", round(cevap, 3), "✓")

# %% Görev 3: Haftanın gününe göre ortalama yolculuk: en yüksek gün ile en düşük gün ortalaması farkı (1 basamak)
m = gunluk.groupby(gunluk.tarih.dt.dayofweek).yolculuk.mean(); cevap = m.max() - m.min()
assert abs(cevap - 215.615385) <= 1.078076925, cevap
print("Görev 3:", round(cevap, 1), "✓")
