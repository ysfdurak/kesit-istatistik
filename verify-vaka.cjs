/* Depo vakası (vaka/depo/): Kesit İstatistik motoruyla Welch t-testi, SciPy ile hesaplanan beklenen değerlerle aynı mı? */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
global.window=global;vm.runInThisContext(fs.readFileSync(__dirname+'/docs/analysis-engine.js','utf8'));
const A=window.AnalysisEngine,html=fs.readFileSync(__dirname+'/vaka/depo/index.html','utf8'),csv=JSON.parse(html.match(/const CSV=("(?:[^"\\]|\\.)*")/)[1]);
const bek=JSON.parse(fs.readFileSync(__dirname+'/vaka/depo/beklenen.json','utf8')).istatistik;
const L=csv.trim().split('\n'),h=L[0].split(','),d=h.indexOf('duzen'),s=h.indexOf('sure_sn'),R=L.slice(1).map(l=>l.split(','));
const e=R.filter(r=>r[d]==='eski').map(r=>+r[s]),y=R.filter(r=>r[d]==='yeni').map(r=>+r[s]);
const m=a=>a.reduce((t,x)=>t+x,0)/a.length,v=a=>{const k=m(a);return a.reduce((t,x)=>t+(x-k)**2,0)/(a.length-1)};
const va=v(e)/e.length,vb=v(y)/y.length,se=Math.sqrt(va+vb),df=(va+vb)**2/(va**2/(e.length-1)+vb**2/(y.length-1)),fark=m(e)-m(y),t=fark/se,k=A.tInv(.975,df);
const got={fark,t,df,p:A.tP(t,df),alt:fark-k*se,ust:fark+k*se};
for(const n of Object.keys(got))assert.ok(Math.abs(got[n]-bek[n])<1e-6,n+': '+got[n]+' ≠ '+bek[n]);
assert.ok(got.p<.05&&got.ust<bek.esik,'karar: istatistiksel fark var, operasyonel eşiğin altında');
console.log(JSON.stringify({vaka:'depo',p:got.p,ust:got.ust,esik:bek.esik}));

// İkinci örnek (İzmir): aynı görünen kazanç, farklı vardiya dağılımı. Toplam fark anlamlı, vardiya içinde fark yok.
const bek2=JSON.parse(fs.readFileSync(__dirname+'/vaka/depo/beklenen.json','utf8')).istatistik2;
const csv2=JSON.parse(html.match(/const CSV2=("(?:[^"\\]|\\.)*")/)[1]).trim().split('\n'),h2=csv2[0].split(','),R2=csv2.slice(1).map(l=>l.split(','));
const iV=h2.indexOf('vardiya'),iD=h2.indexOf('duzen'),iS=h2.indexOf('sure_sn'),al=(dz,va)=>R2.filter(r=>r[iD]===dz&&(!va||r[iV]===va)).map(r=>+r[iS]);
const welch=(a,b)=>{const va=v(a)/a.length,vb=v(b)/b.length,se=Math.sqrt(va+vb),df=(va+vb)**2/(va**2/(a.length-1)+vb**2/(b.length-1)),d=m(a)-m(b),t=d/se,k=A.tInv(.975,df);return {fark:d,p:A.tP(t,df),alt:d-k*se,ust:d+k*se};};
const top=welch(al('eski'),al('yeni'));
for(const n of ['fark','p','alt','ust'])assert.ok(Math.abs(top[n]-bek2[n])<1e-6,'İzmir '+n+': '+top[n]+' ≠ '+bek2[n]);
let duz=0;for(const va of ['Gündüz','Gece']){const r=welch(al('eski',va),al('yeni',va)),b=bek2.katman[va];for(const n of ['fark','p','alt','ust'])assert.ok(Math.abs(r[n]-b[n])<1e-6,'İzmir '+va+' '+n);assert.ok(r.alt<0&&r.ust>0,va+' vardiyasında aralık sıfırı içermeli');duz+=bek2.agirlik[va]*r.fark;}
assert.ok(top.p<.05&&Math.abs(duz-bek2.duzeltilmis)<1e-9&&Math.abs(duz)<.5,'İzmir: toplam fark anlamlı, karışım sabitken fark yok');
assert.ok(Math.abs(top.fark-bek.fark)<.4,'İzmir kazancı Gebze ile aynı görünmeli');
console.log(JSON.stringify({vaka:'depo-izmir',toplam:top.fark,p:top.p,duzeltilmis:duz}));

// Denetim D03: aralığın tamamı sıfırın altındaysa karar metni kötüleşmeyi söyler ("sıfırı içeriyor" demez).
{
  const i=html.indexOf('function karar(r,esik,g){'),j=html.indexOf("</p></div>'};}",i)+"</p></div>'};}".length;
  const ctx={vkSay:(x,n)=>Number(x).toFixed(n).replace('.',',')};vm.createContext(ctx);vm.runInContext(html.slice(i,j)+';this.karar=karar;',ctx);
  const kot=ctx.karar({d:-1.2,p:.035,alt:-2.3,ust:-.1},4,.95);
  assert.ok(!kot.anl&&/kötüleşme/.test(kot.html)&&!/sıfırı içeriyor/.test(kot.html)&&!/≥ 0,05/.test(kot.html),'negatif aralık: '+kot.html);
  assert.ok(/1,200 sn daha uzun/.test(kot.html),'fark mutlak değerle yazılmalı');
  assert.ok(/sıfırı içeriyor/.test(ctx.karar({d:.3,p:.4,alt:-.5,ust:1.1},4,.95).html),'sıfırı içeren aralık');
  assert.ok(ctx.karar({d:2,p:.001,alt:1,ust:3},4,.95).anl,'pozitif aralık');
}
// Denetim D04: içinde yalnız sayı geçen alakasız metin "aralığı açıkladın" sayılmaz.
{
  const re=new Function('return '+html.match(/M=\[\[(\/.*?\/),'Farkın büyüklüğünü/)[1])();
  assert.ok(!re.test('üç kişi öğle yemeğine gitti, 3 kişi 12:30 da döndü'.toLocaleLowerCase('tr-TR')),'sayı tek başına aralık değil');
  for(const t of ['fark 1,9 sn, %95 güven aralığı 1,6–2,2 sn','aralık 1,6 ile 2,2 arasında','ga 1.6-2.2'])assert.ok(re.test(t),t);
}
// Denetim D07: kayıt reddedilirse uzman ekranı açılmaz.
assert.ok(/if\(!vkKaydet\(\{metin:/.test(html)&&/if\(!vkKaydet\(\{ornek2:/.test(html),'kaydet düğmeleri vkKaydet sonucuna bakmalı');
console.log(JSON.stringify({vaka:'depo-karar-ve-degerlendirme',ok:true}));
