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
