# Kesit İstatistik — müfredat ve öğrenme deneyimi incelemesi

İnceleme tarihi: 8 Kasım 2026. Bu çalışma istatistik editörü, veri/ML/süreç uygulayıcısı ve yeni başlayan öğrenen bakışlarıyla yapılan tasarım değerlendirmesidir; gerçek kişilerle kullanılabilirlik testi veya bağımsız uzman onayı değildir.

## Karşılaştırmanın sınırı

Kaynakların herkese açık müfredat ve açıklama sayfaları incelendi. Brilliant'ın oturum gerektiren dersleri ve kişiselleştirme sistemi denenmedi; pazarlama iddiaları doğrulanmış öğrenme etkisi gibi kabul edilmedi. Khan Academy konu listesi arama indeksinde görüldü; doğrudan sayfa okunamadığı için ayrıntılı etkileşim değerlendirmesine dahil edilmedi. Seeing Theory arşivlenmiş bir kaynaktır. Puan veya öğrenme başarısı sıralaması yapılmadı.

| Kaynak | Gözlenen yaklaşım | Kesit'teki somut açık | Uygulanan yön |
|---|---|---|---|
| Seeing Theory | Altı bölüm; olasılık, dağılım, çıkarım, Bayes ve regresyon. Güven aralığında n/güven düzeyi ve tekrar örnekleme; bootstrap'te yeniden çekim. | Statik grafikler kavramın mekanizmasını yeterince göstermiyor. | Değiştirilebilir görsel keşifler; özellikle kapsama, taban oranı, örnekleme ve yeniden örnekleme. |
| OpenIntro Statistics | Veri tanıma, hedefler, örnekleme/deney, açıklayıcı grafikler, alıştırmalar ve ham veri bağlantıları. | Ders hedefleri zaman zaman soru cümlesi; veri birimi ve grafik okuma yönlendirmesi dağınık. | Gözlenebilir kazanım, veri bağlamı, yorum ve kontrol sorusu ayrı gösteriliyor. |
| Introduction to Modern Statistics | Erken çok değişkenli düşünme; önce simülasyonla çıkarım, ardından CLT yaklaşımı; rehberli öğretici ve analiz vakaları. | İleri modeller erken görünüyor; sayısal formülle kavramsal simülasyon sırası ters. | Ortak başlangıç merdiveni; sezgi ve görselden formalizme ilerleme; çekirdek/uzmanlık ayrımı. |
| Brilliant | Kamuya açık sayfada adımlı problem çözme, anlık geri bildirim ve başlangıç düzeyine göre öneri. Konular: görsel keşif, olasılık, regresyon, sınıflandırma. | Bir ekranda çok uzun metin ve çok sayıda seçenek; sonraki eylem belirsiz. | Beş adımlı ders akışı; yanlış cevaba açıklama ve tekrar bağlantısı. Tam adaptif öğrenme iddiası yok. |
| ISLP | Regresyon, sınıflandırma, yeniden örnekleme, düzenlileştirme, ağaç, SVM, derin öğrenme, sağkalım, gözetimsiz öğrenme ve çoklu test; her bölüm sonunda kod laboratuvarı. | Çalışan Python defterleri var ama yeni başlayanın ilk yolu olarak uygun değil; varsayımlar ve model seçimi gerekçesi görünür değil. | Defterler derinleşme katmanında; kavram/koşul/karar önce. Çoklu test ve model değerlendirme içeriği güçlendiriliyor. |

## Üç bakışla bulgular

**İstatistik editörü:** Kapsam, ders sayısı ve çalışan hesap doğrulaması öğretim kalitesinin yerine geçmez. Tasarım/ölçüm, örnekleme yanlılığı, çıkarım hedefi, etki-belirsizlik ayrımı, çoklu bakış, grafik ekseni ve rapor dili birlikte değerlendirilmelidir. Konu panosunu dört farklı derse bağlamak ders düzeyinde özgün öğretim sayılmaz.

**Uygulayıcı:** Veri analizi/BI için doğru payda ve karşılaştırma; veri bilimi için tasarım, çıkarım ve nedensellik; ML için sızıntı, seçim, kayıp ve kalibrasyon; süreç/kalite için ölçüm, zaman sırası ve kararlılık gerekir. Bütün ileri konular dört yolun da zorunlu çekirdeği olmamalı. Uzmanlık seçilebilir kalır; yönetici bakışı ayrı bir meslek rotası değil karar denetim katmanıdır.

