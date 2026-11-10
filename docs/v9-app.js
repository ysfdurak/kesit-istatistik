/* Kesit İstatistik V9 · Kesit verileriyle vakalar, alıştırma atölyesi, sık hatalar, mülakat, seviye testi */
(function (g) {
'use strict';
const C = g.COURSE, E = g.AnalysisEngine, X = g.KESIT_ECOSYSTEM, K = g.KesitV9Content;
const KEY = 'kesit-stat-v9';
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const $ = s => document.querySelector(s);
const nf = (x, d = 2) => Number(x).toLocaleString('tr-TR', {maximumFractionDigits: d, minimumFractionDigits: 0});
const lessonById = id => C.lessons.find(l => l.id === id);
const lessonLink = id => { const l = lessonById(id); return l ? `<a class="v9-chip" href="#lesson/${id}">${esc(id.slice(1))} · ${esc(l.title)}</a>` : ''; };
const APPS = {
  sql: {name: 'Kesit SQL', url: 'https://ysfdurak.github.io/kesit-sql/'},
  powerbi: {name: 'Kesit Power BI', url: 'https://ysfdurak.github.io/kesit-powerbi/'},
  python: {name: 'Kesit Python', url: 'https://ysfdurak.github.io/kesit-python/'}
};

/* ---------- kayıt ---------- */
let store = {version: 1, practice: {}, cases: {}, interview: {}, placement: null};
let storeError = '';
function validStore(s) {
  return s && s.version === 1 && typeof s.practice === 'object' && !Array.isArray(s.practice) &&
    Object.values(s.practice).every(v => v && Number.isInteger(v.a) && Number.isInteger(v.c) && v.c <= v.a) &&
    typeof s.cases === 'object' && typeof s.interview === 'object';
}
try { const raw = localStorage.getItem(KEY); if (raw) { const s = JSON.parse(raw); if (validStore(s)) store = {...store, ...s}; else storeError = 'format'; } } catch (e) { storeError = 'okuma'; }
function save() { if (storeError === 'format') return false; try { localStorage.setItem(KEY, JSON.stringify(store)); return true; } catch (e) { return false; } }
function toast(t) { const el = $('#toast'); if (!el) return; el.textContent = t; el.style.display = 'block'; clearTimeout(toast.t); toast.t = setTimeout(() => { el.style.display = 'none'; }, 3000); }
function copyText(t) {
  const ok = () => toast('Kod kopyalandı.');
  if (navigator.clipboard?.writeText) navigator.clipboard.writeText(t).then(ok, () => fallback());
  else fallback();
  function fallback() { const ta = document.createElement('textarea'); ta.value = t; document.body.appendChild(ta); ta.select(); try { document.execCommand('copy'); ok(); } catch (e) { toast('Kopyalanamadı; metni seçip kopyala.'); } ta.remove(); }
}

/* ---------- ortak bileşenler ---------- */
function head(eyebrow, title, intro) {
  return `<div class="page-title"><div><div class="eyebrow">${eyebrow}</div><h1>${title}</h1><div class="intro">${intro}</div></div><span class="pill"><span class="status-dot"></span> V9</span></div>`;
}
function codeTabs(id, items) {
  const avail = items.filter(x => x.code);
  return `<div class="v9-code" data-codetabs="${id}"><div class="v9-code-tabs" role="tablist" aria-label="Araç">${avail.map((x, i) => `<button type="button" role="tab" aria-selected="${i === 0}" data-code-tab="${i}">${esc(x.label)}</button>`).join('')}</div>${avail.map((x, i) => `<div class="v9-code-panel" data-code-panel="${i}" ${i ? 'hidden' : ''}><button type="button" class="btn tiny v9-copy" data-copy>Kopyala</button><pre><code>${esc(x.code)}</code></pre>${x.note ? `<p class="v9-muted">${x.note}</p>` : ''}</div>`).join('')}</div>`;
}
function chart(c) {
  if (!c || !c.values) return '';
  const W = 620, H = 260, L = 54, R = 16, T = 18, B = 54, n = c.values.length;
  const vals = c.values.map(v => v ?? 0), his = (c.hi || []).map((v, i) => v ?? vals[i]), los = (c.lo || []).map((v, i) => v ?? vals[i]);
  const log = !!c.log;
  let max = Math.max(...vals, ...his), min = c.min ?? (log ? Math.min(...vals) / 1.6 : Math.min(0, ...vals, ...los));
  if (c.max) max = c.max; else max = max * 1.12;
  if (max === min) max = min + 1;
  const tf = v => log ? Math.log10(v) : v;
  const y = v => T + (H - T - B) * (1 - (tf(v) - tf(min)) / (tf(max) - tf(min)));
  const bw = (W - L - R) / n, gap = Math.min(18, bw * .25);
  const ticks = log ? [10, 100, 1000, 10000].filter(t => t >= min && t <= max) : Array.from({length: 5}, (_, i) => min + (max - min) * i / 4);
  let s = `<svg viewBox="0 0 ${W} ${H}" class="v9-chart" role="img" aria-label="${esc(c.caption || 'Grafik')}">`;
  ticks.forEach(t => { s += `<line x1="${L}" x2="${W - R}" y1="${y(t)}" y2="${y(t)}" class="v9-grid"/><text x="${L - 8}" y="${y(t) + 4}" text-anchor="end" class="v9-tick">${nf(t, Math.abs(max - min) < 10 ? 1 : 0)}</text>`; });
  vals.forEach((v, i) => {
    const x0 = L + i * bw + gap / 2, w = bw - gap, base = y(log ? min : Math.max(min, 0)), top = y(v);
    s += `<rect x="${x0}" y="${Math.min(top, base)}" width="${w}" height="${Math.max(1, Math.abs(base - top))}" rx="4" class="v9-bar ${c.kind === 'hist' ? 'hist' : ''}"><title>${esc(c.labels[i])}: ${nf(v)} ${esc(c.unit || '')}</title></rect>`;
    if (c.hi && c.hi[i] != null) { const cx = x0 + w / 2; s += `<line x1="${cx}" x2="${cx}" y1="${y(c.hi[i])}" y2="${y(c.lo[i])}" class="v9-err"/><line x1="${cx - 7}" x2="${cx + 7}" y1="${y(c.hi[i])}" y2="${y(c.hi[i])}" class="v9-err"/><line x1="${cx - 7}" x2="${cx + 7}" y1="${y(c.lo[i])}" y2="${y(c.lo[i])}" class="v9-err"/>`; }
    if (c.kind !== 'hist' || n <= 10) s += `<text x="${x0 + w / 2}" y="${Math.min(top, base, c.hi && c.hi[i] != null ? y(c.hi[i]) : top) - 6}" text-anchor="middle" class="v9-val">${nf(v, 1)}</text>`;
    const showLabel = c.kind !== 'hist' || i % 2 === 0;
    if (showLabel) s += `<text x="${x0 + w / 2}" y="${H - B + 18}" text-anchor="middle" class="v9-lab">${esc(c.labels[i])}</text>`;
  });
  (c.marks || []).forEach(([name, v]) => { if (c.kind !== 'hist') return; const x = L + ((v - c.start) / c.step) * bw; s += `<line x1="${x}" x2="${x}" y1="${T}" y2="${H - B}" class="v9-mark"/><text x="${x + 4}" y="${T + 12}" class="v9-mark-t">${esc(name)} ${nf(v, 1)}</text>`; });
  s += `<text x="${L}" y="${H - 8}" class="v9-cap">${esc(c.caption || '')}${c.unit ? ' · ' + esc(c.unit) : ''}${log ? ' · log ölçek' : ''}</text></svg>`;
  return `<figure class="v9-fig">${s}</figure>`;
}

/* Seçenek sırası: kimliğe bağlı kararlı karıştırma (doğru cevap hep aynı yerde durmasın). */
function order(n, key) { let h = 2166136261; for (const ch of String(key)) h = Math.imul(h ^ ch.charCodeAt(0), 16777619) >>> 0; const a = Array.from({length: n}, (_, i) => i); for (let i = n - 1; i > 0; i--) { h = Math.imul(h ^ (h >>> 15), 2246822507) >>> 0; const j = h % (i + 1); [a[i], a[j]] = [a[j], a[i]]; } return a; }
/* ---------- 1) Kesit verileriyle vakalar ---------- */
function dataPage() {
  const done = Object.keys(store.cases).filter(k => store.cases[k]).length;
  const ds = X.datasets;
  return head('KESİT EKOSİSTEMİ', 'Aynı veri, yeni soru: istatistik.', 'Kesit SQL, Power BI ve Python\'da sorguladığın kurgusal şirket verileri burada istatistik sorusuna dönüşür. Her vakada önce tahmin edersin; sonra SQL ile veriyi hazırlar, Python ile test eder, Power BI ölçüsüyle raporlar ve sonucu sınırlarıyla yorumlarsın.') +
  `<div class="v9-eco">${Object.values(APPS).map(a => `<a class="v9-eco-app" href="${a.url}" target="_blank" rel="noopener"><b>${esc(a.name)}</b><span>Aynı veri setleri ↗</span></a>`).join('')}<div class="v9-eco-flow"><span>SQL ile hazırla</span>→<span>Python ile test et</span>→<span>Power BI ile raporla</span>→<span>İstatistikle yorumla</span></div></div>` +
  `<div class="stats"><div class="stat"><div><strong>${X.cases.length}</strong><small>Vaka</small></div></div><div class="stat"><div><strong>${Object.keys(ds).length}</strong><small>Ortak veri seti</small></div></div><div class="stat"><div><strong>${done}/${X.cases.length}</strong><small>Bitirdiğin vaka</small></div></div><div class="stat"><div><strong>3</strong><small>Araç: SQL · DAX · Python</small></div></div></div>` +
  Object.entries(ds).map(([name, d]) => {
    const cs = X.cases.filter(c => c.dataset === name);
    return `<section class="v9-ds"><div class="section-head"><div><h2>${esc(name)}</h2><p>${esc(d.desc)}</p></div></div><div class="cards v9-case-grid">${cs.map(c => `<a class="card v9-case-card ${store.cases[c.id] ? 'done' : ''}" href="#data/${c.id}"><span class="eyebrow">${esc(c.method)}</span><h3>${esc(c.title)}</h3><p>${esc(c.question)}</p><span class="v9-meta">${store.cases[c.id] ? '✓ Bitirildi · ' : ''}Tablolar: ${c.tables.map(esc).join(', ')}</span></a>`).join('')}</div></section>`;
  }).join('') +
  `<div class="article v9-note"><h2>Sayılar nereden geliyor?</h2><p>Bütün sonuçlar kardeş uygulamalarla satır satır aynı CSV dosyalarından <code>ecosystem_cases_v9.py</code> betiğiyle hesaplandı. Python kodları veriyi doğrudan GitHub'dan okur; kendi bilgisayarında çalıştırınca aynı sayıları görürsün (bootstrap aralıkları rastgele tohuma göre birkaç ondalık değişebilir). Şirketler, kişiler ve kayıtlar hayalidir.</p></div>`;
}
function casePage(id) {
  const c = X.cases.find(x => x.id === id);
  if (!c) return dataPage();
  const i = X.cases.indexOf(c), prev = X.cases[i - 1], next = X.cases[i + 1];
  const app = APPS[c.app];
  const answered = store.cases[c.id + ':p'];
  return `<div class="v9-case">` +
  `<nav class="v9-back"><a href="#data">← Kesit verileriyle vakalar</a><span>${esc(c.dataset)} · Vaka ${i + 1}/${X.cases.length}</span></nav>` +
  `<div class="v9-case-head"><div class="eyebrow">${esc(c.dataset).toUpperCase()} · ${c.tables.map(esc).join(' · ')}</div><h1>${esc(c.title)}</h1><p class="intro">${esc(c.question)}</p><p class="v9-muted"><b>Analiz birimi:</b> ${esc(c.unit)}</p></div>` +
  `<ol class="v9-steps">` +
  `<li><h2>Önce tahmin et</h2><form class="v9-predict" data-predict="${c.id}"><p><b>${esc(c.predict.q)}</b></p>${order(c.predict.options.length, c.id).map(k => `<label class="option"><input type="radio" name="p-${c.id}" value="${k}"> <span>${esc(c.predict.options[k])}</span></label>`).join('')}<button class="btn" type="submit">Kontrol et</button><div class="v9-pfb" role="status" aria-live="polite">${answered ? `<div class="feedback good"><b>Doğru yanıt:</b> ${esc(c.predict.options[c.predict.correct])}<p>${esc(c.predict.why)}</p></div>` : ''}</div></form></li>` +
  `<li><h2>Yöntemi seç</h2><p><b>${esc(c.method)}</b></p><p>${esc(c.why)}</p></li>` +
  `<li><h2>Araçlarda uygula</h2><p class="v9-muted">SQL'de veriyi hazırla, Python'da testi çalıştır, Power BI'da raporun ölçüsünü kur. Python kodu veriyi doğrudan GitHub'dan okur.</p>${codeTabs(c.id, [{label: 'SQL', code: c.sql, note: 'SQLite yazımı (Kesit SQL varsayılanı). Yüzdelik gibi bazı fonksiyonlar SQL türüne göre değişir.'}, {label: 'Python', code: c.python, note: 'pandas, scipy ve statsmodels gerekir. Kesit Python\'daki tarayıcı motorunda da çalışır (statsmodels ilk çalıştırmada yüklenir).'}, {label: 'Power BI (DAX)', code: c.dax, note: 'Tablo adları Kesit Power BI vaka paketindeki adlarla aynıdır.'}])}<p><a class="text-link" href="${app.url}" target="_blank" rel="noopener">Bu veriyi ${esc(app.name)}'de aç ↗</a></p></li>` +
  `<li><h2>Sonucu oku</h2><div class="v9-result"><table class="v9-table"><tbody>${c.results.map(([a, b]) => `<tr><th scope="row">${esc(a)}</th><td>${esc(b)}</td></tr>`).join('')}</tbody></table>${chart(c.chart)}</div></li>` +
  `<li><h2>Karara çevir</h2><p>${esc(c.read)}</p><div class="v9-limit"><b>Bu analiz neyi söyleyemez?</b><p>${esc(c.limits)}</p></div></li>` +
  `<li><h2>Konuyu derinleştir</h2><div class="v9-chips">${c.lessons.map(lessonLink).join('')}</div><label class="v9-label" for="case-note-${c.id}">Karar notun (bu cihazda saklanır)</label><textarea id="case-note-${c.id}" data-case-note="${c.id}" rows="4" placeholder="Bulgu, belirsizlik, karar ve sonraki doğrulama…">${esc(store.cases[c.id + ':note'] || '')}</textarea><div class="actions"><button class="btn primary" data-v9="finish-case" data-id="${c.id}">${store.cases[c.id] ? '✓ Bitirildi' : 'Vakayı bitirdim'}</button></div></li>` +
  `</ol><nav class="v9-pager">${prev ? `<a class="btn" href="#data/${prev.id}">← ${esc(prev.title)}</a>` : '<span></span>'}${next ? `<a class="btn" href="#data/${next.id}">${esc(next.title)} →</a>` : '<a class="btn" href="#data">Tüm vakalar</a>'}</nav></div>`;
}

/* ---------- 2) Alıştırma atölyesi (parametreli üretici sorular) ---------- */
let seed = (Date.now() % 2147483647) || 1;
function rnd() { seed = (Math.imul(48271, seed) % 2147483647 + 2147483647) % 2147483647; return seed / 2147483647; }
const ri = (a, b) => a + Math.floor(rnd() * (b - a + 1));
const rf = (a, b, d = 2) => Number((a + rnd() * (b - a)).toFixed(d));
const pick = a => a[Math.floor(rnd() * a.length)];
const lc = (n, k) => { let s = 0; for (let i = 1; i <= k; i++) s += Math.log(n - k + i) - Math.log(i); return s; };
const median = a => { const b = [...a].sort((x, y) => x - y), m = b.length >> 1; return b.length % 2 ? b[m] : (b[m - 1] + b[m]) / 2; };
const sdS = a => { const m = a.reduce((s, x) => s + x, 0) / a.length; return Math.sqrt(a.reduce((s, x) => s + (x - m) ** 2, 0) / (a.length - 1)); };
const P = (x, d = 2) => nf(x, d);
const GEN = [
  {id:'orneklem',lesson:'s01',title:'Örnekleme oranı',group:'Temel',make(){const N=pick([800,1200,2000,2500,4000,5000]),n=pick([20,40,50,100,150,200]);const a=n/N*100;return{q:`Bir depodaki ${P(N,0)} siparişten ${n} tanesi rastgele inceleniyor. Örnekleme oranı yüzde kaçtır?`,unit:'%',answer:a,dec:2,hint:'Oran = n / N × 100',steps:[`n = ${n}, N = ${P(N,0)}`,`${n} / ${P(N,0)} = ${P(n/N,4)}`,`× 100 = %${P(a)}`]}}},
  {id:'medyan',lesson:'s05',title:'Medyan',group:'Temel',make(){const n=pick([7,8]),a=Array.from({length:n},()=>ri(2,30));a[n-1]=ri(60,120);const m=median(a),s=[...a].sort((x,y)=>x-y);return{q:`Toplama süreleri (dk): ${a.join(', ')}. Medyan kaçtır?`,unit:'dk',answer:m,dec:2,hint:'Sırala; tek sayıda gözlemde ortadaki, çift sayıda ortadaki iki değerin ortalaması.',steps:[`Sıralı: ${s.join(', ')}`,n%2?`Ortadaki (${(n+1)/2}.) değer: ${m}`:`Ortadaki iki değer: ${s[n/2-1]} ve ${s[n/2]} → (${s[n/2-1]} + ${s[n/2]}) / 2 = ${P(m)}`,`Ortalama ${P(a.reduce((x,y)=>x+y,0)/n)} olur: son değer ortalamayı çeker, medyanı etkilemez.`]}}},
  {id:'sd',lesson:'s06',title:'Örneklem standart sapması',group:'Temel',make(){const a=Array.from({length:5},()=>ri(2,14)),m=a.reduce((x,y)=>x+y,0)/5,ss=a.reduce((x,y)=>x+(y-m)**2,0);return{q:`Beş günlük hata sayıları: ${a.join(', ')}. Örneklem standart sapması (n − 1 ile) kaçtır?`,unit:'',answer:sdS(a),dec:3,hint:'s = √[ Σ(x − x̄)² / (n − 1) ]',steps:[`x̄ = ${P(m,2)}`,`Σ(x − x̄)² = ${P(ss,3)}`,`s² = ${P(ss,3)} / 4 = ${P(ss/4,3)}`,`s = √${P(ss/4,3)} = ${P(sdS(a),3)}`]}}},
  {id:'cv',lesson:'s06',title:'Değişim katsayısı',group:'Temel',make(){const m=ri(20,90),s=rf(2,25,1);return{q:`Ortalama teslim süresi ${m} dk, standart sapma ${P(s,1)} dk. Değişim katsayısı yüzde kaçtır?`,unit:'%',answer:s/m*100,dec:2,hint:'CV = s / x̄ × 100',steps:[`${P(s,1)} / ${m} = ${P(s/m,4)}`,`× 100 = %${P(s/m*100)}`,'CV birimsizdir; farklı ölçekteki süreçlerin değişkenliğini karşılaştırır.']}}},
  {id:'iqr',lesson:'s07',title:'IQR ve üst çit',group:'Temel',make(){const q1=ri(20,40),q3=q1+ri(8,25);const f=q3+1.5*(q3-q1);return{q:`Q1 = ${q1} dk, Q3 = ${q3} dk. Tukey üst çiti (Q3 + 1,5·IQR) kaç dakikadır?`,unit:'dk',answer:f,dec:2,hint:'IQR = Q3 − Q1; üst çit = Q3 + 1,5 × IQR',steps:[`IQR = ${q3} − ${q1} = ${q3-q1}`,`1,5 × ${q3-q1} = ${P(1.5*(q3-q1))}`,`Üst çit = ${q3} + ${P(1.5*(q3-q1))} = ${P(f)}`,'Çitin üstü "incelenecek" demektir; silinecek demek değildir.']}}},
  {id:'agirlik',lesson:'s08',title:'Ağırlıklı oran',group:'Temel',make(){const n1=ri(20,80),n2=ri(400,1200),p1=ri(30,60),p2=ri(5,15);const t=(n1*p1+n2*p2)/(n1+n2);return{q:`Şube A: ${n1} müşteri, dönüşüm %${p1}. Şube B: ${n2} müşteri, dönüşüm %${p2}. Toplam dönüşüm yüzde kaçtır?`,unit:'%',answer:t,dec:2,hint:'Toplam oran = (n₁p₁ + n₂p₂) / (n₁ + n₂). Basit ortalama yanlıştır.',steps:[`Dönüşen: ${n1}×${p1/100} + ${n2}×${p2/100} = ${P(n1*p1/100+n2*p2/100,2)}`,`Toplam müşteri: ${n1+n2}`,`Oran = %${P(t)} (basit ortalama %${P((p1+p2)/2)} olurdu)`]}}},
  {id:'birlesim',lesson:'s09',title:'Birleşim olasılığı',group:'Temel',make(){const a=rf(.2,.5),b=rf(.2,.5),ab=rf(.03,Math.min(a,b)-.02);return{q:`P(geç teslim) = ${P(a)}, P(hasarlı) = ${P(b)}, P(ikisi birden) = ${P(ab)}. P(geç teslim ya da hasarlı) kaçtır?`,unit:'',answer:a+b-ab,dec:3,hint:'P(A ∪ B) = P(A) + P(B) − P(A ∩ B)',steps:[`${P(a)} + ${P(b)} − ${P(ab)} = ${P(a+b-ab,3)}`,'Kesişim çıkarılmazsa ikisi birden olan siparişler iki kez sayılır.']}}},
  {id:'kosullu',lesson:'s10',title:'Koşullu olasılık (çapraz tablo)',group:'Temel',make(){const a=ri(20,80),b=ri(100,300),c=ri(10,60),d=ri(200,500);return{q:`Mobil kanalda ${a} iade, ${b} iadesiz sipariş; web kanalında ${c} iade, ${d} iadesiz sipariş var. P(iade | mobil) yüzde kaçtır?`,unit:'%',answer:a/(a+b)*100,dec:2,hint:'P(A | B) = P(A ∩ B) / P(B): yalnızca mobil satırına bak.',steps:[`Mobil toplam = ${a} + ${b} = ${a+b}`,`${a} / ${a+b} = %${P(a/(a+b)*100)}`,`Karşılaştır: P(iade | web) = %${P(c/(c+d)*100)}`]}}},
  {id:'bayes',lesson:'s11',title:'Bayes: pozitif öngörü değeri',group:'Temel',make(){const pr=pick([.5,1,2,5]),se=pick([90,95,99]),sp=pick([90,95,98]);const tp=pr/100*se/100,fp=(1-pr/100)*(1-sp/100),ppv=tp/(tp+fp)*100;return{q:`Hatalı ürün oranı %${P(pr,1)}. Kontrol cihazı hatalıların %${se}'unu yakalıyor, sağlamların %${sp}'sini doğru geçiriyor. Cihaz "hatalı" dediğinde ürünün gerçekten hatalı olma olasılığı yüzde kaçtır?`,unit:'%',answer:ppv,dec:1,tol:.6,hint:'PPV = duyarlılık·taban / [duyarlılık·taban + (1 − özgüllük)·(1 − taban)]',steps:[`Doğru alarm: ${P(pr/100,4)} × ${P(se/100)} = ${P(tp,5)}`,`Yanlış alarm: ${P(1-pr/100,4)} × ${P(1-sp/100)} = ${P(fp,5)}`,`PPV = ${P(tp,5)} / ${P(tp+fp,5)} = %${P(ppv,1)}`,'Taban oran düşükse iyi bir test bile çok yanlış alarm üretir.']}}},
  {id:'beklenen',lesson:'s12',title:'Beklenen değer',group:'Temel',make(){const p1=rf(.5,.8),p2=Number((1-p1).toFixed(2)),k=ri(200,800),z=ri(1000,4000);const ev=p1*k-p2*z;return{q:`Bir kampanya %${P(p1*100,0)} olasılıkla ${k} TL kâr, %${P(p2*100,0)} olasılıkla ${z} TL zarar getiriyor. Beklenen sonuç kaç TL'dir?`,unit:'TL',answer:ev,dec:2,hint:'E[X] = Σ x · P(x)',steps:[`${P(p1)} × ${k} = ${P(p1*k)}`,`${P(p2)} × (−${z}) = ${P(-p2*z)}`,`E[X] = ${P(ev)} TL`,'Beklenen değer riskin büyüklüğünü söylemez; varyansı da düşün.']}}},
  {id:'binom',lesson:'s13',title:'Binom olasılığı',group:'Orta',make(){const n=ri(8,20),p=pick([.05,.1,.15,.2,.3]),k=ri(0,Math.min(4,n));const pr=Math.exp(lc(n,k)+k*Math.log(p)+(n-k)*Math.log(1-p));return{q:`Her siparişin iade olasılığı ${P(p)}. ${n} bağımsız siparişte tam ${k} iade olma olasılığı kaçtır? (4 ondalık)`,unit:'',answer:pr,dec:4,tol:.0006,hint:'P(X = k) = C(n,k) pᵏ (1 − p)ⁿ⁻ᵏ',steps:[`C(${n},${k}) = ${P(Math.round(Math.exp(lc(n,k))),0)}`,`p^k = ${P(p**k,6)}, (1−p)^(n−k) = ${P((1-p)**(n-k),6)}`,`Çarpım = ${P(pr,4)}`]}}},
  {id:'poisson',lesson:'s13',title:'Poisson olasılığı',group:'Orta',make(){const l=rf(1,6,1),k=ri(0,5);let f=1;for(let i=2;i<=k;i++)f*=i;const pr=Math.exp(-l)*l**k/f;return{q:`Saatte ortalama ${P(l,1)} arıza bildirimi geliyor. Bir saatte tam ${k} bildirim gelme olasılığı kaçtır? (4 ondalık)`,unit:'',answer:pr,dec:4,tol:.0006,hint:'P(X = k) = e^(−λ) λᵏ / k!',steps:[`e^(−${P(l,1)}) = ${P(Math.exp(-l),5)}`,`λ^k / k! = ${P(l**k,4)} / ${f} = ${P(l**k/f,4)}`,`P = ${P(pr,4)}`,'Varsayım: olaylar bağımsız ve oran saat içinde sabit.']}}},
  {id:'z',lesson:'s14',title:'z puanı ve normal olasılık',group:'Orta',make(){const mu=ri(30,60),sg=ri(4,12),x=mu+pick([-2,-1.5,-1,-.5,.5,1,1.25,1.5,2])*sg;const z=(x-mu)/sg,pr=E.normalCDF(z)*100;return{q:`Teslim süresi yaklaşık normal: ortalama ${mu} dk, standart sapma ${sg} dk. Bir siparişin ${P(x,1)} dakikadan kısa sürme olasılığı yüzde kaçtır?`,unit:'%',answer:pr,dec:1,tol:.15,hint:'z = (x − μ) / σ; P(X < x) = Φ(z)',steps:[`z = (${P(x,1)} − ${mu}) / ${sg} = ${P(z,2)}`,`Φ(${P(z,2)}) = ${P(pr/100,4)}`,`= %${P(pr,1)}`]}}},
  {id:'se',lesson:'s18',title:'Standart hata',group:'Orta',make(){const s=rf(4,30,1),n=pick([16,25,36,49,64,100,144]);return{q:`Örneklem standart sapması ${P(s,1)}, n = ${n}. Ortalamanın standart hatası kaçtır?`,unit:'',answer:s/Math.sqrt(n),dec:3,hint:'SE = s / √n',steps:[`√${n} = ${Math.sqrt(n)}`,`SE = ${P(s,1)} / ${Math.sqrt(n)} = ${P(s/Math.sqrt(n),3)}`,'n dört katına çıkınca SE yarıya iner.']}}},
  {id:'ciort',lesson:'s19',title:'Ortalama için %95 aralık',group:'Orta',make(){const m=rf(30,60,1),s=rf(5,15,1),n=pick([100,144,225,400]);const se=s/Math.sqrt(n),u=m+1.96*se;return{q:`n = ${n}, x̄ = ${P(m,1)}, s = ${P(s,1)}. Büyük örneklem z yaklaşımıyla %95 güven aralığının üst sınırı kaçtır?`,unit:'',answer:u,dec:2,tol:.02,hint:'x̄ ± 1,96 · s/√n',steps:[`SE = ${P(s,1)} / ${Math.sqrt(n)} = ${P(se,4)}`,`Hata payı = 1,96 × ${P(se,4)} = ${P(1.96*se,3)}`,`Üst sınır = ${P(m,1)} + ${P(1.96*se,3)} = ${P(u)}`]}}},
  {id:'cioran',lesson:'s19',title:'Oran için hata payı',group:'Orta',make(){const n=pick([400,500,800,1000,1200]),k=ri(Math.round(n*.08),Math.round(n*.4));const p=k/n,m=1.96*Math.sqrt(p*(1-p)/n)*100;return{q:`${n} müşteriden ${k} tanesi şikâyet etti. Wald yöntemiyle %95 hata payı kaç yüzde puandır?`,unit:'puan',answer:m,dec:2,tol:.03,hint:'Hata payı = 1,96 · √[p(1 − p)/n]',steps:[`p̂ = ${k}/${n} = ${P(p,4)}`,`√[${P(p,4)} × ${P(1-p,4)} / ${n}] = ${P(Math.sqrt(p*(1-p)/n),5)}`,`× 1,96 × 100 = ${P(m)} puan`,'Küçük n veya uç oranlarda Wilson aralığını tercih et.']}}},
  {id:'nbuyukluk',lesson:'s20',title:'Oran için örneklem büyüklüğü',group:'Orta',make(){const e=pick([2,3,4,5]),p=pick([.5,.3,.2]);const n=Math.ceil(1.96**2*p*(1-p)/(e/100)**2);return{q:`Beklenen oran yaklaşık ${P(p)}. %95 güvenle ±${e} puan hata payı için en az kaç gözlem gerekir?`,unit:'gözlem',answer:n,dec:0,tol:1.01,hint:'n = z² p(1 − p) / E², yukarı yuvarla',steps:[`z² = 1,96² = 3,8416`,`p(1 − p) = ${P(p*(1-p),4)}`,`E² = ${P((e/100)**2,6)}`,`n = ${P(1.96**2*p*(1-p)/(e/100)**2,1)} → ${n}`]}}},
  {id:'ztest',lesson:'s21',title:'z testi ve p değeri',group:'Orta',make(){const mu=ri(40,60),sg=ri(6,15),n=pick([36,49,64,100]),xb=mu+pick([-1,1])*rf(.8,3.2,1);const z=(xb-mu)/(sg/Math.sqrt(n)),p=2*(1-E.normalCDF(Math.abs(z)));return{q:`Hedef ortalama ${mu}, σ = ${sg} biliniyor. n = ${n} gözlemde x̄ = ${P(xb,1)}. İki yönlü p değeri kaçtır? (4 ondalık)`,unit:'',answer:p,dec:4,tol:.0015,hint:'z = (x̄ − μ₀) / (σ/√n); p = 2 · [1 − Φ(|z|)]',steps:[`SE = ${sg}/√${n} = ${P(sg/Math.sqrt(n),4)}`,`z = ${P(xb-mu,2)} / ${P(sg/Math.sqrt(n),4)} = ${P(z,3)}`,`p = 2 × [1 − Φ(${P(Math.abs(z),3)})] = ${P(p,4)}`]}}},
  {id:'fwer',lesson:'s22',title:'Çoklu test: aile hata oranı',group:'Orta',make(){const m=pick([3,5,8,10,15,20]),a=pick([.05,.1]);const f=(1-(1-a)**m)*100;return{q:`Birbirinden bağımsız ${m} metrik, her biri α = ${P(a)} ile test ediliyor ve hiçbirinde gerçek etki yok. En az bir yanlış alarm olasılığı yüzde kaçtır?`,unit:'%',answer:f,dec:1,tol:.15,hint:'FWER = 1 − (1 − α)ᵐ',steps:[`(1 − ${P(a)})^${m} = ${P((1-a)**m,4)}`,`1 − ${P((1-a)**m,4)} = %${P(f,1)}`,`Bonferroni eşiği: α/m = ${P(a/m,4)}`]}}},
  {id:'cohen',lesson:'s23',title:'Cohen d',group:'Orta',make(){const m1=rf(40,60,1),m2=m1+rf(1,8,1),s1=rf(6,12,1),s2=rf(6,12,1);const sp=Math.sqrt((s1**2+s2**2)/2),d=(m2-m1)/sp;return{q:`Eşit büyüklükte iki grup: A ortalama ${P(m1,1)}, s = ${P(s1,1)}; B ortalama ${P(m2,1)}, s = ${P(s2,1)}. Cohen d kaçtır?`,unit:'',answer:d,dec:3,tol:.005,hint:'d = (x̄_B − x̄_A) / s_birleşik; eşit n için s_birleşik = √[(s₁² + s₂²)/2]',steps:[`s_birleşik = √[(${P(s1**2,2)} + ${P(s2**2,2)}) / 2] = ${P(sp,3)}`,`d = ${P(m2-m1,1)} / ${P(sp,3)} = ${P(d,3)}`,'d, farkı ortak yayılım biriminde anlatır; iş eşiğiyle birlikte yorumla.']}}},
  {id:'welch',lesson:'s26',title:'Welch t istatistiği',group:'Orta',make(){const n1=ri(20,60),n2=ri(20,60),m1=rf(30,50,1),m2=m1+rf(-6,6,1),s1=rf(4,12,1),s2=rf(4,12,1);const se=Math.sqrt(s1**2/n1+s2**2/n2),t=(m2-m1)/se;return{q:`A: n=${n1}, x̄=${P(m1,1)}, s=${P(s1,1)}. B: n=${n2}, x̄=${P(m2,1)}, s=${P(s2,1)}. Welch t istatistiği (B − A) kaçtır?`,unit:'',answer:t,dec:3,tol:.005,hint:'t = (x̄_B − x̄_A) / √(s_A²/n_A + s_B²/n_B)',steps:[`s_A²/n_A = ${P(s1**2/n1,4)}, s_B²/n_B = ${P(s2**2/n2,4)}`,`SE = √${P(s1**2/n1+s2**2/n2,4)} = ${P(se,4)}`,`t = ${P(m2-m1,1)} / ${P(se,4)} = ${P(t,3)}`]}}},
  {id:'kikare',lesson:'s28',title:'2×2 ki-kare istatistiği',group:'Orta',make(){const a=ri(20,80),b=ri(20,80),c=ri(20,80),d=ri(20,80),n=a+b+c+d;const chi=n*(a*d-b*c)**2/((a+b)*(c+d)*(a+c)*(b+d));return{q:`Çapraz tablo: [${a}, ${b}; ${c}, ${d}]. Süreklilik düzeltmesi olmadan Pearson χ² kaçtır?`,unit:'',answer:chi,dec:3,tol:.01,hint:'2×2 için χ² = n(ad − bc)² / [(a+b)(c+d)(a+c)(b+d)]',steps:[`n = ${n}, ad − bc = ${a*d-b*c}`,`Pay = ${P(n*(a*d-b*c)**2,0)}`,`Payda = ${P((a+b)*(c+d)*(a+c)*(b+d),0)}`,`χ² = ${P(chi,3)} (sd = 1; 3,84 üstü %5'te anlamlı)`]}}},
  {id:'egim',lesson:'s30',title:'Korelasyondan regresyon eğimi',group:'Orta',make(){const r=rf(-.9,.9),sx=rf(2,10,1),sy=rf(5,40,1);return{q:`r = ${P(r)}, s_x = ${P(sx,1)}, s_y = ${P(sy,1)}. y'nin x'e göre en küçük kareler eğimi kaçtır?`,unit:'',answer:r*sy/sx,dec:3,tol:.005,hint:'b = r · s_y / s_x',steps:[`${P(r)} × ${P(sy,1)} / ${P(sx,1)} = ${P(r*sy/sx,3)}`,'Eğim birimlidir: x bir birim artınca y\'nin ortalama değişimi.']}}},
  {id:'odds',lesson:'s32',title:'Lojistik katsayıdan odds oranı',group:'Orta',make(){const b=rf(-1.2,1.2);return{q:`Lojistik regresyonda "premium üye" katsayısı β = ${P(b)}. Odds oranı kaçtır?`,unit:'',answer:Math.exp(b),dec:3,tol:.005,hint:'OR = e^β',steps:[`e^${P(b)} = ${P(Math.exp(b),3)}`,`Odds ${Math.exp(b)>1?'%'+P((Math.exp(b)-1)*100,1)+' artar':'%'+P((1-Math.exp(b))*100,1)+' azalır'}; olasılık değişimi taban olasılığa bağlıdır.`]}}},
  {id:'ab',lesson:'s33',title:'A/B testi z istatistiği',group:'İleri',make(){const nA=pick([900,1000,1200,1500]),nB=pick([900,1000,1200,1500]),kA=ri(Math.round(nA*.08),Math.round(nA*.14)),kB=ri(Math.round(nB*.09),Math.round(nB*.17));const pA=kA/nA,pB=kB/nB,pp=(kA+kB)/(nA+nB),z=(pB-pA)/Math.sqrt(pp*(1-pp)*(1/nA+1/nB));return{q:`A: ${kA}/${nA} dönüşüm. B: ${kB}/${nB} dönüşüm. Birleşik oranla iki oran z istatistiği (B − A) kaçtır?`,unit:'',answer:z,dec:3,tol:.01,hint:'z = (p̂_B − p̂_A) / √[p̂(1 − p̂)(1/n_A + 1/n_B)]',steps:[`p̂_A = ${P(pA,4)}, p̂_B = ${P(pB,4)}, birleşik p̂ = ${P(pp,4)}`,`SE = ${P(Math.sqrt(pp*(1-pp)*(1/nA+1/nB)),5)}`,`z = ${P(pB-pA,4)} / SE = ${P(z,3)}`,'|z| > 1,96 iki yönlü %5\'te anlamlıdır; kararı aralıkla ver.']}}},
  {id:'us',lesson:'s38',title:'Basit üstel düzeltme',group:'İleri',make(){const a=pick([.2,.3,.4,.5]),f=ri(100,200),y=f+ri(-40,40);return{q:`α = ${P(a)}. Bu haftanın tahmini ${f}, gerçekleşen ${y}. Gelecek haftanın tahmini kaçtır?`,unit:'',answer:a*y+(1-a)*f,dec:2,hint:'F(t+1) = α·y(t) + (1 − α)·F(t)',steps:[`${P(a)} × ${y} = ${P(a*y)}`,`${P(1-a)} × ${f} = ${P((1-a)*f)}`,`Tahmin = ${P(a*y+(1-a)*f)}`,'α büyüdükçe son gözleme daha çok ağırlık verilir.']}}},
  {id:'beta',lesson:'s41',title:'Beta-Binom sonsal ortalama',group:'İleri',make(){const a=pick([1,2,5]),b=pick([1,8,20]),n=ri(20,120),k=ri(1,Math.round(n*.3));return{q:`Önsel Beta(${a}, ${b}). ${n} denemede ${k} başarı gözlendi. Sonsal ortalama kaçtır? (4 ondalık)`,unit:'',answer:(a+k)/(a+b+n),dec:4,tol:.0006,hint:'Sonsal: Beta(a + k, b + n − k); ortalama = (a + k)/(a + b + n)',steps:[`Sonsal = Beta(${a+k}, ${b+n-k})`,`Ortalama = ${a+k} / ${a+b+n} = ${P((a+k)/(a+b+n),4)}`,`Gözlenen oran ${P(k/n,4)}; önsel tahmini ${P(a/(a+b),4)} yönüne çeker.`]}}},
  {id:'ikl',lesson:'s49',title:'I grafiği kontrol limiti',group:'İleri',make(){const m=rf(20,60,1),mr=rf(1,6,2);return{q:`Bireysel ölçümlerin ortalaması ${P(m,1)}, ortalama hareketli aralık MR̄ = ${P(mr)}. I grafiğinin üst kontrol limiti kaçtır?`,unit:'',answer:m+3*mr/1.128,dec:2,tol:.02,hint:'σ̂ = MR̄ / 1,128; ÜKL = x̄ + 3σ̂',steps:[`σ̂ = ${P(mr)} / 1,128 = ${P(mr/1.128,4)}`,`ÜKL = ${P(m,1)} + 3 × ${P(mr/1.128,4)} = ${P(m+3*mr/1.128)}`,'Limit sürecin kendi değişkenliğinden gelir; spesifikasyon sınırı değildir.']}}},
  {id:'cpk',lesson:'s50',title:'Süreç yeterliliği Cpk',group:'İleri',make(){const lsl=ri(90,95),usl=lsl+ri(8,14),mu=rf(lsl+2,usl-2,1),s=rf(.8,2.5);const cpk=Math.min(usl-mu,mu-lsl)/(3*s);return{q:`Alt sınır ${lsl}, üst sınır ${usl}. Süreç ortalaması ${P(mu,1)}, σ = ${P(s)}. Cpk kaçtır?`,unit:'',answer:cpk,dec:3,tol:.005,hint:'Cpk = min(ÜSL − μ, μ − ASL) / 3σ',steps:[`ÜSL − μ = ${P(usl-mu,2)}, μ − ASL = ${P(mu-lsl,2)}`,`min = ${P(Math.min(usl-mu,mu-lsl),2)}`,`Cpk = ${P(Math.min(usl-mu,mu-lsl),2)} / ${P(3*s,2)} = ${P(cpk,3)}`,'1,33 altı çoğu sektörde yetersiz sayılır; önce kararlılığı kontrol et.']}}},
  {id:'precision',lesson:'s54',title:'Precision ve recall',group:'İleri',make(){const tp=ri(30,150),fp=ri(10,120),fn=ri(10,100);return{q:`Gecikme modeli: TP = ${tp}, FP = ${fp}, FN = ${fn}. Precision yüzde kaçtır?`,unit:'%',answer:tp/(tp+fp)*100,dec:2,hint:'Precision = TP / (TP + FP)',steps:[`${tp} / (${tp} + ${fp}) = %${P(tp/(tp+fp)*100)}`,`Recall = ${tp} / (${tp} + ${fn}) = %${P(tp/(tp+fn)*100)}`,'Hangisinin önemli olduğu yanlış alarm ve kaçırma maliyetine bağlıdır.']}}},
  {id:'komb',lesson:'s57',title:'Kombinasyon',group:'Orta',make(){const n=ri(6,15),k=ri(2,Math.min(5,n-1));const c=Math.round(Math.exp(lc(n,k)));return{q:`${n} depo bölgesinden ${k} tanesi denetim için seçilecek (sıra önemsiz). Kaç farklı seçim yapılabilir?`,unit:'',answer:c,dec:0,tol:.5,hint:'C(n, k) = n! / [k! (n − k)!]',steps:[`C(${n}, ${k}) = ${n}! / (${k}! × ${n-k}!)`,`= ${P(c,0)}`]}}},
  {id:'little',lesson:'s82',title:'Little yasası',group:'İleri',make(){const l=ri(30,180),w=ri(4,40);return{q:`Sorter girişine saatte ortalama ${l} koli geliyor ve bir koli sistemde ortalama ${w} dakika kalıyor. Sistemde ortalama kaç koli vardır?`,unit:'koli',answer:l*w/60,dec:2,hint:'L = λ · W (birimleri eşitle)',steps:[`λ = ${l}/saat = ${P(l/60,3)}/dk`,`L = ${P(l/60,3)} × ${w} = ${P(l*w/60)}`,'Varsayım: kararlı süreç (uzun dönemde geliş = çıkış).']}}},
  {id:'f1',lesson:'s106',title:'F1 skoru',group:'İleri',make(){const tp=ri(30,150),fp=ri(10,120),fn=ri(10,100);const p=tp/(tp+fp),r=tp/(tp+fn),f=2*p*r/(p+r);return{q:`TP = ${tp}, FP = ${fp}, FN = ${fn}. F1 skoru kaçtır? (3 ondalık)`,unit:'',answer:f,dec:3,tol:.002,hint:'F1 = 2·P·R / (P + R) = 2TP / (2TP + FP + FN)',steps:[`Precision = ${P(p,4)}, recall = ${P(r,4)}`,`F1 = 2 × ${P(p,4)} × ${P(r,4)} / (${P(p+r,4)}) = ${P(f,3)}`,'F1 iki hatayı eşit tartar; maliyetler eşit değilse eşik maliyetle seçilir.']}}}
];
let current = null;
function practiceStats() {
  const v = Object.values(store.practice), a = v.reduce((s, x) => s + x.a, 0), c = v.reduce((s, x) => s + x.c, 0);
  return {a, c, kinds: Object.keys(store.practice).length};
}
function weakest() {
  return GEN.map(gn => ({gn, s: store.practice[gn.id]})).filter(x => x.s && x.s.a >= 1).sort((x, y) => (x.s.c / x.s.a) - (y.s.c / y.s.a) || y.s.a - x.s.a).slice(0, 5).filter(x => x.s.c / x.s.a < .8);
}
function practicePage(id) {
  const gn = GEN.find(x => x.id === id);
  if (gn) return practiceRun(gn);
  const st = practiceStats(), wk = weakest();
  const groups = ['Temel', 'Orta', 'İleri'];
  return head('ALIŞTIRMA ATÖLYESİ', 'Her seferinde yeni sayılarla çöz.', `${GEN.length} soru türü her açılışta yeni değerler üretir. Önce kendin hesapla; yanlışta formül ipucu, sonra adım adım çözüm açılır. Doğru cevaplar bu cihazda sayılır ve zayıf konuların öne çıkar.`) +
  `<div class="stats"><div class="stat"><div><strong>${GEN.length}</strong><small>Soru türü</small></div></div><div class="stat"><div><strong>${st.a}</strong><small>Denediğin soru</small></div></div><div class="stat"><div><strong>${st.a ? '%' + Math.round(st.c / st.a * 100) : '—'}</strong><small>Doğruluk</small></div></div><div class="stat"><div><strong>${st.kinds}/${GEN.length}</strong><small>Denenen tür</small></div></div></div>` +
  `<div class="actions v9-actions"><button class="btn primary" data-v9="practice-mix">Karışık 10 soru başlat →</button>${wk.length ? `<button class="btn" data-v9="practice-weak">Zayıf konularımı çalış</button>` : ''}</div>` +
  (wk.length ? `<div class="article v9-weak"><h2>Tekrar etmen önerilen konular</h2><ul>${wk.map(x => `<li><a href="#practice/${x.gn.id}">${esc(x.gn.title)}</a> · ${x.s.c}/${x.s.a} doğru · ${lessonLink(x.gn.lesson)}</li>`).join('')}</ul></div>` : '') +
  groups.map(gr => `<section><div class="section-head"><div><h2>${gr}</h2></div></div><div class="cards v9-gen-grid">${GEN.filter(x => x.group === gr).map(x => { const s = store.practice[x.id]; return `<a class="card v9-gen" href="#practice/${x.id}"><span class="eyebrow">Ders ${esc(x.lesson.slice(1))}</span><h3>${esc(x.title)}</h3><span class="v9-meta">${s ? `${s.c}/${s.a} doğru` : 'Henüz denenmedi'}</span></a>`; }).join('')}</div></section>`).join('');
}
let mixQueue = [];
function practiceRun(gn) {
  current = {gn, item: gn.make(), tries: 0, done: false};
  const s = store.practice[gn.id], l = lessonById(gn.lesson);
  const pos = mixQueue.length ? `<span class="pill">Karışık set · kalan ${mixQueue.length}</span>` : '';
  return `<nav class="v9-back"><a href="#practice">← Alıştırma atölyesi</a>${pos}</nav>` +
  `<div class="article v9-practice"><div class="eyebrow">${esc(gn.group).toUpperCase()} · DERS ${esc(gn.lesson.slice(1))} · ${esc(l ? l.title : '')}</div><h1>${esc(gn.title)}</h1>` +
  `<form id="v9-practice-form" class="v9-qform"><p class="v9-q">${esc(current.item.q)}</p><div class="v9-answer"><label for="v9-ans">Cevabın${current.item.unit ? ' (' + esc(current.item.unit) + ')' : ''}</label><input id="v9-ans" inputmode="decimal" autocomplete="off" placeholder="Ör. 12,5"><button class="btn primary" type="submit">Kontrol et</button></div><p class="v9-muted">Ondalık için virgül veya nokta kullanabilirsin. ${current.item.dec ? current.item.dec + ' ondalığa kadar yuvarla.' : 'Tam sayı yaz.'}</p><div id="v9-pfeed" role="status" aria-live="polite"></div></form>` +
  `<div class="actions"><button class="btn" data-v9="hint">İpucu: formül</button><button class="btn" data-v9="solve">Çözümü göster</button><button class="btn" data-v9="next-q">${mixQueue.length ? 'Sıradaki soru →' : 'Yeni sayılarla tekrar →'}</button></div>` +
  `<p class="v9-meta">${s ? `Bu türde ${s.c}/${s.a} doğru.` : 'Bu türdeki ilk denemen.'} ${lessonLink(gn.lesson)}</p></div>`;
}
function parseNum(t) { t = String(t).trim().replace(/\s/g, '').replace('%', ''); if (/^-?\d{1,3}(\.\d{3})+(,\d+)?$/.test(t)) t = t.replace(/\./g, ''); t = t.replace(',', '.').replace('−', '-'); return t === '' ? NaN : Number(t); }
function checkAnswer() {
  if (!current || current.done) return;
  const v = parseNum($('#v9-ans').value), it = current.item, fb = $('#v9-pfeed');
  if (!Number.isFinite(v)) { fb.innerHTML = '<div class="feedback bad">Sayı olarak okunamadı. Ör. 12,5 yaz.</div>'; return; }
  const tol = it.tol ?? Math.max(Math.abs(it.answer) * .005, it.dec >= 3 ? .0015 : it.dec === 0 ? .5 : .011);
  const ok = Math.abs(v - it.answer) <= tol;
  const rec = store.practice[current.gn.id] || {a: 0, c: 0};
  if (current.tries === 0) { rec.a++; if (ok) rec.c++; rec.t = Date.now(); store.practice[current.gn.id] = rec; save(); }
  current.tries++;
  if (ok) { current.done = true; fb.innerHTML = `<div class="feedback good"><b>Doğru.</b> Cevap: ${nf(it.answer, it.dec)}${it.unit ? ' ' + esc(it.unit) : ''}<ol class="v9-sol">${it.steps.map(s => `<li>${esc(s)}</li>`).join('')}</ol></div>`; }
  else if (current.tries === 1) fb.innerHTML = `<div class="feedback bad"><b>Henüz değil.</b> Yazdığın: ${nf(v, 6)}. İpucu: <code>${esc(it.hint)}</code><br>Bir kez daha dene ya da çözümü aç.</div>`;
  else { current.done = true; fb.innerHTML = `<div class="feedback bad"><b>Doğru cevap: ${nf(it.answer, it.dec)}${it.unit ? ' ' + esc(it.unit) : ''}</b><ol class="v9-sol">${it.steps.map(s => `<li>${esc(s)}</li>`).join('')}</ol><p>Bu tür zayıf konular listene eklendi. ${lessonLink(current.gn.lesson)}</p></div>`; }
}

/* ---------- 3) Sık hatalar ---------- */
let mTag = 'Tümü', mSearch = '';
function mistakesList() {
  const q = mSearch.toLocaleLowerCase('tr');
  const rows = K.MISTAKES.filter(m => (mTag === 'Tümü' || m.tag === mTag) && (!q || (m.title + m.wrong + m.right + m.example).toLocaleLowerCase('tr').includes(q)));
  return rows.length ? rows.map(m => `<article class="v9-mistake" id="${m.id}"><span class="eyebrow">${esc(m.tag)}</span><h3>${esc(m.title)}</h3><div class="v9-wr"><div class="v9-wrong"><b>Yanlış düşünce</b><p>${esc(m.wrong)}</p></div><div class="v9-right"><b>Doğrusu</b><p>${esc(m.right)}</p></div></div><p class="v9-ex"><b>Örnek:</b> ${esc(m.example)}</p><div class="v9-chips">${m.lessons.map(lessonLink).join('')}</div></article>`).join('') : '<p class="v9-muted">Bu filtreyle eşleşen kayıt yok.</p>';
}
function mistakesPage() {
  const tags = ['Tümü', ...new Set(K.MISTAKES.map(m => m.tag))];
  return head('SIK HATALAR', 'Analizi bozan düşünce kalıpları.', `${K.MISTAKES.length} yaygın hata: neden yanlış olduğu, doğru yaklaşım, Kesit verilerinden bir örnek ve ilgili dersler. Bir rapor yazmadan önce kontrol listesi gibi kullan.`) +
  `<div class="filters v9-filters"><input id="v9-msearch" type="search" placeholder="Hatalarda ara (ör. p değeri, korelasyon)" value="${esc(mSearch)}" aria-label="Sık hatalarda ara"><div class="v9-tags" role="group" aria-label="Kategori">${tags.map(t => `<button type="button" class="btn tiny ${t === mTag ? 'primary' : ''}" data-v9-tag="${esc(t)}">${esc(t)}</button>`).join('')}</div></div><div id="v9-mlist">${mistakesList()}</div>`;
}

/* ---------- 4) Mülakat ---------- */
const ROLE_TITLES = {ortak: 'Ortak çekirdek', analist: 'Veri analizi ve BI', bilim: 'Veri bilimi', ml: 'Makine öğrenmesi', operasyon: 'Süreç ve kalite'};
function interviewPage(role) {
  if (!K.INTERVIEW[role]) role = 'ortak';
  const qs = K.INTERVIEW[role], total = Object.values(K.INTERVIEW).flat().length, ready = Object.values(store.interview).filter(Boolean).length;
  return head('MÜLAKAT HAZIRLIĞI', 'İstatistik sorularına yapılandırılmış cevap.', `${total} soru, yalnızca istatistik ve rol bağlamında; davranışsal soru yok. Önce kendi cevabını yaz, sonra güçlü cevabın unsurlarıyla karşılaştır. Takip sorusu, mülakatçının derine inme biçimini gösterir.`) +
  `<div class="v9-roletabs" role="tablist" aria-label="Rol">${Object.keys(K.INTERVIEW).map(r => `<a role="tab" aria-selected="${r === role}" class="btn ${r === role ? 'primary' : ''}" href="#interview/${r}">${esc(ROLE_TITLES[r])} <span>${K.INTERVIEW[r].length}</span></a>`).join('')}</div>` +
  `<p class="v9-meta">Hazırım olarak işaretlediğin: ${ready}/${total}</p>` +
  qs.map((q, i) => { const id = role + '-' + i; return `<details class="v9-iq"><summary><span class="v9-lvl ${q.level}">${esc(q.level)}</span> ${esc(q.q)} ${store.interview[id] ? '<b class="v9-ok">✓</b>' : ''}</summary><div class="v9-iq-body"><label class="v9-label" for="iq-${id}">Kendi cevabın (kaydedilmez, düşünme alanı)</label><textarea id="iq-${id}" rows="3" placeholder="2–4 cümlede cevapla…"></textarea><details class="v9-reveal"><summary>Güçlü cevabın unsurlarını göster</summary><ul>${q.strong.map(s => `<li>${esc(s)}</li>`).join('')}</ul><p class="v9-weakans"><b>Zayıf cevap örneği:</b> ${esc(q.weak)}</p><p><b>Takip sorusu:</b> ${esc(q.follow)}</p><div class="v9-chips">${q.lessons.map(lessonLink).join('')}</div></details><label class="v9-check"><input type="checkbox" data-iq="${id}" ${store.interview[id] ? 'checked' : ''}> Bu soruya hazırım</label></div></details>`; }).join('');
}

/* ---------- 5) Seviye testi ---------- */
function placementQs() { return ['temel', 'orta', 'ileri'].flatMap(lv => K.PLACEMENT[lv].map(id => ({lv, l: lessonById(id)}))).filter(x => x.l && x.l.concept); }
function placementPage() {
  const qs = placementQs(), last = store.placement;
  return head('SEVİYE TESTİ', 'Nereden başlamalısın?', `${qs.length} kavram sorusu: 5 temel, 5 orta, 5 ileri. Not verilmez; sonuçta başlangıç noktası ve tekrar etmen gereken dersler önerilir. Süre sınırı yok, emin değilsen tahmin etme, boş bırak.`) +
  (last ? `<div class="article v9-last"><b>Son sonucun (${new Date(last.t).toLocaleDateString('tr-TR')}):</b> Temel ${last.s.temel}/5 · Orta ${last.s.orta}/5 · İleri ${last.s.ileri}/5 → <a href="#lesson/${last.start}">${esc(lessonById(last.start)?.title || '')}</a></div>` : '') +
  `<form id="v9-place" class="v9-place">${qs.map((x, i) => `<fieldset class="v9-pq"><legend><span class="v9-lvl ${x.lv}">${x.lv}</span> ${i + 1}. ${esc(x.l.concept.q)}</legend>${order(x.l.concept.options.length, 'pl' + x.l.id).map(k => `<label class="option"><input type="radio" name="pq${i}" value="${k}"> <span>${esc(x.l.concept.options[k])}</span></label>`).join('')}<label class="option v9-skip"><input type="radio" name="pq${i}" value="-1"> <span>Bilmiyorum</span></label></fieldset>`).join('')}<button class="btn primary" type="submit">Sonucu gör</button></form><div id="v9-place-result" role="status" aria-live="polite"></div>`;
}
function scorePlacement(form) {
  const qs = placementQs(), s = {temel: 0, orta: 0, ileri: 0}, wrong = [];
  qs.forEach((x, i) => { const v = form.querySelector(`input[name=pq${i}]:checked`); const ok = v && Number(v.value) === x.l.concept.correct; if (ok) s[x.lv]++; else wrong.push(x); });
  let start, msg;
  if (s.temel < 4) { start = 's01'; msg = 'Temel modüllerden başla. İlk üç modül veriyi tanımayı, özetlemeyi ve olasılığı kurar; sonraki her konu bunlara dayanır.'; }
  else if (s.orta < 4) { start = 's13'; msg = 'Temelin sağlam. Dağılımlar modülünden (Ders 13) başla; örnekleme, testler ve regresyon bunu izler.'; }
  else if (s.ileri < 4) { start = 's33'; msg = 'Orta düzey çıkarımı biliyorsun. Deney ve nedensellikten (Ders 33) başlayıp rolünün ileri modüllerine geç.'; }
  else { start = 's53'; msg = 'İleri sorularda da güçlüsün. Model değerlendirme modülü ve Kesit verileriyle vakalar seni en çok zorlayacak bölümler.'; }
  store.placement = {s, start, t: Date.now()}; save();
  return `<div class="article v9-presult"><h2>Önerilen başlangıç: <a href="#lesson/${start}">${esc(start.slice(1))} · ${esc(lessonById(start).title)}</a></h2><p>${msg}</p><div class="stats"><div class="stat"><div><strong>${s.temel}/5</strong><small>Temel</small></div></div><div class="stat"><div><strong>${s.orta}/5</strong><small>Orta</small></div></div><div class="stat"><div><strong>${s.ileri}/5</strong><small>İleri</small></div></div></div>${wrong.length ? `<h3>Tekrar etmen önerilen dersler</h3><div class="v9-chips">${wrong.map(x => lessonLink(x.l.id)).join('')}</div><details><summary>Kaçırdığın soruların açıklamaları</summary>${wrong.map(x => `<p><b>${esc(x.l.concept.q)}</b><br>Doğru yanıt: ${esc(x.l.concept.options[x.l.concept.correct])}. ${esc(x.l.concept.explanation || '')}</p>`).join('')}</details>` : '<p>Bütün soruları doğru yanıtladın.</p>'}<div class="actions"><a class="btn primary" href="#lesson/${start}">Bu dersten başla →</a><a class="btn" href="#practice">Alıştırma atölyesi</a></div></div>`;
}

/* ---------- ders sayfası köprüsü, ana sayfa ve ilerleme ekleri ---------- */
function lessonBridge(id) {
  const t = K.TOOLS[id], cs = X.cases.filter(c => c.lessons.includes(id)), gs = GEN.filter(x => x.lesson === id), ms = K.MISTAKES.filter(m => m.lessons.includes(id));
  if (!t && !cs.length && !gs.length && !ms.length) return '';
  return `<section class="v9-bridge" aria-label="Kesit ekosistemiyle bağlantı"><div class="eyebrow">KESİT EKOSİSTEMİ · BU KONUYU UYGULA</div>` +
  (t ? `<h3>Araçlarda bu kavram</h3>${codeTabs('l-' + id, [{label: 'SQL', code: t.sql}, {label: 'Power BI (DAX)', code: t.dax}, {label: 'Python', code: t.py}])}` : '') +
  (cs.length ? `<h3>Gerçek Kesit verisinde</h3><ul class="v9-links">${cs.map(c => `<li><a href="#data/${c.id}">${esc(c.dataset)} · ${esc(c.title)}</a></li>`).join('')}</ul>` : '') +
  (gs.length ? `<h3>Yeni sayılarla alıştırma</h3><div class="v9-chips">${gs.map(x => `<a class="v9-chip" href="#practice/${x.id}">${esc(x.title)} →</a>`).join('')}</div>` : '') +
  (ms.length ? `<h3>Bu konudaki sık hatalar</h3><ul class="v9-links">${ms.map(m => `<li><a href="#mistakes" data-v9-goto="${m.id}">${esc(m.title)}</a></li>`).join('')}</ul>` : '') + `</section>`;
}
function homeStrip() {
  const st = practiceStats();
  return `<section class="v9-home" aria-label="Uygula ve hazırlan"><div class="section-head"><div><h2>Uygula ve hazırlan</h2><p>Dersten sonra: gerçek Kesit verisi, sınırsız alıştırma ve mülakat.</p></div></div><div class="cards v9-home-grid">` +
  `<a class="card" href="#data"><span class="eyebrow">KESİT VERİLERİYLE</span><h3>${X.cases.length} vaka, 6 ortak veri seti</h3><p>Kesit SQL, Power BI ve Python'daki aynı şirket verilerinde A/B testi, regresyon, sayım modelleri ve aykırı değer kuralları.</p></a>` +
  `<a class="card" href="#practice"><span class="eyebrow">ALIŞTIRMA ATÖLYESİ</span><h3>${GEN.length} soru türü, her seferinde yeni sayı</h3><p>${st.a ? `${st.a} soru denedin, %${Math.round(st.c / st.a * 100)} doğru.` : 'Formül ipucu ve adım adım çözüm.'}</p></a>` +
  `<a class="card" href="#placement"><span class="eyebrow">SEVİYE TESTİ</span><h3>15 soruda başlangıç noktan</h3><p>${store.placement ? 'Son önerin: ' + esc(lessonById(store.placement.start)?.title || '') : 'Temel, orta ve ileri kavramlardan 5\'er soru.'}</p></a>` +
  `<a class="card" href="#interview"><span class="eyebrow">MÜLAKAT</span><h3>${Object.values(K.INTERVIEW).flat().length} istatistik sorusu</h3><p>Rol bazlı; güçlü cevap unsurları, zayıf cevap örneği ve takip sorusu.</p></a>` +
  `<a class="card" href="#mistakes"><span class="eyebrow">SIK HATALAR</span><h3>${K.MISTAKES.length} hata kalıbı</h3><p>p değeri, korelasyon, çoklu test, sızıntı… Raporlamadan önce kontrol et.</p></a></div></section>`;
}
function progressStrip() {
  const st = practiceStats(), done = X.cases.filter(c => store.cases[c.id]).length, ready = Object.values(store.interview).filter(Boolean).length;
  return `<section class="article v9-prog"><h2>Uygulama alanları</h2><div class="stats"><div class="stat"><div><strong>${done}/${X.cases.length}</strong><small>Kesit vakası</small></div></div><div class="stat"><div><strong>${st.c}/${st.a}</strong><small>Alıştırma doğru/deneme</small></div></div><div class="stat"><div><strong>${ready}</strong><small>Hazır mülakat sorusu</small></div></div><div class="stat"><div><strong>${store.placement ? store.placement.s.temel + store.placement.s.orta + store.placement.s.ileri + '/15' : '—'}</strong><small>Seviye testi</small></div></div></div><p class="v9-muted">Bu kayıtlar da ilerleme yedeğine dahildir.</p></section>`;
}

/* ---------- yönlendirme ve olaylar ---------- */
const pages = {
  data: rest => rest ? casePage(rest) : dataPage(),
  practice: rest => { if (!rest) mixQueue = []; return practicePage(rest); },
  mistakes: () => mistakesPage(),
  interview: rest => interviewPage(rest || 'ortak'),
  placement: () => placementPage()
};
const labels = {data: 'Kesit verileriyle', practice: 'Alıştırma atölyesi', mistakes: 'Sık hatalar', interview: 'Mülakat hazırlığı', placement: 'Seviye testi'};
function mount(page, lesson) {
  if (page === 'lesson' && lesson) { const col = document.querySelector('.lesson-layout > :last-child'); if (col && !col.querySelector('.v9-bridge')) col.insertAdjacentHTML('beforeend', lessonBridge(lesson.id)); }
  if (page === 'home') { const h = document.querySelector('#main .current-session') || document.querySelector('#main .guide-home'); if (h && !document.querySelector('.v9-home')) h.insertAdjacentHTML('afterend', homeStrip()); }
  if (page === 'progress') { const s = document.querySelector('#main .stats'); if (s && !document.querySelector('.v9-prog')) s.insertAdjacentHTML('afterend', progressStrip()); }
  if (page === 'practice') $('#v9-ans')?.focus({preventScroll: true});
  if (page === 'mistakes' && pendingGoto) { const el = document.getElementById(pendingGoto); pendingGoto = ''; if (el) { el.scrollIntoView({block: 'start'}); el.classList.add('v9-flash'); } }
}
let pendingGoto = '';
document.addEventListener('click', e => {
  const t = e.target;
  const tab = t.closest('[data-code-tab]');
  if (tab) { const box = tab.closest('[data-codetabs]'), i = tab.dataset.codeTab; box.querySelectorAll('[data-code-tab]').forEach(b => b.setAttribute('aria-selected', String(b === tab))); box.querySelectorAll('[data-code-panel]').forEach(p => p.hidden = p.dataset.codePanel !== i); return; }
  const cp = t.closest('[data-copy]');
  if (cp) { copyText(cp.parentElement.querySelector('code').textContent); return; }
  const tag = t.closest('[data-v9-tag]');
  if (tag) { mTag = tag.dataset.v9Tag; document.querySelectorAll('[data-v9-tag]').forEach(b => b.classList.toggle('primary', b === tag)); $('#v9-mlist').innerHTML = mistakesList(); return; }
  const go = t.closest('[data-v9-goto]');
  if (go) { pendingGoto = go.dataset.v9Goto; mTag = 'Tümü'; mSearch = ''; return; }
  const a = t.closest('[data-v9]');
  if (!a) return;
  const act = a.dataset.v9;
  if (act === 'finish-case') { const id = a.dataset.id; store.cases[id] = true; const n = document.querySelector(`[data-case-note="${id}"]`); if (n) store.cases[id + ':note'] = n.value.slice(0, 20000); save(); a.textContent = '✓ Bitirildi'; toast('Vaka bitirildi ve notun kaydedildi.'); }
  else if (act === 'hint' && current) { $('#v9-pfeed').innerHTML = `<div class="feedback"><b>Formül:</b> <code>${esc(current.item.hint)}</code></div>`; }
  else if (act === 'solve' && current) { if (!current.done && current.tries === 0) { const rec = store.practice[current.gn.id] || {a: 0, c: 0}; rec.a++; rec.t = Date.now(); store.practice[current.gn.id] = rec; save(); } current.done = true; current.tries = Math.max(1, current.tries); $('#v9-pfeed').innerHTML = `<div class="feedback"><b>Cevap: ${nf(current.item.answer, current.item.dec)}${current.item.unit ? ' ' + esc(current.item.unit) : ''}</b><ol class="v9-sol">${current.item.steps.map(s => `<li>${esc(s)}</li>`).join('')}</ol></div>`; }
  else if (act === 'next-q') { if (mixQueue.length) { const nx = mixQueue.shift(); if (location.hash === '#practice/' + nx) rerender(); else location.hash = 'practice/' + nx; } else rerender(); }
  else if (act === 'practice-mix') { const ids = [...GEN].sort(() => rnd() - .5).slice(0, 10).map(x => x.id); const first = ids.shift(); mixQueue = ids; location.hash = 'practice/' + first; }
  else if (act === 'practice-weak') { const ids = weakest().map(x => x.gn.id); if (!ids.length) return; const first = ids.shift(); mixQueue = ids; location.hash = 'practice/' + first; }
});
function rerender() { const m = location.hash.slice(1).split('/'); if (m[0] === 'practice' && m[1]) { $('#main').innerHTML = practicePage(m[1]); $('#v9-ans')?.focus(); } }
document.addEventListener('submit', e => {
  if (e.target.id === 'v9-practice-form') { e.preventDefault(); checkAnswer(); }
  else if (e.target.id === 'v9-place') { e.preventDefault(); const r = $('#v9-place-result'); r.innerHTML = scorePlacement(e.target); r.scrollIntoView({behavior: 'smooth', block: 'start'}); }
  else if (e.target.matches('[data-predict]')) {
    e.preventDefault(); const id = e.target.dataset.predict, c = X.cases.find(x => x.id === id), sel = e.target.querySelector('input:checked'), fb = e.target.querySelector('.v9-pfb');
    if (!sel) { fb.innerHTML = '<div class="feedback bad">Önce bir seçenek işaretle.</div>'; return; }
    const ok = Number(sel.value) === c.predict.correct; store.cases[id + ':p'] = true; save();
    fb.innerHTML = `<div class="feedback ${ok ? 'good' : 'bad'}"><b>${ok ? 'İyi tahmin.' : 'Bu kez değil.'}</b> Doğru yanıt: ${esc(c.predict.options[c.predict.correct])}<p>${esc(c.predict.why)}</p></div>`;
  }
});
document.addEventListener('input', e => {
  if (e.target.id === 'v9-msearch') { mSearch = e.target.value; $('#v9-mlist').innerHTML = mistakesList(); }
});
document.addEventListener('change', e => {
  if (e.target.matches('[data-iq]')) { store.interview[e.target.dataset.iq] = e.target.checked; save(); }
  if (e.target.matches('[data-case-note]')) { store.cases[e.target.dataset.caseNote + ':note'] = e.target.value.slice(0, 20000); save(); }
});

g.KesitV9 = {
  pages, labels, mount, GEN, cases: X.cases,
  exportState: () => JSON.parse(JSON.stringify(store)),
  importState(s) { if (!validStore(s)) return false; store.practice = {...s.practice, ...store.practice}; Object.entries(s.practice).forEach(([k, v]) => { const o = store.practice[k]; if (!o || v.a > o.a) store.practice[k] = v; }); store.cases = {...s.cases, ...store.cases}; store.interview = {...s.interview, ...store.interview}; store.placement = store.placement || s.placement || null; return save(); },
  _test: {parseNum, chart, lessonBridge}
};
})(window);
