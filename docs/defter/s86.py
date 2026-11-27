# S86 · Anket ağırlıkları ve etkin örneklem
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

# %% Görev 1: Anket ağırlığı: çalışma modelinin anket içindeki payı ile çalışan tablosundaki payı oranı; "uzaktan" ağırlığı (popülasyon payı / örneklem payı, 4 basamak)
d = survey[survey.wave == "2024-Q4"].merge(emp[["emp_id", "work_mode"]], on="emp_id"); cevap = (emp.work_mode == "uzaktan").mean() / (d.work_mode == "uzaktan").mean()
assert abs(cevap - 0.851917) <= 0.004259585000000001, cevap
print("Görev 1:", round(cevap, 4), "✓")

# %% Görev 2: Kish etkin örneklem: ağırlıklar w (her yanıtlayana kendi modelinin ağırlığı), n_eff = (Σw)² / Σw² (Q4 dalgası, 1 basamak)
d = survey[survey.wave == "2024-Q4"].merge(emp[["emp_id", "work_mode"]], on="emp_id"); w = d.work_mode.map(emp.work_mode.value_counts(normalize=True) / d.work_mode.value_counts(normalize=True)); cevap = w.sum() ** 2 / (w ** 2).sum()
assert abs(cevap - 1105.511819) <= 5.527559095, cevap
print("Görev 2:", round(cevap, 1), "✓")

# %% Görev 3: Ağırlıklı ortalama bağlılık (Q4, aynı ağırlıklar, boşlar hariç, 4 basamak)
d = survey[survey.wave == "2024-Q4"].merge(emp[["emp_id", "work_mode"]], on="emp_id").dropna(subset=["engagement"]); w = d.work_mode.map(emp.work_mode.value_counts(normalize=True) / d.work_mode.value_counts(normalize=True)); cevap = (w * d.engagement).sum() / w.sum()
assert abs(cevap - 3.580449) <= 0.017902245, cevap
print("Görev 3:", round(cevap, 4), "✓")
