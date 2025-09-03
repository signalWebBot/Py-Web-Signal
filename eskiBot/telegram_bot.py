"""
Telegram Bot entegrasyonu
"""

import requests
import json
from typing import Dict, List
from datetime import datetime, timezone, timedelta
from config import Config

class TelegramBot:
    def __init__(self):
        self.bot_token = Config.TELEGRAM_BOT_TOKEN
        self.group_id = Config.TELEGRAM_GROUP_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def send_signal(self, signal_data: Dict) -> bool:
        """Formatlanmış sinyal mesajı gönderir"""
        try:
            message = self._format_signal_message(signal_data)
            return self._send_message(message)
        except Exception as e:
            print(f"Sinyal gönderme hatası: {e}")
            return False
    
    def _format_signal_message(self, data: Dict) -> str:
        """Sinyal mesajını formatlar"""
        symbol = data['symbol']
        signal_type = data['signal_type']  # 'new', 'second', 'third', etc.
        price = data['price']
        percentage = data['percentage']
        volume_24h = data['volume_24h']
        volume_category = data['volume_category']
        trades_history = data.get('trades_history', [])
        cash_5min = data.get('cash_5min', 0)
        
        # Başlık ve sinyal türü
        if signal_type == 'new':
            header = f"#{symbol} • 🆕 Sinyal"
        else:
            signal_num = data.get('signal_number', 2)  # Sinyal numarasını al
            signal_number_emoji = self._get_signal_number(signal_type, signal_num)
            header = f"#{symbol} • {signal_number_emoji}. Sinyal"
        
        # Ana bilgiler - Artış yüzdesi en üstte
        message_parts = [
            volume_category,
            "",
            header,
        ]
        
        # Artış yüzdesi formatı - EN ÜSTTE
        if signal_type == 'new':
            message_parts.append(f"Artış Yüzdesi: %+{percentage:.2f}")
        else:
            # 3. sinyalden itibaren bir önceki sinyalin yüzdesini göster
            signal_number = data.get('signal_number', 2)
            if signal_number >= 3:
                previous_percentage = data.get('previous_percentage', percentage)
                message_parts.append(f"Artış Yüzdesi: %+{previous_percentage:.2f} --> %{percentage:.2f}")
            else:
                initial_percentage = data.get('initial_percentage', percentage)
                message_parts.append(f"Artış Yüzdesi: %+{initial_percentage:.2f} --> %{percentage:.2f}")
            
            # 2. sinyal ve sonrasında ilk sinyal yüzdesini ekle
            initial_percentage = data.get('initial_percentage', percentage)
            message_parts.append(f"İlk Sinyal: %{initial_percentage:.2f}")
        
        message_parts.extend([
            "",
            f"🎯 Fiyat: ${price:.8f}",
            f"💰 5dk Nakit: ${cash_5min:,.0f}",
            f"📊 24s Hacim: {self._format_volume(volume_24h)}",
        ])
        
        # Trade history sadece düşük ve orta hacimli coinlerde göster
        if not volume_category.startswith("--- Yüksek Hacim"):
            message_parts.extend([
                "",
                "----------------------------"
            ])
            # Trade history
            for trade in trades_history:
                message_parts.append(trade)
        else:
            # Yüksek hacimli coinlerde sadece boş satır ekle
            message_parts.append("")
        
        # Analiz zamanı - UTC'den Türkiye saatine çevir
        utc_now = datetime.now(timezone.utc)
        turkey_timezone = timezone(timedelta(hours=3))
        turkey_time = utc_now.astimezone(turkey_timezone)
        current_time = turkey_time.strftime("%H:%M:%S")
        message_parts.extend([
            "",
            f"🕐 Analiz: {current_time} • Gate.io"
        ])
        
        return "\n".join(message_parts)
    
    def _get_signal_number(self, signal_type: str, signal_number: int = None) -> str:
        """Sinyal numarasını emoji formatında döndürür"""
        emoji_numbers = {
            'second': '2️⃣',
            'third': '3️⃣',
            'fourth': '4️⃣',
            'fifth': '5️⃣',
            'sixth': '6️⃣',
            'seventh': '7️⃣',
            'eighth': '8️⃣',
            'ninth': '9️⃣',
        }
        
        # 10'dan büyük sayılar için
        if signal_number and signal_number >= 10:
            return self._get_double_digit_emoji(signal_number)
        
        return emoji_numbers.get(signal_type, '🔟')
    
    def _get_double_digit_emoji(self, number: int) -> str:
        """10+ sayılar için çift emoji döndürür"""
        digit_emojis = {
            '0': '0️⃣', '1': '1️⃣', '2': '2️⃣', '3': '3️⃣', '4': '4️⃣',
            '5': '5️⃣', '6': '6️⃣', '7': '7️⃣', '8': '8️⃣', '9': '9️⃣'
        }
        
        number_str = str(number)
        emoji_result = ""
        
        for digit in number_str:
            emoji_result += digit_emojis.get(digit, digit)
        
        return emoji_result
    
    def _format_volume(self, volume: float) -> str:
        """Hacmi formatlar"""
        if volume >= 1000000:
            return f"{volume / 1000000:.1f}M"
        elif volume >= 1000:
            return f"{volume / 1000:.0f}k"
        else:
            return f"{volume:.0f}"
    
    def _send_message(self, message: str) -> bool:
        """Telegram'a mesaj gönderir"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.group_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get('ok'):
                print(f"Sinyal başarıyla gönderildi: {message[:50]}...")
                return True
            else:
                print(f"Telegram API hatası: {result}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"Telegram bağlantı hatası: {e}")
            return False
        except Exception as e:
            print(f"Mesaj gönderme hatası: {e}")
            return False
    
    def send_test_message(self) -> bool:
        """Test mesajı gönderir"""
        test_message = "🤖 Gate.io Sinyal Botu aktif edildi!"
        return self._send_message(test_message)
    
    def format_trade_history_line(self, trade_data: Dict) -> str:
        """Trade history satırını formatlar"""
        # Örnek format: "08.08 04:24    +5.355,97  66,4% => 71,6% - V: % 15,9"
        date_str = trade_data.get('date', '00.00')
        time_str = trade_data.get('time', '00:00')
        amount = trade_data.get('amount', 0)
        before_change = trade_data.get('before_change', 0)
        after_change = trade_data.get('after_change', 0)
        volume_change = trade_data.get('volume_change', 0)
        
        return f"{date_str} {time_str}    +{amount:,.2f}  {before_change:.1f}% => {after_change:.1f}% - V: % {volume_change:.1f}"
