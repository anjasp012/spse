from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from models import db, User, Favorite
from utils import login_required, role_required
from modules.redis_tender import fetch as redis_tender
from modules.redis_nontender import fetch as redis_nontender
from modules.fetch_tender import fetch as fetch_tender
from modules.fetch_nontender import fetch as fetch_nontender
from datetime import datetime, timedelta
import uuid
import pytz

jakarta = pytz.timezone('Asia/Jakarta')

def create_routes(app):

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            try:
                username = request.form.get('username', '').strip()
                password = request.form.get('password', '')
                duration = request.form.get('duration', '')

                # Validasi input
                if not username or not password:
                    flash('Username dan password harus diisi', 'danger')
                    return redirect(url_for('register'))

                if len(username) < 3:
                    flash('Username minimal 3 karakter', 'danger')
                    return redirect(url_for('register'))

                if len(password) < 6:
                    flash('Password minimal 6 karakter', 'danger')
                    return redirect(url_for('register'))

                # Cek apakah username sudah ada
                if User.query.filter_by(username=username).first():
                    flash('Username sudah terdaftar', 'danger')
                    return redirect(url_for('register'))

                # Tentukan lama aktif berdasarkan pilihan
                now = datetime.now(jakarta)
                if duration == '3hari':
                    active_until = now + timedelta(days=3)
                elif duration == '6hari':
                    active_until = now + timedelta(days=6)
                elif duration == '1bulan':
                    active_until = now + timedelta(days=30)
                else:
                    active_until = None

                user = User(username=username, role='user', active_until=active_until)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()

                app.logger.info(f"User registered: {username}")
                flash('Registrasi berhasil! Silakan login.', 'success')
                return redirect(url_for('login'))

            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Registration error: {str(e)}")
                flash('Terjadi kesalahan saat registrasi. Silakan coba lagi.', 'danger')
                return redirect(url_for('register'))

        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            try:
                username = request.form.get('username', '').strip()
                password = request.form.get('password', '')

                # Validasi input
                if not username or not password:
                    flash('Username dan password harus diisi', 'danger')
                    return redirect(url_for('login'))

                user = User.query.filter_by(username=username).first()

                if not user:
                    flash('User tidak ditemukan', 'danger')
                    return redirect(url_for('login'))

                if not user.check_password(password):
                    flash('Password salah', 'danger')
                    return redirect(url_for('login'))

                if not user.is_active():
                    flash('Akun sudah kadaluarsa', 'danger')
                    return redirect(url_for('login'))

                # 🔒 Cek apakah user sedang login di tempat lain (kecuali admin)
                if user.session_id and user.role != 'admin':
                    flash('Akun ini sudah login di perangkat lain. Logout dulu sebelum login lagi.', 'danger')
                    return redirect(url_for('login'))

                # ✅ Login berhasil
                session_id = str(uuid.uuid4())
                user.session_id = session_id
                user.last_activity = datetime.now(jakarta)
                db.session.commit()

                session['user_id'] = user.id
                session['session_id'] = session_id
                session['username'] = user.username
                session['role'] = user.role

                app.logger.info(f"User logged in: {username}")
                flash(f'Selamat datang, {user.username}!', 'success')
                if user.role == 'admin':
                    return redirect(url_for('dashboard'))
                elif user.role == 'user':
                    return redirect(url_for('tender'))

            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Login error: {str(e)}")
                flash('Terjadi kesalahan saat login. Silakan coba lagi.', 'danger')
                return redirect(url_for('login'))

        return render_template('login.html')

    @app.route('/dashboard')
    def dashboard():
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu', 'warning')
            return redirect(url_for('login'))

        user = User.query.get(session['user_id'])
        return render_template('dashboard.html', user=user)

    @app.route('/favorites')
    def favorites_page():
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu', 'warning')
            return redirect(url_for('login'))
        return render_template('favorites.html')

    @app.route("/admin")
    @login_required
    @role_required('admin')
    def admin_dashboard():
        return render_template("admin_dashboard.html")

    @app.route("/user")
    @login_required
    @role_required('user')
    def user_dashboard():
        return render_template("user_dashboard.html")

    @app.route("/")
    def tender():
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu', 'warning')
            return redirect(url_for('login'))
        return render_template("tender.html")

    @app.route('/fetch-tender')
    def fetchtender():
        try:
            tahun = int(request.args.get('tahun', 2025))
            # Validasi range tahun
            if tahun < 2020 or tahun > 2030:
                return jsonify({"error": "Tahun harus antara 2020-2030"}), 400

            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 100))

            # Validasi pagination
            if page < 1:
                return jsonify({"error": "Page harus >= 1"}), 400
            if per_page < 1 or per_page > 1000:
                return jsonify({"error": "Per page harus antara 1-1000"}), 400

            instansi = request.args.get('instansi')
            lpse = request.args.get('lpse')
            kementerian = request.args.get('kementerian')

            # Prioritas: instansi > lpse (untuk slug LPSE)
            final_instansi = instansi or lpse

            # Kementerian sekarang difilter terpisah berdasarkan field '2' (Satker)

            kategoriId = request.args.get('kategoriId')
            tahapan = request.args.get('tahapan')
            status = request.args.get('status')

            tender = fetch_tender(tahun=tahun, instansi=final_instansi, kategoriId=kategoriId, page=page, per_page=per_page, tahapan=tahapan, status=status, kementerian=kementerian)
            return jsonify(tender)
        except ValueError as e:
            return jsonify({"error": f"Invalid input: {str(e)}"}), 400
        except Exception as e:
            return jsonify({"error": f"Server error: {str(e)}"}), 500

    @app.route('/redis-tender', methods=['POST'])
    def redistender():
        try:
            data = request.get_json() or {}
            tahun = int(data.get('tahun', 2025))

            # Validasi range tahun
            if tahun < 2020 or tahun > 2030:
                return jsonify({"error": "Tahun harus antara 2020-2030"}), 400

            tender = redis_tender(tahun=tahun)
            return jsonify(tender)
        except ValueError as e:
            return jsonify({"error": f"Invalid input: {str(e)}"}), 400
        except Exception as e:
            return jsonify({"error": f"Server error: {str(e)}"}), 500

    @app.route('/get-filter-options')
    def get_filter_options():
        try:
            tahun = int(request.args.get('tahun', 2025))
            filter_type = request.args.get('type', 'tahapan')  # tahapan, kategori, instansi

            # Validasi range tahun
            if tahun < 2020 or tahun > 2030:
                return jsonify({"error": "Tahun harus antara 2020-2030"}), 400

            # Ambil semua data dari Redis
            all_data = fetch_tender(tahun=tahun, page=1, per_page=10000)

            # Extract unique values based on filter type
            unique_values = set()

            if filter_type == 'tahapan':
                # Tahapan ada di index 3
                for item in all_data.get('data', []):
                    tahapan = item.get('3')
                    if tahapan and tahapan != '-':
                        unique_values.add(tahapan)

            elif filter_type == 'kategori':
                # Kategori biasanya dari metadata atau bisa dari field tertentu
                for item in all_data.get('data', []):
                    kategori = item.get('kategori')
                    if kategori and kategori != '-':
                        unique_values.add(kategori)

            elif filter_type == 'instansi':
                # Instansi (LPSE Slug)
                for item in all_data.get('data', []):
                    instansi = item.get('instansi')
                    if instansi and instansi != '-':
                        unique_values.add(instansi)

            elif filter_type == 'kl':
                # Kementerian/Lembaga (Satuan Kerja) - Index 2
                for item in all_data.get('data', []):
                    # Data di Redis tersimpan dengan key string '0', '1', '2', dst
                    kl = item.get('2')
                    if kl and kl != '-':
                        unique_values.add(kl)

            # Sort and return
            return jsonify(sorted(list(unique_values)))

        except Exception as e:
            app.logger.error(f"Error fetching filter options: {str(e)}")
            return jsonify({"error": f"Server error: {str(e)}"}), 500

    @app.route("/non-tender")
    def non_tender():
        return render_template("non-tender.html")

    @app.route('/fetch-non-tender')
    def fetchnon_tender():
        try:
            tahun = int(request.args.get('tahun', 2025))
            # Validasi range tahun
            if tahun < 2020 or tahun > 2030:
                return jsonify({"error": "Tahun harus antara 2020-2030"}), 400

            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 100))

            # Validasi pagination
            if page < 1:
                return jsonify({"error": "Page harus >= 1"}), 400
            if per_page < 1 or per_page > 1000:
                return jsonify({"error": "Per page harus antara 1-1000"}), 400

            instansi = request.args.get('instansi')
            kategoriId = request.args.get('kategoriId')

            tender = fetch_nontender(tahun=tahun, instansi=instansi, kategoriId=kategoriId, page=page, per_page=per_page)
            return jsonify(tender)
        except ValueError as e:
            return jsonify({"error": f"Invalid input: {str(e)}"}), 400
        except Exception as e:
            return jsonify({"error": f"Server error: {str(e)}"}), 500

    @app.route('/redis-non-tender', methods=['POST'])
    def redisnontender():
        try:
            data = request.get_json() or {}
            tahun = int(data.get('tahun', 2025))

            # Validasi range tahun
            if tahun < 2020 or tahun > 2030:
                return jsonify({"error": "Tahun harus antara 2020-2030"}), 400

            nontender = redis_nontender(tahun=tahun)
            return jsonify(nontender)
        except ValueError as e:
            return jsonify({"error": f"Invalid input: {str(e)}"}), 400
            return jsonify({"error": f"Server error: {str(e)}"}), 500

    @app.route('/add-favorite', methods=['POST'])
    def add_favorite():
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401

        data = request.get_json()
        kode_tender = data.get('kode_tender')

        if not kode_tender:
            return jsonify({'error': 'Kode tender required'}), 400

        existing = Favorite.query.filter_by(user_id=session['user_id'], kode_tender=kode_tender).first()
        if existing:
            return jsonify({'message': 'Already favorited'}), 200

        fav = Favorite(
            user_id=session['user_id'],
            kode_tender=kode_tender
        )
        db.session.add(fav)
        db.session.commit()

        return jsonify({'message': 'Added to favorites'}), 200

    @app.route('/remove-favorite', methods=['POST'])
    def remove_favorite():
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401

        data = request.get_json()
        kode_tender = data.get('kode_tender')

        if not kode_tender:
            return jsonify({'error': 'Kode tender required'}), 400

        fav = Favorite.query.filter_by(user_id=session['user_id'], kode_tender=kode_tender).first()
        if fav:
            db.session.delete(fav)
            db.session.commit()
            return jsonify({'message': 'Removed from favorites'}), 200

        return jsonify({'message': 'Not found'}), 404

    @app.route('/get-favorites')
    def get_favorites():
        if 'user_id' not in session:
            return jsonify([]), 200

        favorites = Favorite.query.filter_by(user_id=session['user_id']).all()
        favorite_kode_list = [f.kode_tender for f in favorites]

        # Jika hanya perlu list kode_tender untuk checking
        if request.args.get('detail') != 'true':
            return jsonify(favorite_kode_list)

        # Jika perlu detail, ambil dari Redis dan filter
        try:
            # Get tahun dari parameter atau default 2025
            tahun = int(request.args.get('tahun', 2025))

            # Ambil semua data dari Redis untuk tahun tersebut
            all_data = fetch_tender(tahun=tahun, page=1, per_page=10000)

            # Filter hanya data yang ada di favorites
            filtered_data = []
            for item in all_data.get('data', []):
                kode = item.get('0')  # kode tender ada di index 0
                if kode in favorite_kode_list:
                    filtered_data.append({
                        'kode_tender': kode,
                        'instansi': item.get('instansi', '-'),
                        'nama_paket': item.get('1', '-'),
                        'satuan_kerja': item.get('2', '-'),
                        'tahapan': item.get('3', '-'),
                        'anggaran': item.get('4', '-')
                    })

            return jsonify(filtered_data)
        except Exception as e:
            app.logger.error(f"Error fetching favorites detail: {str(e)}")
            return jsonify({'error': 'Failed to fetch favorites'}), 500

    @app.route('/logout')
    def logout():
        user = User.query.filter_by(id=session['user_id']).first()
        if user:
            user.session_id = None
            user.last_activity = None
            db.session.commit()
        session.clear()
        flash('Anda telah logout', 'success')
        return redirect(url_for('login'))
