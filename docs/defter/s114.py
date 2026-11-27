# S114 · Araç değişken ve doğal deney
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

# %% Görev 1: Araç değişken sezgisi (Wald oranı): A/B'de rastgele atama (B) aracı, "en az bir web olayı" aracıcı, dönüşüm sonuç. Atamanın dönüşüme etkisi (yüzde puan, 2 basamak)
pa, pb = ab.groupby("variant").converted.mean(); cevap = 100 * (pb - pa)
assert abs(cevap - 3.762351) <= 0.018811755, cevap
print("Görev 1:", round(cevap, 2), "✓")

# %% Görev 2: Atamanın "en az bir web olayı" oranına etkisi (B − A, yüzde puan, 2 basamak)
w = ab.user_id.isin(web.user_id); cevap = 100 * (w[ab.variant == "B"].mean() - w[ab.variant == "A"].mean())
assert abs(cevap - 1.901188) <= 0.009505940000000001, cevap
print("Görev 2:", round(cevap, 2), "✓")

# %% Görev 3: Bu iki sayının neden "Wald oranı" için zayıf araç uyarısı verdiğini görmek için: ilk adım etkisinin standart hatası (yüzde puan, 2 basamak)
w = ab.user_id.isin(web.user_id); a, b = w[ab.variant == "A"], w[ab.variant == "B"]; cevap = 100 * np.sqrt(a.mean() * (1 - a.mean()) / len(a) + b.mean() * (1 - b.mean()) / len(b))
assert abs(cevap - 2.048661) <= 0.010243305000000001, cevap
print("Görev 3:", round(cevap, 2), "✓")
