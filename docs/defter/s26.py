# S26 · Bağımsız gruplar ve Welch testi
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

# %% Görev 1: Welch t testi: B grubunda geliri olanlar ile A grubunda geliri olanların ortalama geliri (revenue > 0) farklı mı? t istatistiği (B − A, 3 basamak)
a = ab[(ab.variant == "A") & (ab.revenue > 0)].revenue; b = ab[(ab.variant == "B") & (ab.revenue > 0)].revenue; cevap = stats.ttest_ind(b, a, equal_var=False).statistic
assert abs(cevap - 1.807989) <= 0.009039945, cevap
print("Görev 1:", round(cevap, 3), "✓")

# %% Görev 2: Aynı testin p değeri (4 basamak)
a = ab[(ab.variant == "A") & (ab.revenue > 0)].revenue; b = ab[(ab.variant == "B") & (ab.revenue > 0)].revenue; cevap = stats.ttest_ind(b, a, equal_var=False).pvalue
assert abs(cevap - 0.071953) <= 0.000359765, cevap
print("Görev 2:", round(cevap, 4), "✓")

# %% Görev 3: Kart ve nakit ödemeli teslimlerin süre ortalaması farkı (kart − nakit, dakika, 3 basamak)
cevap = teslim[teslim.payment == "kart"].sure.mean() - teslim[teslim.payment == "nakit"].sure.mean()
assert abs(cevap - 0.224502) <= 0.00112251, cevap
print("Görev 3:", round(cevap, 3), "✓")
