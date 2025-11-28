from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Silahkan login terlebih dahulu", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from models import User

            user_id = session.get('user_id')
            if not user_id:
                flash("Silahkan login terlebih dahulu", "warning")
                return redirect(url_for('login'))

            user = User.query.get(user_id)
            if not user or user.role != role:
                flash("Akses ditolak", "danger")
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu', 'warning')
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('Anda tidak memiliki akses ke halaman ini', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function
