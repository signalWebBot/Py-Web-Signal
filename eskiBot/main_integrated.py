#!/usr/bin/env python3
"""
Gate.io Sinyal Botu - Entegre Versiyon
Bot ve web arayüzü aynı anda çalışır
"""

import threading
import time
from signal_manager import SignalManager
from gateio_api import GateioAPI
from config import Config
from web_app import web_data, start_web_server

def main():
    """Ana fonksiyon - bot ve web'i başlatır"""
    print("=" * 60)
    print("🚀 GATE.IO SİNYAL BOTU - ENTEGRE VERSİYON")
    print("=" * 60)
    print("📊 %35+ artış tespiti")
    print("🎯 Otomatik sinyal gönderimi")
    print("📱 Telegram entegrasyonu")
    print("🌐 Web arayüzü: AKTİF")
    print("=" * 60)
    
    try:
        # Gate.io API başlat
        gateio = GateioAPI()
        
        # Signal Manager başlat
        signal_manager = SignalManager(gateio)
        
        # Web veri yöneticisine signal manager'ı bağla
        web_data['signal_manager'] = signal_manager
        
        print("🤖 Signal bot başlatılıyor...")
        
        # Bot'u ayrı thread'de başlat
        bot_thread = threading.Thread(target=signal_manager.start_monitoring, daemon=True)
        bot_thread.start()
        
        print("🌐 Web sunucusu başlatılıyor...")
        
        # Web sunucusunu ana thread'de başlat
        start_web_server()
        
    except KeyboardInterrupt:
        print("\n🛑 Bot durduruluyor...")
    except Exception as e:
        print(f"❌ Hata: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
