#!/usr/bin/env python3
"""
Initial data setup for SQLite database
"""

import hashlib
from database import get_db_session, User, BotSetting
from datetime import datetime

def setup_initial_data():
    """Setup initial users and bot settings"""
    print("🚀 Setting up initial data...")
    
    db = get_db_session()
    try:
        # Create users
        users_data = [
            {
                'username': 'murat',
                'password': '123456',  # Will be hashed
                'email': 'murat@signalweb.com'
            },
            {
                'username': 'admin', 
                'password': 'admin123',
                'email': 'admin@signalweb.com'
            },
            {
                'username': 'mannetta',
                'password': 'mannetta123',
                'email': 'mannetta@signalweb.com'
            }
        ]
        
        for user_data in users_data:
            # Check if user exists
            existing_user = db.query(User).filter(User.username == user_data['username']).first()
            if not existing_user:
                # Hash password
                password_hash = hashlib.sha256(user_data['password'].encode()).hexdigest()
                
                user = User(
                    username=user_data['username'],
                    password_hash=password_hash,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(user)
                print(f"✅ Created user: {user_data['username']}")
            else:
                print(f"⚠️ User already exists: {user_data['username']}")
        
        # Create bot settings
        bot_settings = [
            ('bot_status', '1', 'Bot durumu (1: aktif, 0: pasif)'),
            ('initial_pump_threshold', '35', 'İlk sinyal için minimum artış yüzdesi'),
            ('second_signal_threshold', '20', 'İkinci sinyal için ek artış yüzdesi'),
            ('next_signal_threshold', '10', 'Sonraki sinyaller için artış yüzdesi'),
            ('drop_threshold', '25', 'Takipten çıkarma eşiği'),
            ('low_volume_threshold', '100000', 'Düşük hacim eşiği'),
            ('medium_volume_threshold', '300000', 'Orta hacim eşiği'),
            ('min_trade_amount', '100', 'Minimum işlem miktarı'),
            ('telegram_bot_token', '7649876404:AAHCFuUJQlRcVKGwQCGN653_KlRkAYZNBjE', 'Telegram bot token'),
            ('telegram_group_id', '-4887711321', 'Telegram grup ID'),
            ('scan_interval', '15', 'Tarama aralığı (saniye)'),
            ('followup_interval', '45', 'Takip aralığı (saniye)'),
            ('telegram_enabled', '1', 'Telegram mesaj gönderimi (1: açık, 0: kapalı)')
        ]
        
        for key, value, description in bot_settings:
            # Check if setting exists
            existing_setting = db.query(BotSetting).filter(BotSetting.setting_key == key).first()
            if not existing_setting:
                setting = BotSetting(
                    setting_key=key,
                    setting_value=value,
                    description=description,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(setting)
                print(f"✅ Created setting: {key}")
            else:
                print(f"⚠️ Setting already exists: {key}")
        
        db.commit()
        print("✅ Initial data setup completed successfully!")
        
    except Exception as e:
        print(f"❌ Error setting up initial data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    setup_initial_data()
