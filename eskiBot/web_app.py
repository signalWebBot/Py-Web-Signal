"""
Flask Web Uygulaması - Signal Bot Dashboard
"""

from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_socketio import SocketIO, emit
import threading
import time
import os
import json
from datetime import datetime, timezone, timedelta
from signal_manager import SignalManager
from gateio_api import GateioAPI
from config import Config
from database import get_db_session, init_database, Signal, TrackedCoin, BotSetting, User
import hashlib

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'signal-bot-secret-key-2024')
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize database
init_database()

# Global değişkenler
signal_manager = None
web_data = {
    'signals': [],
    'tracked_coins': [],
    'bot_status': 'stopped',
    'last_update': None,
    'stats': {
        'total_signals': 0,
        'active_tracking': 0,
        'last_signal_time': 'Yok'
    }
}

def create_signal_manager():
    """Signal manager oluşturur"""
    global signal_manager
    if signal_manager is None:
        gateio_api = GateioAPI()
        signal_manager = SignalManager(gateio_api)
        # Web callback'i ayarla
        signal_manager.set_web_callback(web_signal_callback)
    return signal_manager

def web_signal_callback(signal_data):
    """Web arayüzüne sinyal bildirimi"""
    try:
        # Sinyali database'e kaydet
        db = get_db_session()
        try:
            signal = Signal(
                symbol=signal_data['symbol'],
                currency_pair=signal_data['currency_pair'],
                signal_type=signal_data.get('signal_type', 'new'),
                price=signal_data['price'],
                percentage=signal_data['percentage'],
                initial_percentage=signal_data['initial_percentage'],
                volume_24h=signal_data['volume_24h'],
                volume_category=signal_data['volume_category'],
                trades_history=json.dumps(signal_data.get('trades_history', [])),
                cash_5min=signal_data.get('cash_5min', 0),
                volatility_24h=signal_data.get('volatility_24h', 0)
            )
            db.add(signal)
            db.commit()
        finally:
            db.close()
        
        # Sinyali web_data'ya ekle
        web_data['signals'].insert(0, signal_data)
        if len(web_data['signals']) > 100:  # Son 100 sinyali tut
            web_data['signals'] = web_data['signals'][:100]
        
        # Web socket ile real-time bildirim
        socketio.emit('new_signal', signal_data)
        
        # İstatistikleri güncelle
        update_web_stats()
        
    except Exception as e:
        print(f"Web callback hatası: {e}")

def update_web_stats():
    """Web istatistiklerini güncelle"""
    try:
        if signal_manager:
            web_data['stats'] = signal_manager.get_web_stats()
            web_data['tracked_coins'] = list(signal_manager.tracked_coins.values())
            web_data['last_update'] = datetime.now(timezone(timedelta(hours=3))).strftime('%H:%M:%S')
    except Exception as e:
        print(f"Stats güncelleme hatası: {e}")

@app.route('/')
def index():
    """Ana sayfa"""
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Giriş sayfası"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Database'den kullanıcı kontrolü
        db = get_db_session()
        try:
            user = db.query(User).filter(User.username == username).first()
            if user and user.password_hash == hashlib.sha256(password.encode()).hexdigest():
                session['username'] = username
                return redirect(url_for('index'))
            else:
                return render_template('login.html', error='Kullanıcı adı veya şifre hatalı')
        finally:
            db.close()
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Çıkış"""
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/api/signals')
def api_signals():
    """Sinyaller API"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    db = get_db_session()
    try:
        # Son 100 sinyali çek
        signals = db.query(Signal).order_by(Signal.created_at.desc()).limit(100).all()
        
        signals_data = []
        for signal in signals:
            signals_data.append({
                'id': signal.id,
                'symbol': signal.symbol,
                'currency_pair': signal.currency_pair,
                'signal_type': signal.signal_type,
                'price': signal.price,
                'percentage': signal.percentage,
                'initial_percentage': signal.initial_percentage,
                'volume_24h': signal.volume_24h,
                'volume_category': signal.volume_category,
                'trades_history': signal.trades_history,
                'cash_5min': signal.cash_5min,
                'volatility_24h': signal.volatility_24h,
                'timestamp': signal.created_at.isoformat()
            })
        
        return jsonify({
            'signals': signals_data,
            'stats': web_data['stats'],
            'last_update': web_data['last_update']
        })
    finally:
        db.close()

@app.route('/api/tracked')
def api_tracked():
    """Takip edilen coinler API"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    return jsonify({
        'tracked_coins': web_data['tracked_coins'],
        'stats': web_data['stats']
    })

@app.route('/api/bot/start', methods=['POST'])
def api_bot_start():
    """Bot başlatma API"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        if web_data['bot_status'] == 'running':
            return jsonify({'status': 'already_running'})
        
        # Bot'u ayrı thread'de başlat
        def start_bot():
            global signal_manager
            signal_manager = create_signal_manager()
            web_data['bot_status'] = 'running'
            signal_manager.start_monitoring()
        
        bot_thread = threading.Thread(target=start_bot, daemon=True)
        bot_thread.start()
        
        return jsonify({'status': 'started'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bot/stop', methods=['POST'])
def api_bot_stop():
    """Bot durdurma API"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        web_data['bot_status'] = 'stopped'
        # Bot'u durdurma mantığı burada olacak
        return jsonify({'status': 'stopped'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bot/status')
def api_bot_status():
    """Bot durumu API"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    return jsonify({
        'status': web_data['bot_status'],
        'stats': web_data['stats'],
        'last_update': web_data['last_update']
    })

@app.route('/signals')
def signals_page():
    """Sinyaller sayfası"""
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('signals.html')

@app.route('/tracked')
def tracked_page():
    """Takip edilenler sayfası"""
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('tracked.html')

@app.route('/special')
def special_page():
    """Özel takip sayfası"""
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('special.html')

@app.route('/pusu_signals')
def pusu_signals_page():
    """Pusu sinyalleri sayfası"""
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('pusu_signals.html')

@app.route('/settings')
def settings_page():
    """Ayarlar sayfası"""
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('settings.html')

@socketio.on('connect')
def handle_connect():
    """WebSocket bağlantısı"""
    print('Client connected')
    emit('status', {'status': web_data['bot_status']})

@socketio.on('disconnect')
def handle_disconnect():
    """WebSocket bağlantı kesilmesi"""
    print('Client disconnected')

def start_web_server():
    """Web sunucusunu başlatır"""
    print("🌐 Web sunucusu başlatılıyor...")
    print("📱 Dashboard: http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    start_web_server()
