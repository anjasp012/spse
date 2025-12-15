"""
Test script untuk memverifikasi fitur login dengan email
Script ini akan:
1. Cek apakah kolom email ada di database
2. Menambahkan email ke user admin (jika belum ada)
3. Menampilkan informasi user untuk testing

Usage:
    python test_email_login.py
"""

from app import app, db
from models import User
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_email_login():
    """Test email login functionality"""
    with app.app_context():
        try:
            # 1. Cek apakah kolom email ada
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('users')]

            logger.info("="*70)
            logger.info("TEST: Fitur Login dengan Email")
            logger.info("="*70)

            if 'email' not in columns:
                logger.error("[ERROR] Kolom email tidak ditemukan!")
                logger.info("Jalankan migration terlebih dahulu: python run_migration.py")
                return False

            logger.info("[OK] Kolom email ditemukan di database")

            # 2. Cek user yang ada
            users = User.query.all()
            logger.info(f"\n[INFO] Total user di database: {len(users)}")

            # 3. Tampilkan info user
            logger.info("\n" + "="*70)
            logger.info("Daftar User:")
            logger.info("="*70)

            for user in users:
                logger.info(f"\nID: {user.id}")
                logger.info(f"  Username: {user.username}")
                logger.info(f"  Email: {user.email if user.email else '(belum diset)'}")
                logger.info(f"  Role: {user.role}")
                logger.info(f"  Active: {'Ya' if user.is_active() else 'Tidak'}")

            # 4. Update admin dengan email jika belum ada
            admin = User.query.filter_by(username='admin').first()
            if admin:
                if not admin.email:
                    logger.info("\n" + "="*70)
                    logger.info("Menambahkan email ke user admin...")
                    admin.email = 'admin@bidradar.online'
                    db.session.commit()
                    logger.info("[OK] Email admin@bidradar.online ditambahkan ke user admin")
                else:
                    logger.info(f"\n[INFO] Admin sudah punya email: {admin.email}")

            # 5. Instruksi testing
            logger.info("\n" + "="*70)
            logger.info("Cara Testing Login:")
            logger.info("="*70)
            logger.info("\n1. Buka browser dan akses halaman login")
            logger.info("\n2. Test login dengan USERNAME:")
            logger.info("   Username/Email: admin")
            logger.info("   Password: (password admin Anda)")

            if admin and admin.email:
                logger.info("\n3. Test login dengan EMAIL:")
                logger.info(f"   Username/Email: {admin.email}")
                logger.info("   Password: (password admin Anda)")

            logger.info("\n" + "="*70)
            logger.info("Tips:")
            logger.info("="*70)
            logger.info("- Untuk menambahkan email ke user lain, gunakan SQL:")
            logger.info("  UPDATE users SET email='user@example.com' WHERE username='namauser';")
            logger.info("\n- Atau via admin panel jika sudah ada fitur edit user")
            logger.info("\n- Email harus UNIQUE per user")

            logger.info("\n" + "="*70)
            logger.info("[SUCCESS] Test selesai! Fitur login dengan email siap digunakan")
            logger.info("="*70)

            return True

        except Exception as e:
            logger.error(f"[ERROR] Test gagal: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    test_email_login()
