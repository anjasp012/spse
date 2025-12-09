from flask import Flask, session, redirect, url_for, flash, request
from config import Config
from models import db, User
from routes import create_routes
from logger import setup_logger
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)
app.config.from_object(Config)

# Setup logging
logger = setup_logger(app)

db.init_app(app)

create_routes(app)


# ============================================================
#  MIDDLEWARE CEK ACTIVE_UNTIL & IDLE TIMEOUT (WIB)
# ============================================================
MAX_IDLE_MINUTES = 30  # user akan di-logout jika idle lebih dari ini
JAKARTA_TZ = pytz.timezone('Asia/Jakarta')

@app.before_request
def check_user_session():
    # Abaikan halaman login, register, logout, static
    if request.endpoint in ['login', 'register', 'static', 'logout']:
        return

    user_id = session.get('user_id')
    session_id = session.get('session_id')

    if not user_id or not session_id:
        return

    user = User.query.get(user_id)
    if not user:
        user = User.query.filter_by(id=session['user_id']).first()
        if user:
            user.session_id = None
            user.last_activity = None
            db.session.commit()
        session.clear()
        return redirect(url_for('login'))

    # 1. Cek session masih valid (tidak login di device lain)
    if user.session_id != session_id and user.role != 'admin':
        user = User.query.filter_by(id=session['user_id']).first()
        if user:
            user.session_id = None
            user.last_activity = None
            db.session.commit()
        session.clear()
        flash('Sesi Anda sudah tidak valid. Silakan login ulang.', 'warning')
        return redirect(url_for('login'))

    # Waktu sekarang WIB
    now_wib = datetime.now(JAKARTA_TZ)

    # 2. Cek active_until (subscription / langganan) tetap pakai UTC
    utc_now = datetime.utcnow()
    if user.active_until and utc_now > user.active_until:
        user = User.query.filter_by(id=session['user_id']).first()
        if user:
            user.session_id = None
            user.last_activity = None
            db.session.commit()
        session.clear()
        flash('Akun Anda sudah kadaluarsa. Silakan perpanjang langganan.', 'warning')
        return redirect(url_for('login'))

    # 3. Cek idle timeout (pakai WIB)
    if user.last_activity:
        # pastikan last_activity juga aware timezone WIB
        if user.last_activity.tzinfo is None:
            last_activity_wib = pytz.utc.localize(user.last_activity).astimezone(JAKARTA_TZ)
        else:
            last_activity_wib = user.last_activity

        idle_time = (now_wib - last_activity_wib).total_seconds() / 60  # menit
        if idle_time > MAX_IDLE_MINUTES:
            user = User.query.filter_by(id=session['user_id']).first()
            if user:
                user.session_id = None
                user.last_activity = None
                db.session.commit()
            session.clear()
            flash(f'Sesi Anda idle lebih dari {MAX_IDLE_MINUTES} menit. Silakan login kembali.', 'warning')
            return redirect(url_for('login'))

    # 4. Update last_activity tiap request (WIB)
    user.last_activity = now_wib
    db.session.commit()


# ============================================================
#  RUN APP
# ============================================================
if __name__ == "__main__":
    app.run(debug=True)
