from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pytz

db = SQLAlchemy()
jakarta = pytz.timezone('Asia/Jakarta')

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='user')  # admin / user
    active_until = db.Column(db.DateTime, nullable=True)
    session_id = db.Column(db.String(255), nullable=True)
    last_activity = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_active(self):
        if self.active_until:
            now = datetime.now(jakarta)
            # Jika active_until tidak punya timezone, tambahkan info timezone Jakarta
            if self.active_until.tzinfo is None:
                active_until = jakarta.localize(self.active_until)
            else:
                active_until = self.active_until
            return now <= active_until

        return True

class Favorite(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    kode_tender = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(20), nullable=False, default='tender')  # 'tender' or 'nontender'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(jakarta))

    user = db.relationship('User', backref=db.backref('favorites', lazy=True))

    __table_args__ = (db.UniqueConstraint('user_id', 'kode_tender', 'type', name='unique_user_favorite_type'),)
