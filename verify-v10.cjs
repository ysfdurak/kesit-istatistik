// Kesit İstatistik V10 denetimi: ders içi Kesit verisi alıştırmaları, defterler, Excel kitapları.
// Cevapların kendisi alistirma_v10.py'de kod çalıştırılarak üretilir; burada yapı, dosyalar ve arayüz mantığı denetlenir.
const fs = require('fs'), path = require('path'), vm = require('vm'), assert = require('assert');
const D = path.join(__dirname, 'docs');
const ctx = {window: {}, console};
ctx.window.window = ctx.window;
vm.createContext(ctx);
for (const f of ['content.js', 'ders-alistirma.js']) vm.runInContext(fs.readFileSync(path.join(D, f), 'utf8'), ctx);
const C = ctx.window.COURSE, A = ctx.window.KESIT_DERS_ALISTIRMA;
assert(A && A.dersler && A.hazirlik, 'ders-alistirma.js yüklenmedi');
let gorev = 0;
const ids = new Set();
for (const l of C.lessons) {
  const ts = A.dersler[l.id];
  assert(ts && ts.length >= 3, `${l.id}: en az 3 görev olmalı`);
  for (const t of ts) {
    gorev++;
    assert(!ids.has(t.id), 'yinelenen görev kimliği ' + t.id); ids.add(t.id);
    assert(/^s\d{2,3}-v\d$/.test(t.id), 'kimlik biçimi ' + t.id);
    assert(Number.isFinite(t.cevap), t.id + ' cevap sayı değil');
    assert(Number.isInteger(t.d) && t.d >= 0 && t.d <= 6, t.id + ' ondalık');
    assert(!/<\/?[a-z]/i.test(t.soru.replace(/<\/?b>/g, '')), t.id + ': soruda <b> dışında etiket var');
    assert(/\bcevap\s*=/.test(t.kod), t.id + ': kod cevap atamıyor');
    assert(Array.isArray(t.veri), t.id + ': veri listesi yok');
    for (const v of t.veri) assert(fs.existsSync(path.join(D, 'data', 'kesit', v + '.csv')), t.id + ': eksik CSV ' + v);
  }
  for (const e of ['.ipynb', '.py']) assert(fs.existsSync(path.join(D, 'defter', l.id + e)), 'defter eksik ' + l.id + e);
  assert(fs.existsSync(path.join(D, 'excel', `modul-${String(l.module + 1).padStart(2, '0')}.xlsx`)), 'Excel kitabı eksik: modül ' + (l.module + 1));
  const nb = JSON.parse(fs.readFileSync(path.join(D, 'defter', l.id + '.ipynb'), 'utf8'));
  assert.strictEqual(nb.cells.filter(c => c.cell_type === 'code').length, ts.length + 1, l.id + ': defter hücre sayısı');
}
assert.strictEqual(Object.keys(A.dersler).length, C.lessons.length, 'derste olmayan görev kümesi var');
for (const f of ['data/kesit-veri.zip', 'defter/kesit-defterler.zip', 'v10-alistirma.js', 'v10.css']) assert(fs.existsSync(path.join(D, f)), 'eksik ' + f);
const idx = fs.readFileSync(path.join(D, 'index.html'), 'utf8'), sw = fs.readFileSync(path.join(D, 'sw.js'), 'utf8');
assert(idx.indexOf('<script src="v9-app.js"></script><script src="ders-alistirma.js"></script><script src="v10-alistirma.js"></script>') > 0, 'index.html betik sırası (v9-app → ders-alistirma → v10-alistirma, app.js öncesi)');
assert(idx.indexOf('v10-alistirma.js') < idx.indexOf('src="app.js"'), 'v10 app.js öncesinde yüklenmeli');
for (const f of ['ders-alistirma.js', 'v10-alistirma.js', 'v10.css']) assert(sw.includes('"' + f + '"'), 'sw.js CORE: ' + f);

// arayüz mantığı: sayı ayrıştırma ve tolerans
const ui = {window: {KESIT_DERS_ALISTIRMA: A, COURSE: C, KesitV9: {mount() {}, exportState: () => ({}), importState: () => true}}, document: {addEventListener() {}}, localStorage: {getItem: () => null, setItem() {}}};
ui.window.window = ui.window; Object.assign(ui, {console});
vm.createContext(ui);
vm.runInContext('var window=this.window,document=this.document,localStorage=this.localStorage;' + fs.readFileSync(path.join(D, 'v10-alistirma.js'), 'utf8'), ui);
const K = ui.window.KesitV10;
const ornek = {'0,123': 0.123, '0.123': 0.123, '1.234,5': 1234.5, '1,234.5': 1234.5, '%12,5': 12.5, ' -3 ': -3, '1e-3': 0.001, '37,74 TL': 37.74, 'abc': NaN, '': NaN};
for (const [s, v] of Object.entries(ornek)) { const r = K.sayi(s); assert(Number.isNaN(v) ? Number.isNaN(r) : Math.abs(r - v) < 1e-12, `sayi(${JSON.stringify(s)}) = ${r}`); }
for (const k in A.dersler) for (const t of A.dersler[k]) {
  const yuv = Number(t.cevap.toFixed(t.d));
  assert(Math.abs(yuv - t.cevap) <= K.tolerans(t) + 1e-12, t.id + ': yuvarlanmış cevap kabul edilmiyor');
  assert(K.tolerans(t) < Math.max(Math.abs(t.cevap) * 0.05, 1.01 * Math.pow(10, -t.d) + (t.tol || 0)), t.id + ': tolerans çok geniş');
}
const html = K.panel('s05');
assert(html.includes('defter/s05.ipynb') && html.includes('excel/modul-02.xlsx') && html.includes('data-v10="denetle"'), 'panel bağlantıları');
console.log(`V10 alıştırmaları tamam: ${C.lessons.length} ders, ${gorev} görev, ${new Set(C.lessons.map(l => l.module)).size} Excel kitabı.`);
