"""
Migration script untuk menambahkan kolom email ke tabel users
Script ini akan membuat file SQL yang bisa dijalankan manual

Usage:
    1. python generate_email_migration_sql.py
    2. Jalankan SQL yang dihasilkan di database Anda
"""

import os

# SQL untuk berbagai jenis database
sql_statements = {
    'mysql': """
-- Migration: Menambahkan kolom email ke tabel users (MySQL/MariaDB)
-- Cek apakah kolom sudah ada
SET @dbname = DATABASE();
SET @tablename = "users";
SET @columnname = "email";
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (table_name = @tablename)
      AND (table_schema = @dbname)
      AND (column_name = @columnname)
  ) > 0,
  "SELECT 'Kolom email sudah ada' AS MESSAGE;",
  "ALTER TABLE users ADD COLUMN email VARCHAR(120) UNIQUE AFTER username;"
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;
""",
    'postgresql': """
-- Migration: Menambahkan kolom email ke tabel users (PostgreSQL)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'email'
    ) THEN
        ALTER TABLE users ADD COLUMN email VARCHAR(120) UNIQUE;
        RAISE NOTICE 'Kolom email berhasil ditambahkan';
    ELSE
        RAISE NOTICE 'Kolom email sudah ada';
    END IF;
END $$;
""",
    'sqlite': """
-- Migration: Menambahkan kolom email ke tabel users (SQLite)
-- SQLite tidak support IF NOT EXISTS untuk ALTER TABLE, jadi cek manual
-- Jika kolom sudah ada, query ini akan error dan bisa diabaikan
ALTER TABLE users ADD COLUMN email VARCHAR(120);
"""
}

def generate_migration_files():
    """Generate migration SQL files"""
    output_dir = os.path.dirname(os.path.abspath(__file__))

    print("="*70)
    print("Membuat file SQL migration untuk menambahkan kolom email")
    print("="*70)

    for db_type, sql in sql_statements.items():
        filename = f"migration_add_email_{db_type}.sql"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(sql)

        print(f"[OK] File dibuat: {filename}")

    print("="*70)
    print("\nCara menggunakan:")
    print("1. Pilih file SQL sesuai database Anda:")
    print("   - migration_add_email_mysql.sql untuk MySQL/MariaDB")
    print("   - migration_add_email_postgresql.sql untuk PostgreSQL")
    print("   - migration_add_email_sqlite.sql untuk SQLite")
    print("\n2. Jalankan file SQL tersebut di database Anda")
    print("\n3. Atau jalankan manual query SQL berikut:")
    print("\n   MySQL/MariaDB:")
    print("   ALTER TABLE users ADD COLUMN email VARCHAR(120) UNIQUE;")
    print("\n   PostgreSQL:")
    print("   ALTER TABLE users ADD COLUMN email VARCHAR(120) UNIQUE;")
    print("\n   SQLite:")
    print("   ALTER TABLE users ADD COLUMN email VARCHAR(120);")
    print("="*70)

if __name__ == '__main__':
    generate_migration_files()
