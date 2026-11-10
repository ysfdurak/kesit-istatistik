# Kesit İstatistik · V9 değerlendirme raporu (10 Kasım 2026)

V8/V9-öncesi sürüm; Kesit SQL, Kesit Power BI ve Kesit Python ile karşılaştırılarak eksiklik, müfredat, kullanım kolaylığı, öğreticilik ve ekosistem bağlantısı yönünden değerlendirildi. Bu bir iç incelemedir; gerçek kullanıcı testi değildir.

## Güçlü yönler (korundu)
- **Müfredat geniş ve dengeli.** 30 modül / 120 ders; betimselden nedensel çıkarıma, kaliteden istatistiksel öğrenmeye. Her derste sezgi, varsayım, akıl yürütme, vaka ve kaynak alanları var.
- **Öğretim akışı güçlü.** Anla → Gör → Çöz → Dene → Aktar; tahmin sorusu, seçeneğe özel geri bildirim, ön koşula dönüş.
- **Hesaplar doğrulanmış.** 39 SciPy referansı, NumPy/scikit-learn karşılaştırmaları, yöntem sınırları ekranda açık.
- **Dürüst kapsam dili.** "Pilot yapılmadı", "hazır çalıştırma" gibi sınırlar açıkça yazılı.

## Bulunan eksikler
| Alan | Bulgu | Kardeşlerle karşılaştırma | V9'da yapılan |
|---|---|---|---|
| Ekosistem | Kenar çubuğunda yalnız dış bağlantı vardı; veri setleri tamamen ayrıydı (depo/talep sentetik verileri). | SQL, PBI ve Python aynı 5–6 şirket verisini satır satır paylaşıyor. | 13 vaka ortak verilerle; her vakada SQL + Python + DAX; Python kodu veriyi kesit-python deposundan okur. |
| Alıştırma hacmi | Ders başına 1 sayısal + 1 kavram + 1 uygulama sorusu (toplam 360). | SQL 1.944, PBI 1.250, Python 3.240 ders içi alıştırma. | 33 parametreli üretici: her açılışta yeni sayı, ipucu, adımlı çözüm, zayıf konular, karışık set. |
| Araç bağlantısı | İstatistik kavramının SQL/DAX/Python karşılığı gösterilmiyordu. | Diğer uygulamalar araç odaklı. | 29 derse "Araçlarda bu kavram" kutusu; ilgili vaka, alıştırma ve sık hata bağlantıları. |
| Mülakat | Yoktu. | PBI 185, Python 292 soru. | 48 soru, rol bazlı, davranışsal soru yok; güçlü cevap unsurları, zayıf cevap, takip sorusu. |
| Sık hatalar | Ders içi uyarılar dağınıktı, toplu liste yoktu. | PBI ve Python'da ayrı bölüm. | 32 hata kalıbı, aranabilir, kategoriye göre, Kesit örnekli. |
| Seviye testi | Başlangıç kontrolü vardı ama başlangıç noktası önermiyordu. | SQL ve PBI'da var. | 15 soruluk test, seviye bazlı öneri ve tekrar dersleri. |
| Kullanım kolaylığı | Menüde yeni alanlar yoktu; geri bildirim yolu yoktu; favicon/manifest yoktu (404). | Kardeşlerde Issues bağlantısı, PWA, çevrimdışı. | "Uygula ve hazırlan" menü grubu, ana sayfa kartları, "Sorun bildir", favicon, manifest, service worker. |
| Depo | README ZIP kurulum talimatı anlatıyordu; canlı bağlantı, ekran görüntüsü, lisans yoktu. | Kardeşlerde ortak README yapısı ve MIT + CC BY-NC. | README kardeş biçiminde; LICENSE, LICENSE-ICERIK, NASIL.md; CI'ya `verify-v9.cjs`. |

## Hâlâ açık olanlar (öneri)
1. **Kardeş uygulamalardan geri bağlantı.** SQL/PBI/Python README ve menülerinde Kesit İstatistik yok; o depoların `kaynak` dalında eklenmeli.
2. **Tarayıcıda çalışan vaka kodu.** Python kodları şu an kopyala-çalıştır; Kesit Python'daki Pyodide motoruna "bu kodu aç" bağlantısı (URL ile kod aktarımı) iki uygulamayı daha sıkı bağlar.
3. **Sınav ve belge.** Kardeşlerdeki yol sonu sınavı ve tamamlama belgesi burada yok.
4. **Aralıklı tekrar.** Alıştırma kayıtları zayıf konuları gösteriyor ama zamanlanmış tekrar yok.
5. **Kullanıcı pilotu.** 5–10 kişilik küçük bir pilot, hangi derslerin zor olduğunu ve seviye testinin doğruluğunu ölçer.
