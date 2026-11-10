window.ConceptTeaching = (() => {
  const {core} = window.ConceptData;
  const methods = window.ConceptMethods;
  const course = window.COURSE;
  const esc = value => String(value).replace(/[&<>"']/g, c => ({
    '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'
  }[c]));
  const format = n => n.toLocaleString('tr-TR',{maximumFractionDigits:3});
  const responses = new Map();
  const areas = [
    ['Veri, ölçüm ve örnekleme',[0,1,4,21]],
    ['Olasılık ve matematiksel temel',[2,3,14,15,27,29]],
    ['Çıkarım ve belirsizlik',[5,6,10,16,18]],
    ['İlişki ve modelleme',[7,11,17]],
    ['Deney ve nedensellik',[8,28]],
    ['Tahmin, süreçler ve risk',[9,19,20]],
    ['Kalite ve olay süresi',[12]],
    ['Makine öğrenmesi ve model değerlendirme',[13,22,23,24,25,26]]
  ];

  // Aralık ve nokta şeritleri, dersin çözümlü tablosundaki sayıları yeniden kullanır.
  const charts = {
    s05:{unit:'Süre · dakika',ticks:[0,12,24,36,48],rows:[
      ['İlk süreler',[2,3,3,4,18]],['Son işlem uzadı',[2,3,3,4,48]],['Ortalama (önce → sonra)',[6,12]],['Medyan (iki durumda)',[3]]],
      caption:'En uzun işlem değişirken orta sıra aynı kalır. Ortalama sağa kayar.'},
    s06:{unit:'Süre · dakika',ticks:[4,7,10,13,16],rows:[['A istasyonu',[9,10,11]],['B istasyonu',[4,10,16]]],
      caption:'Her iki istasyon 10 dakika çevresinde. B’nin noktaları daha uzak.'},
    s08:{unit:'Zamanında teslim · %',ticks:[80,85,90,95,100],rows:[
      ['Önce (ham)',[96.2]],['Sonra (ham)',[88.5]],['Sonra (aynı karma)',[97.5]]],
      caption:'Ham kıyas sola giderken, önceki ağırlıklarla yapılan kıyas sağa gider.'},
    s18:{unit:'Süre ölçeği · saniye',ticks:[0,3,6,9,12],rows:[
      ['Tekil süre SD (her n)',[12]],['Ortalamanın SE · n=9',[4]],['Ortalamanın SE · n=36',[2]],['Ortalamanın SE · n=144',[1]]],
      caption:'Örnek büyüdüğünde işlem oynaklığı aynı kalır. Ortalamanın standart hatası küçülür.'},
    s19:{unit:'Ortalama ölçeği',ticks:[46,48,50,52,54,56,58],reference:50,refLabel:'Gerçek değer 50',rows:[
      ['Örnek 1',[],[46,53]],['Örnek 2',[],[49,56]],['Örnek 3',[],[51,58]]],
      caption:'Kırmızı çizgi sabit gerçek değeri, yatay şeritler farklı örneklerden kurulan aralıkları gösterir.'},
    s23:{unit:'Süre kazanımı · saniye',ticks:[0,.5,1,1.5,2],reference:1,refLabel:'İş eşiği 1 sn',rows:[
      ['Pilot 1',[.8],[.2,1.4]],['Pilot 2 (alıştırma)',[],[1.1,1.8]]],
      caption:'İlk aralık iş eşiğini kesiyor. İkinci aralığın tamamı eşiğin üstünde.'},
    s54:{unit:'Gecikme olasılığı · %',ticks:[0,20,40,60,80,100],rows:[
      ['Düşük risk · tahmin',[20]],['Düşük risk · gerçekleşen',[20]],['Yüksek risk · tahmin',[60]],['Yüksek risk · gerçekleşen',[40]]],
      caption:'Yüksek risk grubunda tahmin sağda, gerçekleşen oran solda. Sıralama ve kalibrasyon farklıdır.'},
    'competing-risk':{unit:'3. zamana kadar arıza · %',ticks:[0,5,10,15,20],rows:[
      ['Rakip olay dahil',[17]],['Rakip olay sansür kabul edilirse',[19]]],
      caption:'Yöntemler farklı sorulara yanıt verir. İki puan fark örnekleme hatası değildir.'}
  };

  function chart(id) {
    const c = charts[id];
    if (!c) return '';
    const [min,max] = [c.ticks[0],c.ticks.at(-1)];
    const x = n => 26+(n-min)/(max-min)*448;
    const grid = c.ticks.map(n => `<line x1="${x(n)}" x2="${x(n)}" y1="3" y2="33" class="concept-gridline"/>`).join('');
    return `<figure class="concept-chart" aria-label="${esc(c.caption)}">
      ${c.reference!==undefined?`<div class="concept-ref">┊ ${esc(c.refLabel)}</div>`:''}
      ${c.rows.map(([label,points,range],i)=>`<div class="concept-chart-lane">
        <span>${esc(label)}</span>
        <svg viewBox="0 0 500 36" role="img" aria-label="${esc((range||points).map(format).join(' ile '))}">
          ${grid}<line x1="26" y1="18" x2="474" y2="18" class="concept-gridline"/>
          ${c.reference!==undefined?`<line x1="${x(c.reference)}" x2="${x(c.reference)}" y1="0" y2="36" class="concept-marker"/>`:''}
          ${range?`<line x1="${x(range[0])}" x2="${x(range[1])}" y1="18" y2="18" class="concept-interval ${i%2?'alternate':''}"/>`:''}
          ${points.map((p,j)=>`<circle cx="${x(p)}" cy="${points.indexOf(p)===j?18:9}" r="5" class="concept-point ${i%2?'alternate':''}"/>`).join('')}
        </svg></div>`).join('')}
      <div class="concept-axis-row"><svg class="concept-axis" viewBox="0 0 500 22" aria-hidden="true">${c.ticks.map(n=>`<text x="${x(n)}" y="17" text-anchor="middle">${format(n)}</text>`).join('')}</svg></div>
      <div class="concept-axis-title">${esc(c.unit)}</div>
      <figcaption>${esc(c.caption)}</figcaption>
    </figure>`;
  }

  function table(c) {
    return `<div class="table-wrap concept-table"><table><thead><tr>${c.columns.map(x=>`<th scope="col">${esc(x)}</th>`).join('')}</tr></thead><tbody>
      ${c.rows.map(row=>`<tr>${row.map(x=>`<td>${esc(x)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
  }

  function question(id, kind, q) {
    const key = id+'-'+kind;
    const order = [...q.options];
    if (([...key].reduce((sum,ch)=>sum+ch.charCodeAt(0),0)%2)===0) order.reverse();
    const previous = responses.get(key);
    return `<form class="concept-check" data-concept-id="${esc(id)}" data-concept-kind="${kind}">
      <fieldset><legend>${esc(q.question)}</legend>
      ${order.map(o=>{
        const index = q.options.indexOf(o);
        return `<label><input type="radio" name="concept-choice" value="${index}" required ${index===previous?'checked':''}><span>${esc(o.label)}</span></label>`;
      }).join('')}</fieldset>
      <button class="btn" type="submit">Gerekçeyi gör</button>
      <p class="concept-feedback ${previous===undefined?'':q.options[previous].correct?'is-right':'is-retry'}" role="status">${previous===undefined?'':esc(q.options[previous].feedback)}</p>
    </form>`;
  }

  function methodsFor(id) {
    const related = Object.entries(methods).filter(([,m])=>m.base.includes(id));
    return related.length?`<aside class="concept-extension"><b>Sonraki yöntem</b><div class="actions">${related.map(([key,m])=>`<a href="#method/${key}" class="btn tiny">${esc(m.title)} →</a>`).join('')}</div></aside>`:'';
  }

  function intro(id,c=core[id]) {
    if (!c) return '';
    return `<section class="article concept-intro">
      <span class="eyebrow">ÖNCE TAHMİN ET</span><h2>${esc(c.goal)}</h2>
      <p class="concept-situation">${esc(c.situation)}</p>
      ${question(id,'predict',c.predict)}
      <details class="concept-explanation" ${responses.has(id+'-predict')?'open':''}>
        <summary>Kavramın mantığını aç</summary>
        <p>${esc(c.rule)}</p><p>${esc(c.takeaway)}</p>
      </details>
    </section>`;
  }

  function worked(id,c=core[id]) {
    if (!c) return '';
    return `<section class="article concept-worked"><span class="eyebrow">AYNI ÖRNEĞİ ADIM ADIM ÇÖZ</span>
      <h2>Hesabın arkasındaki fikir</h2><p>${esc(c.situation)}</p>
      ${table(c)}<ol class="concept-steps">${c.steps.map(s=>`<li>${esc(s)}</li>`).join('')}</ol>
      <div class="concept-conclusion"><b>Kararda kullanırken</b><p>${esc(c.takeaway)}</p></div>
      ${methodsFor(id)}
    </section>`;
  }

  function visual(id) {
    const c = core[id];
    if (!c) return '';
    return `<section class="article concept-visual"><span class="eyebrow">ÖRNEĞİ GÖR</span>
      <h2>Neyi karşılaştırıyoruz?</h2><p>${esc(c.situation)}</p>
      ${chart(id)||table(c)}<p class="concept-small">Aşağıdaki canlı keşif, aynı fikri kendi örnek sayılarıyla denemeni sağlar.</p></section>`;
  }

  function transfer(id,c=core[id]) {
    if (!c) return '';
    return `<section class="article concept-transfer"><span class="eyebrow">BAĞLAMI DEĞİŞTİR</span><h2>Aynı düşünceyi yeni soruda kullan</h2>
      ${question(id,'transfer',c.transfer)}<p class="concept-small">Gerekçeyi kendi cümlenle söyle. Yanıt bu oturumda hatırlanır ve ders puanını değiştirmez.</p></section>`;
  }

  function summary(l) {
    const c = core[l.id];
    if (!c) return '';
    return `<section class="article concept-summary">
      <span class="eyebrow">DERS SONU / KAVRAM PANOSU</span><h2>${esc(c.goal)}</h2>
      <p class="concept-situation">${esc(c.situation)}</p>
      ${chart(l.id)||table(c)}
      <ol class="concept-steps">${c.steps.map(x=>`<li>${esc(x)}</li>`).join('')}</ol>
      <div class="concept-conclusion"><b>Akılda kalsın</b><p>${esc(c.takeaway)}</p></div>
      <div class="actions"><a href="#lesson/${l.id}" class="btn">Derse dön →</a><button data-action="print" class="btn">Yazdır / PDF</button></div>
    </section>`;
  }

  function cards(entries) {
    return `<div class="method-grid">${entries.map(([key,m])=>`<a class="method-card" href="#method/${key}">
      <span class="eyebrow">${esc(m.area)}</span><h3>${esc(m.title)}</h3><p>${esc(m.goal)}</p>
      <span class="text-link">Dersi aç →</span></a>`).join('')}</div>`;
  }

  function searchMethods(text, level, module) {
    if (level!=='all'&&level!=='ileri') return '';
    const q = text.trim().toLocaleLowerCase('tr-TR');
    const entries = Object.entries(methods).filter(([,m])=>{
      if(module!=='all'&&!m.base.some(id=>String(course.lessons.find(l=>l.id===id).module)===String(module)))return false;
      return [m.title,m.goal,m.area,m.rule].join(' ').toLocaleLowerCase('tr-TR').includes(q);
    });
    return entries.length?`<section class="method-library"><h2>Seçmeli yöntem dersleri</h2>${cards(entries)}</section>`:'';
  }

  function coverage(state) {
    const role = course.roles.find(r=>r.id===state.role)||course.roles[0];
    const entries = Object.entries(methods);
    const picks = entries.filter(([,m])=>m.roles.includes(role.id));
    const starterCount = new Set(course.starter.flatMap(m=>m.ids)).size;
    return `<section class="article concept-map">
      <span class="eyebrow">MÜFREDATIN İÇERİK DENETİMİ</span>
      <h1>Hangi alanı, hangi derinlikte öğreniyorum?</h1>
      <p>Ders, modül, yöntem ve iş vakası ayrı sayılır. Aynı ders birden fazla rolde kullanılabilir.</p>
      <div class="concept-counts">
        <div><b>${course.modules.length}</b><span>ana modül</span></div>
        <div><b>${course.lessons.length}</b><span>modüllerdeki ders</span></div>
        <div><b>${Object.keys(core).length}</b><span>kavram akışı yenilenen mevcut ders</span></div>
        <div><b>${entries.length}</b><span>ek seçmeli yöntem dersi</span></div>
      </div>
      <p><b>İlk kez öğreniyorsan</b> ortak başlangıçtaki ${starterCount} dersten ilerle.
        <b>${esc(role.title)} için</b> ${role.coreLessons.length} çekirdek ders öneriliyor.</p>
      <div class="actions"><a href="#start" class="btn primary">Ortak başlangıcı aç →</a><a href="#path" class="btn">Rol yolumu aç →</a></div>
      <h2>Ana derslerin dağılımı</h2>
      <div class="table-wrap"><table><thead><tr><th>Alan</th><th>Modül</th><th>Ders</th><th>Yenilenen kavram akışı</th><th>Rol çekirdeği</th></tr></thead>
      <tbody>${areas.map(([area,mods])=>{
        const ls=course.lessons.filter(l=>mods.includes(l.module));
        return `<tr><td>${esc(area)}</td><td>${mods.length}</td><td>${ls.length}</td><td>${ls.filter(l=>core[l.id]).length}</td><td>${ls.filter(l=>role.coreLessons.includes(l.id)).length}</td></tr>`;
      }).join('')}</tbody></table></div>
      <p class="concept-small">İleri uygulama defterleri, iş vakaları ve kavram görselleri bu ders sayılarına tekrar eklenmez.</p>
      <h2>Rolün için seçmeli derinleşme</h2>${cards(picks)}
      <details><summary>Tüm seçmeli yöntemleri göster · ${entries.length}</summary>${cards(entries)}</details>
      <details><summary>Bu haritanın kapsam sınırı</summary>
        <p>Dersler uygulamalı istatistik ve karar okuryazarlığına odaklanır. Ölçü kuramı, ileri asimptotik ispatlar, mekânsal istatistik ve uzmanlık alanlarının bütün yöntemleri bu müfredatın kapsamında yer almaz.</p>
        <p>Seçmeli yöntem derslerinde açıklama, elde çözülmüş örnek ve iki kavram kontrolü vardır. Hesaplayıcı ve tam model uyumu olan çalışmalar, atölye ve ileri uygulama ekranlarında ayrıca gösterilir.</p>
        <a href="#review" class="btn">Önceki kaynak karşılaştırması →</a></details>
    </section>`;
  }

  function methodPage() {
    const id = location.hash.split('/')[1];
    const c = Object.hasOwn(methods,id)?methods[id]:null;
    if (!c) return '<p>Bu yöntem bulunamadı. <a href="#curriculum">Kazanım haritasına dön →</a></p>';
    return `<a class="text-link" href="#curriculum">← Kazanım haritası</a>
      <div class="page-title"><div><span class="eyebrow">SEÇMELİ DERS / ${esc(c.area)}</span><h1>${esc(c.title)}</h1><p>${esc(c.goal)}</p></div></div>
      <details class="prerequisite-hint"><summary>Bu dersten önce hangi konular yararlı?</summary>
      ${c.base.map(key=>`<a class="btn tiny" href="#lesson/${key}">${esc(course.lessons.find(l=>l.id===key).title)} →</a>`).join('')}</details>
      ${intro(id,c)}${chart(id)}${worked(id,c)}${transfer(id,c)}`;
  }

  function mount() {
    for(const form of document.querySelectorAll('[data-concept-id]')) {
      form.onsubmit = event => {
        event.preventDefault();
        const {conceptId:id,conceptKind:kind} = form.dataset;
        const c = core[id]||methods[id];
        const chosen = form.querySelector('input[name="concept-choice"]:checked');
        if (!chosen||!c?.[kind]?.options[chosen.value]) return;
        const index = Number(chosen.value);
        responses.set(id+'-'+kind,index);
        const option = c[kind].options[index];
        const feedback = form.querySelector('.concept-feedback');
        feedback.textContent = (option.correct?'Doğru. ':'Tekrar düşün. ')+option.feedback;
        feedback.className = 'concept-feedback '+(option.correct?'is-right':'is-retry');
        const explanation = form.closest('.concept-intro')?.querySelector('details');
        if (explanation) explanation.open = true;
      };
    }
  }

  return {core,methods,areas,intro,worked,visual,transfer,summary,coverage,methodPage,searchMethods,methodsFor,mount};
})();
