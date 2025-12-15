"""
Migration untuk Email Field - Update untuk Required Email
==========================================================

PERUBAHAN:
1. Menambahkan kolom email (jika belum ada)
2. Mengisi email kosong dengan default value (username@localhost.local)
3. Mengubah kolom email menjadi NOT NULL
4. Menambahkan UNIQUE constraint

CARA MANUAL MIGRATION DI SERVER:
=================================

1. BACKUP DATABASE DULU!
   mysqldump -u username -p database_name > backup_$(date +%Y%m%d).sql

2. Login ke MySQL/MariaDB:
   mysql -u username -p database_name

3. Jalankan query di bawah sesuai database Anda

"""

# ========================================
# MYSQL / MariaDB
# ========================================
MYSQL_MIGRATION = """
-- Step 1: Tambah kolom email jika belum ada
ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR(120) DEFAULT NULL;

-- Step 2: Update user yang belum punya email dengan default value
UPDATE users
SET email = CONCAT(username, '@localhost.local')
WHERE email IS NULL OR email = '';

-- Step 3: Ubah kolom email jadi NOT NULL dan UNIQUE
ALTER TABLE users
MODIFY COLUMN email VARCHAR(120) NOT NULL,
ADD UNIQUE KEY unique_email (email);

-- Verifikasi
SELECT id, username, email FROM users LIMIT 10;
"""

# ========================================
# PostgreSQL
# ========================================
POSTGRESQL_MIGRATION = """
-- Step 1: Tambah kolom email jika belum ada
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'email'
    ) THEN
        ALTER TABLE users ADD COLUMN email VARCHAR(120);
    END IF;
END $$;

-- Step 2: Update user yang belum punya email dengan default value
UPDATE users
SET email = username || '@localhost.local'
WHERE email IS NULL OR email = '';

-- Step 3: Ubah kolom email jadi NOT NULL dan UNIQUE
ALTER TABLE users
ALTER COLUMN email SET NOT NULL;

ALTER TABLE users
ADD CONSTRAINT unique_email UNIQUE (email);

-- Verifikasi
SELECT id, username, email FROM users LIMIT 10;
"""

# ========================================
# SQLite
# ========================================
SQLITE_MIGRATION = """
-- SQLite tidak support ALTER COLUMN, jadi harus recreate table

-- Step 1: Backup table
CREATE TABLE users_backup AS SELECT * FROM users;

-- Step 2: Update email yang kosong
UPDATE users_backup
SET email = username || '@localhost.local'
WHERE email IS NULL OR email = '';

-- Step 3: Drop table lama
DROP TABLE users;

-- Step 4: Create table baru dengan email NOT NULL
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    role VARCHAR(10) NOT NULL DEFAULT 'user',
    active_until DATETIME,
    session_id VARCHAR(255),
    last_activity DATETIME
);

-- Step 5: Copy data dari backup
INSERT INTO users (id, username, email, password, role, active_until, session_id, last_activity)
SELECT id, username, email, password, role, active_until, session_id, last_activity
FROM users_backup;

-- Step 6: Drop backup table
DROP TABLE users_backup;

-- Verifikasi
SELECT id, username, email FROM users LIMIT 10;
"""

def save_migration_files():
    """Simpan file migration untuk berbagai database"""
    migrations = {
        'mysql': MYSQL_MIGRATION,
        'postgresql': POSTGRESQL_MIGRATION,
        'sqlite': SQLITE_MIGRATION
    }

    for db_type, sql in migrations.items():
        filename = f"migration_email_required_{db_type}.sql"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(sql.strip())
        print(f"[OK] {filename} created")

    print("\n" + "="*70)
    print("CARA MIGRATION DI SERVER:")
    print("="*70)
    print("\n1. BACKUP DATABASE TERLEBIH DAHULU!")
    print("2. Pilih file sesuai database:")
    print("   - migration_email_required_mysql.sql")
    print("   - migration_email_required_postgresql.sql")
    print("   - migration_email_required_sqlite.sql")
    print("\n3. Jalankan di database server")
    print("="*70)

if __name__ == '__main__':
    save_migration_files()
