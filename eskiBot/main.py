"""
Gate.io Sinyal Botu - Ana dosya
"""

import sys
import signal
import traceback
from signal_manager import SignalManager

def signal_handler(sig, frame):
    """Ctrl+C ile güvenli kapatma"""
    print('\n🛑 Bot kapatılıyor...')
    sys.exit(0)

def main():
    """Ana fonksiyon"""
    print("=" * 50)
    print("🚀 GATE.IO SİNYAL BOTU")
    print("=" * 50)
    print("📊 %35+ artış tespiti")
    print("🎯 Otomatik sinyal gönderimi")
    print("📱 Telegram entegrasyonu")
    print("=" * 50)
    
    # Ctrl+C handler
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Signal manager'ı başlat
        signal_manager = SignalManager()
        signal_manager.start_monitoring()
        
    except KeyboardInterrupt:
        print("\n🛑 Bot kullanıcı tarafından durduruldu")
    except Exception as e:
        print(f"\n❌ Kritik hata oluştu: {e}")
        print("\n📋 Hata detayları:")
        traceback.print_exc()
    finally:
        print("\n👋 Bot kapatıldı")

if __name__ == "__main__":
    main()
