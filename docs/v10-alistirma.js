/* Kesit İstatistik V10: ders sayfasında "Kesit verisiyle hesapla" paneli.
   Görevler ders-alistirma.js içinde (alistirma_v10.py üretir). Burada yalnız gösterim, cevap denetimi ve ilerleme kaydı var.
   KesitV9.mount sarılır: app.js her çizimde mount çağırır, panel o anda ders sütununa eklenir. */
(function (g) {
  'use strict';
  const A = g.KESIT_DERS_ALISTIRMA, V9 = g.KesitV9;
  if (!A || !V9) return;
  const KEY = 'kesit-istatistik-v10';
  let kayit = {};
  try { kayit = JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch (e) { kayit = {}; }
  const sakla = () => { try { localStorage.setItem(KEY, JSON.stringify(kayit)); } catch (e) { /* özel pencere: yalnız bu oturum */ } };
  const esc = s => String(s).replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
  const soruHTML = s => esc(s).replace(/&lt;(\/?)b&gt;/g, '<$1b>');
  const tolerans = t => Math.max(Math.abs(t.cevap) * 0.005, 0.5 * Math.pow(10, -t.d), t.tol || 0); // tol: rastgelelik ya da kütüphane sürümü farkı için ek pay
  const bicim = (v, d) => Number(v).toLocaleString('tr-TR', {minimumFractionDigits: d, maximumFractionDigits: d});
  function sayi(s) {
    s = String(s).trim().replace(/\s/g, '').replace(/[%₺]/g, '').replace(/^TL|TL$/i, '');
    if (!s) return NaN;
    if (/^-?\d{1,3}(\.\d{3})+,\d+$/.test(s) || /^-?\d{1,3}(\.\d{3}){2,}$/.test(s)) s = s.replace(/\./g, '').replace(',', '.');   // 1.234,5 · 1.234.567 (tek nokta ondalıktır: 0.123)
    else if (/^-?\d+,\d+$/.test(s)) s = s.replace(',', '.');                                    // 0,123
    else if (/^-?\d{1,3}(,\d{3})+(\.\d+)?$/.test(s)) s = s.replace(/,/g, '');                  // 1,234.5
    return /^-?(\d+\.?\d*|\.\d+)(e-?\d+)?$/i.test(s) ? Number(s) : NaN;
  }
  const modulNo = id => { const l = (g.COURSE && g.COURSE.lessons || []).find(x => x.id === id); return l ? l.module + 1 : null; };
  const iki = n => String(n).padStart(2, '0');

  function panel(id) {
    const ts = A.dersler[id];
    if (!ts) return '';
    const m = modulNo(id), bitti = ts.filter(t => kayit[t.id] && kayit[t.id].ok).length;
    const veri = [...new Set(ts.flatMap(t => t.veri))].join(', ');
    return `<section class="v10-panel" id="v10-${id}" aria-labelledby="v10-b-${id}">
<div class="v10-bas"><span class="eyebrow">UYGULAMA · KESİT VERİSİ</span><h3 id="v10-b-${id}">Kesit verisiyle hesapla</h3>
<p>Bu dersin yöntemini gerçek boyutlu kurgusal veride uygula: ${ts.length} görev, cevabını yaz, uygulama denetlesin.${veri ? ` Kullanılan tablolar: <code>${esc(veri)}</code>.` : ''}</p>
<p class="v10-ilerleme" data-v10-ilerleme="${id}">${bitti} / ${ts.length} görev tamam</p></div>
<ol class="v10-liste">${ts.map((t, i) => gorev(t, i)).join('')}</ol>
<div class="v10-indir"><b>Bilgisayarında çöz:</b>
<a class="btn" href="defter/${id}.ipynb" download>Ders defteri (.ipynb)</a>
<a class="btn" href="defter/${id}.py" download>Python betiği (.py)</a>
${m ? `<a class="btn" href="excel/modul-${iki(m)}.xlsx" download>Excel kitabı · Modül ${m}</a>` : ''}
<a class="btn" href="data/kesit-veri.zip" download>Veri paketi (.zip, 1 MB)</a>
<a class="btn" href="defter/kesit-defterler.zip" download>Tüm defterler (.zip)</a>
<details><summary>Nasıl kullanılır?</summary><p>Veri paketini aç, oluşan <code>kesit/</code> klasörünü defterin yanına koy. Defter her görevi aynı kodla hesaplar ve sonucu <code>assert</code> ile denetler. Excel kitabında veriyi kendi formüllerinle hesapla, sonucu sarı hücreye yaz; Kontrol sütunu Doğru ya da Tekrar dene der. Makine öğrenmesi, MCMC ve karma model görevleri Excel ile pratik değildir; onları defterle çöz.</p></details></div>
</section>`;
  }
  function gorev(t, i) {
    const k = kayit[t.id] || {}, durum = k.ok ? 'ok' : '';
    return `<li class="v10-gorev ${durum}" data-v10-id="${t.id}">
<p class="v10-soru"><b>Görev ${i + 1}.</b> ${soruHTML(t.soru)}</p>
<div class="v10-giris"><label class="sr-only" for="v10-in-${t.id}">Görev ${i + 1} cevabı</label>
<input id="v10-in-${t.id}" inputmode="decimal" autocomplete="off" placeholder="${t.d ? 'ör. ' + bicim(0, t.d) : 'tam sayı'}" value="${k.v != null ? esc(k.v) : ''}">
<button class="btn primary" data-v10="denetle" data-id="${t.id}">Denetle</button>
${t.ipucu ? `<button class="btn" data-v10="ipucu" data-id="${t.id}">İpucu</button>` : ''}
<button class="btn" data-v10="coz" data-id="${t.id}">Çözümü göster</button></div>
<div class="v10-geri" data-v10-geri="${t.id}" aria-live="polite">${k.ok ? `<div class="feedback good">✓ Doğru. Beklenen: <b>${bicim(t.cevap, t.d)}</b></div>` : ''}</div>
</li>`;
  }
  function bul(id) { for (const k in A.dersler) { const t = A.dersler[k].find(x => x.id === id); if (t) return [k, t]; } return []; }
  function kodHTML(t) {
    return `<details open><summary>Python çözümü</summary><p class="v10-not">Önce hazırlık kodu tabloları yükler (<code>teslim</code> = teslim edilen yemek siparişleri, <code>inen</code> = inen uçuşlar, <code>gunluk</code> = günlük bisiklet yolculuğu ve hava).</p>
<pre><code>${esc(t.kod)}</code></pre><details><summary>Hazırlık kodu</summary><pre><code>${esc(A.hazirlik)}</code></pre></details></details>`;
  }
  function ilerleme(ders) {
    const ts = A.dersler[ders], el = document.querySelector(`[data-v10-ilerleme="${ders}"]`);
    if (el) el.textContent = `${ts.filter(t => kayit[t.id] && kayit[t.id].ok).length} / ${ts.length} görev tamam`;
  }
  document.addEventListener('click', e => {
    const b = e.target.closest('[data-v10]');
    if (!b) return;
    const [ders, t] = bul(b.dataset.id);
    if (!t) return;
    const geri = document.querySelector(`[data-v10-geri="${t.id}"]`), li = b.closest('.v10-gorev');
    if (b.dataset.v10 === 'ipucu') { geri.innerHTML = `<div class="feedback"><b>İpucu:</b> <code>${esc(t.ipucu)}</code></div>`; return; }
    if (b.dataset.v10 === 'coz') { geri.innerHTML = `<div class="feedback">Beklenen sonuç: <b>${bicim(t.cevap, t.d)}</b> (kabul aralığı ±${bicim(tolerans(t), Math.max(t.d, 2) + 1)})</div>` + kodHTML(t); return; }
    const ham = li.querySelector('input').value, v = sayi(ham);
    if (!isFinite(v)) { geri.innerHTML = '<div class="feedback bad">Bir sayı yaz: ondalık için virgül ya da nokta kullanabilirsin (0,123 veya 0.123).</div>'; return; }
    const ok = Math.abs(v - t.cevap) <= tolerans(t) + 1e-12;
    const r = kayit[t.id] || {a: 0};
    r.a = (r.a || 0) + 1; r.v = ham; r.t = Date.now(); if (ok) r.ok = true;
    kayit[t.id] = r; sakla();
    li.classList.toggle('ok', !!r.ok);
    geri.innerHTML = ok
      ? `<div class="feedback good">✓ Doğru. Beklenen: <b>${bicim(t.cevap, t.d)}</b></div>`
      : `<div class="feedback bad">Tekrar dene. ${Math.abs(v) > 0 && Math.abs(t.cevap / v - 100) < 1 ? 'Sonucu yüzde olarak mı yazdın? Soru oran istiyor olabilir. ' : Math.abs(v * 100 - t.cevap) < Math.abs(t.cevap) * 0.01 ? 'Soru yüzde istiyor: oranı 100 ile çarp. ' : ''}${r.a >= 2 ? 'İki denemeden sonra çözümü açıp kodu inceleyebilirsin.' : ''}</div>`;
    ilerleme(ders);
  });
  document.addEventListener('keydown', e => {
    if (e.key !== 'Enter' || !e.target.matches('.v10-gorev input')) return;
    e.preventDefault(); e.target.closest('.v10-gorev').querySelector('[data-v10="denetle"]').click();
  });

  const eski = V9.mount;
  V9.mount = function (page, lesson) {
    const sonuc = eski.apply(this, arguments);
    if (page === 'lesson' && lesson && A.dersler[lesson.id] && !document.getElementById('v10-' + lesson.id)) {
      const col = document.querySelector('.lesson-layout > :last-child');
      if (col) { const br = col.querySelector('.v9-bridge'); br ? br.insertAdjacentHTML('beforebegin', panel(lesson.id)) : col.insertAdjacentHTML('beforeend', panel(lesson.id)); }
    }
    return sonuc;
  };
  const eskiExport = V9.exportState, eskiImport = V9.importState;
  V9.exportState = () => Object.assign(eskiExport(), {v10: JSON.parse(JSON.stringify(kayit))});
  V9.importState = function (s) {
    if (s && s.v10 && typeof s.v10 === 'object') { for (const k in s.v10) { const v = s.v10[k]; if (/^s\d{2,3}-v\d$/.test(k) && v && typeof v === 'object') kayit[k] = Object.assign({}, kayit[k] || {}, {ok: !!(v.ok || (kayit[k] && kayit[k].ok)), a: Number(v.a) || 0}); } sakla(); }
    return eskiImport.apply(this, arguments);
  };
  g.KesitV10 = {panel, sayi, tolerans, _kayit: () => kayit};
})(window);
