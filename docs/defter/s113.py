# S113 · Eğilim skoru, eşleştirme ve IPW
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

# %% Görev 1: Eğilim skoru: hibrit çalışma (tedavi) olasılığı ~ eğitim + şehir İstanbul mu, lojistik; eğitim düzeyi "Lisans" olmayanlar için ortalama eğilim skoru (4 basamak)
d = emp.assign(t=(emp.work_mode == "hibrit").astype(int), ist=(emp.city == "İstanbul").astype(int)); ps = smf.logit("t ~ C(education) + ist", d).fit(disp=0).predict(d); cevap = ps[d.education != "Lisans"].mean()
assert abs(cevap - 0.25561) <= 0.002, cevap
print("Görev 1:", round(cevap, 4), "✓")

# %% Görev 2: IPW: hibrit ve diğer çalışanların gönüllü ayrılma oranı farkı (hibrit − diğer, eğilim skoru ağırlıklı, yüzde puan, 2 basamak)
d = emp.assign(t=(emp.work_mode == "hibrit").astype(int), ist=(emp.city == "İstanbul").astype(int), y=(emp.term_type == "gönüllü").astype(int)); ps = smf.logit("t ~ C(education) + ist", d).fit(disp=0).predict(d); w = np.where(d.t == 1, 1 / ps, 1 / (1 - ps)); cevap = 100 * (np.average(d.y[d.t == 1], weights=w[d.t == 1]) - np.average(d.y[d.t == 0], weights=w[d.t == 0]))
assert abs(cevap - 0.435547) <= 0.05, cevap
print("Görev 2:", round(cevap, 2), "✓")

# %% Görev 3: Ham fark: hibrit − diğer gönüllü ayrılma oranı (yüzde puan, 2 basamak)
y = emp.term_type == "gönüllü"; h = emp.work_mode == "hibrit"; cevap = 100 * (y[h].mean() - y[~h].mean())
assert abs(cevap - -3.330927) <= 0.016654635, cevap
print("Görev 3:", round(cevap, 2), "✓")
