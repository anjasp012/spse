"""
Migration script untuk menjalankan SQL migration ke database
Script ini akan membaca konfigurasi dari .env dan menjalankan migration

Usage:
    python run_migration.py
"""

from app import app
from models import db
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """Run SQL migration to add email column"""
    with app.app_context():
        try:
            # Cek apakah kolom email sudah ada
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('users')]

            if 'email' in columns:
                logger.info("[OK] Kolom 'email' sudah ada di tabel users")
                logger.info("[OK] Login dengan email sudah aktif!")
                return True

            logger.info("Menambahkan kolom 'email' ke tabel users...")

            # Deteksi jenis database
            db_url = str(db.engine.url)

            if 'mysql' in db_url or 'mariadb' in db_url:
                # MySQL/MariaDB
                logger.info("Database: MySQL/MariaDB")
                sql = "ALTER TABLE users ADD COLUMN email VARCHAR(120) UNIQUE AFTER username"
            elif 'postgresql' in db_url:
                # PostgreSQL
                logger.info("Database: PostgreSQL")
                sql = "ALTER TABLE users ADD COLUMN email VARCHAR(120) UNIQUE"
            elif 'sqlite' in db_url:
                # SQLite
                logger.info("Database: SQLite")
                sql = "ALTER TABLE users ADD COLUMN email VARCHAR(120)"
            else:
                logger.error(f"Database tidak dikenali: {db_url}")
                return False

            # Jalankan migration
            with db.engine.connect() as conn:
                conn.execute(db.text(sql))
                conn.commit()

            logger.info("[OK] Kolom 'email' berhasil ditambahkan!")
            logger.info("[OK] User sekarang bisa login dengan username atau email")
            return True

        except Exception as e:
            logger.error(f"Error saat menambahkan kolom email: {str(e)}")
            logger.info("\nSolusi alternatif:")
            logger.info("1. Pastikan MySQL/database sedang berjalan")
            logger.info("2. Atau jalankan query SQL berikut secara manual:")
            logger.info("\n   MySQL/MariaDB:")
            logger.info("   ALTER TABLE users ADD COLUMN email VARCHAR(120) UNIQUE;")
            logger.info("\n   PostgreSQL:")
            logger.info("   ALTER TABLE users ADD COLUMN email VARCHAR(120) UNIQUE;")
            logger.info("\n   SQLite:")
            logger.info("   ALTER TABLE users ADD COLUMN email VARCHAR(120);")
            return False

if __name__ == '__main__':
    logger.info("="*70)
    logger.info("Migration: Menambahkan kolom email ke tabel users")
    logger.info("="*70)

    success = run_migration()

    logger.info("="*70)
    if success:
        logger.info("Migration berhasil!")
    else:
        logger.info("Migration gagal - lihat error di atas")
    logger.info("="*70)
