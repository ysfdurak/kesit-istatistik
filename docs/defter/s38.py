# S38 · Naif tahmin ve üstel düzeltme
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

# %% Görev 1: Naif tahmin: yarın = bugün. Günlük yolculuk serisinde naif tahminin ortalama mutlak hatası (MAE, 2 basamak)
cevap = gunluk.yolculuk.diff().abs().mean()
assert abs(cevap - 94.296703) <= 0.47148351499999996, cevap
print("Görev 1:", round(cevap, 2), "✓")

# %% Görev 2: Mevsimsel naif tahmin (geçen haftanın aynı günü) MAE (2 basamak)
cevap = gunluk.yolculuk.diff(7).abs().mean()
assert abs(cevap - 90.529412) <= 0.45264706, cevap
print("Görev 2:", round(cevap, 2), "✓")

# %% Görev 3: Basit üstel düzeltme (α = 0,3, ilk değer ilk gözlem): son gün için düzeltilmiş değer (2 basamak)
s = gunluk.yolculuk.astype(float); cevap = s.ewm(alpha=0.3, adjust=False).mean().iloc[-1]
assert abs(cevap - 1372.903307) <= 6.864516535, cevap
print("Görev 3:", round(cevap, 2), "✓")
