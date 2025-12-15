"""
Migration script untuk menambahkan kolom email ke tabel users
Jalankan script ini untuk update database agar support login dengan email

Usage:
    python add_email_column.py
"""

from app import app, db
from models import User
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_email_column():
    """Add email column to users table"""
    with app.app_context():
        try:
            # Check if column already exists
            from sqlalchemy import inspect, Column, String
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('users')]

            if 'email' in columns:
                logger.info("✓ Kolom 'email' sudah ada di tabel users")
                return

            # Add email column
            logger.info("Menambahkan kolom 'email' ke tabel users...")

            # For SQLite
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE users ADD COLUMN email VARCHAR(120)'))
                conn.commit()

            logger.info("✓ Kolom 'email' berhasil ditambahkan!")
            logger.info("✓ User sekarang bisa login dengan username atau email")

        except Exception as e:
            logger.error(f"Error saat menambahkan kolom email: {str(e)}")
            logger.info("Jika menggunakan PostgreSQL/MySQL, gunakan query SQL berikut:")
            logger.info("ALTER TABLE users ADD COLUMN email VARCHAR(120) UNIQUE;")
            raise

if __name__ == '__main__':
    logger.info("="*60)
    logger.info("Migration: Menambahkan kolom email ke tabel users")
    logger.info("="*60)
    add_email_column()
    logger.info("="*60)
    logger.info("Migration selesai!")
    logger.info("="*60)
