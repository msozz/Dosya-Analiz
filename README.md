<div align="center">

# 📁 Dosya Analiz

**Proje klasörlerinizi analiz edin, Excel, Word ve PDF dosyalarınızın detaylı Markdown raporlarını oluşturun.**

[![Python](https://img.shields.io/badge/Python-3.8+-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-Web_UI-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

[🚀 Hızlı Başlangıç](#-hızlı-başlangıç) •
[✨ Özellikler](#-özellikler) •
[🌐 Web Arayüzü](#-web-arayüzü) •
[📖 Kullanım](#-kullanım) •
[🤝 Katkıda Bulunun](#-katkıda-bulunun)

</div>

---

## 🎯 Nedir?

**Dosya Analiz**, yazılımcılara verilen proje klasörlerini hızlıca analiz etmeyi sağlayan bir araçtır. Klasör yapısını çıkarır, Excel/Word/PDF dosyalarını detaylı analiz eder ve sonuçları okunabilir Markdown raporlarına dönüştürür.

### 📋 Ne Yapar?

| Özellik | Açıklama |
|---------|----------|
| 📁 **Klasör Yapısı** | Tüm klasör ağacını görsel olarak çıkarır |
| 📊 **Excel Analizi** | Sayfalar, formüller, hücre bağımlılıkları, tablolar, veri doğrulama |
| 📝 **Word Analizi** | Başlık yapısı, tablolar, içerik önizleme, resim ve meta bilgiler |
| 📕 **PDF Analizi** | Sayfa sayısı, tablolar, metin çıkarma, metadata |
| 📄 **Raporlama** | Her klasöre MD rapor + toplu ana rapor oluşturur |
| 🌐 **Web Arayüzü** | Tarayıcı üzerinden kullanım (opsiyonel) |

---

## 🚀 Hızlı Başlangıç

### Kurulum

```bash
# Repoyu klonlayın
git clone https://github.com/muhammedsiracozer/dosya-analiz.git
cd dosya-analiz

# Bağımlılıkları yükleyin
pip install -r requirements.txt
```

### Komut Satırından Kullanım

```bash
# Belirli bir klasörü analiz et
python dosya_analiz.py /path/to/project

# Mevcut klasörü analiz et
python dosya_analiz.py .
```

### Web Arayüzü ile Kullanım

```bash
# Web sunucusunu başlat
python app.py

# Tarayıcıda aç: http://127.0.0.1:5000
```

---

## ✨ Özellikler

### 📊 Excel Analizi (`.xlsx`, `.xlsm`, `.xls`)

- ✅ Sayfa isimleri ve boyutları
- ✅ Sütun başlıkları
- ✅ Formül tespiti ve listeleme
- ✅ Hücre bağımlılıkları (hangi hücre hangi hücreye bağlı)
- ✅ Birleştirilmiş hücreler
- ✅ Veri doğrulama kuralları
- ✅ Koşullu biçimlendirme
- ✅ Tanımlı isimler (Named Ranges)
- ✅ Örnek veri önizleme

### 📝 Word Analizi (`.docx`)

- ✅ Paragraf ve kelime sayısı
- ✅ Başlık yapısı (içindekiler)
- ✅ Tablo analizi
- ✅ Gömülü resimler
- ✅ Üstbilgi / Altbilgi
- ✅ İçerik önizleme

### 📕 PDF Analizi (`.pdf`)

- ✅ Sayfa sayısı ve metadata
- ✅ Sayfa bazlı kelime sayısı
- ✅ Tablo tespiti ve çıkarma
- ✅ Metin çıkarma
- ✅ İçerik önizleme

### 📁 Klasör Analizi

- ✅ Görsel klasör ağacı
- ✅ Dosya türü dağılımı
- ✅ Boyut hesaplama
- ✅ Her klasöre ayrı rapor
- ✅ Birleştirilmiş ana rapor

---

## 🌐 Web Arayüzü

Dosya Analiz, modern ve kullanıcı dostu bir web arayüzü ile birlikte gelir:

### Web Arayüzü Özellikleri

- 🖱️ **Sürükle-Bırak** desteği
- 📤 **ZIP Yükleme** ile klasör analizi
- 📍 **Yerel Yol** ile analiz (sunucu tarafı)
- 📋 **Sonuç Kopyalama** ve indirme
- 🌙 **Karanlık Tema**
- 📱 **Responsive** tasarım

### Web Sunucusu Seçenekleri

```bash
# Varsayılan ayarlarla başlat
python app.py

# Özel port ile başlat
python app.py --port 8080

# Ağdaki diğer cihazlardan erişim için
python app.py --host 0.0.0.0 --port 5000

# Debug modunda başlat (geliştirme için)
python app.py --debug
```

---

## 📖 Kullanım

### Komut Satırı Kullanımı

```bash
# Temel kullanım
python dosya_analiz.py <klasör_yolu>

# Örnekler
python dosya_analiz.py ~/Documents/MyProject
python dosya_analiz.py ./proje-klasoru
python dosya_analiz.py .

# Yardım
python dosya_analiz.py --help
```

### Çıktı Yapısı

Analiz tamamlandığında şu yapı oluşturulur:

```
proje-klasoru/
├── _ANALIZ_RAPORLARI/          ← Tüm raporların toplandığı klasör
│   ├── ANA_RAPOR.md            ← Genel özet + tüm alt raporlar
│   ├── KOK_KLASOR_RAPORU.md    ← Kök klasör raporu
│   └── alt_klasor_RAPORU.md    ← Her alt klasör için ayrı rapor
├── PROJE_ANALIZ_RAPORU.md      ← Ana rapor kopyası (kolay erişim için)
├── _KLASOR_RAPORU.md           ← Kök klasöre ait rapor
└── alt-klasor/
    └── _KLASOR_RAPORU.md       ← Bu klasöre ait rapor
```

### Rapor İçeriği Örneği

```markdown
# 📁 Klasör Raporu: `proje-klasoru`

## 📋 Özet
| Öğe | Sayı |
|-----|------|
| Alt Klasörler | 5 |
| Toplam Dosya | 23 |
| Excel Dosyaları | 3 |

## 📊 Excel Dosya Analizleri

### 📊 `veri.xlsx`
- **Sayfa Sayısı:** 3
- **Sayfalar:** Özet, Detay, Parametreler
- **Formül Sayısı:** 45
```

---

## 🔧 Gereksinimler

### Zorunlu

- Python 3.8+

### Opsiyonel (Analiz Kütüphaneleri)

| Kütüphane | Amaç | Kurulum |
|-----------|------|---------|
| `openpyxl` | Excel .xlsx analizi | `pip install openpyxl` |
| `xlrd` | Eski Excel .xls analizi | `pip install xlrd` |
| `python-docx` | Word .docx analizi | `pip install python-docx` |
| `pdfplumber` | PDF analizi | `pip install pdfplumber` |
| `Flask` | Web arayüzü | `pip install flask` |

### Toplu Kurulum

```bash
pip install -r requirements.txt
```

---

## 📁 Proje Yapısı

```
dosya-analiz/
├── dosya_analiz.py      # Ana analiz scripti (CLI)
├── app.py               # Flask web uygulaması
├── requirements.txt     # Python bağımlılıkları
├── README.md            # Bu dosya
├── LICENSE              # MIT Lisansı
├── .gitignore           # Git ignore kuralları
├── templates/           # HTML şablonları
│   ├── index.html       # Ana sayfa
│   └── 404.html         # 404 sayfası
└── static/              # Statik dosyalar
```

---

## 🛠️ Geliştirme

### Yerel Geliştirme Ortamı

```bash
# Sanal ortam oluştur
python -m venv venv
source venv/bin/activate  # Linux/macOS
# veya
.\venv\Scripts\activate   # Windows

# Bağımlılıkları yükle
pip install -r requirements.txt

# Debug modunda çalıştır
python app.py --debug
```

---

## 🤝 Katkıda Bulunun

Katkılarınızı memnuniyetle karşılıyoruz! 

1. Bu repoyu fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'feat: Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

---

## 📄 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

---

<div align="center">

**[⬆ Başa Dön](#-dosya-analiz)**

Made with ❤️ by Muhammed Sırac Özer, for developers

</div>
