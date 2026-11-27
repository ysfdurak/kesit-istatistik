# S33 · A/B testi ve randomizasyon
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

# %% Görev 1: A/B: dönüşüm farkı (B − A) için %95 Wald güven aralığının alt sınırı (yüzde puan, 2 basamak)
x = ab.groupby("variant").converted.agg(["mean", "count"]); pa, na = x.loc["A"]; pb, nb = x.loc["B"]; se = np.sqrt(pa * (1 - pa) / na + pb * (1 - pb) / nb); cevap = 100 * (pb - pa - 1.96 * se)
assert abs(cevap - 0.846878) <= 0.005, cevap
print("Görev 1:", round(cevap, 2), "✓")

# %% Görev 2: Aynı aralığın üst sınırı (yüzde puan, 2 basamak)
x = ab.groupby("variant").converted.agg(["mean", "count"]); pa, na = x.loc["A"]; pb, nb = x.loc["B"]; se = np.sqrt(pa * (1 - pa) / na + pb * (1 - pb) / nb); cevap = 100 * (pb - pa + 1.96 * se)
assert abs(cevap - 6.677825) <= 0.033389125000000006, cevap
print("Görev 2:", round(cevap, 2), "✓")

# %% Görev 3: Örneklem oranı uyumsuzluğu (SRM) denetimi: 50/50 beklenen bölünmede ki-kare uygunluk p değeri (4 basamak)
n = ab.variant.value_counts(); cevap = stats.chisquare([n["A"], n["B"]]).pvalue
assert abs(cevap - 0.263552) <= 0.00131776, cevap
print("Görev 3:", round(cevap, 4), "✓")
