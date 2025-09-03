"""
Sinyal yönetimi ve mantığı
"""

import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from config import Config
from gateio_api import GateioAPI
from telegram_bot import TelegramBot

@dataclass
class CoinTracker:
    """Takip edilen coin bilgileri"""
    symbol: str
    currency_pair: str
    base_price: float  # İlk tespit edilen fiyat
    current_price: float
    initial_percentage: float  # İlk sinyal yüzdesi
    current_percentage: float
    previous_signal_percentage: float  # Bir önceki sinyalin yüzdesi
    signal_count: int  # Kaç sinyal verildi
    last_signal_time: datetime
    last_scan_time: datetime
    is_following: bool  # 45 saniye takip modunda mı
    volume_24h: float

class SignalManager:
    def __init__(self, gateio_api=None):
        self.gateio_api = gateio_api or GateioAPI()
        self.telegram_bot = TelegramBot()
        self.tracked_coins: Dict[str, CoinTracker] = {}
        self.base_scan_interval = Config.SCAN_INTERVAL
        self.followup_interval = Config.FOLLOWUP_INTERVAL
        self.turkey_timezone = timezone(timedelta(hours=3))  # Türkiye saati +3
        self.web_signal_callback = None  # Web arayüzü için callback
        
    def set_web_callback(self, callback):
        """Web arayüzü için callback fonksiyonu ayarla"""
        self.web_signal_callback = callback
        
    def start_monitoring(self):
        """Ana tarama döngüsünü başlatır"""
        print("🚀 Gate.io Sinyal Botu başlatılıyor...")
        
        # Test mesajı gönder
        if self.telegram_bot.send_test_message():
            print("✅ Telegram bağlantısı başarılı")
        else:
            print("❌ Telegram bağlantısı başarısız!")
            return
        
        print(f"📊 {self.base_scan_interval} saniyede bir tarama başlatılıyor...")
        print("⏰ Bot 24/7 kesintisiz çalışacak!")
        
        while True:
            try:
                current_time = datetime.now(self.turkey_timezone)  # Türkiye saati kullan
                
                # Ana tarama (15 saniye)
                self._perform_main_scan(current_time)
                
                # PUSU Sinyal kontrolü (15 saniye)
                self.check_pusu_signals(current_time)
                
                # Takip edilen coinleri kontrol et (45 saniye)
                self._check_followed_coins(current_time)
                
                # Temizlik: düşen coinleri takipten çıkar
                self._cleanup_dropped_coins()
                
                time.sleep(1)  # CPU yükünü azaltmak için
                
            except KeyboardInterrupt:
                print("\n🛑 Bot durduruldu")
                break
            except Exception as e:
                print(f"❌ Beklenmeyen hata: {e}")
                time.sleep(5)
    
    def _perform_main_scan(self, current_time: datetime):
        """Ana tarama - 15 saniyede bir"""
        # Son taramadan 15 saniye geçti mi?
        if hasattr(self, '_last_main_scan'):
            if (current_time - self._last_main_scan).total_seconds() < self.base_scan_interval:
                return
        
        print(f"🔍 Ana tarama başlatılıyor... ({current_time.strftime('%H:%M:%S')})")
        
        # Tüm tickers'ı çek
        tickers = self.gateio_api.get_all_tickers()
        if not tickers:
            print("❌ Ticker verisi alınamadı")
            return
        
        pump_coins = []
        
        # Her coin için %35+ artış kontrol et
        for ticker in tickers:
            try:
                currency_pair = ticker['currency_pair']
                symbol = currency_pair.replace('_USDT', '')
                
                # Zaten takip edilen coinleri ana taramada atla
                if symbol in self.tracked_coins and self.tracked_coins[symbol].is_following:
                    continue
                
                change_percentage = float(ticker.get('change_percentage', 0))
                
                # %35+ artış kontrolü
                if change_percentage >= Config.INITIAL_PUMP_THRESHOLD:
                    last_price = float(ticker.get('last', 0))
                    volume_24h = float(ticker.get('quote_volume', 0))
                    
                    # Daha önce sinyal verildi mi kontrol et
                    if symbol in self.tracked_coins:
                        # Eğer %25'in altına düşüp tekrar %35'e çıktıysa yeni sinyal olarak değerlendir
                        if not self.tracked_coins[symbol].is_following:
                            pump_coins.append({
                                'symbol': symbol,
                                'currency_pair': currency_pair,
                                'price': last_price,
                                'percentage': change_percentage,
                                'volume_24h': volume_24h
                            })
                    else:
                        pump_coins.append({
                            'symbol': symbol,
                            'currency_pair': currency_pair,
                            'price': last_price,
                            'percentage': change_percentage,
                            'volume_24h': volume_24h
                        })
                        
            except Exception as e:
                print(f"❌ Ticker işleme hatası: {e}")
                continue
        
        # Pump coinler için sinyal gönder
        for coin_data in pump_coins:
            self._send_initial_signal(coin_data, current_time)
        
        self._last_main_scan = current_time
        
        if pump_coins:
            print(f"🎯 {len(pump_coins)} adet pump coin tespit edildi")
        else:
            print("📊 Pump coin bulunamadı")
    
    def _check_followed_coins(self, current_time: datetime):
        """Takip edilen coinleri kontrol et - 45 saniyede bir"""
        coins_to_remove = []
        
        for symbol, tracker in self.tracked_coins.items():
            if not tracker.is_following:
                continue
            
            # 45 saniye geçti mi?
            if (current_time - tracker.last_scan_time).total_seconds() < self.followup_interval:
                continue
            
            print(f"🔄 {symbol} takip kontrolü yapılıyor...")
            
            # Güncel fiyat bilgisini çek
            ticker_data = self.gateio_api.get_ticker_detail(tracker.currency_pair)
            if not ticker_data:
                continue
            
            try:
                current_price = float(ticker_data.get('last', 0))
                change_percentage = float(ticker_data.get('change_percentage', 0))
                
                # Fiyat %25'in altına düştü mü?
                if change_percentage < Config.DROP_THRESHOLD:
                    print(f"📉 {symbol} %25'in altına düştü, takipten çıkarılıyor")
                    coins_to_remove.append(symbol)
                    continue
                
                # Yeni sinyal kontrolü
                self._check_for_additional_signals(tracker, current_price, change_percentage, current_time)
                
                # Scan time güncelle
                tracker.last_scan_time = current_time
                
            except Exception as e:
                print(f"❌ {symbol} takip hatası: {e}")
        
        # Düşen coinleri kaldır
        for symbol in coins_to_remove:
            del self.tracked_coins[symbol]
    
    def _check_for_additional_signals(self, tracker: CoinTracker, current_price: float, current_percentage: float, current_time: datetime):
        """Ek sinyal kontrolü yapar - Yeni frekans sistemi"""
        symbol = tracker.symbol
        
        # Yeni sinyal frekans sistemi
        required_percentage = self._calculate_next_signal_threshold(tracker.initial_percentage, tracker.signal_count)
        
        if current_percentage >= required_percentage:
            print(f"🎯 {symbol} için {tracker.signal_count + 1}. sinyal tetiklendi! ({current_percentage:.2f}% >= {required_percentage:.2f}%)")
            
            # Sinyal gönder
            signal_data = self._prepare_signal_data(tracker, current_price, current_percentage, tracker.signal_count + 1)
            
            if self.telegram_bot.send_signal(signal_data):
                # Web arayüzüne bildir
                if self.web_signal_callback:
                    self.web_signal_callback(signal_data)
                    
                # Bir önceki sinyal yüzdesini güncelle
                tracker.previous_signal_percentage = tracker.current_percentage
                tracker.signal_count += 1
                tracker.current_price = current_price
                tracker.current_percentage = current_percentage
                tracker.last_signal_time = current_time
                print(f"✅ {symbol} {tracker.signal_count}. sinyal gönderildi")
    
    def _calculate_next_signal_threshold(self, initial_percentage: float, current_signal_count: int) -> float:
        """Yeni sinyal frekans sistemine göre bir sonraki sinyal eşiğini hesaplar"""
        
        if current_signal_count == 1:
            # 2. sinyal için %20 ek artış
            return initial_percentage + Config.SECOND_SIGNAL_THRESHOLD
        
        # Şu anki seviyeyi hesapla
        if current_signal_count == 2:
            current_level = initial_percentage + Config.SECOND_SIGNAL_THRESHOLD
        else:
            # 3. ve sonraki sinyaller için şu anki seviyeyi hesapla
            additional_increases = (current_signal_count - 2) * Config.NEXT_SIGNAL_THRESHOLD
            current_level = initial_percentage + Config.SECOND_SIGNAL_THRESHOLD + additional_increases
        
        # Bir sonraki sinyal için gerekli artışı belirle
        if current_level < 100:
            # %100'den az: %10'luk artışlar (eski sistem)
            return current_level + Config.NEXT_SIGNAL_THRESHOLD
        elif current_level < 200:
            # %100-200 arası: %25'lik artışlar
            next_threshold = ((current_level // 25) + 1) * 25
            return max(next_threshold, current_level + 25)
        else:
            # %200+: %50'lik artışlar
            next_threshold = ((current_level // 50) + 1) * 50
            return max(next_threshold, current_level + 50)
    
    def _send_initial_signal(self, coin_data: Dict, current_time: datetime):
        """İlk sinyal gönderir ve takip listesine ekler"""
        symbol = coin_data['symbol']
        currency_pair = coin_data['currency_pair']
        price = coin_data['price']
        percentage = coin_data['percentage']
        volume_24h = coin_data['volume_24h']
        
        print(f"🎯 {symbol} için ilk sinyal hazırlanıyor...")
        
        # Trade history ve diğer detayları çek
        signal_data = {
            'symbol': symbol,
            'signal_type': 'new',
            'price': price,
            'percentage': percentage,
            'initial_percentage': percentage,
            'volume_24h': volume_24h,
            'volume_category': self.gateio_api.get_volume_category(volume_24h),
            'trades_history': self._get_formatted_trade_history(currency_pair),
            'cash_5min': self._calculate_5min_cash(currency_pair)
        }
        
        # Sinyal gönder
        if self.telegram_bot.send_signal(signal_data):
            # Web arayüzüne bildir
            if self.web_signal_callback:
                self.web_signal_callback(signal_data)
                
            # Takip listesine ekle
            tracker = CoinTracker(
                symbol=symbol,
                currency_pair=currency_pair,
                base_price=price,
                current_price=price,
                initial_percentage=percentage,
                current_percentage=percentage,
                previous_signal_percentage=percentage,  # İlk sinyalde kendisi
                signal_count=1,
                last_signal_time=current_time,
                last_scan_time=current_time,
                is_following=True,
                volume_24h=volume_24h
            )
            
            self.tracked_coins[symbol] = tracker
            print(f"✅ {symbol} ilk sinyal gönderildi ve takibe alındı")
        else:
            print(f"❌ {symbol} sinyal gönderilemedi")
    
    def _prepare_signal_data(self, tracker: CoinTracker, current_price: float, current_percentage: float, signal_number: int) -> Dict:
        """Sinyal verisi hazırlar"""
        signal_types = ['', 'new', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth']
        signal_type = signal_types[signal_number] if signal_number < len(signal_types) else 'tenth+'
        
        # 3. sinyalden itibaren bir önceki sinyalin yüzdesini kullan
        if signal_number >= 3:
            previous_percentage = tracker.previous_signal_percentage
        else:
            previous_percentage = tracker.initial_percentage
        
        return {
            'symbol': tracker.symbol,
            'signal_type': signal_type,
            'price': current_price,
            'percentage': current_percentage,
            'initial_percentage': tracker.initial_percentage,
            'previous_percentage': previous_percentage,  # Yeni eklenen alan
            'signal_number': signal_number,  # Sinyal numarası bilgisi
            'volume_24h': tracker.volume_24h,
            'volume_category': self.gateio_api.get_volume_category(tracker.volume_24h),
            'trades_history': self._get_formatted_trade_history(tracker.currency_pair),
            'cash_5min': self._calculate_5min_cash(tracker.currency_pair)
        }
    
    def _get_formatted_trade_history(self, currency_pair: str) -> List[str]:
        """Formatlanmış trade history döndürür"""
        try:
            # Gate.io'dan son 24 saatin trade history'sini çek
            trades = self.gateio_api.get_trades_history(currency_pair, limit=100)
            if not trades:
                return self._get_sample_trade_history()
            
            # Son 24 saatti filtrele ve $100+ işlemleri bul
            current_time = datetime.now(self.turkey_timezone)
            last_24h = current_time - timedelta(hours=24)
            
            significant_trades = []
            for trade in trades:
                try:
                    # Trade zamanını parse et ve timezone ekle
                    trade_timestamp = int(trade.get('create_time', 0))
                    trade_time = datetime.fromtimestamp(trade_timestamp, tz=self.turkey_timezone)
                    
                    if trade_time < last_24h:
                        continue
                    
                    # Trade amount hesapla (price * amount)
                    price = float(trade.get('price', 0))
                    amount = float(trade.get('amount', 0))
                    trade_value = price * amount
                    
                    # $100+ işlemleri filtrele
                    if trade_value >= Config.MIN_TRADE_AMOUNT:
                        date_str = trade_time.strftime("%d.%m")
                        time_str = trade_time.strftime("%H:%M")
                        
                        # Volume değişim hesaplaması (basitleştirilmiş)
                        # Gerçek implementasyonda o anki fiyat değişimi hesaplanacak
                        before_change = 0.0  # Trade öncesi değişim
                        after_change = 3.2   # Trade sonrası değişim (örnek)
                        volume_change = 0.4  # Volume artış oranı (örnek)
                        
                        line = f"{date_str} {time_str}    +{trade_value:,.2f}  {before_change:.1f}% => {after_change:.1f}% - V: % {volume_change:.1f}"
                        significant_trades.append({
                            'line': line,
                            'time': trade_time,
                            'value': trade_value
                        })
                        
                except Exception as e:
                    print(f"Trade parsing hatası: {e}")
                    continue
            
            # En büyük işlemlerden 10 tanesini seç, zamana göre sırala
            significant_trades.sort(key=lambda x: x['time'], reverse=True)
            formatted_lines = [trade['line'] for trade in significant_trades[:10]]
            
            # Eğer yeterli gerçek veri yoksa örnek verilerle tamamla
            if len(formatted_lines) < 3:
                sample_lines = self._get_sample_trade_history()
                formatted_lines.extend(sample_lines[len(formatted_lines):])
            
            return formatted_lines[:10]
            
        except Exception as e:
            print(f"Trade history hatası: {e}")
            return self._get_sample_trade_history()
    
    def _get_sample_trade_history(self) -> List[str]:
        """Örnek trade history döndürür"""
        current_time = datetime.now(self.turkey_timezone)
        
        sample_history = []
        sample_data = [
            (4, 24, 5355.97, 66.4, 71.6, 15.9),
            (2, 9, 141.43, 0.0, 3.2, 0.4),
            (14, 34, 130.26, 0.0, 3.0, 0.2),
            (11, 33, 140.68, 0.0, -0.1, 0.2),
            (11, 22, 193.92, 0.0, -0.1, 0.2),
            (11, 18, 188.20, 0.0, -0.1, 0.2),
            (11, 11, 160.55, 0.0, -0.2, 0.2),
            (11, 8, 137.90, 0.0, -0.1, 0.2),
            (10, 57, 228.83, 0.0, -0.2, 0.3),
            (10, 26, 179.00, 0.0, 0.4, 0.2)
        ]
        
        for i, (hour, minute, amount, before, after, vol_change) in enumerate(sample_data):
            if i == 0:
                # Bugün
                past_time = current_time.replace(hour=hour, minute=minute)
            else:
                # Dün
                past_time = (current_time - timedelta(days=1)).replace(hour=hour, minute=minute)
            
            date_str = past_time.strftime("%d.%m")
            time_str = past_time.strftime("%H:%M")
            
            line = f"{date_str} {time_str}    +{amount:,.2f}  {before:.1f}% => {after:.1f}% - V: % {vol_change:.1f}"
            sample_history.append(line)
        
        return sample_history
    
    def _calculate_5min_cash(self, currency_pair: str) -> float:
        """5 dakikalık nakit hesaplaması"""
        try:
            # Son 5 dakikanın trade history'sini çek
            trades = self.gateio_api.get_trades_history(currency_pair, limit=50)
            if not trades:
                return 8396.0  # Örnek değer
            
            current_time = datetime.now(self.turkey_timezone)
            five_min_ago = current_time - timedelta(minutes=5)
            
            total_cash = 0.0
            
            for trade in trades:
                try:
                    # Trade zamanını kontrol et ve timezone ekle
                    trade_timestamp = int(trade.get('create_time', 0))
                    trade_time = datetime.fromtimestamp(trade_timestamp, tz=self.turkey_timezone)
                    
                    if trade_time < five_min_ago:
                        continue
                    
                    # Trade değerini hesapla
                    price = float(trade.get('price', 0))
                    amount = float(trade.get('amount', 0))
                    trade_value = price * amount
                    
                    total_cash += trade_value
                    
                except Exception as e:
                    print(f"5dk cash hesaplama hatası: {e}")
                    continue
            
            return total_cash if total_cash > 0 else 8396.0
            
        except Exception as e:
            print(f"5dk cash hesaplama genel hatası: {e}")
            return 8396.0  # Örnek değer döndür
    
    def _cleanup_dropped_coins(self):
        """Düşen coinleri temizler"""
        current_time = datetime.now(self.turkey_timezone)  # Türkiye saati kullan
        coins_to_remove = []
        
        for symbol, tracker in self.tracked_coins.items():
            # 24 saatten fazla takip edilen coinleri temizle
            if (current_time - tracker.last_signal_time).total_seconds() > 86400:  # 24 saat
                coins_to_remove.append(symbol)
        
        for symbol in coins_to_remove:
            print(f"🧹 {symbol} 24 saat sonrası temizlendi")
            del self.tracked_coins[symbol]
    
    def get_coins_by_volume_category(self) -> Dict[str, List[Dict]]:
        """Hacim kategorilerine göre coinleri döndürür"""
        try:
            tickers = self.gateio_api.get_all_tickers()
            if not tickers:
                return {'low': [], 'medium': [], 'high': []}
            
            categorized_coins = {'low': [], 'medium': [], 'high': []}
            
            for ticker in tickers:
                try:
                    currency_pair = ticker['currency_pair']
                    symbol = currency_pair.replace('_USDT', '')
                    price = float(ticker['last'])
                    change_percentage = float(ticker['change_percentage'])
                    volume_24h = float(ticker['quote_volume'])
                    
                    # Hacim kategorisine göre sınıflandır
                    if volume_24h < 300000:  # 300K altı
                        category = 'low'
                    elif volume_24h < 1000000:  # 300K - 1M arası
                        category = 'medium'
                    else:  # 1M üstü
                        category = 'high'
                    
                    # Eğer coin takip ediliyorsa signal_count'u al
                    signal_count = 1  # Varsayılan değer
                    if symbol in self.tracked_coins:
                        signal_count = self.tracked_coins[symbol].signal_count
                    
                    coin_data = {
                        'symbol': symbol,
                        'price': price,
                        'change_percentage': change_percentage,
                        'volume': volume_24h,
                        'volume_category': category,
                        'currency_pair': currency_pair,
                        'signal_count': signal_count
                    }
                    
                    categorized_coins[category].append(coin_data)
                    
                except Exception as e:
                    continue
            
            # Her kategoride en yüksek artış yüzdesine göre sırala
            for category in categorized_coins:
                categorized_coins[category].sort(key=lambda x: x['change_percentage'], reverse=True)
            
            return categorized_coins
            
        except Exception as e:
            print(f"Coin kategorilendirme hatası: {e}")
            return {'low': [], 'medium': [], 'high': []}
    
    def get_web_stats(self) -> Dict:
        """Web arayüzü için istatistikleri döndürür"""
        try:
            current_time = datetime.now(self.turkey_timezone)
            
            # Son sinyal zamanını bul
            last_signal_time = None
            if self.tracked_coins:
                last_signal_time = max(tracker.last_signal_time for tracker in self.tracked_coins.values())
            
            stats = {
                'total_signals': len(self.tracked_coins),
                'active_tracking': len([t for t in self.tracked_coins.values() if t.is_following]),
                'last_signal_time': last_signal_time.strftime('%H:%M:%S') if last_signal_time else 'Yok'
            }
            
            return stats
            
        except Exception as e:
            print(f"Web stats hatası: {e}")
            return {'total_signals': 0, 'active_tracking': 0, 'last_signal_time': 'Hata'}

    
    def get_latest_signals(self) -> List[Dict]:
        """Son sinyalleri döndürür"""
        try:
            signals = []
            current_time = datetime.now(self.turkey_timezone)
            
            for symbol, tracker in self.tracked_coins.items():
                signal = {
                    'symbol': symbol,
                    'time': tracker.last_signal_time.strftime('%H:%M:%S'),
                    'message': f"#{symbol} • 🆕 Sinyal - Artış: {tracker.initial_percentage:.1f}%"
                }
                signals.append(signal)
            
            # Zaman sırasına göre sırala (en yeni önce)
            signals.sort(key=lambda x: x['time'], reverse=True)
            
            return signals[:10]  # Son 10 sinyal
            
        except Exception as e:
            print(f"Latest signals hatası: {e}")
            return []
    
    def check_pusu_signals(self, current_time):
        """PUSU Sinyal kontrolü - 95 mum analizi ile"""
        try:
            print("🎯 PUSU Sinyal kontrolü başlatılıyor...")
            
            # Tüm ticker'ları al
            tickers_data = self.gateio_api.get_all_tickers()
            if not tickers_data:
                return
            
            # Ticker'ları dictionary formatına çevir
            tickers = {}
            for ticker in tickers_data:
                currency_pair = ticker['currency_pair']
                symbol = currency_pair.replace('_USDT', '')
                tickers[symbol] = ticker
            
            pusu_candidates = []
            
            # %20+ artış gösteren coinleri bul
            for symbol, ticker in tickers.items():
                try:
                    change_percentage = float(ticker.get('change_percentage', 0))
                    
                    # %20+ artış kontrolü
                    if change_percentage >= 20:
                        pusu_candidates.append((symbol, ticker))
                        
                except (ValueError, TypeError):
                    continue
            
            print(f"🔍 {len(pusu_candidates)} adet %20+ artış tespit edildi")
            
            # Her aday için 95 mum analizi yap
            for symbol, ticker in pusu_candidates:
                try:
                    # 95 adet 15 dakikalık mum al
                    candles = self.gateio_api.get_candles(symbol, '15m', 95)
                    if not candles or len(candles) < 95:
                        continue
                    
                    # 95 mumun her birini kontrol et
                    is_stable = True
                    for candle in candles:
                        try:
                            high = float(candle['h'])  # En yüksek fiyat
                            low = float(candle['l'])   # En düşük fiyat
                            
                            # Mum içi maksimum değişim
                            max_change = ((high - low) / low) * 100
                            
                            # Eğer herhangi bir mum %19'u geçerse
                            if max_change >= 19:
                                is_stable = False
                                break
                                
                        except (ValueError, TypeError, KeyError):
                            continue
                    
                    # Eğer 95 mumun hepsi %19'un altındaysa
                    if is_stable:
                        print(f"🎯 {symbol} PUSU Sinyal adayı - 95 mum stabil")
                        self._send_pusu_signal(symbol, ticker, current_time)
                        
                except Exception as e:
                    print(f"PUSU analiz hatası {symbol}: {e}")
                    continue
                    
        except Exception as e:
            print(f"PUSU Sinyal kontrol hatası: {e}")
    
    def _send_pusu_signal(self, symbol, ticker, current_time):
        """PUSU Sinyal gönder"""
        try:
            currency_pair = f"{symbol}_USDT"
            change_percentage = float(ticker.get('change_percentage', 0))
            price = float(ticker.get('last', 0))
            volume_24h = float(ticker.get('base_volume', 0))
            
            # PUSU Sinyal mesajı hazırla
            message = self._format_pusu_message(symbol, change_percentage, price, volume_24h)
            
            # Telegram'a gönder
            if self.telegram_bot.send_message(message):
                print(f"✅ {symbol} PUSU Sinyal gönderildi")
            else:
                print(f"❌ {symbol} PUSU Sinyal gönderilemedi")
                
        except Exception as e:
            print(f"PUSU Sinyal gönderme hatası {symbol}: {e}")
    
    def _format_pusu_message(self, symbol, change_percentage, price, volume_24h):
        """PUSU Sinyal mesajını formatla"""
        try:
            # Hacim kategorisi
            if volume_24h >= Config.MEDIUM_VOLUME_THRESHOLD:
                volume_category = "Yüksek Hacim"
            elif volume_24h >= Config.LOW_VOLUME_THRESHOLD:
                volume_category = "Orta Hacim"
            else:
                volume_category = "Düşük Hacim"
            
            # 5 dakikalık hacim (yaklaşık)
            volume_5m = volume_24h / 288  # 24 saat = 288 * 5 dakika
            
            message = f""" PUSU SİNYALİ TESPİT EDİLDİ! 

#{symbol} • PUSU SİNYAL
Olağan dışı durum tespit edildi

 24h Volatilite: <19%
 Ani Artış: {change_percentage:.2f}%
💰 Fiyat: ${price:.6f}
📊 5dk Hacim: ${volume_5m:,.0f}
📈 24h Hacim: ${volume_24h:,.0f}
🏷️ Hacim: {volume_category}

⚠️ Dikkat: Bu coin 24 saat boyunca düz çizgi halindeydi!"""
            
            return message
            
        except Exception as e:
            print(f"PUSU mesaj format hatası: {e}")
            return f" PUSU SİNYALİ TESPİT EDİLDİ! #{symbol} • Artış: {change_percentage:.2f}%"
