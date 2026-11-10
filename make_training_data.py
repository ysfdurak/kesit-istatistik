import csv,math,random,datetime,pathlib,json
p=pathlib.Path('docs/data');p.mkdir(exist_ok=True);r=random.Random(20261108)
users={i:('B' if r.random()<.5 else 'A') for i in range(1,181)}
rows=[]
for i in range(1,1441):
 u=1+(i%180); day=(i-1)//24; items=r.randint(1,24);special=int(r.random()<.22);shift='Gece' if r.random()<.30 else 'Gunduz';depot='D1' if u%2 else 'D2';group=users[u]
 true=4+.45*items+3*special+(1.3 if shift=='Gece' else 0)-(1 if group=='B' else 0)+r.gauss(0,2)
 duration=round(max(.5,true),2);prob=1/(1+math.exp(-(-4+.07*items+.9*special+.4*(shift=='Gece')+.35*(depot=='D2'))));late=int(r.random()<prob)
 measured='' if (shift=='Gece' and r.random()<.14) or r.random()<.02 else duration
 rows.append([f'S{i:04}',f'M{u:03}',str(datetime.date(2026,1,1)+datetime.timedelta(days=day)),depot,shift,group,items,special,measured,late])
with (p/'operasyon_egitim.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['siparis_id','musteri_id','tarih','depo','vardiya','atama_grubu','urun_adedi','ozel_islem','sure_dakika','gecikti']);w.writerows(rows)
with (p/'talep_egitim.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['tarih','adet','kampanya'])
 for day in range(180):
  camp=int(day%30 in [1,2,3]); y=max(0,round(100+.25*day+20*math.sin(2*math.pi*day/7)+30*camp+r.gauss(0,8)));w.writerow([str(datetime.date(2026,1,1)+datetime.timedelta(days=day)),y,camp])
with (p/'guvenilirlik_egitim.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['birim_id','takip_gun','olay','grup'])
 for i in range(1,201):
  life=r.weibullvariate(60,1.7);follow=r.uniform(20,80);w.writerow([f'C{i:03}',round(min(life,follow),2),int(life<=follow),'A' if i%2 else 'B'])
print('Sentetik setler: 1.440 sipariş, 180 gün, 200 sansürlü takip.')
