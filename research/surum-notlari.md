# Kesit İstatistik — V5

Kesit ailesinin tipografi, renk ve gezinme düzenini koruyan Türkçe istatistik öğrenme uygulaması. Hesaplar, ilerleme ve vaka notları tarayıcıda çalışır.

## Öğretim düzeni

Dört kullanım yolu: veri analizi ve BI, veri bilimi, makine öğrenmesi, süreç ve kalite analizi. Genel iş analistliği ayrı bir istatistik uzmanlığı olarak sunulmaz. KPI, oran, örnekleme ve karşılaştırma ihtiyaçları ortak temel ve analiz yolundadır.

Her konu iş sorusu, veri üretim bağlamı, yöntem gerekçesi, çözümlü yürüyüş, yanlış yorum ve karar notuyla açılır. Mevcut 120 ders ve ilerleme kimlikleri korunur. Yeni 30 konu anlatımı, ilgili dört dersin ortak çerçevesidir; 120 bağımsız yeni anlatım olarak sayılmaz.

Görsel rehberler de konu düzeyindedir: gerçek hesap grafikleri, doğal frekans ağacı, karşılaştırmalı nokta grafikleri veya yöntem seçimini açıklayan şemalar kullanılır. Her biri bağlamı, yorum sınırını ve aynı başlangıç verisini değiştirme bağlantısını içerir. SVG olarak indirilebilir.

## Analiz atölyesi

30 rehberli çalışma: betimsel analiz, eksiklik, dağılımlar, koşullu olasılık, CLT, t ve Wilson aralıkları, güç planlama, tek/eşleştirilmiş/Welch t, ANOVA, Fisher/ki-kare, Mann–Whitney, korelasyon, regresyon/artıklar, A/B, bootstrap, permütasyon, zaman tabanları, I–MR, kuyruk, sağkalım, Beta-Bernoulli, olabilirlik, Metropolis, PCA, sınıflandırma değerlendirmesi, öğrenme/cezalandırma ve konformal aralıklar.

Çalışma akışı: önce tahmin → girdileri değiştir → hesabı ve grafiği oku → varsayım ve karar notu yaz → JSON kaydı indir. Kullanıcının değiştirdiği girdiler gerçek hesabı, grafiği ve yorumu günceller.

Yöntem sınırları ekranda açıktır: güç normal yaklaşımdır; ANOVA klasik ve post-hoc içermez; Spearman p yaklaşık referanstır; zaman çalışması ARIMA eğitmez; iki boyutlu PCA bütün gizli değişken modellerini uygulamaz; MCMC öğretim amaçlı random-walk Metropolis ve klasik split-Rhat kullanır. Sınıflandırma çalışması verilen olasılıkları değerlendirir, model eğitmez. Polinom çalışması gerçekten ayrı eğitim/test örnekleri üzerinde öğrenir. IV/IPW/RD, karma modeller ve diğer ileri aileler ilgili derslerde anlatılır; bunların hepsinin çalıştırılabilir motoru olduğu iddia edilmez.

## Üretim ve doğrulama

- `python curriculum_v3.py`: V2 temelini okuyup V3 konu/rol içeriğini yeniden üretir.
- `python make_training_data.py`: sentetik vaka CSV'lerini üretir.
- `node verify.cjs`: ders kimlikleri, 120 bağımsız sayısal soru referansı, 720 ders bölümü, tüm çalışma varsayılanları, konu SVG'leri ve eski rol/ilerleme uyumluluğu.
- `node verify-engine.cjs`: 39 sabit SciPy referansı, geçersiz girdiler, yeniden üretilebilir permütasyon, KM risk kümesi, kuyruk ve MCMC kontrolleri.
- `python scipy_reference.py`: SciPy kurulu ortamda referansları yeniler (doğrulama ortamı: SciPy 1.17.0). Üretimde Python/SciPy gerekmez.

Masaüstü tarayıcı kontrolünde dört yol, Welch girdisi değişiminin sonuç/grafik/yorum bağlantısı ve yeni konu rehberi doğrulandı. Mobil düzen CSS ile hazırlanmıştır; bu revizyonda telefon iframe denetimi önizleme bağlantı hatası nedeniyle tamamlanamadı.

## Dosyalar

`docs/analysis-engine.js` sayısal çekirdek; `workshops.js` rehberli çalışmalar; `topic-posters.js` konu panoları; `learning-v3.css` yeni öğretim düzeni; `app.js` gezinme, dersler ve ilerleme; `cases.js` açık bitirme vakaları; `vendor/` yerel Kesit fontları ve lisansları.

