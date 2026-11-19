// Ders okuma sayfalarını üretir: /kesit-istatistik/ders/<ders>/ (arama motorları için statik HTML).
// Kaynak: docs/content.js (window.COURSE). Elle düzenleme yapma; içerik değişince yeniden çalıştır:
//   node tools/ders-sayfalari.mjs
// Üretilenler: ders/<slug>/index.html (120 ders), ders/index.html (modül listesi), ders/statik.css (kopya değil, aşağıdaki
// küçük stil), sitemap.xml (ana sayfa + ders listesi + dersler).
import { readFileSync, writeFileSync, mkdirSync, rmSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const BASE = 'https://ysfdurak.github.io/kesit-istatistik/';
const APP = '../../docs/';
const OG = BASE + 'ekran/karsilama.png';
const today = new Date().toISOString().slice(0, 10);

const ctx = { window: {} };
vm.createContext(ctx);
vm.runInContext(readFileSync(join(ROOT, 'docs/content.js'), 'utf8'), ctx);
const C = ctx.window.COURSE;

const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const TR = { ç: 'c', ğ: 'g', ı: 'i', İ: 'i', ö: 'o', ş: 's', ü: 'u', â: 'a', î: 'i', û: 'u' };
const slugify = (t) =>
  t.toLocaleLowerCase('tr').replace(/[çğıİöşüâîû]/g, (c) => TR[c] ?? c).normalize('NFKD').replace(/[̀-ͯ]/g, '')
    .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 70).replace(/-+$/, '');
const LEVEL = { temel: 'Temel', orta: 'Orta', ileri: 'İleri' };
const summary = (text, max = 155) => {
  const t = String(text).replace(/\s+/g, ' ').trim();
  if (t.length <= max) return t;
  const cut = t.slice(0, max);
  const dot = cut.lastIndexOf('. ');
  return dot > 80 ? cut.slice(0, dot + 1) : cut.slice(0, cut.lastIndexOf(' ')) + '…';
};

// Sıra: uygulamadaki gibi ders numarası (s01 → s120)
const lessons = [...C.lessons].sort((a, b) => Number(a.id.slice(1)) - Number(b.id.slice(1)));
const used = new Set();
for (const l of lessons) {
  let s = slugify(l.title);
  while (used.has(s)) s += '-' + l.id;
  used.add(s);
  l._slug = s;
}

const head = ({ title, desc, url, type = 'article', jsonLd, css }) => `<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; base-uri 'none'; form-action 'none'"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(title)} | Kesit İstatistik</title><meta name="description" content="${esc(desc)}"><link rel="canonical" href="${url}">
<meta property="og:type" content="${type}"><meta property="og:locale" content="tr_TR"><meta property="og:site_name" content="Kesit İstatistik"><meta property="og:title" content="${esc(title)}"><meta property="og:description" content="${esc(desc)}"><meta property="og:url" content="${url}"><meta property="og:image" content="${OG}"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="${css}../docs/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/vendor/fonts.css"><link rel="stylesheet" href="${css}statik.css">${jsonLd ? `<script type="application/ld+json">${JSON.stringify(jsonLd)}</script>` : ''}</head>`;

const foot = `<footer class="st-f">Kesit ücretsiz bir eğitim ve portföy projesidir. Örneklerdeki veriler hayalidir. <a href="/">Kesit ana sayfası</a></footer></body></html>`;

