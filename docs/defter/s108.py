# S108 · Model karşılaştırması ve eşleştirilmiş belirsizlik
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

# %% Görev 1: Model karşılaştırması: 10 katlı CV (StratifiedKFold, shuffle, random_state = 0) AUC farkları (lojistik − karar ağacı max_depth 3) ortalaması (4 basamak)
from sklearn.model_selection import train_test_split
d = ab.merge(web.groupby("user_id").agg(olay=("event_id", "count"), mobil=("device", lambda s: (s == "mobile").mean())).reset_index(), on="user_id", how="left").fillna(0)
d["B"] = (d.variant == "B").astype(int)
X, y = d[["B", "olay", "mobil"]], d.converted
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
from sklearn.model_selection import cross_val_score, StratifiedKFold; from sklearn.linear_model import LogisticRegression; from sklearn.tree import DecisionTreeClassifier; from sklearn.preprocessing import StandardScaler; from sklearn.pipeline import make_pipeline; cv = StratifiedKFold(10, shuffle=True, random_state=0); a = cross_val_score(make_pipeline(StandardScaler(), LogisticRegression()), X, y, cv=cv, scoring="roc_auc"); b = cross_val_score(DecisionTreeClassifier(max_depth=3, random_state=0), X, y, cv=cv, scoring="roc_auc"); cevap = (a - b).mean()
assert abs(cevap - 0.000269) <= 0.005, cevap
print("Görev 1:", round(cevap, 4), "✓")

# %% Görev 2: Aynı farkların eşleştirilmiş t testi p değeri (4 basamak)
from sklearn.model_selection import train_test_split
d = ab.merge(web.groupby("user_id").agg(olay=("event_id", "count"), mobil=("device", lambda s: (s == "mobile").mean())).reset_index(), on="user_id", how="left").fillna(0)
d["B"] = (d.variant == "B").astype(int)
X, y = d[["B", "olay", "mobil"]], d.converted
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
from sklearn.model_selection import cross_val_score, StratifiedKFold; from sklearn.linear_model import LogisticRegression; from sklearn.tree import DecisionTreeClassifier; from sklearn.preprocessing import StandardScaler; from sklearn.pipeline import make_pipeline; cv = StratifiedKFold(10, shuffle=True, random_state=0); a = cross_val_score(make_pipeline(StandardScaler(), LogisticRegression()), X, y, cv=cv, scoring="roc_auc"); b = cross_val_score(DecisionTreeClassifier(max_depth=3, random_state=0), X, y, cv=cv, scoring="roc_auc"); cevap = stats.ttest_rel(a, b).pvalue
assert abs(cevap - 0.978595) <= 0.02, cevap
print("Görev 2:", round(cevap, 4), "✓")

# %% Görev 3: Lojistik regresyonun 10 kat AUC standart sapması (4 basamak)
from sklearn.model_selection import train_test_split
d = ab.merge(web.groupby("user_id").agg(olay=("event_id", "count"), mobil=("device", lambda s: (s == "mobile").mean())).reset_index(), on="user_id", how="left").fillna(0)
d["B"] = (d.variant == "B").astype(int)
X, y = d[["B", "olay", "mobil"]], d.converted
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
from sklearn.model_selection import cross_val_score, StratifiedKFold; from sklearn.linear_model import LogisticRegression; from sklearn.preprocessing import StandardScaler; from sklearn.pipeline import make_pipeline; cevap = cross_val_score(make_pipeline(StandardScaler(), LogisticRegression()), X, y, cv=StratifiedKFold(10, shuffle=True, random_state=0), scoring="roc_auc").std(ddof=1)
assert abs(cevap - 0.076636) <= 0.005, cevap
print("Görev 3:", round(cevap, 4), "✓")
