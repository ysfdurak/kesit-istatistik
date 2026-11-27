# S111 · Faktör analizi ve gizli değişkenler
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

# %% Görev 1: Faktör analizi sezgisi: anket üç maddesinin (enps, engagement, manager_score) korelasyon matrisinin en büyük özdeğeri (boşlar satırca atılır, 3 basamak)
R = survey[["enps", "engagement", "manager_score"]].dropna().corr(); cevap = np.linalg.eigvalsh(R).max()
assert abs(cevap - 2.136077) <= 0.010680384999999999, cevap
print("Görev 1:", round(cevap, 3), "✓")

# %% Görev 2: Bu özdeğerin toplam varyans içindeki payı (yüzde, 1 basamak)
R = survey[["enps", "engagement", "manager_score"]].dropna().corr(); cevap = 100 * np.linalg.eigvalsh(R).max() / 3
assert abs(cevap - 71.202582) <= 0.35601291, cevap
print("Görev 2:", round(cevap, 1), "✓")

# %% Görev 3: Cronbach alfa: üç madde standartlaştırılmış (k·r̄ / (1 + (k−1)·r̄), 3 basamak)
R = survey[["enps", "engagement", "manager_score"]].dropna().corr().to_numpy(); r = R[np.triu_indices(3, 1)].mean(); cevap = 3 * r / (1 + 2 * r)
assert abs(cevap - 0.794419) <= 0.003972095, cevap
print("Görev 3:", round(cevap, 3), "✓")