function lessonPage(l, i) {
  const mod = C.modules[l.module];
  const url = `${BASE}ders/${l._slug}/`;
  const desc = summary(l.body);
  const prev = lessons[i - 1], next = lessons[i + 1];
  const sources = (l.sources || []).filter((s) => /^https?:/.test(s.url));
  const n = l.numeric, c = l.concept, a = l.applicationCheck;
  const jsonLd = {
    '@context': 'https://schema.org', '@type': 'LearningResource', name: l.title, description: desc, inLanguage: 'tr',
    isAccessibleForFree: true, learningResourceType: 'Ders', educationalLevel: LEVEL[l.level] || l.level,
    timeRequired: `PT${l.minutes || 20}M`, url,
    isPartOf: { '@type': 'Course', name: 'Kesit İstatistik', url: BASE, provider: { '@type': 'Person', name: 'Yusuf Durak' } },
  };
  const section = (h, body) => (body ? `<h2>${h}</h2>${body}` : '');
  const p = (t) => (t ? `<p>${esc(t)}</p>` : '');
  const mc = (q, title) =>
    q && q.q
      ? `<div class="tip"><b>${title}</b>${esc(q.q)}<ul>${(q.options || []).map((o) => `<li>${esc(o)}</li>`).join('')}</ul><details><summary>Cevabı göster</summary><p><b>Doğru cevap:</b> ${esc((q.options || [])[q.correct ?? 0])}</p>${p(q.explanation)}</details></div>`
      : '';
  return `${head({ title: l.title, desc, url, jsonLd, css: '../' })}
<body class="st"><a class="st-skip" href="#icerik">Ana içeriğe geç</a><header class="st-h"><a class="st-b" href="../../">Kesit İstatistik</a><nav aria-label="Konum"><a href="../">Tüm dersler</a></nav></header>
<main id="icerik" class="st-m"><span class="st-e">${esc(LEVEL[l.level] || l.level)} · ${esc(mod.title)} · ≈ ${l.minutes || 20} dk</span><h1>${esc(l.title)}</h1><p class="st-l">${esc(desc)}</p>
<div class="st-c"><a class="st-p" href="${APP}#lesson/${l.id}">Uygulamada aç, alıştırmaları çöz</a><span>Ücretsiz, hesap gerekmez, kurulum yok.</span></div>
<p class="st-not">Bu sayfa dersin okuma sürümüdür. Etkileşimli grafikler, her açılışta yeni sayı üreten alıştırmalar ve vaka çalışması uygulamadadır.</p>
<article class="panel theory">
${section('Konu', p(l.body))}
${section('Sezgi', p(l.intuition))}
${section('Ne zaman kullanılır?', p(l.when))}
${l.formula ? `<h2>Formül</h2><pre class="code">${esc(l.formula)}</pre>` : ''}
${section('Örnek', p(l.example) + (l.reasoning ? `<div class="tip"><b>Adım adım</b>${esc(l.reasoning)}</div>` : ''))}
${section('Varsayımlar ve kontroller', p(l.assumptions))}
${l.caution ? `<div class="tip"><b>Dikkat</b>${esc(l.caution)}</div>` : ''}
${l.learning?.term ? `<h2>Kavram: ${esc(l.learning.term)}</h2>${p(l.learning.explanation)}` : ''}
${n && n.q ? `<h2>Kendini dene</h2><div class="tip"><b>Hesap sorusu</b>${esc(n.q)}<details><summary>Çözümü göster</summary>${p(n.solution)}</details></div>` : ''}
${mc(c, 'Kavram sorusu')}
${mc(a, 'Uygulama sorusu')}
${l.case ? `<h2>Vaka sorusu</h2>${p(l.case)}` : ''}
${l.objectives?.length ? `<h2>Bu dersin sonunda</h2><ul>${l.objectives.map((o) => `<li>${esc(o)}</li>`).join('')}</ul>` : ''}
${sources.length ? `<h2>Kaynaklar</h2><ul>${sources.map((s) => `<li><a href="${esc(s.url)}" rel="noopener">${esc(s.title)}</a></li>`).join('')}</ul>` : ''}
</article>
<div class="st-c"><a class="st-p" href="${APP}#lesson/${l.id}">Alıştırmalara geç</a></div>
<nav class="st-n" aria-label="Ders sırası">${prev ? `<a href="../${prev._slug}/">← ${esc(prev.title)}</a>` : '<span></span>'}${next ? `<a href="../${next._slug}/">${esc(next.title)} →</a>` : ''}</nav></main>
${foot}`;
}

function indexPage() {
  const url = `${BASE}ders/`;
  const desc = `${lessons.length} ücretsiz Türkçe istatistik dersi: ortalama ve standart sapmadan hipotez testlerine, regresyondan Bayes'e. Kurulum ve hesap gerekmez.`;
  const byLevel = ['temel', 'orta', 'ileri'];
  const body = byLevel
    .map((lv) => {
      const mods = C.modules.map((m, i) => ({ m, i })).filter(({ m }) => m.level === lv);
      if (!mods.length) return '';
      return `<h2>${LEVEL[lv]}</h2>${mods
        .map(({ m, i }) => `<h3>${esc(m.title)}</h3><ul>${lessons.filter((l) => l.module === i).map((l) => `<li><a href="${l._slug}/">${esc(l.title)}</a></li>`).join('')}</ul>`)
        .join('')}`;
    })
    .join('');
  return `${head({ title: 'İstatistik dersleri', desc, url, type: 'website', css: '' })}
<body class="st"><a class="st-skip" href="#icerik">Ana içeriğe geç</a><header class="st-h"><a class="st-b" href="../">Kesit İstatistik</a></header><main id="icerik" class="st-m"><h1>İstatistik dersleri</h1><p class="st-l">${lessons.length} ücretsiz Türkçe ders. Metni burada oku, alıştırmaları uygulamada çöz.</p><div class="st-c"><a class="st-p" href="../docs/">Uygulamayı aç</a></div><div class="st-d">${body}</div></main>
${foot}`;
}

const out = join(ROOT, 'ders');
if (existsSync(out)) for (const l of lessons) rmSync(join(out, l._slug), { recursive: true, force: true });
lessons.forEach((l, i) => {
  const dir = join(out, l._slug);
  mkdirSync(dir, { recursive: true });
  writeFileSync(join(dir, 'index.html'), lessonPage(l, i));
});
writeFileSync(join(out, 'index.html'), indexPage());

const urls = [BASE, `${BASE}ders/`, ...lessons.map((l) => `${BASE}ders/${l._slug}/`), `${BASE}vaka/depo/`];
writeFileSync(
  join(ROOT, 'sitemap.xml'),
  `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.map((u) => `<url><loc>${u}</loc><lastmod>${today}</lastmod></url>`).join('\n')}\n</urlset>\n`,
);
console.log(`${lessons.length} ders sayfası, ders listesi ve sitemap.xml (${urls.length} adres) yazıldı.`);
