# S105 · İç içe çapraz doğrulama ve seçim yanlılığı
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

# %% Görev 1: İç içe çapraz doğrulama: lojistik regresyonda C ∈ {0,01; 0,1; 1; 10} için GridSearchCV (iç 3 kat) + dış 5 kat (StratifiedKFold, shuffle, random_state = 0) ortalama AUC (4 basamak)
from sklearn.model_selection import train_test_split
d = ab.merge(web.groupby("user_id").agg(olay=("event_id", "count"), mobil=("device", lambda s: (s == "mobile").mean())).reset_index(), on="user_id", how="left").fillna(0)
d["B"] = (d.variant == "B").astype(int)
X, y = d[["B", "olay", "mobil"]], d.converted
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
from sklearn.model_selection import GridSearchCV, cross_val_score, StratifiedKFold; from sklearn.linear_model import LogisticRegression; from sklearn.preprocessing import StandardScaler; from sklearn.pipeline import make_pipeline; gs = GridSearchCV(make_pipeline(StandardScaler(), LogisticRegression()), {"logisticregression__C": [.01, .1, 1, 10]}, cv=3, scoring="roc_auc"); cevap = cross_val_score(gs, X, y, cv=StratifiedKFold(5, shuffle=True, random_state=0), scoring="roc_auc").mean()
assert abs(cevap - 0.53714) <= 0.005, cevap
print("Görev 1:", round(cevap, 4), "✓")

# %% Görev 2: Seçim yanlılığı: aynı ızgarada yalnız GridSearchCV (5 kat) en iyi skoru (4 basamak); iç içe sonuçtan iyimser mi?
from sklearn.model_selection import train_test_split
d = ab.merge(web.groupby("user_id").agg(olay=("event_id", "count"), mobil=("device", lambda s: (s == "mobile").mean())).reset_index(), on="user_id", how="left").fillna(0)
d["B"] = (d.variant == "B").astype(int)
X, y = d[["B", "olay", "mobil"]], d.converted
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
from sklearn.model_selection import GridSearchCV, StratifiedKFold; from sklearn.linear_model import LogisticRegression; from sklearn.preprocessing import StandardScaler; from sklearn.pipeline import make_pipeline; cevap = GridSearchCV(make_pipeline(StandardScaler(), LogisticRegression()), {"logisticregression__C": [.01, .1, 1, 10]}, cv=StratifiedKFold(5, shuffle=True, random_state=0), scoring="roc_auc").fit(X, y).best_score_
assert abs(cevap - 0.53753) <= 0.005, cevap
print("Görev 2:", round(cevap, 4), "✓")

# %% Görev 3: Toplam örnek sayısı
from sklearn.model_selection import train_test_split
d = ab.merge(web.groupby("user_id").agg(olay=("event_id", "count"), mobil=("device", lambda s: (s == "mobile").mean())).reset_index(), on="user_id", how="left").fillna(0)
d["B"] = (d.variant == "B").astype(int)
X, y = d[["B", "olay", "mobil"]], d.converted
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
cevap = len(X)
assert abs(cevap - 2000.0) <= 10.0, cevap
print("Görev 3:", round(cevap, 0), "✓")
