# S48 · Çok değişkenli testler ve hiyerarşik yapı
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

# %% Görev 1: Hotelling yerine basit kontrol: hibrit ve ofis çalışanlarının (engagement, manager_score) ortalama vektörleri arasındaki Öklit farkı (3 basamak)
d = survey.merge(emp[["emp_id", "work_mode"]], on="emp_id").dropna(subset=["engagement", "manager_score"]); m = d.groupby("work_mode")[["engagement", "manager_score"]].mean(); cevap = np.sqrt(((m.loc["hibrit"] - m.loc["ofis"]) ** 2).sum())
assert abs(cevap - 0.190682) <= 0.00095341, cevap
print("Görev 1:", round(cevap, 3), "✓")

# %% Görev 2: Hiyerarşik özet: çalışma modeline göre bağlılık ortalamalarının ağırlıksız ortalaması (3 basamak)
d = survey.merge(emp[["emp_id", "work_mode"]], on="emp_id"); cevap = d.groupby("work_mode").engagement.mean().mean()
assert abs(cevap - 3.590984) <= 0.017954920000000003, cevap
print("Görev 2:", round(cevap, 3), "✓")

# %% Görev 3: engagement ile manager_score arasındaki korelasyon (3 basamak)
cevap = survey.engagement.corr(survey.manager_score)
assert abs(cevap - 0.58012) <= 0.0029005999999999997, cevap
print("Görev 3:", round(cevap, 3), "✓")
