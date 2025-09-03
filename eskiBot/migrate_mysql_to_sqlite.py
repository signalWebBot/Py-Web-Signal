#!/usr/bin/env python3
"""
MySQL to SQLite Migration Script
Migrates data from existing MySQL database to SQLite
"""

import mysql.connector
import sqlite3
import json
from datetime import datetime
from database import get_db_session, BotSetting, User, Signal, TrackedCoin, SpecialWatchlist, TradeHistory, BotLog

# MySQL connection settings
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '4AX5my789',  # Your MySQL password
    'database': 'signal_web',
    'charset': 'utf8mb4'
}

def connect_mysql():
    """Connect to MySQL database"""
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        return connection
    except mysql.connector.Error as e:
        print(f"❌ MySQL connection error: {e}")
        return None

def migrate_users():
    """Migrate users table"""
    print("🔄 Migrating users...")
    
    mysql_conn = connect_mysql()
    if not mysql_conn:
        return False
    
    try:
        cursor = mysql_conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        
        db = get_db_session()
        migrated_count = 0
        
        for user in users:
            # Check if user already exists
            existing_user = db.query(User).filter(User.username == user['username']).first()
            if not existing_user:
                new_user = User(
                    id=user['id'],
                    username=user['username'],
                    password_hash=user['password_hash'],
                    created_at=user['created_at'],
                    updated_at=user['updated_at']
                )
                db.add(new_user)
                migrated_count += 1
        
        db.commit()
        print(f"✅ Migrated {migrated_count} users")
        return True
        
    except Exception as e:
        print(f"❌ Users migration error: {e}")
        db.rollback()
        return False
    finally:
        mysql_conn.close()
        db.close()

def migrate_bot_settings():
    """Migrate bot_settings table"""
    print("🔄 Migrating bot settings...")
    
    mysql_conn = connect_mysql()
    if not mysql_conn:
        return False
    
    try:
        cursor = mysql_conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM bot_settings")
        settings = cursor.fetchall()
        
        db = get_db_session()
        migrated_count = 0
        
        for setting in settings:
            # Check if setting already exists
            existing_setting = db.query(BotSetting).filter(BotSetting.setting_key == setting['setting_key']).first()
            if not existing_setting:
                new_setting = BotSetting(
                    id=setting['id'],
                    setting_key=setting['setting_key'],
                    setting_value=setting['setting_value'],
                    description=setting['description'],
                    created_at=setting['created_at'],
                    updated_at=setting['updated_at']
                )
                db.add(new_setting)
                migrated_count += 1
        
        db.commit()
        print(f"✅ Migrated {migrated_count} bot settings")
        return True
        
    except Exception as e:
        print(f"❌ Bot settings migration error: {e}")
        db.rollback()
        return False
    finally:
        mysql_conn.close()
        db.close()

def migrate_signals():
    """Migrate signals table"""
    print("🔄 Migrating signals...")
    
    mysql_conn = connect_mysql()
    if not mysql_conn:
        return False
    
    try:
        cursor = mysql_conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM signals ORDER BY created_at DESC LIMIT 1000")  # Last 1000 signals
        signals = cursor.fetchall()
        
        db = get_db_session()
        migrated_count = 0
        
        for signal in signals:
            # Check if signal already exists (by symbol and created_at)
            existing_signal = db.query(Signal).filter(
                Signal.symbol == signal['symbol'],
                Signal.created_at == signal['created_at']
            ).first()
            
            if not existing_signal:
                new_signal = Signal(
                    id=signal['id'],
                    symbol=signal['symbol'],
                    currency_pair=signal['currency_pair'],
                    signal_type=signal.get('signal_type', 'new'),
                    price=signal['price'],
                    percentage=signal['percentage'],
                    initial_percentage=signal['initial_percentage'],
                    volume_24h=signal['volume_24h'],
                    volume_category=signal['volume_category'],
                    trades_history=signal.get('trades_history'),
                    cash_5min=signal.get('cash_5min', 0),
                    volatility_24h=signal.get('volatility_24h', 0),
                    created_at=signal['created_at']
                )
                db.add(new_signal)
                migrated_count += 1
        
        db.commit()
        print(f"✅ Migrated {migrated_count} signals")
        return True
        
    except Exception as e:
        print(f"❌ Signals migration error: {e}")
        db.rollback()
        return False
    finally:
        mysql_conn.close()
        db.close()

