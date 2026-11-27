# S07 · Yüzdelikler, IQR ve aykırı değerler
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

# %% Görev 1: Teslim süresinin IQR'ı (Q3 − Q1, dakika, 2 basamak; pandas quantile varsayılanı)
cevap = teslim.sure.quantile(.75) - teslim.sure.quantile(.25)
assert abs(cevap - 14.333333) <= 0.071666665, cevap
print("Görev 1:", round(cevap, 2), "✓")

# %% Görev 2: Tukey üst çitinin (Q3 + 1,5·IQR) üstünde kalan teslim sayısı
q1, q3 = teslim.sure.quantile([.25, .75]); cevap = (teslim.sure > q3 + 1.5 * (q3 - q1)).sum()
assert abs(cevap - 105.0) <= 0.525, cevap
print("Görev 2:", round(cevap, 0), "✓")

# %% Görev 3: Kart harcamalarında tutarın (mutlak değer) 95. yüzdeliği (TL, 2 basamak)
cevap = txns[txns.txn_type == "kart_harcama"].amount.abs().quantile(.95)
assert abs(cevap - 12789.0435) <= 63.9452175, cevap
print("Görev 3:", round(cevap, 2), "✓")
