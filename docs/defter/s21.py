# S21 · Hipotezler, p değeri ve karar
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

# %% Görev 1: A/B: B ile A dönüşüm oranı farkının iki oran z testi istatistiği (birleşik oranla, 3 basamak)
x = ab.groupby("variant").converted.agg(["sum", "count"]); p = x["sum"].sum() / x["count"].sum(); se = np.sqrt(p * (1 - p) * (1 / x.loc["A", "count"] + 1 / x.loc["B", "count"])); cevap = (x.loc["B", "sum"] / x.loc["B", "count"] - x.loc["A", "sum"] / x.loc["A", "count"]) / se
assert abs(cevap - 2.51736) <= 0.0125868, cevap
print("Görev 1:", round(cevap, 3), "✓")

# %% Görev 2: Aynı testin iki yönlü p değeri (4 basamak)
x = ab.groupby("variant").converted.agg(["sum", "count"]); p = x["sum"].sum() / x["count"].sum(); se = np.sqrt(p * (1 - p) * (1 / x.loc["A", "count"] + 1 / x.loc["B", "count"])); z = (x.loc["B", "sum"] / x.loc["B", "count"] - x.loc["A", "sum"] / x.loc["A", "count"]) / se; cevap = 2 * stats.norm.sf(abs(z))
assert abs(cevap - 0.011824) <= 5.9119999999999996e-05, cevap
print("Görev 2:", round(cevap, 4), "✓")

# %% Görev 3: Teslim süresi ortalaması 30 dakikadan farklı mı? Tek örneklem t istatistiği (3 basamak)
cevap = stats.ttest_1samp(teslim.sure, 30).statistic
assert abs(cevap - 58.559577) <= 0.292797885, cevap
print("Görev 3:", round(cevap, 3), "✓")
