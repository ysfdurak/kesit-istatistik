# Kesit İstatistik nasıl çalışır? (proje rehberi)

Bu belge projeye hâkim olmak, bir soru geldiğinde cevap verebilmek ve güvenle değişiklik yapmak için yazıldı. Önce mimariyi, sonra veri akışını, en sonda sık yapılan işlerin tarifini bulursun.

## 1. Büyük resim
- **Statik site.** Sunucu, veritabanı, derleme adımı yok. `docs/index.html` bütün CSS ve JS dosyalarını sırayla yükler; sayfalar `location.hash` ile değişir (`#lesson/s19`, `#data/am-ab-donusum`).
- **Neden VPS gerekmiyor?** Kalıcı veri kullanıcının tarayıcısında (`localStorage`), giriş/hesap yok, hesaplar istemcide. GitHub Pages yeterli. Ortak skor tablosu, hesap veya sunucu tarafında yapay zekâ eklemek istersen o zaman VPS (veya benzeri arka uç) gerekir.
- **İçerik ve kod ayrı.** Ders içeriği Python betikleriyle üretilip `docs/*.js` veri dosyalarına yazılır; arayüz bu veriyi okur.

## 2. Dosyalar (docs/)
| Dosya | Görev |
|---|---|
| `content.js` | `window.COURSE`: 30 modül, 120 ders, 4 rol. Her derste anlatım, formül, örnek, 3 alıştırma (`numeric`, `concept`, uygulama). |
| `app.js` | Ana uygulama: `render()` hash'e göre sayfayı seçer; ilerleme kaydı (`kesit-stat-v1`), dersler, kütüphane, laboratuvar, yedek indir/yükle. |
| `analysis-engine.js`, `math.js` | Sayısal çekirdek: normal/t/ki-kare dağılımları, t testleri, Wilson, ANOVA, bootstrap, MCMC… |
| `workshops.js`, `visual-learning.js`, `topic-posters.js`, `diagrams.js` | Atölyeler, 50 kavram keşfi, konu panoları ve ders grafikleri. |
| `business-*.js`, `case-teaching.js` | V6–V7 iş vakaları (depo, talep, kalite…) ve hazır senaryolar. |
| `concept-*.js`, `learning-guide.js`, `pedagogy-data.js` | V5–V8 Anla/Gör/Çöz/Dene/Aktar akışı, kavram öğretimi, terim rehberi, müfredat haritası. |
| **`ecosystem-data-v9.js`** | `window.KESIT_ECOSYSTEM`: 13 Kesit vakası. **Elle düzenlenmez**, `ecosystem_cases_v9.py` üretir. |
| **`v9-content.js`** | `window.KesitV9Content`: sık hatalar, mülakat soruları, seviye testi ders listesi, ders → SQL/DAX/Python köprüsü. Elle düzenlenir. |
| **`v9-app.js`** | `window.KesitV9`: V9 sayfaları (`#data`, `#practice`, `#mistakes`, `#interview`, `#placement`), 33 alıştırma üreticisi, ders/ana sayfa/ilerleme ekleri, kendi kaydı (`kesit-stat-v9`). |
| `v9.css` | V9 görünümü (açık/koyu tema değişkenlerini kullanır). |
| `sw.js`, `sw-register.js`, `manifest.webmanifest` | Çevrimdışı kopya: önce ağ, ağ yoksa önbellek. Sürüm değişince `CACHE` adını artır. |

### V9 app.js'e nasıl bağlanıyor?
`app.js` içindeki `render()` üç yerde V9'u çağırır: (1) `labels` nesnesine `KesitV9.labels` eklenir, (2) sayfa tablosuna `KesitV9.pages` eklenir (hash'in kalan kısmı parametre olarak gider), (3) sayfa çizildikten sonra `KesitV9.mount(page, ders)` çalışır ve ders sayfasına "Kesit ekosistemi" kutusunu, ana sayfaya "Uygula ve hazırlan" kartlarını, ilerleme sayfasına V9 istatistiklerini ekler. Yedek dosyası `{...state, v9: KesitV9.exportState()}` biçimindedir; yüklerken `v9` alanı varsa birleştirilir.

