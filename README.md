# Kesit İstatistik · V8

Türkçe, tarayıcıda çalışan istatistik öğrenme uygulaması. Veri analizi ve BI, veri bilimi, makine öğrenmesi ve süreç/kalite rolleri için ayrı öğrenme yolları içerir.

- 30 modülde 120 ders ve 8 seçmeli yöntem dersi
- 22 derste tahmin, gerekçeli geri bildirim, çözümlü örnek ve yeni bağlam sorusu
- 34 tarayıcı atölyesi, 14 iş vakası ve 28 hazır analiz senaryosu
- Sentetik eğitim verileri, kavram panoları ve indirilebilir Python örnekleri

## Bilgisayarda açma

ZIP'i çıkar ve `docs/index.html` dosyasını tarayıcıda aç. Statik sunucuyla denemek için ZIP'in içindeki `kesit-istatistik` klasöründe terminal aç.

Windows PowerShell:

```powershell
py -m http.server 8000 --bind 127.0.0.1 --directory docs
```

macOS veya Linux:

```sh
python3 -m http.server 8000 --bind 127.0.0.1 --directory docs
```

Tarayıcıda [127.0.0.1:8000](http://127.0.0.1:8000/) adresine git. Uygulamayı kullanmak için paket kurulumu, derleme ve API anahtarı gerekmez.

## GitHub Pages'e yayımlama

Önerilen depo adı **`kesit-istatistik`**.

1. GitHub'da `kesit-istatistik` adlı bir depo oluştur. Herkesin erişeceği bir portföy yayını için **Public** seç.
2. ZIP'teki `kesit-istatistik` klasörünün **içeriğini** deponun köküne koy. GitHub'da dosya listesinde `README.md` ve `docs/` yan yana görünmeli. `docs/.nojekyll` dosyasını da yükle.
3. **Settings → Pages → Build and deployment** bölümünde kaynak olarak **Deploy from a branch** seç.
4. Dal olarak **main**, klasör olarak **/docs** seç ve kaydet.
5. İlk yayın tamamlandığında **Settings → Pages** bölümünde gösterilen adresi aç. Proje adresi normalde `https://KULLANICI_ADI.github.io/kesit-istatistik/` biçimindedir.

[GitHub Pages yayın kaynağı rehberi](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)

Git kullanıyorsan yeni ve boş depoya yükleme komutları:

```sh
git init -b main
git add .
git commit -m "Kesit İstatistik V8"
git remote add origin https://github.com/KULLANICI_ADI/kesit-istatistik.git
git push -u origin main
```

## Veri ve ilerleme

Eğitim veri setleri sentetiktir. İlerleme ve notlar tarayıcıda saklanır. Önceki yayın adresindeki ilerlemeyi yeni adrese taşımak için **İlerlemem** bölümünden ilerleme yedeğini indir ve yeni adreste **Yedek yükle** ile içe aktar. Her atölyenin ayrı çıktıları varsa ilgili ekrandan ayrıca indir.

## Kaynak ve kontroller

`docs/` yayımlanacak HTML, CSS, JavaScript, font ve eğitim dosyalarını içerir. Kök dizindeki Python betikleri, çalışılmış örnekleri ve referansları geliştirmek içindir. Sayfaları yayımlamak için bu betikleri çalıştırman gerekmez.

Paket kökünde Node.js ile:

```sh
node verify.cjs
node verify-engine.cjs
node verify-visual.cjs
```

- [Sürüm notları ve içerik geliştirme](research/surum-notlari.md)
- [Yerel font lisansları](docs/vendor/fonts/)