İlerleme ve vaka notları yereldir. Bozuk kayıtların üzerine boş durum yazılmaz. Eski rol kimlikleri dört yeni kullanım yoluna uyarlanır; ders yanıtları ve notlar korunur. Düzenli ilerleme dışa aktarımı önerilir.


## V4 — ileri derslerin uygulamaları

64 ileri ders için 16 çalıştırılmış Jupyter defteri ve eşdeğer Python betikleri eklendi. Her dersin sentetik verisi, kodu, gerçek stdout çıktısı, ayrı grafiği, yorum sınırı ve parametre değiştirme alıştırması vardır. Defterlerin tamamı `advanced_curriculum.py` ile çalıştırılarak üretildi; oluşmayan grafik veya başarısız kod üretimi durdurur. `docs/advanced-content.js` uygulamaya kod/çıktı/metin bağlantılarını, `docs/advanced/` resim ve indirmeleri sağlar. Kullanıcı kodu değiştirmek için yerel Python/Jupyter/VS Code kullanır; tarayıcı çıktıları hazır referans çalıştırmadır.

Kalman, Kish ağırlık ve 1B iki bileşenli Gaussian EM ile tarayıcı çalışmaları 33 oldu. `python verify_advanced_reference.py` NumPy/scikit-learn referanslarını yeniler; `node verify-engine.cjs` bunları JS ile karşılaştırır. EM log olabilirlik monotonluğu, üyelik aralığı ve hatalı girdiler de kontrol edilir.

İleri örnekler arasında MLE/LR, TOST, karma/kantil/Poisson/NB regresyon, çoklu atama+Rubin varyansı, VAR/Kalman, gerçek SVM/NB/LDA/QDA/kNN/ağaç/orman/boosting/MLP eğitimi, nested CV, kalibrasyon, EM/faktör/t-SNE, IPW/2SLS/RD, planlı çoklu bakış ve CUPED, sansürlü Weibull ve KDE bulunur. Birleşik başlıklardaki bütün alternatif aileler uygulanmış sayılmaz; örnekler ilgili koşulları açıkça belirtir.

Mobil tarayıcı doğrulaması V4'te de önizleme sekmesine erişim reddi nedeniyle tamamlanamadı. Bu sınır yayın kontrolünde açıkça korunur.


## V5 — karşılaştırmalı müfredat ve yönlendirme revizyonu

Seeing Theory, OpenIntro/IMS, Brilliant'ın açık açıklamaları ve ISLP karşılaştırıldı. İnceleme `research/benchmark-2026-11-08.md` ve uygulamadaki `#review` sayfasındadır. Khan konu başlıkları indeks düzeyinde değerlendirildi; ayrıntılı ders deneyimi doğrulanmadı. Bu çalışma bağımsız uzman heyeti veya gerçek kullanıcı araştırması olarak sunulmaz.

Ders sayısı 120 olarak korundu. `pedagogy_v5.py` kavrama özgü öğretim rehberini; `curriculum_depth_v5.py` otuz modülün derinleşme, tanı ve çıktı çerçevesini; `assessment_v5.py` temel kavram sorularını ve modül uygulama kontrollerini; `role_core_v5.py` ders düzeyinde rol çekirdeğini üretir. Temiz yeniden üretim sırası: `curriculum_v3.py` → `pedagogy_v5.py` → `curriculum_depth_v5.py` → `assessment_v5.py` → `role_core_v5.py`. İleri analiz dosyaları V4'ten korunur; gerektiğinde `advanced_curriculum.py` ile yeniden üretilir.

Yeni varsayılan ders akışı Anla/Gör/Çöz/Dene/Aktar. Eski araçlar ayrıntı menüsünde korunur. Başlangıç merdiveni, not vermeyen başlangıç kontrolü, ön koşula dönüş, örnekli terim/sembol araması ve açık sonraki adım vardır. Öğrenme görünümü tercihi ayrı `kesit-stat-learning-v5` kaydındadır; bozuk tercih kaydının üzerine yazılmaz. Eski `kesit-stat-v1` başarı ve vaka notları korunur. Eski cevapların korunması, yenilenmiş soru sürümünde tekrar yanıtlandığı anlamına gelmez.

`docs/visual-learning.js` 50 kavram keşfi sağlar: örnekleme, tür/eksik/grafik okuma, merkez/yayılım/ağırlık, olasılık, kapsama/CLT/güç, etki/çoklu kontrol, karşılaştırma/regresyon, 2×2 etkileşim, sınıflandırma, Bayes/yeniden örnekleme, zaman/PCA/öğrenme, ölçüm ve sağkalım. Hesap modeli ve kapsam sınırları görünürdür. Görseller etkileşimle değişir; büyütme iletişim kutusu dar ekranda ayrıntı okumayı sağlar. Aynı kavramın ilişkili derslerde kullanıldığı açıkça belirtilir; 120 farklı yeni simülasyon iddiası yoktur.

