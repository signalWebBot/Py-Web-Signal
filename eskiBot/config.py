"""
Konfigürasyon dosyası - Bot ayarları
"""

import os

class Config:
    # Telegram Bot Ayarları
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', "7649876404:AAHCFuUJQlRcVKGwQCGN653_KlRkAYZNBjE")
    TELEGRAM_GROUP_ID = int(os.getenv('TELEGRAM_GROUP_ID', -4887711321))
    
    # Gate.io API Ayarları
    GATEIO_BASE_URL = os.getenv('GATEIO_BASE_URL', "https://api.gateio.ws/api/v4")
    
    # Sinyal Ayarları
    SCAN_INTERVAL = int(os.getenv('SCAN_INTERVAL', 15))  # 15 saniye
    INITIAL_PUMP_THRESHOLD = int(os.getenv('INITIAL_PUMP_THRESHOLD', 35))  # %35 artış için ilk sinyal
    SECOND_SIGNAL_THRESHOLD = int(os.getenv('SECOND_SIGNAL_THRESHOLD', 20))  # %20 ek artış için 2. sinyal
    NEXT_SIGNAL_THRESHOLD = int(os.getenv('NEXT_SIGNAL_THRESHOLD', 10))  # %10'luk artışlar için sonraki sinyaller
    FOLLOWUP_INTERVAL = int(os.getenv('FOLLOWUP_INTERVAL', 45))  # 45 saniye takip aralığı
    DROP_THRESHOLD = int(os.getenv('DROP_THRESHOLD', 25))  # %25'e düşünce takipten çıkar
    
    # Hacim Kategorileri
    LOW_VOLUME_THRESHOLD = int(os.getenv('LOW_VOLUME_THRESHOLD', 100000))  # 100k altı düşük hacim
    MEDIUM_VOLUME_THRESHOLD = int(os.getenv('MEDIUM_VOLUME_THRESHOLD', 300000))  # 300k altı orta hacim
    
    # Trade History Ayarları
    MIN_TRADE_AMOUNT = int(os.getenv('MIN_TRADE_AMOUNT', 100))  # Minimum 100 dolar alım
    
    # Bot 7/24 çalışır - çalışma saati kısıtlaması yok
    
    # Blacklist - Bu coinler taranmayacak
    BLACKLISTED_PATTERNS = [
        'USDT', 'USDC', 'BUSD', 'DAI',  # Stablecoinler
        '3S', '3L', '5S', '5L',  # Leverage tokenler
        'BEAR', 'BULL'  # Leverage tokenler
    ]
