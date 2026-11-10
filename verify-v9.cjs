'use strict';
// V9 regresyon kontrolleri: ekosistem vakaları, alıştırma üreticileri, içerik bağlantıları.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const ctx = {console, Math, Date, JSON, Number, String, Object, Array, Set, Map, Intl, localStorage: {getItem: () => null, setItem() {}}};
ctx.window = ctx; ctx.globalThis = ctx;
ctx.document = {addEventListener() {}, querySelector: () => null, querySelectorAll: () => []};
vm.createContext(ctx);
for (const f of ['content.js', 'math.js', 'analysis-engine.js', 'ecosystem-data-v9.js', 'v9-content.js', 'v9-app.js'])
  vm.runInContext(fs.readFileSync('docs/' + f, 'utf8'), ctx, {filename: f});
const C = ctx.COURSE, X = ctx.KESIT_ECOSYSTEM, K = ctx.KesitV9Content, V = ctx.KesitV9;
const ids = new Set(C.lessons.map(l => l.id));
const html = fs.readFileSync('docs/index.html', 'utf8');

// 1) Ekosistem vakaları
assert.equal(X.cases.length, 13, '13 vaka');
assert.equal(new Set(X.cases.map(c => c.id)).size, X.cases.length, 'Benzersiz vaka kimliği');
for (const c of X.cases) {
  for (const k of ['title', 'question', 'unit', 'method', 'why', 'sql', 'python', 'dax', 'read', 'limits']) assert.ok(c[k] && c[k].length > 10, `${c.id}.${k}`);
  assert.ok(c.predict.options[c.predict.correct], `${c.id} tahmin doğru seçeneği`);
  assert.ok(c.results.length >= 3 && c.results.every(r => r.length === 2 && !/NaN|undefined|null/.test(r[1])), `${c.id} sonuçlar`);
  assert.ok(c.lessons.every(id => ids.has(id)), `${c.id} ders bağlantıları`);
  assert.ok(c.python.includes(X.raw), `${c.id} Python kodu ortak veriyi okur`);
  assert.equal(c.chart.labels.length, c.chart.values.length, `${c.id} grafik`);
  assert.ok(Object.hasOwn(X.datasets, c.dataset), `${c.id} veri seti`);
  assert.doesNotMatch(c.results.map(r => r[1]).join(' '), /\d\.\d{1,2}(?!\d)(?![\d.]*e)/, `${c.id} Türkçe ondalık`);
}
// Bilinen sabit referanslar (ecosystem_cases_v9.py çıktısı)
const ab = X.cases.find(c => c.id === 'am-ab-donusum').results;
assert.match(ab[0][1], /106\/975/); assert.match(ab[1][1], /150\/1025/); assert.match(ab[2][1], /3,76 puan/);
assert.match(X.cases.find(c => c.id === 'hv-rotar-kuyruk').results[1][1], /%60,5/);

// 2) Alıştırma üreticileri: 300 tekrar, sonlu cevap, adımlarda NaN yok
assert.ok(V.GEN.length >= 30, 'En az 30 soru türü');
assert.equal(new Set(V.GEN.map(g => g.id)).size, V.GEN.length, 'Benzersiz üretici');
for (const g of V.GEN) {
  assert.ok(ids.has(g.lesson), `${g.id} ders`);
  for (let i = 0; i < 300; i++) {
    const it = g.make();
    assert.ok(Number.isFinite(it.answer), `${g.id} cevap sonlu`);
    assert.ok(it.q && it.hint && it.steps.length >= 1, `${g.id} metin`);
    assert.doesNotMatch(it.q + it.steps.join(' '), /NaN|undefined|Infinity/, `${g.id} metin bozuk`);
  }
}
// Bağımsız hesap kontrolleri
const E = ctx.AnalysisEngine;
assert.ok(Math.abs(E.normalCDF(1.96) - 0.975) < 1e-3, 'Normal CDF');
const p = V._test.parseNum;
assert.equal(p('12,5'), 12.5); assert.equal(p('1.234,5'), 1234.5); assert.equal(p('%7,2'), 7.2); assert.equal(p('−3,1'), -3.1); assert.ok(Number.isNaN(p('')));

// 3) İçerik bağlantıları
assert.ok(K.MISTAKES.length >= 30 && K.MISTAKES.every(m => m.lessons.every(id => ids.has(id))), 'Sık hata dersleri');
const iq = Object.values(K.INTERVIEW).flat();
assert.ok(iq.length >= 45 && iq.every(q => q.strong.length >= 2 && q.weak && q.follow && q.lessons.every(id => ids.has(id))), 'Mülakat soruları');
assert.ok(Object.keys(K.INTERVIEW).filter(k => k !== 'ortak').every(r => C.roles.some(x => x.id === r)), 'Mülakat rolleri');
const pl = Object.values(K.PLACEMENT).flat();
assert.equal(pl.length, 15); assert.ok(pl.every(id => ids.has(id) && C.lessons.find(l => l.id === id).concept), 'Seviye testi soruları');
assert.ok(Object.keys(K.TOOLS).every(id => ids.has(id)) && Object.values(K.TOOLS).every(t => t.sql && t.dax && t.py), 'Araç köprüsü');

// 4) Sayfa bağlantıları
for (const f of ['v9.css', 'ecosystem-data-v9.js', 'v9-content.js', 'v9-app.js', 'sw-register.js', 'manifest.webmanifest']) assert.match(html, new RegExp(f.replace('.', '\\.')), f + ' bağlı');
assert.ok(html.indexOf('v9-app.js') < html.indexOf('src="app.js"'), 'V9 modülü app.js öncesinde yüklenir');
for (const k of Object.keys(V.pages)) assert.match(html, new RegExp(`href="#${k}"`), `${k} menüde`);
const sw = fs.readFileSync('docs/sw.js', 'utf8');
for (const m of sw.match(/"([^"]+\.(?:js|css|woff2|svg|webmanifest))"/g)) assert.ok(fs.existsSync('docs/' + m.slice(1, -1)), 'SW dosyası var: ' + m);
console.log(`PASS: ${X.cases.length} Kesit vakası, ${V.GEN.length} üretici × 300, ${K.MISTAKES.length} sık hata, ${iq.length} mülakat sorusu, seviye testi ve SW önbellek listesi.`);
