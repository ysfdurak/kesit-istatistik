# Kesit İstatistik · Proje rehberi (hâkimiyet dokümanı)

> Bu belge projeye bakıp her şeyi görebilmen, mülakatta yardımsız anlatabilmen ve güvenle değişiklik yapabilmen için yazıldı. Dosya dosya teknik tarif [NASIL.md](NASIL.md)'dedir; burası **neden**, **içeride gerçekte ne oluyor** ve **hangi karar neye yol açtı** sorularını cevaplar. Ortak altyapı (GitHub, Pages, lisans, güvenlik) diğer Kesit projeleriyle aynıdır.
>
> Uyarı işaretleri: **⚠ Şöyle daha iyi olur** (öneri, karar değil) · **🧪 Burada bir test daha yapalım** (doğrulanmamış ya da riskli) · **[doğrulanacak]** (kanıtı yok).

## 1. Bir bakışta

| | |
|---|---|
| Ne | Sıfırdan ileri seviyeye Türkçe istatistik eğitimi: 30 modül, 120 ders, alıştırma, vaka, mülakat |
| Kimin için | Veri analisti/BI, veri bilimi, ML, süreç-kalite yolunda ilerleyen; özellikle iş hayatında istatistiği karar için kullanacak kişi |
| Canlı | https://ysfdurak.github.io/kesit-istatistik/ (uygulama `docs/` altında) |
| Depo | `ysfdurak/kesit-istatistik` (tek dal `main`; kaynak ve yayın aynı yerde) |
| Durum | V9 + V10 (Kasım 2026). Gerçek öğrenci pilotu yapılmadı |
| Sunucu | Yok. GitHub Pages; ilerleme tarayıcıda (`localStorage`) |

## 2. Sorun ve kararlar (mülakatın asıl konusu)

**Sorun.** İstatistik dersleri ya formül ezberletir ya da oyuncak veriyle (10 sayı) çalışır. İş hayatında karşılaşılan şey ise binlerce satırlık, eksikli, çarpık veridir ve sorulan soru "p kaç" değil "ne karar vereyim"dir.

| Karar | Neden | Sonucu |
|---|---|---|
| Statik site, sunucu yok | Hesap/giriş gerekmiyor; her hesap tarayıcıda yapılabilir | Barındırma ücretsiz, bakım yok; ama ortak skor tablosu, öğretmen paneli yapılamaz (yapılacaksa VPS gerekir) |
| İçerik Python betiklerinden üretilir | Formül ve sonuçların SciPy/statsmodels ile aynı olması gerekiyor | `docs/*.js` veri dosyaları elle düzenlenmez; değişiklik betikte yapılır |
| Kardeş Kesit uygulamalarıyla **aynı veri** | SQL'de sorguladığın tabloyu Power BI'da raporlayıp burada test edersin | Vakalar ve V10 görevleri gerçek boyutlu kurgusal veride; veri değişirse iki betik yeniden çalıştırılır |
| Her derste 3 kontrollü uygulamalı görev (V10) | Önceki sürümde derslerin uygulaması rastgele sayılı üreticilerle sınırlıydı; "gerçek veride yapabiliyor muyum?" sorusu cevapsızdı | 360 görev, aynı kod defterde ve Excel'de |
| Tek doğruluk kaynağı: görev kodu | Cevap elle yazılırsa kod, defter ve uygulama birbirinden kopar | Cevap = `exec(kod)`; defterdeki kod aynı metin, `assert` aynı cevabı denetler |

## 3. Mimari ve veri akışı

```
kesit-python/data/*.csv ──► alistirma_v10.py ──┬──► docs/data/kesit/*.csv + kesit-veri.zip
 (kardeş depo, ortak veri)     (görev kodlarını  ├──► docs/ders-alistirma.js  (window.KESIT_DERS_ALISTIRMA)
                                çalıştırır)      ├──► docs/defter/sNN.ipynb · sNN.py · kesit-defterler.zip
                                                 └──► docs/excel/modul-NN.xlsx

docs/index.html ─ content.js … v9-app.js ─ ders-alistirma.js ─ v10-alistirma.js ─ app.js
                                    │                                │             │
                              KesitV9.mount ◄──── sarılır ───────────┘   render() her çizimde mount çağırır
                                    └─► ders sayfasına "Kesit verisiyle hesapla" paneli
```

