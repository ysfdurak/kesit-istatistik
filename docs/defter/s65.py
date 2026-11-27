# S65 · Mann–Whitney ve Wilcoxon
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

# %% Görev 1: Mann–Whitney U: kart ve nakit ödemeli teslimlerin süreleri; iki yönlü p değeri (4 basamak)
cevap = stats.mannwhitneyu(teslim[teslim.payment == "kart"].sure, teslim[teslim.payment == "nakit"].sure).pvalue
assert abs(cevap - 0.368718) <= 0.00184359, cevap
print("Görev 1:", round(cevap, 4), "✓")

# %% Görev 2: Wilcoxon işaretli sıralar: iki dalgadaki bağlılık değişimi; p değeri (4 basamak)
p = survey.pivot_table(index="emp_id", columns="wave", values="engagement").dropna(); cevap = stats.wilcoxon(p["2024-Q4"], p["2024-Q2"]).pvalue
assert abs(cevap - 0.189962) <= 0.0009498099999999999, cevap
print("Görev 2:", round(cevap, 4), "✓")

# %% Görev 3: Kart − nakit teslim süresi medyanları farkı (dakika, 2 basamak)
cevap = teslim[teslim.payment == "kart"].sure.median() - teslim[teslim.payment == "nakit"].sure.median()
assert abs(cevap - 0.633333) <= 0.005, cevap
print("Görev 3:", round(cevap, 2), "✓")
