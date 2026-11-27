# S89 · Ampirik risk ve genelleme
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

# %% Görev 1: Ampirik risk: yolculuk ~ sıcaklık modelinin eğitim MSE değeri (1 basamak)
cevap = smf.ols("yolculuk ~ sicaklik", gunluk).fit().mse_resid * (len(gunluk) - 2) / len(gunluk)
assert abs(cevap - 21777.664035) <= 108.888320175, cevap
print("Görev 1:", round(cevap, 1), "✓")

# %% Görev 2: İlk 70 gün eğitim, kalanı test: test MSE (1 basamak)
tr, te = gunluk.iloc[:70], gunluk.iloc[70:]; m = smf.ols("yolculuk ~ sicaklik", tr).fit(); cevap = ((te.yolculuk - m.predict(te)) ** 2).mean()
assert abs(cevap - 47631.009006) <= 238.15504503, cevap
print("Görev 2:", round(cevap, 1), "✓")

# %% Görev 3: Aynı bölmede eğitim MSE (1 basamak); test ile farkı genelleme açığıdır.
tr = gunluk.iloc[:70]; m = smf.ols("yolculuk ~ sicaklik", tr).fit(); cevap = (m.resid ** 2).mean()
assert abs(cevap - 13879.994624) <= 69.39997312000001, cevap
print("Görev 3:", round(cevap, 1), "✓")
