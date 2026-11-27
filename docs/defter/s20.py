# S20 · Örneklem büyüklüğü ve güç
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

# %% Görev 1: Dönüşüm oranını ±2 puan hata payıyla (%95) ölçmek için gereken örneklem: p = A grubunun oranı (yukarı yuvarla)
p = ab[ab.variant == "A"].converted.mean(); cevap = math.ceil(1.96 ** 2 * p * (1 - p) / 0.02 ** 2)
assert abs(cevap - 931.0) <= 4.655, cevap
print("Görev 1:", round(cevap, 0), "✓")

# %% Görev 2: Teslim süresi ortalamasını ±1 dakika hata payıyla (%95) tahmin etmek için gereken n (std teslim süresinden, yukarı yuvarla)
cevap = math.ceil((1.96 * teslim.sure.std() / 1) ** 2)
assert abs(cevap - 446.0) <= 2.23, cevap
print("Görev 2:", round(cevap, 0), "✓")

# %% Görev 3: A ve B oranları arasındaki farkı %80 güç, %5 anlamlılıkla saptamak için grup başına gereken n (Cohen h ile; yukarı yuvarla)
from statsmodels.stats.power import NormalIndPower; pa, pb = ab.groupby("variant").converted.mean(); h = 2 * np.arcsin(np.sqrt(pb)) - 2 * np.arcsin(np.sqrt(pa)); cevap = math.ceil(NormalIndPower().solve_power(h, alpha=.05, power=.8))
assert abs(cevap - 1228.0) <= 6.140000000000001, cevap
print("Görev 3:", round(cevap, 0), "✓")
