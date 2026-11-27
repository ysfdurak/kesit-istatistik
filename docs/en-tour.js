/* İngilizce tanıtım turu (?lang=en ile açılır, ?lang=tr ile kapanır; aynı sekmede bütün Kesit uygulamalarında sürer).
 * Kesit Türkçe veri eğitimidir ve Türkçe kalır. Tur, İngilizce okuyan ziyaretçiye her ekranın ne işe yaradığını anlatan
 * bir panel ve menü/başlıkların altında küçük İngilizce karşılıklar ekler. Uygulamaya özel içerik CONFIG'tedir; altındaki
 * motor bütün Kesit uygulamalarında ve İngilizce Atölyesi'nde aynıdır. Bu dosya ana sayfa deposundaki
 * araclar/en-tour/ betiğiyle üretilir. */
(function (root) {
  'use strict';
  const CONFIG = {
    key: 'kesit_lang',
    bg: '#16323a',
    accent: '#9fe0c9',
    intro: "Kesit İstatistik is one of five Kesit apps that teach data skills — Excel, SQL, Power BI, Python and statistics — <b>in Turkish</b>, in the browser, with no setup or account. Teaching data work in Turkish is the point of the project, so the interface stays Turkish; code, functions and technical terms are in English as at work. This guide explains each screen.",
    glossSelector: "nav button, aside button, aside a[data-page], .side a[data-page], h1, main h2",
    blockGloss: "h1, main h2",
    navGloss: "nav button, aside button, aside a[data-page], .side a[data-page]",
    gloss: {
      "Ana sayfa": "Home",
      "Öğrenme yolları": "Learning paths",
      "Dersler": "Lessons",
      "Tekrar": "Review",
      "Seviye testi": "Placement test",
      "Pratik": "Practice",
      "Sınavlar": "Exams",
      "Mülakat": "Interview",
      "Mülakat hazırlığı": "Interview prep",
      "Bitirme projeleri": "Capstone projects",
      "Belgelerim": "My certificates",
      "Veri setleri": "Datasets",
      "Sık hatalar": "Common mistakes",
      "Sık hatalar ve ipuçları": "Common mistakes and tips",
      "Sözlük": "Glossary",
      "Profil": "Profile",
      "Hakkında": "About",
      "Menü": "Menu",
      "Nereden başlayalım?": "Where shall we start?",
      "Hedefine göre yol seç": "Pick a path for your goal",
      "Uygula ve hazırlan": "Apply and get ready",
      "Bilgini sına": "Test yourself",
      "ÖĞREN": "Learn",
      "PRATİK": "Practice",
      "ARAÇLAR": "Tools",
      "KARİYER": "Career",
      "REFERANS": "Reference",
      "Başlangıç rehberi": "Getting started",
      "İş problemi çöz": "Solve a business problem",
      "Kavramı gör": "See the concept",
      "Konu panoları": "Topic boards",
      "İlerlemem": "My progress",
      "Kapsam ve kalite": "Scope and quality",
      "Kesit verileriyle": "With Kesit data",
      "Alıştırma atölyesi": "Practice workshop",
      "Formülden önce neyi gördüğünü anla.": "Understand what you see before the formula.",
      "Şu an neye ihtiyacın var?": "What do you need right now?",
      "İstatistiği hangi iş için kullanacaksın?": "What will you use statistics for?"
    },
    route: () => {
      const h = location.hash.replace(/^#\/?/, '').split(/[/?&]/)[0];
      if (!h) return 'home';
      if (/^ders-|^lesson$|^l$/.test(h)) return 'lesson';
      const a = {"path":"paths","library":"curr","placement":"test","progress":"profile","mistakes":"hatalar","interview":"mulakat"};
      return a[h] || h;
    },
    guide: {
      "paths": {
        "t": "Learning paths",
        "p": "4 paths: data analysis and BI, data science, machine learning, process and quality analysis."
      },
      "review": {
        "t": "Review",
        "p": "Spaced repetition: questions you got wrong come back after increasing intervals until you answer them correctly several times."
      },
      "test": {
        "t": "Placement test",
        "p": "Places you at the right level."
      },
      "profile": {
        "t": "My progress",
        "p": "Progress, saved to a file and merged on another device; includes practice, case and interview records."
      },
      "hakkinda": {
        "t": "About",
        "p": "How the app was built and verified, its known limits, and the licence. Product decisions are Yusuf Durak’s; code and content were developed with AI (Claude) and checked by automated tests."
      },
      "belgeler": {
        "t": "My certificates",
        "p": "A completion certificate generated in the browser after finishing a path. It is not verifiable and is not an official certificate — the app says so on the page."
      },
      "hatalar": {
        "t": "Common mistakes",
        "p": "32 common statistical mistakes with the correct reasoning."
      },
      "dict": {
        "t": "Glossary",
        "p": "Key terms with short Turkish explanations."
      },
      "data": {
        "t": "With Kesit data",
        "p": "13 cases on the datasets shared with Kesit SQL, Power BI and Python. Each case: a prediction, choice of method, SQL + Python + DAX code, the result computed from the real data, a chart, the decision and its limits."
      },
      "projeler": {
        "t": "Capstone projects",
        "p": "End-of-path projects on the shared datasets."
      },
      "lesson": {
        "t": "Inside a lesson",
        "p": "What the concept means before the formula, with applied examples. Related lessons end with the SQL, DAX and Python equivalent of the concept."
      },
      "home": {
        "t": "Kesit İstatistik",
        "p": "120 lessons in 30 modules plus 8 elective method lessons, from population and sample to tests, regression, experiments, time series, Bayes, quality, statistical learning and causal inference. Calculators are checked against SciPy references; case results are computed with pandas, SciPy and statsmodels. Every lesson ends with 3 hands-on tasks on the shared Kesit data (360 in total), with a downloadable Python notebook per lesson and an Excel workbook per module.",
        "try": "Open “Kesit verileriyle” (With Kesit data) to see a statistics question answered with SQL, Python and DAX on the shared datasets."
      },
      "start": {
        "t": "Getting started",
        "p": "Where to begin depending on your background and goal."
      },
      "curr": {
        "t": "Lessons",
        "p": "All modules in Basic, Intermediate and Advanced levels."
      },
      "lab": {
        "t": "Solve a business problem",
        "p": "Business cases: choose the method, run it and turn the result into a decision with its limits."
      },
      "explore": {
        "t": "See the concept",
        "p": "50 visual concept explorations."
      },
      "infographics": {
        "t": "Topic boards",
        "p": "One-page visual summaries of each topic."
      },
      "quality": {
        "t": "Scope and quality",
        "p": "What the curriculum covers and how the results were verified."
      },
      "practice": {
        "t": "Practice workshop",
        "p": "33 question types that generate new numbers each time, with formula hints, step-by-step solutions and a list of weak topics."
      },
      "mulakat": {
        "t": "Interview prep",
        "p": "48 statistics interview questions by role: what a strong answer contains, a weak example and a follow-up question."
      }
    },
  };
  /* ---------- Tur motoru (bütün uygulamalarda aynı; içerik yukarıdaki CONFIG'tedir) ---------- */
  const C = CONFIG;
  // Tur yalnızca bu sekmede açık kalır (sessionStorage): ?lang=en ile açılır, aynı sekmede gezerken sürer,
  // yeni bir ziyarette uygulama yine Türkçe açılır. Eski sürüm seçimi kalıcı tuttuğu için o kayıt silinir.
  let on = false;
  try {
    localStorage.removeItem(C.key);
    const q = new URLSearchParams(location.search).get('lang');
    if (q === 'en') sessionStorage.setItem(C.key, 'en');
    if (q === 'tr') sessionStorage.removeItem(C.key);
    on = sessionStorage.getItem(C.key) === 'en';
  } catch {}
  if (!on) return;
  root.EN_TOUR = true;
  let clicked = null; // URL'si değişmeyen uygulamalarda son tıklanan bölüm
  const norm = s => (s || '').replace(/\s+/g, ' ').trim();
  const strip = s => norm(s).replace(/^[^\p{L}\p{N}]+/u, '').replace(/\s*[›→↗»]$/, '');

  function glossAll() {
    document.querySelectorAll(C.glossSelector).forEach(el => {
      if (el.dataset.enGloss || el.closest('#en-tour')) return;
      const own = C.glossText ? C.glossText(el) : el.innerText;
      const en = C.gloss[norm(own)] || C.gloss[strip(own)];
      if (!en || en === strip(own)) return;
      el.dataset.enGloss = '1';
      const s = document.createElement('span');
      s.className = 'en-gloss';
      s.lang = 'en';
      s.textContent = en;
      if (C.blockGloss && el.matches(C.blockGloss)) s.classList.add('en-block');
      else if (C.navGloss && el.matches(C.navGloss)) el.classList.add('en-nav');
      el.appendChild(s);
    });
  }

  const CSS = `
  .en-gloss{display:inline-block;margin-left:6px;font-size:11px;font-weight:500;letter-spacing:0;text-transform:none;opacity:.7;font-style:italic}
  .en-nav{flex-wrap:wrap!important}
  .en-nav>.en-gloss{display:block;flex-basis:100%;margin:1px 0 0 ${C.navIndent || '28px'};font-size:10.5px;line-height:1.2}
  .en-gloss.en-block{display:block;margin:2px 0 0;font-size:12px;line-height:1.3}
  #en-tour{position:fixed;right:16px;bottom:16px;z-index:2147483000;width:min(360px,calc(100vw - 32px));max-height:calc(100vh - 32px);overflow:auto;background:${C.bg || '#1f2a44'};color:#f4f6fb;border-radius:14px;box-shadow:0 14px 40px rgba(0,0,0,.28);font:14px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif;text-align:left}
  #en-tour header{display:flex;align-items:center;justify-content:space-between;gap:8px;padding:11px 14px 0}
  #en-tour header b{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:${C.accent || '#ffd479'}}
  #en-tour header button{all:unset;cursor:pointer;border:1px solid rgba(255,255,255,.35);border-radius:8px;padding:1px 8px;font-size:12px}
  #en-tour .en-body{padding:4px 14px 13px}
  #en-tour h3{margin:4px 0 6px;font-size:16px;color:#fff;font-weight:700}
  #en-tour p{margin:0 0 8px}
  #en-tour .en-try{background:rgba(255,255,255,.08);border-left:3px solid ${C.accent || '#ffd479'};padding:7px 10px;border-radius:6px}
  #en-tour a{color:${C.accent || '#ffd479'}}
  #en-tour .en-foot{font-size:12px;opacity:.75;margin:6px 0 0}
  #en-tour.en-min .en-body{display:none}
  #en-tour.en-min{width:auto}
  #en-tour.en-min header{padding:9px 12px}
  @media (max-width:640px){#en-tour{right:8px;left:8px;bottom:8px;width:auto;max-height:45vh}}
  @media print{#en-tour,.en-gloss{display:none!important}}
  ${C.css || ''}`;

  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
  let panel, btn, lastKey;
  function render(force) {
    const k = C.route(clicked) || 'home';
    if (k === lastKey && !force) return;
    lastKey = k;
    const g = C.guide[k] || C.guide.home;
    let first = false;
    try {
      first = !sessionStorage.getItem(C.key + '_seen');
      sessionStorage.setItem(C.key + '_seen', '1');
    } catch {}
    panel.querySelector('.en-body').innerHTML = `
      ${first ? `<p>${C.intro}</p>` : ''}
      <h3>${esc(g.t)}</h3>
      <p>${g.p}</p>
      ${g.try ? `<p class="en-try"><b>Try this:</b> ${g.try}</p>` : ''}
      <p class="en-foot">${C.foot || 'Small English labels under menus and headings are part of this guide.'} <a href="?lang=tr">Turn off</a></p>`;
  }
  function setMin(min, remember) {
    panel.classList.toggle('en-min', min);
    btn.textContent = min ? 'Show' : 'Hide';
    btn.setAttribute('aria-expanded', String(!min));
    if (remember)
      try {
        localStorage.setItem(C.key + '_min', min ? '1' : '');
      } catch {}
  }
  function mount() {
    const style = document.createElement('style');
    style.textContent = CSS;
    document.head.appendChild(style);
    panel = document.createElement('aside');
    panel.id = 'en-tour';
    panel.lang = 'en';
    panel.setAttribute('aria-label', 'English guide');
    panel.innerHTML = '<header><b>English guide</b><button type="button">Hide</button></header><div class="en-body"></div>';
    btn = panel.querySelector('button');
    btn.addEventListener('click', () => setMin(!panel.classList.contains('en-min'), true));
    document.body.appendChild(panel);
    let min = false;
    try {
      min = localStorage.getItem(C.key + '_min') === '1';
    } catch {}
    setMin(min);
    render(true);
    glossAll();
    // Kullanıcı yazmaya başlayınca panel küçülür, içeriği kapatmaz.
    document.addEventListener('focusin', e => {
      if (!panel.contains(e.target) && e.target.matches('input:not([type=checkbox]):not([type=radio]), textarea, select'))
        setMin(true);
    });
    document.addEventListener(
      'click',
      e => {
        if (panel.contains(e.target) || !C.clickRoute) return;
        const r = C.clickRoute(e.target);
        if (r) clicked = r;
      },
      true
    );
    let t;
    new MutationObserver(() => {
      clearTimeout(t);
      t = setTimeout(() => {
        glossAll();
        render();
      }, 80);
    }).observe(document.body, { childList: true, subtree: true });
    addEventListener('hashchange', () => setTimeout(render, 60));
    addEventListener('popstate', () => setTimeout(render, 60));
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount);
  else mount();
})(window);
