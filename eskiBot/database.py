"""
SQLite Database Models and Connection
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Database file path
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///signal_bot.db')

# Create engine
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BotSetting(Base):
    __tablename__ = "bot_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String(100), unique=True, index=True, nullable=False)
    setting_value = Column(Text, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Signal(Base):
    __tablename__ = "signals"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    currency_pair = Column(String(20), nullable=False)
    signal_type = Column(String(20), default='new')  # new, second, third, pusu, special_up, special_down
    price = Column(Float, nullable=False)
    percentage = Column(Float, nullable=False)
    initial_percentage = Column(Float, nullable=False)
    volume_24h = Column(Float, nullable=False)
    volume_category = Column(String(10), nullable=False)  # low, medium, high
    trades_history = Column(Text)  # JSON string
    cash_5min = Column(Float, default=0)
    volatility_24h = Column(Float, default=0)  # For pusu signals
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Indexes for better performance
    __table_args__ = (
        {'sqlite_autoincrement': True}
    )

class TrackedCoin(Base):
    __tablename__ = "tracked_coins"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, index=True, nullable=False)
    currency_pair = Column(String(20), nullable=False)
    base_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    initial_percentage = Column(Float, nullable=False)
    current_percentage = Column(Float, nullable=False)
    previous_signal_percentage = Column(Float, default=0)
    signal_count = Column(Integer, default=1)
    last_signal_time = Column(DateTime, default=datetime.utcnow)
    last_scan_time = Column(DateTime, default=datetime.utcnow)
    is_following = Column(Boolean, default=True)
    volume_24h = Column(Float, nullable=False)
    below_threshold_at = Column(DateTime)  # When it dropped below 35%
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SpecialWatchlist(Base):
    __tablename__ = "special_watchlist"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, index=True, nullable=False)
    currency_pair = Column(String(20), nullable=False)
    base_price = Column(Float)  # NULL until first signal
    last_price = Column(Float)
    last_percentage = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TradeHistory(Base):
    __tablename__ = "trade_history"
    
    id = Column(Integer, primary_key=True, index=True)
    currency_pair = Column(String(20), nullable=False, index=True)
    trade_time = Column(DateTime, nullable=False, index=True)
    trade_value = Column(Float, nullable=False)
    trade_percentage = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class BotLog(Base):
    __tablename__ = "bot_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(10), nullable=False, index=True)  # INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    details = Column(Text)  # JSON string for additional data
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

# Database functions
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

def get_db_session():
    """Get database session for direct use"""
    return SessionLocal()

def migrate_from_mysql():
    """Migrate data from MySQL to SQLite"""
    # This function will be implemented to migrate existing data
    pass

# Initialize database on import
if __name__ == "__main__":
    init_database()