`node verify.cjs`: mevcut dersler, eski kayıt uyumu, 600 rehber adımı ve yeni rehber/terim/müfredat/inceleme sayfaları. `node verify-visual.cjs`: 50 keşfin üç ayarı, kapsama/yanlılık kontrolleri ve bağımsız fixture karşılaştırmaları. `python verify_visual_reference.py` fixture'ları yeniler. `node verify-engine.cjs` V3/V4 çekirdek karşılaştırmalarını korur.

Tarayıcıda masaüstü ile 390 px iframe genişliğinde başlangıç/ders, canlı ayar ve yanlış cevaptan çözüme dönüş doğrulandı. Görülen sayfalarda yatay taşma yoktu. Gerçek cihaz ve öğrenci pilotu yapılmadı; bütün ekran/bütün tarayıcı kombinasyonlarının doğrulandığı iddia edilmez.

## V6 — İş sorusundan karar notuna

Analiz girişinde kullanıcı rolüne uygun iş problemini seçer; kavramı gör alanı öğrenme desteği olarak ayrıca açıklanır. Her modüle iş bağlamı eklenmiştir. Yedi vaka (toplama yöntemi, eşli model karşılaştırması, paketleme/posthoc, talep/SARIMA, Gage R&R, süreç kontrolü, gecikme sınıflandırması) iki önceden çalıştırılmış senaryo içerir. Tüm veri sentetiktir; gerçek bir şirketin gözlemi/başarısı olarak sunulmaz. Bağımsız birim, yöntem alternatifi, varsayım, gerçek hesap, grafik, yorum sınırı, iki gerekçeli kontrol ve cihazda saklanan karar notu vardır.

Tarayıcıdaki vaka senaryoları hazır çalıştırılmış çıktılardır. Yeniden üretim için CSV, Python ve çıktılı ipynb sunulur; CSV düzenlemek defter girdisini otomatik değiştirmez. Tarayıcı hesaplayıcıları ayrı olarak çalışır; tam McNemar eklendi. s27/s28/s39/s49/s51 dersleri posthoc, eşli kategorik test, zaman bölmesi/tahmin, kontrol grafiği ve çapraz ölçüm varyansı yönünden derinleştirildi. Mevcut 120 ders kimliği ve kullanıcı ilerlemesi korunur.

Üretim: V5 içerik üretim sırasından sonra `python curriculum_v6.py` (bir kez, V5 üzerine), `python business_contexts_v6.py`, `python business_cases_v6.py`. Son komut 14 analizi yürütür, gerçek çıktıları ve defterleri yazar. V6 overlay aynı V5 tabanına uygulanmalıdır; aynı dosyaya tekrar uygulamak açıklamayı çoğaltır.

Doğrulama: `node verify.cjs`, `node verify-engine.cjs`, `node verify-visual.cjs`, `python verify_business_v6.py`. Games–Howell sonuçları bağımsız SciPy `tukey_hsd(equal_var=False)` ile; ölçüm ANOVA kareler toplamları statsmodels OLS ile; McNemar binom referansıyla karşılaştırılır. Eğitim/seçim/final sınırları ve referans/izleme ayrımı doğrulanır. 390px çerçevede vaka/çözüm yatay sayfa taşması olmadan incelendi. Bu kontroller gerçek öğrenci pilotu veya bağımsız uzman heyeti onayı değildir.

## V7 · İş kararları ve ders sonu görselleri

Yedi yeni iş vakası eklenir. KPI bileşimi ve açık teslim, tabakalı sayım ve cevapsız adres, A/B kazanım ve şikayet sınırı, kapasite regresyonu ve pik yük, WMS pilotu ve ön eğilim, gecikme modeli izleme ve stok kantili ayrı veri ve karar sorularına sahiptir. Toplam 14 vaka ve 28 hazır analiz senaryosu bulunur.

Dört rol için doğrudan kullanım alanlarına göre sıralanmış ilk vaka ve seçki gösterilir. Yeni vakalarda sayısal alıştırma ve ipucu çözümden önce açılır. Çözümde karar panosu, gerçek hesap grafiği, yöntem koşulları ve öz değerlendirme ölçütleri yer alır. 16 mevcut dersin Çöz adımına hesaplı iş örneği, Görsel özet adımına vakadan bir grafik ile yorum eklendi.

