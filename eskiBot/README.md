# Gate.io Sinyal Botu

Gate.io borsasında %35+ artış gösteren coinleri tespit edip Telegram'a sinyal gönderen otomatik bot.

## Özellikler

- ✅ 15 saniyede bir tüm coinleri tarar
- ✅ %35+ artış gösteren coinleri tespit eder
- ✅ Leverage tokenları filtreler (3S, 5L vb.)
- ✅ Hacim kategorilendirmesi (Düşük/Orta/Yüksek)
- ✅ Çoklu sinyal sistemi (2., 3., 4. sinyaller)
- ✅ 45 saniye takip sistemi
- ✅ Spam önleme
- ✅ Trade history analizi
- ✅ Telegram entegrasyonu

## Kurulum

```bash
git clone <repo-url>
cd YeniBotSinyal
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python main.py
```

## Yapılandırma

`config.py` dosyasında bot token ve grup ID'sini güncelleyin.

## Railway Deploy

Bu proje Railway'de çalışmaya hazırdır. Sadece GitHub'a push edip Railway'e bağlayın.
