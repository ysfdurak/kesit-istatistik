# S80 · Çoklu seriler ve hiyerarşik tahmin
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

# %% Görev 1: Hiyerarşik tutarlılık: aylık yolculuk toplamlarının toplamı günlük toplama eşit mi? Aylık toplamların toplamı
cevap = gunluk.groupby(gunluk.tarih.dt.month).yolculuk.sum().sum()
assert abs(cevap - 116517.0) <= 582.585, cevap
print("Görev 1:", round(cevap, 0), "✓")

# %% Görev 2: Temmuz ayının toplam içindeki payı (yüzde, 2 basamak)
m = gunluk.groupby(gunluk.tarih.dt.month).yolculuk.sum(); cevap = 100 * m[7] / m.sum()
assert abs(cevap - 33.662041) <= 0.16831020500000002, cevap
print("Görev 2:", round(cevap, 2), "✓")

# %% Görev 3: Yukarıdan aşağı dağıtım: Ağustos tahmini 40.000 ise Ağustos'un haftaiçi günlerine düşen pay (Haziran–Temmuz haftaiçi payıyla, yuvarla)
h = gunluk[gunluk.tarih.dt.month < 8]; pay = h[h.tarih.dt.dayofweek < 5].yolculuk.sum() / h.yolculuk.sum(); cevap = round(40000 * pay)
assert abs(cevap - 28656.0) <= 143.28, cevap
print("Görev 3:", round(cevap, 0), "✓")
