from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from models import db, User, Favorite
from utils import login_required, role_required, admin_required
from modules.redis_tender import fetch as redis_tender
from modules.redis_nontender import fetch as redis_nontender
from modules.fetch_tender import fetch as fetch_tender
from modules.fetch_nontender import fetch as fetch_nontender
from datetime import datetime, timedelta
import uuid
import pytz
import threading

jakarta = pytz.timezone('Asia/Jakarta')

def create_routes(app):

    @app.before_request
    def update_last_activity():
        if 'user_id' in session:
            try:
                # Update last_activity setiap request agar status online akurat
                # Untuk performa, bisa dibatasi misal update tiap 5 menit, tapi untuk sekarang realtime dulu
                user = User.query.get(session['user_id'])
                if user:
                    user.last_activity = datetime.now(jakarta)
                    db.session.commit()
            except Exception as e:
                # Ignore error during activity update to not block request
                pass

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        # Redirect if already logged in
        if 'user_id' in session:
            if session.get('role') == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('index'))

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
        # Redirect if already logged in
        if 'user_id' in session:
            if session.get('role') == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('index'))

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
                    last_active = user.last_activity.strftime("%d-%m-%Y %H:%M") if user.last_activity else "Baru saja"
                    flash(f'⚠️ Login Ditolak: Akun sedang aktif di perangkat lain (Terakhir aktif: {last_active}).\nSilakan logout dari perangkat lama atau tunggu sesi berakhir.', 'danger')
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
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('index'))

            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Login error: {str(e)}")
                flash('Terjadi kesalahan saat login. Silakan coba lagi.', 'danger')
                return redirect(url_for('login'))

        return render_template('login.html')

    # Route moved to /admin

    @app.route('/favorites')
    def favorites_page():
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu', 'warning')
            return redirect(url_for('login'))
        return render_template('favorites.html')

    @app.route("/admin")
    @admin_required
    def admin_dashboard():
        import redis

        # Get user statistics
        total_users = User.query.count()
        admin_count = User.query.filter_by(role='admin').count()
        user_count = User.query.filter_by(role='user').count()

        # Count active users
        now = datetime.now(jakarta)
        active_users = User.query.filter(
            (User.active_until == None) | (User.active_until > now)
        ).count()

        # Count tender and non-tender data from Redis
        try:
            r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

            # Count tender data
            total_tender = 0
            for year in range(2020, 2031):
                key = f"spse:{year}:tender"
                if r.exists(key):
                    total_tender += r.llen(key)

            # Count non-tender data
            total_nontender = 0
            for year in range(2020, 2031):
                key = f"spse:{year}:nontender"
                if r.exists(key):
                    total_nontender += r.llen(key)

        except Exception as e:
            app.logger.error(f"Redis error in dashboard: {str(e)}")
            total_tender = 0
            total_nontender = 0

        return render_template("admin/dashboard.html",
                             total_users=total_users,
                             admin_count=admin_count,
                             user_count=user_count,
                             active_users=active_users,
                             total_tender=total_tender,
                             total_nontender=total_nontender,
                             active_page='dashboard')

    # User dashboard removed - users go to / (index)

    # ===== USER MANAGEMENT ROUTES =====
    @app.route("/admin/users")
    @admin_required
    def admin_users():
        users = User.query.all()
        now = datetime.now(jakarta)
        return render_template("admin/users.html", users=users, now=now, active_page='users')


    @app.route("/admin/users/add", methods=['GET', 'POST'])
    @admin_required
    def admin_users_add():
        if request.method == 'POST':
            try:
                username = request.form.get('username', '').strip()
                password = request.form.get('password', '')
                confirm_password = request.form.get('confirm_password', '')
                role = request.form.get('role', 'user')
                active_until_str = request.form.get('active_until', '')

                # Validation
                if not username or not password:
                    flash('Username dan password harus diisi', 'danger')
                    return redirect(url_for('admin_users_add'))

                if len(username) < 3 or len(username) > 50:
                    flash('Username harus 3-50 karakter', 'danger')
                    return redirect(url_for('admin_users_add'))

                if not username.replace('_', '').isalnum():
                    flash('Username hanya boleh huruf, angka, dan underscore', 'danger')
                    return redirect(url_for('admin_users_add'))

                if len(password) < 6:
                    flash('Password minimal 6 karakter', 'danger')
                    return redirect(url_for('admin_users_add'))

                if password != confirm_password:
                    flash('Password dan konfirmasi password tidak cocok', 'danger')
                    return redirect(url_for('admin_users_add'))

                if role not in ['admin', 'user']:
                    flash('Role tidak valid', 'danger')
                    return redirect(url_for('admin_users_add'))

                # Check if username already exists
                if User.query.filter_by(username=username).first():
                    flash('Username sudah digunakan', 'danger')
                    return redirect(url_for('admin_users_add'))

                # Parse active_until
                active_until = None
                if active_until_str:
                    try:
                        # Parse datetime-local format: YYYY-MM-DDTHH:MM
                        active_until = datetime.strptime(active_until_str, '%Y-%m-%dT%H:%M')
                        active_until = jakarta.localize(active_until)

                        # Validate future date
                        if active_until <= datetime.now(jakarta):
                            flash('Tanggal aktif harus di masa depan', 'danger')
                            return redirect(url_for('admin_users_add'))
                    except ValueError:
                        flash('Format tanggal tidak valid', 'danger')
                        return redirect(url_for('admin_users_add'))

                # Create user
                new_user = User(
                    username=username,
                    role=role,
                    active_until=active_until
                )
                new_user.set_password(password)

                db.session.add(new_user)
                db.session.commit()

                flash(f'User {username} berhasil ditambahkan', 'success')
                return redirect(url_for('admin_users'))

            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Add user error: {str(e)}")
                flash('Terjadi kesalahan saat menambahkan user', 'danger')
                return redirect(url_for('admin_users_add'))

        return render_template("admin/user_form.html", user=None, action='add')

    @app.route("/admin/users/edit/<int:user_id>", methods=['GET', 'POST'])
    @admin_required
    def admin_users_edit(user_id):
        user = User.query.get_or_404(user_id)

        if request.method == 'POST':
            try:
                username = request.form.get('username', '').strip()
                password = request.form.get('password', '')
                confirm_password = request.form.get('confirm_password', '')
                role = request.form.get('role', 'user')
                active_until_str = request.form.get('active_until', '')

                # Validation
                if not username:
                    flash('Username harus diisi', 'danger')
                    return redirect(url_for('admin_users_edit', user_id=user_id))

                if len(username) < 3 or len(username) > 50:
                    flash('Username harus 3-50 karakter', 'danger')
                    return redirect(url_for('admin_users_edit', user_id=user_id))

                if not username.replace('_', '').isalnum():
                    flash('Username hanya boleh huruf, angka, dan underscore', 'danger')
                    return redirect(url_for('admin_users_edit', user_id=user_id))

                # Check if username already exists (except current user)
                existing_user = User.query.filter_by(username=username).first()
                if existing_user and existing_user.id != user_id:
                    flash('Username sudah digunakan', 'danger')
                    return redirect(url_for('admin_users_edit', user_id=user_id))

                # Validate password if provided
                if password:
                    if len(password) < 6:
                        flash('Password minimal 6 karakter', 'danger')
                        return redirect(url_for('admin_users_edit', user_id=user_id))

                    if password != confirm_password:
                        flash('Password dan konfirmasi password tidak cocok', 'danger')
                        return redirect(url_for('admin_users_edit', user_id=user_id))

                if role not in ['admin', 'user']:
                    flash('Role tidak valid', 'danger')
                    return redirect(url_for('admin_users_edit', user_id=user_id))

                # Parse active_until
                active_until = None
                if active_until_str:
                    try:
                        active_until = datetime.strptime(active_until_str, '%Y-%m-%dT%H:%M')
                        active_until = jakarta.localize(active_until)
                    except ValueError:
                        flash('Format tanggal tidak valid', 'danger')
                        return redirect(url_for('admin_users_edit', user_id=user_id))

                # Update user
                user.username = username
                user.role = role
                user.active_until = active_until

                if password:  # Only update password if provided
                    user.set_password(password)

                db.session.commit()

                flash(f'User {username} berhasil diupdate', 'success')
                return redirect(url_for('admin_users'))

            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Edit user error: {str(e)}")
                flash('Terjadi kesalahan saat mengupdate user', 'danger')
                return redirect(url_for('admin_users_edit', user_id=user_id))

        return render_template("admin/user_form.html", user=user, action='edit')

    @app.route("/admin/users/delete/<int:user_id>", methods=['POST'])
    @admin_required
    def admin_users_delete(user_id):
        try:
            # Prevent self-deletion
            if user_id == session.get('user_id'):
                flash('Anda tidak dapat menghapus akun sendiri', 'danger')
                return redirect(url_for('admin_users'))

            user = User.query.get_or_404(user_id)
            username = user.username

            db.session.delete(user)
            db.session.commit()

            flash(f'User {username} berhasil dihapus', 'success')
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Delete user error: {str(e)}")
            flash('Terjadi kesalahan saat menghapus user', 'danger')

        return redirect(url_for('admin_users'))


    @app.route("/")
    @login_required
    def index():
        return render_template("tender.html")

    @app.route('/fetch-tender')
    def fetchtender():
        try:
            tahun = int(request.args.get('tahun', 2026))
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
            search_nama = request.args.get('search_nama')

            tender = fetch_tender(tahun=tahun, instansi=final_instansi, kategoriId=kategoriId, page=page, per_page=per_page, tahapan=tahapan, status=status, kementerian=kementerian, search_nama=search_nama)
            return jsonify(tender)
        except ValueError as e:
            return jsonify({"error": f"Invalid input: {str(e)}"}), 400
        except Exception as e:
            return jsonify({"error": f"Server error: {str(e)}"}), 500

    @app.route('/redis-tender', methods=['POST'])
    def redistender():
        try:
            data = request.get_json() or {}
            tahun = int(data.get('tahun', 2026))

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
        """Get unique filter options from Redis data"""
        try:
            tahun = int(request.args.get('tahun', 2026))
            filter_type = request.args.get('type', 'tahapan')
            source = request.args.get('source', 'tender')  # 'tender' or 'nontender'

            # Validasi range tahun
            if tahun < 2020 or tahun > 2030:
                return jsonify({"error": "Tahun harus antara 2020-2030"}), 400

            # Ambil semua data dari Redis berdasarkan source
            if source == 'nontender':
                all_data = fetch_nontender(tahun=tahun, page=1, per_page=10000)
            else:
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
            tahun = int(request.args.get('tahun', 2026))
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
            search_nama = request.args.get('search_nama')
            kementerian = request.args.get('kementerian')
            tahapan = request.args.get('tahapan')

            tender = fetch_nontender(tahun=tahun, instansi=instansi, kategoriId=kategoriId, page=page, per_page=per_page, search_nama=search_nama, kementerian=kementerian, tahapan=tahapan)
            return jsonify(tender)
        except ValueError as e:
            return jsonify({"error": f"Invalid input: {str(e)}"}), 400
        except Exception as e:
            return jsonify({"error": f"Server error: {str(e)}"}), 500


    @app.route('/redis-non-tender', methods=['POST'])
    def redisnontender():
        try:
            data = request.get_json() or {}
            tahun = int(data.get('tahun', 2026))

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
        fav_type = data.get('type', 'tender')  # 'tender' or 'nontender'

        if not kode_tender:
            return jsonify({'error': 'Kode tender required'}), 400

        existing = Favorite.query.filter_by(user_id=session['user_id'], kode_tender=kode_tender, type=fav_type).first()
        if existing:
            return jsonify({'message': 'Already favorited'}), 200

        fav = Favorite(
            user_id=session['user_id'],
            kode_tender=kode_tender,
            type=fav_type
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
        fav_type = data.get('type', 'tender')  # 'tender' or 'nontender'

        if not kode_tender:
            return jsonify({'error': 'Kode tender required'}), 400

        fav = Favorite.query.filter_by(user_id=session['user_id'], kode_tender=kode_tender, type=fav_type).first()
        if fav:
            db.session.delete(fav)
            db.session.commit()
            return jsonify({'message': 'Removed from favorites'}), 200

        return jsonify({'message': 'Not found'}), 404

    @app.route('/get-favorites')
    def get_favorites():
        if 'user_id' not in session:
            return jsonify([]), 200

        fav_type = request.args.get('type', 'tender')  # 'tender' or 'nontender'
        favorites = Favorite.query.filter_by(user_id=session['user_id'], type=fav_type).all()
        favorite_kode_list = [f.kode_tender for f in favorites]

        # Jika hanya perlu list kode_tender untuk checking
        if request.args.get('detail') != 'true':
            return jsonify(favorite_kode_list)

        # Jika perlu detail, ambil dari Redis dan filter
        try:
            # Get tahun dari parameter atau default 2026
            tahun = int(request.args.get('tahun', 2026))

            # Ambil semua data dari Redis berdasarkan type
            if fav_type == 'nontender':
                all_data = fetch_nontender(tahun=tahun, page=1, per_page=10000)
            else:
                all_data = fetch_tender(tahun=tahun, page=1, per_page=10000)

            # Filter hanya data yang ada di favorites
            filtered_data = []
            for item in all_data.get('data', []):
                kode = item.get('0')  # kode ada di index 0
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

    @app.route('/api/tender-status')
    def tender_status():
        """Check tender scraping progress from Redis"""
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

            # Check status from Redis keys
            status_key = 'scraping:tender:status'
            progress_key = 'scraping:tender:progress'
            message_key = 'scraping:tender:message'

            status = r.get(status_key) or 'idle'
            progress = int(r.get(progress_key) or 0)
            message = r.get(message_key) or 'Menunggu...'

            return jsonify({
                'status': status,
                'progress': progress,
                'message': message
            })
        except Exception as e:
            app.logger.error(f"Error checking tender status: {str(e)}")
            return jsonify({
                'status': 'error',
                'progress': 0,
                'message': str(e)
            }), 500

    @app.route('/api/nontender-status')
    def nontender_status():
        """Check non-tender scraping progress from Redis"""
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

            # Check status from Redis keys
            status_key = 'scraping:nontender:status'
            progress_key = 'scraping:nontender:progress'
            message_key = 'scraping:nontender:message'

            status = r.get(status_key) or 'idle'
            progress = int(r.get(progress_key) or 0)
            message = r.get(message_key) or 'Menunggu...'

            return jsonify({
                'status': status,
                'progress': progress,
                'message': message
            })
        except Exception as e:
            app.logger.error(f"Error checking non-tender status: {str(e)}")
            return jsonify({
                'status': 'error',
                'progress': 0,
                'message': str(e)
            }), 500

    @app.route('/api/start-scraping-tender')
    @admin_required
    def start_scraping_tender():
        """Start tender scraping in background thread"""
        try:
            tahun = int(request.args.get('tahun', 2026))

            # Validasi range tahun
            if tahun < 2020 or tahun > 2030:
                return jsonify({"error": "Tahun harus antara 2020-2030"}), 400

            # Jalankan scraping di background thread
            thread = threading.Thread(target=redis_tender, args=(tahun,))
            thread.daemon = True
            thread.start()

            return jsonify({
                'status': 'loading',
                'message': f'Scraping tender tahun {tahun} dimulai...',
                'tahun': tahun
            })
        except Exception as e:
            app.logger.error(f"Error starting tender scraping: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @app.route('/api/start-scraping-nontender')
    @admin_required
    def start_scraping_nontender():
        """Start non-tender scraping in background thread"""
        try:
            tahun = int(request.args.get('tahun', 2026))

            # Validasi range tahun
            if tahun < 2020 or tahun > 2030:
                return jsonify({"error": "Tahun harus antara 2020-2030"}), 400

            # Jalankan scraping di background thread
            thread = threading.Thread(target=redis_nontender, args=(tahun,))
            thread.daemon = True
            thread.start()

            return jsonify({
                'status': 'loading',
                'message': f'Scraping non-tender tahun {tahun} dimulai...',
                'tahun': tahun
            })
        except Exception as e:
            app.logger.error(f"Error starting non-tender scraping: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

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
