# 🚀 Gate.io Sinyal Botu - Python Web Entegrasyonu

Modern Python tabanlı Gate.io sinyal botu ile Flask web arayüzü entegrasyonu.

## ✨ Özellikler

### 🤖 Bot Özellikleri
- **7/24 Kesintisiz Çalışma** - Hiç durmadan coin taraması
- **%35+ Artış Tespiti** - Yüksek kazanç potansiyeli olan coinler
- **Telegram Entegrasyonu** - Anlık sinyal bildirimleri
- **Çoklu Sinyal Sistemi** - İlk, ikinci ve takip sinyalleri
- **Hacim Analizi** - Düşük, orta, yüksek hacim kategorileri
- **Spam Koruması** - Aynı coin için tekrarlı sinyal engelleme

### 🌐 Web Arayüzü
- **Modern Dashboard** - Bootstrap 5 ile responsive tasarım
- **Real-time Güncellemeler** - Socket.IO ile canlı veri
- **Sinyal Geçmişi** - Tüm sinyallerin detaylı listesi
- **Takip Edilen Coinler** - Aktif coin takibi
- **Özel Takip Listesi** - Manuel coin ekleme
- **Bot Kontrolü** - Başlat/durdur/reset işlemleri
- **Kullanıcı Yönetimi** - Güvenli giriş sistemi

### 📊 Veri Yönetimi
- **SQLite Database** - Hafif ve hızlı veri saklama
- **Veri Export** - CSV formatında dışa aktarma
- **Otomatik Temizlik** - Eski verilerin otomatik silinmesi
- **Backup Sistemi** - Veri yedekleme

## 🛠️ Kurulum

### Gereksinimler
- Python 3.12+
- pip
- Git

### Adımlar

1. **Repository'yi klonlayın:**
```bash
git clone https://github.com/muratbulut/python-webli-sinyal.git
cd python-webli-sinyal
```

2. **Virtual environment oluşturun:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate     # Windows
```

3. **Bağımlılıkları yükleyin:**
```bash
pip install -r eskiBot/requirements.txt
```

4. **Veritabanını başlatın:**
```bash
cd eskiBot
python database.py
python setup_initial_data.py
```

5. **Botu başlatın:**
```bash
python main_integrated.py
```

## ⚙️ Konfigürasyon

### Environment Variables
```bash
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_GROUP_ID=your_group_id

# Gate.io
GATEIO_BASE_URL=https://api.gateio.ws/api/v4

# Bot Ayarları
SCAN_INTERVAL=15
INITIAL_PUMP_THRESHOLD=35
SECOND_SIGNAL_THRESHOLD=20
NEXT_SIGNAL_THRESHOLD=10
FOLLOWUP_INTERVAL=45
DROP_THRESHOLD=25

# Hacim Eşikleri
LOW_VOLUME_THRESHOLD=100000
MEDIUM_VOLUME_THRESHOLD=300000
MIN_TRADE_AMOUNT=100
```

### Varsayılan Kullanıcılar
- **Username:** murat, **Password:** 123456
- **Username:** admin, **Password:** admin123
- **Username:** mannetta, **Password:** mannetta123

## 🚀 Railway Deployment

### 1. Railway'e Deploy
1. Railway hesabınıza giriş yapın
2. "New Project" → "Deploy from GitHub repo"
3. Repository'yi seçin
4. Environment variables'ları ekleyin
5. Deploy edin

### 2. Environment Variables (Railway)
Railway dashboard'da şu environment variables'ları ekleyin:
```
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_GROUP_ID=your_group_id
GATEIO_BASE_URL=https://api.gateio.ws/api/v4
SCAN_INTERVAL=15
INITIAL_PUMP_THRESHOLD=35
SECOND_SIGNAL_THRESHOLD=20
NEXT_SIGNAL_THRESHOLD=10
FOLLOWUP_INTERVAL=45
DROP_THRESHOLD=25
LOW_VOLUME_THRESHOLD=100000
MEDIUM_VOLUME_THRESHOLD=300000
MIN_TRADE_AMOUNT=100
PORT=5000
```

## 📱 Kullanım

### Web Arayüzü
- **Dashboard:** http://localhost:5000
- **Login:** murat / 123456
- **Bot Kontrolü:** Dashboard'dan başlat/durdur
- **Sinyal Takibi:** Sinyaller sayfasından görüntüle

### Telegram
- Bot otomatik olarak sinyalleri gönderir
- Yüksek hacimli coinler öncelikli
- Spam koruması aktif

## 🔧 Geliştirme

### Proje Yapısı
```
eskiBot/
├── main_integrated.py      # Ana başlatma dosyası
├── signal_manager.py       # Bot mantığı
├── gateio_api.py          # Gate.io API entegrasyonu
├── telegram_bot.py        # Telegram entegrasyonu
├── web_app.py             # Flask web uygulaması
├── database.py            # SQLite veritabanı modelleri
├── config.py              # Konfigürasyon
├── templates/             # HTML şablonları
├── static/                # CSS/JS dosyaları
└── requirements.txt       # Python bağımlılıkları
```

### API Endpoints
- `GET /` - Dashboard
- `GET /api/signals` - Sinyal listesi
- `GET /api/tracked` - Takip edilen coinler
- `POST /api/bot/start` - Bot başlat
- `POST /api/bot/stop` - Bot durdur
- `GET /api/bot/status` - Bot durumu

## 📊 Performans

- **Tarama Hızı:** 15 saniye
- **API Limit:** Gate.io rate limit'leri içinde
- **Memory Usage:** ~50MB
- **CPU Usage:** Düşük
- **Database:** SQLite (hafif)

## 🛡️ Güvenlik

- **Password Hashing:** SHA256
- **Session Management:** Flask sessions
- **Input Validation:** Tüm girişler doğrulanır
- **SQL Injection:** SQLAlchemy ORM koruması
- **XSS Protection:** Template escaping

## 📈 Monitoring

- **Bot Logs:** Console ve database
- **Error Tracking:** Exception handling
- **Performance Metrics:** Response times
- **Telegram Status:** Connection monitoring

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 📞 İletişim

- **Developer:** Murat Bulut
- **Email:** murat@signalweb.com
- **GitHub:** [muratbulut](https://github.com/muratbulut)

---

**⚠️ Uyarı:** Bu bot sadece eğitim amaçlıdır. Kripto para yatırımları risklidir. Kendi sorumluluğunuzda kullanın.