def migrate_tracked_coins():
    """Migrate tracked_coins table"""
    print("🔄 Migrating tracked coins...")
    
    mysql_conn = connect_mysql()
    if not mysql_conn:
        return False
    
    try:
        cursor = mysql_conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tracked_coins")
        tracked_coins = cursor.fetchall()
        
        db = get_db_session()
        migrated_count = 0
        
        for coin in tracked_coins:
            # Check if coin already exists
            existing_coin = db.query(TrackedCoin).filter(TrackedCoin.symbol == coin['symbol']).first()
            if not existing_coin:
                new_coin = TrackedCoin(
                    id=coin['id'],
                    symbol=coin['symbol'],
                    currency_pair=coin['currency_pair'],
                    base_price=coin['base_price'],
                    current_price=coin['current_price'],
                    initial_percentage=coin['initial_percentage'],
                    current_percentage=coin['current_percentage'],
                    previous_signal_percentage=coin.get('previous_signal_percentage', 0),
                    signal_count=coin.get('signal_count', 1),
                    last_signal_time=coin['last_signal_time'],
                    last_scan_time=coin['last_scan_time'],
                    is_following=coin.get('is_following', True),
                    volume_24h=coin['volume_24h'],
                    below_threshold_at=coin.get('below_threshold_at'),
                    created_at=coin['created_at'],
                    updated_at=coin['updated_at']
                )
                db.add(new_coin)
                migrated_count += 1
        
        db.commit()
        print(f"✅ Migrated {migrated_count} tracked coins")
        return True
        
    except Exception as e:
        print(f"❌ Tracked coins migration error: {e}")
        db.rollback()
        return False
    finally:
        mysql_conn.close()
        db.close()

def migrate_special_watchlist():
    """Migrate special_watchlist table"""
    print("🔄 Migrating special watchlist...")
    
    mysql_conn = connect_mysql()
    if not mysql_conn:
        return False
    
    try:
        cursor = mysql_conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM special_watchlist")
        watchlist = cursor.fetchall()
        
        db = get_db_session()
        migrated_count = 0
        
        for item in watchlist:
            # Check if item already exists
            existing_item = db.query(SpecialWatchlist).filter(SpecialWatchlist.symbol == item['symbol']).first()
            if not existing_item:
                new_item = SpecialWatchlist(
                    id=item['id'],
                    symbol=item['symbol'],
                    currency_pair=item['currency_pair'],
                    base_price=item.get('base_price'),
                    last_price=item.get('last_price'),
                    last_percentage=item.get('last_percentage', 0),
                    created_at=item['created_at'],
                    updated_at=item['updated_at']
                )
                db.add(new_item)
                migrated_count += 1
        
        db.commit()
        print(f"✅ Migrated {migrated_count} special watchlist items")
        return True
        
    except Exception as e:
        print(f"❌ Special watchlist migration error: {e}")
        db.rollback()
        return False
    finally:
        mysql_conn.close()
        db.close()

def main():
    """Main migration function"""
    print("🚀 Starting MySQL to SQLite migration...")
    print("=" * 50)
    
    # Initialize SQLite database
    from database import init_database
    init_database()
    
    # Migrate tables
    success = True
    success &= migrate_users()
    success &= migrate_bot_settings()
    success &= migrate_signals()
    success &= migrate_tracked_coins()
    success &= migrate_special_watchlist()
    
    if success:
        print("=" * 50)
        print("✅ Migration completed successfully!")
        print("📁 SQLite database: signal_bot.db")
    else:
        print("=" * 50)
        print("❌ Migration completed with errors!")
    
    return success

if __name__ == "__main__":
    main()