**İçeride gerçekte ne oluyor (bir görev denetlenirken):**
1. Kullanıcı `#lesson/s05` açar → `app.js` `render()` dersi çizer → `KesitV9.mount('lesson', ders)` çağrılır.
2. `v10-alistirma.js` bu fonksiyonu yüklenirken sarmıştı: önce V9'un işi (araç köprüsü kutusu), sonra panel ders sütununa, köprünün önüne eklenir.
3. Kullanıcı "37,74" yazar → `sayi()` Türkçe/İngilizce biçimi çözer (0,123 · 1.234,5 · 1,234.5; tek nokta ondalıktır) → `|v − cevap| ≤ tolerans` → sonuç `kesit-istatistik-v10` anahtarına yazılır.
4. İlerleme dosyası indirilirken V9'un `exportState`'i de sarıldığı için V10 kayıtları `v9.v10` altında yedeğe girer; yüklenirken birleştirilir (doğru çözülmüş görev geri "çözülmemiş"e düşmez).

## 4. Teknoloji seçimleri

| Seçim | Neden | Elenen alternatif |
|---|---|---|
| Düz HTML/CSS/JS | Derleme yok, Pages'te doğrudan çalışır | React/Vite: 120 statik ders için gereksiz katman |
| Cevaplar önceden hesaplanır, tarayıcıda Python yok | 360 görev için Pyodide (~10 MB) yüklemek ilk açılışı yavaşlatır; görev cevabı sabit | Tarayıcıda Pyodide: Kesit Python'da var, burada değer/maliyet düşük |
| openpyxl ile Excel, formül İngilizce yazılır | Excel formülü dosyada her zaman İngilizce saklanır, Türkçe Excel `EĞER/MUTLAK` olarak gösterir | Formülü Türkçe yazmak: dosya bozulur |
| Excel kitabı **modül başına** | Her ders için kitap 120 dosya × veri sayfaları = çok büyük; modül 4 dersi bir arada verir | Tek dev kitap: 1 milyon satır sınırına ve 100+ MB'a yaklaşır |
| `bk_gunluk.csv` türetildi | 9 MB'lık yolculuk tablosu yerine günlük özet (92 satır) zaman serisi derslerine yeter | Ham yolculuk tablosu: veri paketi 10 kat büyürdü |

## 5. Kod turu

**`alistirma_v10.py`** (kök, ~640 satır)
- Üstte veri kopyalama ve `bk_gunluk` türetme. Sonra `HAZIRLIK`: defterin ilk hücresi de olan yükleme kodu. Türetilmiş sütunlar burada: `items.tutar`, `flights.gecikme` (dakika), `lk.sure` (dakika); kısayollar `teslim`, `inen`.
- `G('s21', soru, kod, d, ipucu, tol)`: bir görev. `kod` mutlaka `cevap = …` atar. Örnek:
  ```python
  G('s30', 'Basit regresyon: … Eğim b (1 °C başına yolculuk, 3 basamak)',
    'cevap = smf.ols("yolculuk ~ sicaklik", gunluk).fit().params["sicaklik"]', 3)
  ```
- "hesapla" bölümü her kodu `exec` eder; sonlu olmayan sonuç, görevsiz ders ya da 3'ten az görevli ders betiği durdurur.
- Ardından JS, veri zip'i, defterler, Excel kitapları yazılır. `tolerans()` üç çıktıda da aynı kural.

