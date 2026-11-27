# S100 · Marj, SVM ve çekirdekler
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

# %% Görev 1: Doğrusal SVM (LinearSVC, C = 1, dual = "auto", random_state = 0, standartlaştırılmış): test doğruluğu (yüzde, 1 basamak)
from sklearn.model_selection import train_test_split
d = ab.merge(web.groupby("user_id").agg(olay=("event_id", "count"), mobil=("device", lambda s: (s == "mobile").mean())).reset_index(), on="user_id", how="left").fillna(0)
d["B"] = (d.variant == "B").astype(int)
X, y = d[["B", "olay", "mobil"]], d.converted
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
from sklearn.svm import LinearSVC; from sklearn.preprocessing import StandardScaler; from sklearn.pipeline import make_pipeline; cevap = 100 * make_pipeline(StandardScaler(), LinearSVC(C=1, dual="auto", random_state=0)).fit(Xtr, ytr).score(Xte, yte)
assert abs(cevap - 87.166667) <= 0.43583333500000004, cevap
print("Görev 1:", round(cevap, 1), "✓")

# %% Görev 2: Dengesiz sınıfta SVM: class_weight = "balanced" ile test duyarlılığı (recall, yüzde, 1 basamak)
from sklearn.model_selection import train_test_split
d = ab.merge(web.groupby("user_id").agg(olay=("event_id", "count"), mobil=("device", lambda s: (s == "mobile").mean())).reset_index(), on="user_id", how="left").fillna(0)
d["B"] = (d.variant == "B").astype(int)
X, y = d[["B", "olay", "mobil"]], d.converted
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
from sklearn.svm import LinearSVC; from sklearn.preprocessing import StandardScaler; from sklearn.pipeline import make_pipeline; from sklearn.metrics import recall_score; cevap = 100 * recall_score(yte, make_pipeline(StandardScaler(), LinearSVC(C=1, dual="auto", random_state=0, class_weight="balanced")).fit(Xtr, ytr).predict(Xte))
assert abs(cevap - 64.935065) <= 0.32467532499999996, cevap
print("Görev 2:", round(cevap, 1), "✓")

# %% Görev 3: Testteki pozitif sınıf sayısı
from sklearn.model_selection import train_test_split
d = ab.merge(web.groupby("user_id").agg(olay=("event_id", "count"), mobil=("device", lambda s: (s == "mobile").mean())).reset_index(), on="user_id", how="left").fillna(0)
d["B"] = (d.variant == "B").astype(int)
X, y = d[["B", "olay", "mobil"]], d.converted
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
cevap = int(yte.sum())
assert abs(cevap - 77.0) <= 0.5, cevap
print("Görev 3:", round(cevap, 0), "✓")
