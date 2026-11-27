# S107 · Kalibrasyon, Brier ve güvenilirlik diyagramı
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

# %% Görev 1: Brier skoru: lojistik regresyon (standartlaştırılmış) test kümesinde (4 basamak)
from sklearn.model_selection import train_test_split
d = ab.merge(web.groupby("user_id").agg(olay=("event_id", "count"), mobil=("device", lambda s: (s == "mobile").mean())).reset_index(), on="user_id", how="left").fillna(0)
d["B"] = (d.variant == "B").astype(int)
X, y = d[["B", "olay", "mobil"]], d.converted
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
from sklearn.linear_model import LogisticRegression; from sklearn.preprocessing import StandardScaler; from sklearn.pipeline import make_pipeline; from sklearn.metrics import brier_score_loss; cevap = brier_score_loss(yte, make_pipeline(StandardScaler(), LogisticRegression()).fit(Xtr, ytr).predict_proba(Xte)[:, 1])
assert abs(cevap - 0.111507) <= 0.000557535, cevap
print("Görev 1:", round(cevap, 4), "✓")

# %% Görev 2: Herkese eğitim oranını veren modelin Brier skoru (4 basamak)
from sklearn.model_selection import train_test_split
d = ab.merge(web.groupby("user_id").agg(olay=("event_id", "count"), mobil=("device", lambda s: (s == "mobile").mean())).reset_index(), on="user_id", how="left").fillna(0)
d["B"] = (d.variant == "B").astype(int)
X, y = d[["B", "olay", "mobil"]], d.converted
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
from sklearn.metrics import brier_score_loss; cevap = brier_score_loss(yte, np.full(len(yte), ytr.mean()))
assert abs(cevap - 0.111864) <= 0.0005593200000000001, cevap
print("Görev 2:", round(cevap, 4), "✓")

# %% Görev 3: Test kümesinde ortalama tahmin olasılığı ile gerçek oran farkı (yüzde puan, 3 basamak)
from sklearn.model_selection import train_test_split
d = ab.merge(web.groupby("user_id").agg(olay=("event_id", "count"), mobil=("device", lambda s: (s == "mobile").mean())).reset_index(), on="user_id", how="left").fillna(0)
d["B"] = (d.variant == "B").astype(int)
X, y = d[["B", "olay", "mobil"]], d.converted
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
from sklearn.linear_model import LogisticRegression; from sklearn.preprocessing import StandardScaler; from sklearn.pipeline import make_pipeline; p = make_pipeline(StandardScaler(), LogisticRegression()).fit(Xtr, ytr).predict_proba(Xte)[:, 1]; cevap = 100 * (p.mean() - yte.mean())
assert abs(cevap - -0.170396) <= 0.00085198, cevap
print("Görev 3:", round(cevap, 3), "✓")
