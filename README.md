# Kesit İstatistik

**Sıfırdan ileri seviyeye Türkçe istatistik eğitimi. Kurulum yok, hesap yok.** Formülden önce veriyi görürsün; hesabı adım adım takip eder, sonucu bir iş kararına ve o kararın sınırlarına çevirirsin.

**Dene:** https://ysfdurak.github.io/kesit-istatistik/

![Karşılama ekranı](ekran/karsilama.png)

## Neler var?
- **30 modülde 120 ders ve 8 seçmeli yöntem dersi.** Evren ve örneklemden başlar; testler, regresyon, deney, zaman serileri, Bayes, kalite, istatistiksel öğrenme ve nedensel çıkarıma uzanır. Temel, Orta ve İleri seviyeler.
- **4 öğrenme yolu:** veri analizi ve BI, veri bilimi, makine öğrenmesi, süreç ve kalite analizi.
- **Kesit verileriyle 13 vaka (V9):** Kesit SQL, Power BI ve Python'daki ortak kurgusal veri setlerinde (Anadolu Market, Lezzet Kurye, Kanat Havayolları, Pusula İK, Pedal İzmir, Ilgaz Bank) istatistik soruları. Her vakada tahmin, yöntem seçimi, **SQL + Python + DAX** kodu, gerçek veriden hesaplanmış sonuç, grafik, karar ve sınırlar.
- **Alıştırma atölyesi (V9):** 33 soru türü her açılışta yeni sayılar üretir; formül ipucu, adım adım çözüm, zayıf konular listesi ve karışık 10 soruluk setler.
- **Seviye testi, 32 sık hata ve 48 mülakat sorusu (V9).** Mülakat soruları yalnızca istatistik ve role göre; güçlü cevabın unsurları, zayıf cevap örneği ve takip sorusu.
- 34 tarayıcı atölyesi, 14 iş vakası, 28 hazır analiz senaryosu, 50 kavram keşfi, konu panoları ve indirilebilir Python defterleri.

| Kesit verisiyle vaka | Alıştırma atölyesi | Ders ve araç köprüsü |
|---|---|---|
| ![](ekran/vaka.png) | ![](ekran/alistirma.png) | ![](ekran/ders.png) |

