from app import app
from models import db, User
from config import Config
from datetime import datetime, timedelta
import pytz

jakarta = pytz.timezone('Asia/Jakarta')

with app.app_context():
    now = datetime.now(jakarta)  # ✅ Gunakan timezone Jakarta
    inactive_threshold = timedelta(minutes=Config.SESSION_TIMEOUT_MINUTES)  # Dari config

    # Hapus session user yang sudah idle
    expired_users = User.query.filter(
        (User.last_activity != None) &
        (User.last_activity < now - inactive_threshold) &
        (User.role != 'admin')
    ).all()

    for user in expired_users:
        print(f"[{now}] Logout otomatis: {user.username}")
        user.session_id = None

    # Nonaktifkan akun yang masa aktifnya habis
    expired_accounts = User.query.filter(
        (User.active_until != None) &
        (User.active_until < now) &
        (User.role != 'admin')
    ).all()

    for user in expired_accounts:
        print(f"[{now}] Akun kadaluarsa: {user.username}")
        user.session_id = None

    db.session.commit()
    print(f"[{now}] {len(expired_users)} sesi idle & {len(expired_accounts)} akun expired dibersihkan.")
