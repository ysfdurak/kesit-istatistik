# S68 · Eşdeğerlik ve aşağı kalmama testleri
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

# %% Görev 1: Eşdeğerlik (TOST): kart ve cüzdan teslim süreleri ±0,5 dakika içinde eşdeğer mi? İki tek yönlü testten büyük olan p değeri (4 basamak)
from statsmodels.stats.weightstats import ttost_ind; cevap = ttost_ind(teslim[teslim.payment == "kart"].sure, teslim[teslim.payment == "cüzdan"].sure, -0.5, 0.5, usevar="unequal")[0]
assert abs(cevap - 0.076836) <= 0.00038418, cevap
print("Görev 1:", round(cevap, 4), "✓")

# %% Görev 2: Kart − cüzdan ortalama teslim süresi farkı (dakika, 3 basamak)
cevap = teslim[teslim.payment == "kart"].sure.mean() - teslim[teslim.payment == "cüzdan"].sure.mean()
assert abs(cevap - -0.014137) <= 0.0005, cevap
print("Görev 2:", round(cevap, 3), "✓")

# %% Görev 3: Aşağı kalmama: B grubu dönüşümü A'dan en fazla 2 puan kötü olabilir. (pB − pA + 0,02) / SE z istatistiği (3 basamak)
x = ab.groupby("variant").converted.agg(["mean", "count"]); pa, na = x.loc["A"]; pb, nb = x.loc["B"]; se = np.sqrt(pa * (1 - pa) / na + pb * (1 - pb) / nb); cevap = (pb - pa + 0.02) / se
assert abs(cevap - 3.873885) <= 0.019369425, cevap
print("Görev 3:", round(cevap, 3), "✓")