## Kesit ekosistemi
Aynı mantıkla hazırlanmış kardeş eğitimler: **[Kesit SQL](https://ysfdurak.github.io/kesit-sql/)**, **[Kesit Power BI](https://ysfdurak.github.io/kesit-powerbi/)** ve **[Kesit Python](https://ysfdurak.github.io/kesit-python/)**. Önerilen akış: SQL ile veriyi hazırla → Python ile test et → Power BI ile raporla → istatistikle yorumla. Kesit İstatistik'teki vakalar, kardeş uygulamalardaki CSV'lerin aynısını kullanır; Python kodları veriyi doğrudan [kesit-python](https://github.com/ysfdurak/kesit-python/tree/main/data) deposundan okur. İlgili derslerin sonunda ayrıca o kavramın SQL, DAX ve Python karşılığı bulunur.

## Nasıl çalışıyor?
- Sunucu yok: HTML, CSS ve JavaScript; hesaplar tarayıcıda çalışır. Ders içi hesaplayıcılar SciPy referanslarıyla, vaka sonuçları pandas/scipy/statsmodels ile üretilir ve otomatik denetimlerle karşılaştırılır.
- İlerleme yalnızca kullanıcının tarayıcısında saklanır; **İlerlemem** sayfasından dosyaya kaydedilip başka cihazda birleştirilerek yüklenebilir (alıştırma, vaka ve mülakat kayıtları dahil). Kişisel veri toplanmaz.
- İlk ziyaretten sonra service worker dosyaları önbelleğe alır; internet yokken son kopya açılır. Yazı tipleri siteyle birlikte sunulur.


## İngilizce tanıtım turu
Arayüz Türkçe kalır. İngilizce okuyan ziyaretçi için adresin sonuna `?lang=en` eklenir ([https://ysfdurak.github.io/kesit-istatistik/?lang=en](https://ysfdurak.github.io/kesit-istatistik/?lang=en)): her ekranı anlatan bir rehber paneli ve menü/başlıklarda İngilizce karşılıklar açılır; `?lang=tr` kapatır. Ayrıntı: [INGILIZCE-TUR.md](INGILIZCE-TUR.md).
## Kendi bilgisayarında açma
```sh
python3 -m http.server 8000 --bind 127.0.0.1 --directory docs
```
Sonra [127.0.0.1:8000](http://127.0.0.1:8000/) adresini aç. Windows'ta `py -m http.server ...`.

## Kaynak, üretim ve denetim
- Yayınlanan uygulama `docs/` klasöründedir. GitHub Pages `main` dalının kökünden yayınlar; kökteki `index.html` adresteki `#…` bölümünü koruyarak `docs/`'a yönlendirir (ör. `/kesit-istatistik/#path/analist`). Ayarlar → Pages'te kaynak `/docs` seçilirse yönlendirmeye gerek kalmaz; ikisi de çalışır.
- Kök dizindeki Python betikleri içerik ve referans üretir. Yapı, dosyaların görevi ve yeniden üretim sırası: **[NASIL.md](NASIL.md)**.
- Denetim: `node verify.cjs`, `node verify-engine.cjs`, `node verify-visual.cjs`, `node verify-quality.cjs`, `node verify-v9.cjs`. GitHub Actions her değişiklikte hepsini çalıştırır.
- [Sürüm notları](research/surum-notlari.md) · [V9 değerlendirme raporu](research/degerlendirme-v9.md)

## Yapay zekâ kullanımı
Ürün kararlarını, hedef kitleyi ve kapsamı Yusuf Durak belirledi; kod ve içerik yapay zekâ (Claude) ile geliştirildi ve otomatik denetimlerden geçirildi. Gerçek öğrenci pilotu veya bağımsız uzman incelemesi yapılmadı.

## Geri bildirim
Hata ve önerileri bu deponun [Issues](https://github.com/ysfdurak/kesit-istatistik/issues) sayfasına yazabilirsin; uygulamanın alt bilgisindeki **Sorun bildir** bağlantısı da oraya açılır.

## English

**Kesit Statistics** (Kesit İstatistik) teaches statistics from scratch to advanced level, in Turkish, in the browser: no install, no account. You see the data before the formula, follow each calculation step by step and turn the result into a business decision and its limits.

- 120 lessons in 30 modules plus 8 elective method lessons, from population and sample to tests, regression, experiments, time series, Bayes, quality, statistical learning and causal inference.
- 13 cases on the fictional datasets shared with Kesit SQL, Power BI and Python, each with a method choice, SQL + Python + DAX code, a result computed from the data, a chart, a decision and its limits.
- A practice workshop with 33 question types that generate new numbers each time, a placement test, 32 common mistakes and 48 interview questions.
- Progress stays in the browser and can be backed up to a file.

The interface and lessons are in Turkish. Add `?lang=en` to the address ([ysfdurak.github.io/kesit-istatistik/?lang=en](https://ysfdurak.github.io/kesit-istatistik/?lang=en)) for an English guide that explains each screen.

Try it: https://ysfdurak.github.io/kesit-istatistik/ · Sister apps: [SQL](https://github.com/ysfdurak/kesit-sql), [Power BI](https://github.com/ysfdurak/kesit-powerbi), [Python](https://github.com/ysfdurak/kesit-python).

## Sorumluluk notu
Ücretsiz, ticari olmayan bir eğitim ve portföy projesidir; içerik “olduğu gibi” sunulur. Veri setlerindeki tüm şirketler, kişiler ve kayıtlar hayalidir.

## Lisans
- Uygulama kodu: [PolyForm Shield 1.0.0](LICENSE.md). Kişiler, okullar ve şirketler kendi işlerinde ücretsiz kullanabilir; satmak ya da rakip ürün yapmak yazılı izin gerektirir.
- Ders içerikleri ve veri setleri: kodla aynı lisans, [PolyForm Shield 1.0.0](LICENSE.md) (özet: [LICENSE-ICERIK.md](LICENSE-ICERIK.md))
- Yazı tipleri: Bricolage Grotesque, IBM Plex Sans, JetBrains Mono (SIL Open Font License; metinler `docs/vendor/fonts/` içinde)

Kurumunuzda kullanıyorsanız haber verirseniz sevinirim: kurulumda yardımcı olabilir, kurumunuza özel ihtiyaçları birlikte değerlendirebiliriz. İletişim: iletisim@ysfdurak.com

**English:** the app code is released under [PolyForm Shield 1.0.0](LICENSE.md): individuals, schools and companies may use, change and self-host the app and its content for free; selling them or offering a competing product needs written permission. Lesson content and datasets are under the same licence. Contact: contact@ysfdurak.com
