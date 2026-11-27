# S109 · Çok değişkenli normal ve Mahalanobis uzaklığı
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

# %% Görev 1: Mahalanobis: günlük (sıcaklık, yolculuk) için en uzak günün Mahalanobis uzaklığı (ddof = 1 kovaryans, 3 basamak)
X = gunluk[["sicaklik", "yolculuk"]].to_numpy(float); m = X.mean(0); S = np.linalg.inv(np.cov(X.T)); cevap = np.sqrt(np.einsum("ij,jk,ik->i", X - m, S, X - m)).max()
assert abs(cevap - 4.762279) <= 0.023811395000000003, cevap
print("Görev 1:", round(cevap, 3), "✓")

# %% Görev 2: Mahalanobis uzaklığı 2,5'i aşan gün sayısı
X = gunluk[["sicaklik", "yolculuk"]].to_numpy(float); m = X.mean(0); S = np.linalg.inv(np.cov(X.T)); cevap = (np.sqrt(np.einsum("ij,jk,ik->i", X - m, S, X - m)) > 2.5).sum()
assert abs(cevap - 5.0) <= 0.5, cevap
print("Görev 2:", round(cevap, 0), "✓")

# %% Görev 3: Ki-kare(2) dağılımında %95 eşiğin karekökü (Mahalanobis için doğal sınır, 3 basamak)
cevap = np.sqrt(stats.chi2.ppf(.95, 2))
assert abs(cevap - 2.447747) <= 0.012238735, cevap
print("Görev 3:", round(cevap, 3), "✓")