İş verileri sentetiktir. V7 betikleri kendi verilerini yeniden üretir. İndirilebilir CSV, çalıştırılmış defter ve betikler yeni vaka paketinde birlikte yer alır. V7 Python bağımlılıkları ayrı requirements dosyasındadır.

Üretim: V6 içerik sırasından sonra `python curriculum_v7.py` ve `python business_cases_v7.py`. Doğrulama: `node verify.cjs`, `node verify-engine.cjs`, `node verify-visual.cjs`, `python verify_business_v7.py`. Python kontrolü karşılaştırma için scikit-learn kullanır. Model eğitimi ve çözüm grafikleri önceden yürütülür. Gerçek kullanıcılarla öğrenme başarısı ölçülmemiştir.

## V8 · Kavram öğretimi ve müfredat kapsamı

22 mevcut derste tahmin sorusu, seçeneğe özel geri bildirim, kavramın açıklaması, aynı veriden adımlı çözüm ve farklı kontrol sorusu yer alır. Gör adımı dersin veri tablosunu veya sayısal şeridini gösterir ve mevcut canlı keşfe bağlar. Ders sonu panosu yazdırılabilir. Bu kavram yanıtları oturum içinde tutulur. Mevcut ders puanları ve notların kaydı ayrı devam eder.

Sekiz seçmeli yöntem dersi eklenmiştir: deneyde oran metrikleri, küme randomizasyonu, kategorik ölçüm uyumu, Cox modeli, rakip riskler, fazla sıfırlı sayımlar, kesirli faktöriyel ve kesikli talep. Kütüphane araması, ön koşul dersleri ve kazanım haritası bu derslere bağlanır. Her ders elde çözülmüş örnek ve iki yorum kontrolü içerir.

Müfredat haritası 30 modül ve 120 mevcut dersi sekiz alanda bir kez sayar. Yenilenen kavram akışı mevcut derslerin alt kümesidir. Seçmeli dersler ayrıca sayılır. Rol çekirdekleri ortak dersler içerebilir. Vaka ve görsel sayıları ders toplamına dahil edilmez.

Doğrulama: `node verify.cjs`, `node verify-engine.cjs`, `node verify-visual.cjs`. Öğrenme kazanımı gerçek kullanıcı pilotunda ölçülmemiştir.

## V9 · Kesit ekosistemi, alıştırma atölyesi ve hazırlık

Değerlendirme: [degerlendirme-v9.md](degerlendirme-v9.md). Mimari ve üretim: [NASIL.md](../NASIL.md).

- **Kesit verileriyle 13 vaka.** Kesit SQL, Power BI ve Python'un ortak veri setlerinde (Anadolu Market, Lezzet Kurye, Kanat Havayolları, Pusula İK, Pedal İzmir, Ilgaz Bank): iki oran testi, Welch + bootstrap, yüzdelik tabanlı söz, eşik etkisi, Kruskal–Wallis ve kümelenme, Wilson aralıkları, ki-kare + Cramér V ve mekanizma sınaması, anlamsız sonucun raporlanması, log maaş regresyonu, eşli bootstrap, Poisson/negatif binom ve log ölçekte robust aykırı değer. Her vaka: tahmin → yöntem → SQL/Python/DAX → sonuç ve grafik → karar → sınırlar → ilgili dersler ve karar notu. Sayılar `python ecosystem_cases_v9.py <kesit-python/data>` ile üretilir.
- **Alıştırma atölyesi.** 33 parametreli soru türü (temel, orta, ileri); formül ipucu, adımlı çözüm, ilk deneme istatistiği, zayıf konular ve karışık 10 soruluk set.
- **Seviye testi** (15 kavram sorusu, karıştırılmış seçenekler, başlangıç önerisi), **32 sık hata**, **48 rol bazlı mülakat sorusu** (yalnız istatistik).
- **Ders köprüsü.** 29 derste SQL/DAX/Python karşılığı; ilgili Kesit vakası, alıştırma ve sık hata bağlantıları.
- **Kullanım.** Menüde "Uygula ve hazırlan" grubu, ana sayfa kartları, ilerleme sayfasında V9 istatistikleri; yedek dosyası V9 kayıtlarını da taşır (`kesit-stat-v9`). Sorun bildir bağlantısı, favicon, manifest ve çevrimdışı önbellek (önce ağ).
- **Doğrulama.** `node verify-v9.cjs`: vaka bütünlüğü ve sabit referanslar, her üretici × 300 deneme, içerik–ders bağlantıları, menü ve önbellek listesi. Masaüstü (1366 px) ve 390 px genişlikte yatay taşma olmadan tarayıcıda denendi; açık ve koyu tema kontrol edildi. Gerçek kullanıcı pilotu yapılmadı.
