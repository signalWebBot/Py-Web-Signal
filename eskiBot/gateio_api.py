"""
Gate.io API entegrasyonu
"""

import requests
import json
from typing import Dict, List, Optional
from datetime import datetime
from config import Config

class GateioAPI:
    def __init__(self):
        self.base_url = Config.GATEIO_BASE_URL
        self.session = requests.Session()
        
    def get_all_tickers(self) -> Optional[List[Dict]]:
        """Tüm coinlerin fiyat bilgilerini çeker"""
        try:
            url = f"{self.base_url}/spot/tickers"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Blacklist kontrolü ve filtreleme
            filtered_tickers = []
            for ticker in data:
                currency_pair = ticker['currency_pair']
                
                # USDT paritesi olmayanları filtrele
                if not currency_pair.endswith('_USDT'):
                    continue
                    
                # Blacklist kontrolü
                symbol = currency_pair.replace('_USDT', '')
                if self._is_blacklisted(symbol):
                    continue
                    
                filtered_tickers.append(ticker)
                
            return filtered_tickers
            
        except requests.exceptions.RequestException as e:
            print(f"API hatası: {e}")
            return None
        except Exception as e:
            print(f"Beklenmeyen hata: {e}")
            return None
    
    def get_ticker_detail(self, currency_pair: str) -> Optional[Dict]:
        """Belirli bir coin için detaylı bilgi çeker"""
        try:
            url = f"{self.base_url}/spot/tickers"
            params = {"currency_pair": currency_pair}
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data[0] if data else None
            
        except requests.exceptions.RequestException as e:
            print(f"Ticker detay hatası ({currency_pair}): {e}")
            return None
        except Exception as e:
            print(f"Beklenmeyen hata ({currency_pair}): {e}")
            return None
    
    def get_trades_history(self, currency_pair: str, limit: int = 100) -> Optional[List[Dict]]:
        """Son işlem geçmişini çeker"""
        try:
            url = f"{self.base_url}/spot/trades"
            params = {
                "currency_pair": currency_pair,
                "limit": limit
            }
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Trade history hatası ({currency_pair}): {e}")
            return None
        except Exception as e:
            print(f"Beklenmeyen hata ({currency_pair}): {e}")
            return None
    
    def get_volume_data(self, currency_pair: str) -> Optional[Dict]:
        """Hacim ve fiyat değişim bilgilerini çeker"""
        try:
            url = f"{self.base_url}/spot/tickers"
            params = {"currency_pair": currency_pair}
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if not data:
                return None
                
            ticker = data[0]
            
            # Hacim ve değişim oranları
            volume_24h = float(ticker.get('quote_volume', 0))
            change_percentage = float(ticker.get('change_percentage', 0))
            
            return {
                'volume_24h': volume_24h,
                'change_percentage': change_percentage,
                'last_price': float(ticker.get('last', 0)),
                'high_24h': float(ticker.get('high_24h', 0)),
                'low_24h': float(ticker.get('low_24h', 0))
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Volume data hatası ({currency_pair}): {e}")
            return None
        except Exception as e:
            print(f"Beklenmeyen hata ({currency_pair}): {e}")
            return None
    
    def _is_blacklisted(self, symbol: str) -> bool:
        """Coin'in blacklist'te olup olmadığını kontrol eder"""
        symbol_upper = symbol.upper()
        
        for pattern in Config.BLACKLISTED_PATTERNS:
            if pattern in symbol_upper:
                return True
                
        return False
    
    def calculate_percentage_change(self, current_price: float, base_price: float) -> float:
        """Fiyat değişim yüzdesini hesaplar"""
        if base_price == 0:
            return 0.0
            
        return ((current_price - base_price) / base_price) * 100
    
    def format_volume(self, volume: float) -> str:
        """Hacmi okunabilir formatta döndürür"""
        if volume >= 1000000:
            return f"{volume / 1000000:.1f}M"
        elif volume >= 1000:
            return f"{volume / 1000:.0f}k"
        else:
            return f"{volume:.0f}"
    
    def get_volume_category(self, volume: float) -> str:
        """Hacim kategorisini belirler"""
        if volume < Config.LOW_VOLUME_THRESHOLD:
            return "--- Düşük Hacim ---"
        elif volume < Config.MEDIUM_VOLUME_THRESHOLD:
            return "--- Orta Hacim ---"
        else:
            return "--- Yüksek Hacim ---"
    
    def get_candles(self, symbol: str, interval: str = '15m', limit: int = 100) -> Optional[List[Dict]]:
        """Belirli bir coin için mum verilerini çeker"""
        try:
            currency_pair = f"{symbol}_USDT"
            url = f"{self.base_url}/spot/candlesticks"
            
            params = {
                'currency_pair': currency_pair,
                'interval': interval,
                'limit': limit
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Gate.io mum formatı: [timestamp, volume, close, high, low, open]
            candles = []
            for candle_data in data:
                if len(candle_data) >= 6:
                    candle = {
                        't': int(candle_data[0]),  # timestamp
                        'v': float(candle_data[1]),  # volume
                        'c': float(candle_data[2]),  # close
                        'h': float(candle_data[3]),  # high
                        'l': float(candle_data[4]),  # low
                        'o': float(candle_data[5])   # open
                    }
                    candles.append(candle)
            
            return candles
            
        except requests.exceptions.RequestException as e:
            print(f"Candles API hatası ({symbol}): {e}")
            return None
        except Exception as e:
            print(f"Candles beklenmeyen hata ({symbol}): {e}")
            return None