**Yeni başlayan:** İlk oturumda rol jargonundan önce ne öğreneceği ve ne yapacağı görülmeli. Bir ekranda tek soru, tanımlı terim, yorumlanan grafik ve sonraki adım bulunmalı. Başlangıç kontrolü not veya mesleki yeterlilik puanı değildir. Alıştırmaya bakmak tamamlanma sayılmamalı; kayıtlı eski başarılar korunmalı.

## Müfredat değişiklikleri

Mevcut 120 ders silinmeden ve yeni başlık sayısı başarı göstergesi yapılmadan yeniden katmanlandı: ortak başlangıç → rol çekirdeği → iş vakası → seçmeli uzmanlık. Otuz modülün öğrenme hedefleri ve derinleşme notları ayrı hazırlanır. Temel derslere kavrama özgü okuma/çözüm/yanılgı rehberi; ileri derslere ilgili çalışan analiz ve sınır bağlantısı eklenir.

Güçlendirilen ana alanlar: grafik okuryazarlığı ve payda; örnekleme ile rastgele atamanın ayrımı; uzun dönem güven aralığı kapsaması; p değeri ve etki ayrımı; blok ve 2×2 etkileşim; Holm/BH; sonucun karar diline aktarılması; ön koşula geri dönüş ve terim rehberi.

## Kaynaklar

- https://seeing-theory.brown.edu/index.html
- https://seeing-theory.brown.edu/frequentist-inference/index.html
- https://www.openintro.org/book/os/
- https://www.openintro.org/book/ims/
- https://brilliant.org/data/
- https://www.statlearning.com/
- Khan konu listesi (yalnız indeks): https://www.khanacademy.org/math/statistics-probability

## Konu kapsamı karşılaştırmasının yorumu

| Alan | Muadilde görülen örnek | Kesit'te konumu ve revizyon |
|---|---|---|
| Veri ve tasarım | OpenIntro: veri temeli, örnekleme, deney; IMS: erken çok değişkenli keşif | İlk dört derste veri birimi/ölçek/kapsam/grafik; rastgele örnekleme ile atama ayrımı güçlendirildi. |
| Olasılık ve dağılım | Seeing Theory: temel/bileşik olasılık, rassal değişken, ayrık-sürekli, CLT | Taban oranı, sayım, yoğunluk/alan ve CLT farklı görsel keşiflere ayrıldı. |
| Çıkarım | Seeing Theory: nokta tahmini, kapsama, bootstrap; IMS: randomizasyon ve simülasyon | Tekrarlı kapsama, yeniden çekim/karıştırma ayrımı, p/etki ve çoklu kontrol görselleri eklendi. |
| Modelleme | ISLP: regresyon, sınıflandırma, yeniden örnekleme, regularizasyon, ağaç, SVM, derin öğrenme | ML çekirdeğinde kayıp/seçim/sızıntı/kalibrasyon birlikte ele alındı; çalışan kod uzmanlık katmanında tutuldu. |
| Sağkalım/gözetimsiz öğrenme/çoklu test | ISLP içerik listesinde ayrı alanlar | Mevcut dersler korunarak sansür, ölçek, gizli yapı ve Holm/BH yorumları ayrıntılandırıldı. |
| Operasyon ve kalite | Genel istatistik kaynakları bu rolün bütün özel ihtiyaçlarını hedeflemiyor | Ölçüm sistemi, kontrol/spesifikasyon, yeterlilik, sağkalım ve kuyruk çekirdekte; VaR/entropi gibi komşu konular otomatik zorunlu değil. |

Kapsamın daha geniş olması daha etkili öğretim kanıtı değildir. Bu karşılaştırma, hangi kavramın nasıl öğretilmesi gerektiğini belirlemek için kullanıldı; ürünleri test edilmiş bir başarı sırasına koymaz.

## Uygulama sonrası doğrulama

- 120 mevcut ders/yanıt/not kimliği korundu; ders sayısı artırılmadı.
- Kavrama özgü temel anlatımlar, otuz modülde derinleşme/yöntem kontrolü/çıktı notları ve ders düzeyinde rol çekirdeği oluşturuldu.
- Rehberli beş adım, ön koşula dönüş, aramalı terim/sembol rehberi ve soru gerekçeleri eklendi.
- Elli kavram keşfinin varsayılan/uç ayarları kontrol edildi; Holm/BH, z hesabı ve aralık genişliği bağımsız statsmodels/SciPy referanslarıyla karşılaştırıldı.
- 390 px genişlikte başlangıç, ders, canlı ayar ve yanlış cevaptan çözüme dönüş tarayıcıda doğrulandı; sayfa taşması görülmedi. Bu, gerçek Android cihaz testi veya kullanıcı pilotu değildir.
