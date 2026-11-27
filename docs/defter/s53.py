# S53 · Veri sızıntısı ve çapraz doğrulama
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

# %% Görev 1: Sızıntı denetimi: revenue > 0 olan satır sayısı kaç? converted toplamıyla aynıysa revenue hedefin kopyasıdır, özellik olarak kullanılamaz.
cevap = (ab.revenue > 0).sum()
assert abs(cevap - 256.0) <= 1.28, cevap
print("Görev 1:", round(cevap, 0), "✓")

# %% Görev 2: 5 katlı çapraz doğrulama (KFold, shuffle, random_state = 0): yolculuk ~ sıcaklık doğrusal modelinin ortalama R² değeri (3 basamak)
from sklearn.model_selection import cross_val_score, KFold; from sklearn.linear_model import LinearRegression; cevap = cross_val_score(LinearRegression(), gunluk[["sicaklik"]], gunluk.yolculuk, cv=KFold(5, shuffle=True, random_state=0), scoring="r2").mean()
assert abs(cevap - -0.216652) <= 0.0010832600000000002, cevap
print("Görev 2:", round(cevap, 3), "✓")

# %% Görev 3: Zaman sırasını koruyan TimeSeriesSplit (5 bölme) ile aynı modelin ortalama R² değeri (3 basamak)
from sklearn.model_selection import cross_val_score, TimeSeriesSplit; from sklearn.linear_model import LinearRegression; cevap = cross_val_score(LinearRegression(), gunluk[["sicaklik"]], gunluk.yolculuk, cv=TimeSeriesSplit(5), scoring="r2").mean()
assert abs(cevap - -1.068978) <= 0.00534489, cevap
print("Görev 3:", round(cevap, 3), "✓")