## 3. Kesit vakaları nasıl üretiliyor?
1. Kardeş depodaki CSV'ler okunur: `git clone https://github.com/ysfdurak/kesit-python` (veri `data/` altında).
2. `python ecosystem_cases_v9.py ../kesit-python/data` (pandas, numpy, scipy, statsmodels gerekir).
3. Betik her vakada hesabı yapar, Türkçe sayı biçimine çevirir (`trnum`) ve `docs/ecosystem-data-v9.js`'yi yazar.
4. `node verify-v9.cjs` vakaların eksiksiz, ders bağlantılarının geçerli ve bazı sabit sonuçların (A/B: 106/975, 150/1025, fark 3,76 puan; zamanında kalkış %60,5) değişmediğini kontrol eder.

Bir vaka şu alanlardan oluşur: `question` (karar sorusu), `unit` (analiz birimi), `predict` (önce tahmin et), `method`/`why`, `sql`/`python`/`dax`, `results` (tablo), `chart`, `read` (karar), `limits` (söyleyemedikleri), `lessons`.

**Vakalardan öğrenilecek ana dersler** (sorulursa):
- A/B dönüşüm: fark 3,8 puan, %95 aralık 0,9–6,7 → anlamlı ama alt uç küçük.
- Gelir: artışın çoğu dönüşümden; alıcı başı karşılaştırma randomizasyonu korumaz.
- Kurye puanı: korelasyon zayıf görünür (ρ = −0,20) ama 50 dakikada eşik var.
- Araç türü: bisiklet grubu yalnızca 2 kurye → sipariş sayısı yanıltıcı (kümelenme).
- Rötar: akşam oranı yüksek ama neden payları değişmiyor → rotasyon hipotezi desteklenmedi.
- No-show ve çalışma modeli: **anlamsız sonuç** örnekleri; aralıkla raporlanır.
- Maaş: ham fark %7,2, aynı seviye+bölüm %2,3 → Simpson ve aracı değişken.
- Yağmur: Poisson aşırı yayılımlı (χ²/sd ≈ 5,8) → negatif binom.
- Banka: tek IQR kuralı %11 işaretler; kategori içi ve log ölçeği gerçekçi.

## 4. Alıştırma üreticileri
`v9-app.js` içindeki `GEN` dizisinde her öğe `{id, lesson, title, group, make()}`. `make()` rastgele girdilerle `{q, answer, dec, tol?, unit, hint, steps[]}` döndürür. Cevap kontrolü göreli %0,5 veya `tol` toleransıyla yapılır; virgül ve nokta kabul edilir. İlk deneme istatistiğe sayılır, ikinci yanlışta çözüm açılır.

**Yeni üretici eklemek:** `GEN`'e bir öğe ekle, sorudaki sayıların gösterilen ondalıkla birebir aynı olmasına dikkat et (önce yuvarla, sonra hesapla), `node verify-v9.cjs` çalıştır (her üreticiyi 300 kez dener).

## 5. Sık yapılan işler
| İş | Yapılacak |
|---|---|
| Sık hata / mülakat sorusu eklemek | `docs/v9-content.js` içindeki diziye öğe ekle; `lessons` geçerli ders kimliği olmalı. |
| Bir derse SQL/DAX/Python köprüsü eklemek | `TOOLS` nesnesine `sNN: {sql, dax, py}` ekle. |
| Yeni sayfa eklemek | `v9-app.js` içinde `pages` ve `labels`'a ekle; `index.html`'deki `#nav-v9`'a bağlantı koy. |
| Yayın sonrası eski sürüm görünüyor | `sw.js` içindeki `CACHE` adını artır (ör. `kesit-istatistik-v9-2`). |
| Testleri çalıştırmak | Depo kökünde `node verify.cjs && node verify-engine.cjs && node verify-visual.cjs && node verify-quality.cjs && node verify-v9.cjs` |

## 6. Bilinen sınırlar
- Tarayıcıdaki vaka sonuçları önceden hesaplanmıştır; kodu çalıştırmak için kendi Python ortamın veya Kesit Python gerekir.
- Seviye testi mevcut derslerin kavram sorularını kullanır; yönlendirme amaçlıdır, not değildir.
- Gerçek öğrenci pilotu yapılmadı; öğrenme kazanımı ölçülmedi.