**`docs/v10-alistirma.js`** (~120 satır)
- `panel(id)`: HTML üretir. Soru metninde yalnız `<b>` serbest, gerisi `esc()` ile kaçışlanır (XSS koruması; CSP'ye ek kat).
- `sayi()`: Türkçe ondalık kuralları. **Ders:** ilk sürümde "0.123" binlik ayırıcı sanılıp 123 okunuyordu; `verify-v10.cjs` örnek tablosu yakaladı.
- Yanlış cevapta iki akıllı ipucu: değer 100 kat büyükse "oran istiyor olabilir", 100 kat küçükse "yüzde istiyor".
- `V9.mount` sarma: app.js'e dokunmadan yeni ekran eklemenin yolu. **Bu yapı neden iyi:** V9 da aynı yöntemle app.js'e bağlanmıştı; V10 V9'u değiştirmez, üstüne katman ekler.

**`verify-v10.cjs`**: yapı (her derste ≥3 görev, benzersiz kimlik, sonlu cevap, defter hücre sayısı, Excel dosyası), betik sırası ve service worker listesi, `sayi()` örnekleri ve her görevde "yuvarlanmış doğru cevap kabul edilir mi, tolerans çok geniş mi".

## 6. Yayın

Pages `main` kökünden yayınlar; kökteki `index.html` `docs/`'a yönlendirir. Yeni dosya eklendiğinde `docs/sw.js` içindeki `CACHE` adı artırılır (V10: `kesit-istatistik-v10-1`) ve dosya `CORE` listesine yazılır; yoksa eski ziyaretçi önbellekten eski sürümü görür. Excel ve defterler `CORE`'da değil: ilk indirildiklerinde önbelleğe girerler (40 MB'ı herkese zorla indirmemek için).

## 7. Testler

Tam liste: `node verify.cjs && node verify-engine.cjs && node verify-vaka.cjs && node verify-visual.cjs && node verify-quality.cjs && node verify-v9.cjs && node verify-v10.cjs` (CI her gönderimde çalıştırır).

V10 örneklem testi (27 Kasım 2026):

| Adım | Beklenen | Gözlenen | Durum |
|---|---|---|---|
| 120 defterin `.py` sürümü veri klasöründe çalıştırıldı | Tüm `assert`ler geçer | 120/120 (ilk denemede 2 defter `math` eksikti, hazırlığa eklendi) | ✓ |
| Modül 6 kitabı: yarı satıra doğru (yuvarlanmış), yarısına yanlış cevap, LibreOffice ile yeniden hesap | Doğru / Tekrar dene sırayla | Beklendiği gibi | ✓ |
| 390 ve 1350 px, `#lesson/s05`: doğru cevap virgülle + Enter, yanlış cevap, çözümü göster | Yeşil, "Tekrar dene", kod açılır; yatay taşma yok, konsol hatası yok | Beklendiği gibi; ilerleme 1/3 | ✓ |
| `#lesson/s120` → Excel bağlantısı `modul-30.xlsx`; tüm indirme adresleri 200 | | | ✓ |

🧪 **Burada bir test daha yapalım:** Excel kitabını gerçek Microsoft Excel'de (Türkçe) aç: formül `EĞER/MUTLAK` olarak görünmeli, Kontrol sütunu hesaplanmalı. LibreOffice ile denendi, Excel ile denenmedi **[doğrulanacak]**.
🧪 Defterleri Jupyter'de (Windows) aç, `kesit/` klasörü yanındayken baştan sona çalıştır **[doğrulanacak]**.

## 8. Bilinen sınırlar ve sonraki adımlar
- Cevaplar sabittir: kesit-python verisi değişirse `alistirma_v10.py` yeniden çalıştırılmalı; CI bunu yapmaz.
- Rastgelelik içeren görevler (bootstrap, MCMC, orman, boosting, MLP) tohumla sabitlendi ve ek tolerans aldı; farklı NumPy/scikit-learn sürümünde sonuç kayabilir.
- Bazı görevler sadeleştirme içerir (ör. "regresyon süreksizliği" görevinde gerçek bir kesme kuralı yok, sezgi amaçlı). Soru metni bunu söylüyor.
- Excel dosyaları her üretimde ikilik olarak değişir (zip içi zaman damgası) → gereksiz git farkı. ⚠ **Şöyle daha iyi olur:** zip girişlerini sabit tarihle yeniden yazan küçük bir son adım.
- ⚠ **Şöyle daha iyi olur:** Excel kitapları ~24 MB depoya ekledi. Büyürse GitHub Releases'e taşınabilir, uygulama oradan bağlar.
- ⚠ Paneldeki görevler uzun derslerde sayfanın altında kalıyor; ders içindeki "Alıştırmalar" sekmesine kısayol eklenebilir.

## 9. Mülakat soruları ve cevapları
1. **"Cevapların doğru olduğunu nasıl biliyorsun?"** Cevabı ben yazmadım: her görevin kodu çalıştırılıyor ve sonuç cevap oluyor. Aynı kod defterde `assert` ile tekrar çalışıyor; 120 defter temiz geçti. Kodun kendisinin doğru yöntemi seçtiğini ise ders içeriği ve SciPy referans taraması güvenceye alıyor.
2. **"Tolerans neden göreli %0,5?"** Öğrenci sonucu 2-3 basamakla yazar; mutlak tek bir eşik 0,0012 ile 1228 için aynı anda doğru olamaz. Göreli pay + son basamağın yarısı, yuvarlanmış doğru cevabı her zaman kabul eder (test bunu 360 görevde denetliyor).
3. **"Uygulamaya yeni ekranı app.js'i değiştirmeden nasıl ekledin?"** `KesitV9.mount` fonksiyonunu sardım (decorator mantığı): önce eskisi çalışır, sonra benim panelim eklenir. Yükleme sırası önemli: v10 betiği v9'dan sonra, app.js'ten önce.
4. **"Neden tarayıcıda Python çalıştırmadın?"** Cevaplar değişmiyor; çalıştırma maliyetini (10 MB, birkaç saniye) her ziyaretçiye ödetmek yerine bir kez üretim sırasında ödüyorum. Kodu çalıştırmak isteyen defteri indiriyor.
5. **"Görev yazarken neye dikkat ettin?"** Cevabı 0 ya da tahmin edilebilir olan görevleri ayıkladım (ilk taramada 5 tane çıktı: ADF p ≈ 0, TOST p ≈ 0, mod = 0 …), soruyu istatistiği ya da bir sayıyı soracak biçimde yeniden yazdım.
6. **"Excel'de kontrolü nasıl yaptın, cevap dosyada görünmüyor mu?"** Görünüyor: formülün içinde. Bu bir sınav değil öğrenme aracı; amaç öğrencinin kendini denetlemesi. Sınav olsaydı cevap dosyaya konmazdı.

## 10. Kendini test et
<details><summary>Bir görevin cevabını değiştirmek istiyorum. Hangi dosyayı düzenlerim?</summary>`alistirma_v10.py` içindeki görevin `kod`unu; sonra betiği çalıştır. `ders-alistirma.js` elle düzenlenmez.</details>
<details><summary>Yeni bir dosyayı docs/'a ekledim, eski ziyaretçi görmüyor. Neden?</summary>Service worker önbelleği. `sw.js` içinde `CACHE` adını artır, dosyayı `CORE`'a ekle.</details>
<details><summary>"0.123" yazan öğrenci neden yanlış sayılıyordu?</summary>Binlik ayırıcı kuralı tek noktayı da yakalıyordu. Artık binlik için ya iki grup (1.234.567) ya da virgüllü ondalık (1.234,5) gerekiyor.</details>
<details><summary>Excel kitabı numarası ile `l.module` neden farklı?</summary>`content.js`'te modül 0'dan başlar, ekranda +1 gösterilir; dosya adı ekrandaki numarayı kullanır.</details>

## 11. Elle yapılacak alıştırma
1. `alistirma_v10.py`'de `s05` görevlerinden birinin altına kendi görevini ekle: "Teslim süresinin 75. yüzdeliği (dakika, 2 basamak)" → `cevap = teslim.sure.quantile(.75)`.
2. `python alistirma_v10.py ../kesit-python/data` ve `node verify-v10.cjs` çalıştır.
3. `python3 -m http.server 8000 --directory docs` ile aç, `#lesson/s05`'te 4. görevi çöz.

**5 dakikalık demo akışı:** ana sayfa → bir öğrenme yolu → ders 30 (regresyon) → "Kesit verisiyle hesapla": eğimi yanlış yaz, ipucu, doğru yaz → çözümü göster (kod) → defteri indir → Excel kitabını göster (Kontrol sütunu) → "aynı veri Kesit SQL'de de var" diye ekosistem menüsü.

## 12. Değişiklik günlüğü
- **2026-11-27 · V10:** her derse Kesit verisiyle 3 görev (360), ders defterleri (.ipynb/.py), 30 modül Excel kitabı, veri paketi, `verify-v10.cjs` ve CI adımı, bu rehber.
- 2026-11-23 · Depo vakası karar ve değerlendirme kuralları.
- 2026-11-17 · Lisans: PolyForm Shield 1.0.0.
- 2026-11-15 · İngilizce tanıtım turu.
- 2026-11-10 · V9: Kesit ekosistemi vakaları, alıştırma atölyesi, seviye testi, sık hatalar, mülakat.
