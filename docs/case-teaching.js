window.CaseTeaching = (() => {
  const esc = value => String(value).replace(/[&<>"']/g, c => ({
    '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'
  }[c]));
  const roleCases = {
    analist:['sla-mix','audit-sample','experiment-guardrail','capacity-fit','demand','stock-service'],
    bilim:['audit-sample','experiment-guardrail','posthoc','wms-impact','demand','capacity-fit','classifier','risk-monitor'],
    ml:['model-pairs','classifier','risk-monitor','capacity-fit'],
    operasyon:['picking','sla-mix','audit-sample','gage','control','posthoc','capacity-fit','demand','stock-service','wms-impact']
  };

  function list(role, data) {
    return roleCases[role] ? roleCases[role].map(id => data[id]).filter(Boolean) : Object.values(data);
  }
  const fmt = n => n.toLocaleString('tr-TR', {maximumFractionDigits:2});
  const titles = {
    analist:'Bir KPI değişimini açıkla',
    bilim:'Temsil ve belirsizliği ayır',
    ml:'Eşli değerlendirmeyle model kıyasla',
    operasyon:'Yöntem farkını iş eşiğine bağla'
  };

  function starter(role, data) {
    const id = roleCases[role]?.[0];
    if (!data[id]) return '';
    return `<aside class="case-start"><div>
      <span class="eyebrow">ROLÜN İÇİN İLK VAKA</span>
      <h2>${esc(titles[role])}</h2>
      <p>${esc(data[id].title)}</p></div>
      <a class="btn primary" href="#business/${id}">İlk vakayı aç →</a>
    </aside>`;
  }

  function brief(scene) {
    if (!scene.focus) return '';
    return `<section class="case-evidence">
      <span class="eyebrow">ÜÇ ADIMDA BULGU</span>
      <div class="case-evidence-grid">${scene.focus.map(([name,value,meaning], i) => `
        <div><span class="case-evidence-index">0${i+1}</span><b>${esc(name)}</b>
        <strong>${esc(value)}</strong><p>${esc(meaning)}</p></div>`).join('')}</div>
    </section>`;
  }

  function challenge(scene) {
    const x = scene.exercise;
    if (!x) return '';
    return `<form id="case-calculation" class="case-calculation">
      <span class="eyebrow">ÇÖZÜMÜ AÇMADAN ÖNCE</span>
      <h3>Bir sayıyı kendin bul</h3>
      <p>${esc(x.prompt)}</p>
      <label for="case-number">Sonucun (${esc(x.unit)})</label>
      <div class="case-number-row">
        <input id="case-number" name="answer" type="text" inputmode="decimal" autocomplete="off"
          maxlength="24" required placeholder="Örnek: 1,25">
        <button class="btn primary" type="submit">Hesabı kontrol et</button>
      </div>
      <p class="small-note">İki ondalık yeterli. Artı veya eksi yönüne dikkat et.</p>
      <p id="case-number-feedback" aria-live="polite"></p>
      <details><summary>Hesap ipucunu gör</summary><p>${esc(x.why)}</p></details>
    </form>`;
  }

  function bindChallenge(scene) {
    const form = document.querySelector('#case-calculation');
    if (!form || !scene.exercise) return;
    form.onsubmit = event => {
      event.preventDefault();
      const value = form.elements.answer.value.trim().replace(/−/g,'-').replace(',','.');
      const out = document.querySelector('#case-number-feedback');
      if (!/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)$/.test(value) || !Number.isFinite(Number(value))) {
        out.textContent = 'Ondalık bir sayı gir. Örnek: 1,25 veya −0,50.';
        out.className = 'case-number-bad';
        return;
      }
      const correct = Math.abs(Number(value) - scene.exercise.answer) <= 0.015;
      out.className = correct ? 'case-number-good' : 'case-number-bad';
      out.textContent = correct
        ? `Doğru: ${fmt(scene.exercise.answer)} ${scene.exercise.unit}. ${scene.exercise.why}`
        : 'Henüz eşleşmedi. Birimi, farkın yönünü ve paydayı kontrol et. Hesap ipucunu açıp tekrar deneyebilirsin.';
    };
  }

  function rubric(c) {
    return c.rubric ? `<details class="case-rubric"><summary>Karar notumu nasıl değerlendiririm?</summary>
      <ul>${c.rubric.map(x => `<li>${esc(x)}</li>`).join('')}</ul>
      <p>Bu kontrol listesi kendi gerekçeni değerlendirmen içindir.</p></details>` : '';
  }

  function worked(example) {
    if (!example) return '';
    return `<section class="article applied-lesson"><span class="eyebrow">İŞTE NASIL UYGULANIR?</span>
      <h2>${esc(example.title)}</h2><p class="lead-case">${esc(example.question)}</p>
      <ol>${example.worked.map(step => `<li>${esc(step)}</li>`).join('')}</ol>
      <p><b>Yorum.</b> ${esc(example.interpretation)}</p>
      <p><b>Uygulama koşulu.</b> ${esc(example.boundary)}</p>
      <a class="btn primary" href="#business/${esc(example.case)}">Veriyle karar vakasını çöz →</a>
    </section>`;
  }


  const chartByLesson = {
    s03:['unknown',0], s07:['default',0], s08:['default',0], s12:['default',1],
    s17:['default',0], s19:['default',1], s20:['default',0], s23:['complaints',0],
    s24:['default',1], s30:['default',0], s31:['default',0], s33:['default',0],
    s35:['pretrend',0], s54:['default',0], s55:['shift',1], s56:['default',1]
  };

  function summary(lesson, data) {
    if (!lesson.fieldExample) return '';
    const ex = lesson.fieldExample;
    const c = data[ex.case];
    const [scenario, index] = chartByLesson[lesson.id];
    const scene = c.scenes[scenario];
    const plot = scene.plots[index];
    return `<section class="article case-summary">
      <span class="eyebrow">DERS SONU / GÖRSEL KARAR ÖZETİ</span>
      <h2>${esc(ex.title)}</h2>
      <p>${esc(ex.question)}</p>
      <figure>
        <a href="${plot.file}" target="_blank" rel="noopener">
          <img src="${plot.file}" loading="lazy" alt="${esc(plot.caption)}"></a>
        <figcaption>${esc(plot.caption)}</figcaption>
      </figure>
      <p><b>Grafiği karara çevir.</b> ${esc(ex.interpretation)}</p>
      <p><b>Koşulu kontrol et.</b> ${esc(ex.boundary)}</p>
      <div class="actions">
        <a class="btn primary" href="#business/${esc(c.id)}">Senaryoları karşılaştır →</a>
        <a class="btn" href="${plot.file}" download>Grafiği indir · PNG ↓</a>
      </div>
    </section>`;
  }

  return {list,starter,brief,challenge,bindChallenge,rubric,worked,summary};
})();
