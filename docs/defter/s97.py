# S97 · LDA, QDA ve üretici sınıflandırma
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

# %% Görev 1: LDA: (B, olay, mobil) özellikleriyle dönüşüm; test doğruluğu (yüzde, 1 basamak). Ortak hazırlık kodu görevde.
from sklearn.model_selection import train_test_split
d = ab.merge(web.groupby("user_id").agg(olay=("event_id", "count"), mobil=("device", lambda s: (s == "mobile").mean())).reset_index(), on="user_id", how="left").fillna(0)
d["B"] = (d.variant == "B").astype(int)
X, y = d[["B", "olay", "mobil"]], d.converted
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA; cevap = 100 * LDA().fit(Xtr, ytr).score(Xte, yte)
assert abs(cevap - 87.166667) <= 0.43583333500000004, cevap
print("Görev 1:", round(cevap, 1), "✓")

# %% Görev 2: Test kümesinde herkesi "dönüşmez" tahmin etmenin doğruluğu (yüzde, 1 basamak)
from sklearn.model_selection import train_test_split
d = ab.merge(web.groupby("user_id").agg(olay=("event_id", "count"), mobil=("device", lambda s: (s == "mobile").mean())).reset_index(), on="user_id", how="left").fillna(0)
d["B"] = (d.variant == "B").astype(int)
X, y = d[["B", "olay", "mobil"]], d.converted
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
cevap = 100 * (yte == 0).mean()
assert abs(cevap - 87.166667) <= 0.43583333500000004, cevap
print("Görev 2:", round(cevap, 1), "✓")

# %% Görev 3: Eğitim kümesinin boyutu
from sklearn.model_selection import train_test_split
d = ab.merge(web.groupby("user_id").agg(olay=("event_id", "count"), mobil=("device", lambda s: (s == "mobile").mean())).reset_index(), on="user_id", how="left").fillna(0)
d["B"] = (d.variant == "B").astype(int)
X, y = d[["B", "olay", "mobil"]], d.converted
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
cevap = len(Xtr)
assert abs(cevap - 1400.0) <= 7.0, cevap
print("Görev 3:", round(cevap, 0), "✓")
