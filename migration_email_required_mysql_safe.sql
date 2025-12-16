-- =========================================
-- Migration: Add Required Email Field
-- Compatible with MySQL 5.7+ and MariaDB
-- =========================================

-- Step 1: Cek apakah kolom sudah ada, jika belum tambahkan
-- (Jika sudah ada, query ini akan error tapi bisa diabaikan)
ALTER TABLE users ADD COLUMN email VARCHAR(120) DEFAULT NULL AFTER username;

-- Step 2: Update user yang belum punya email dengan default value
UPDATE users
SET email = CONCAT(username, '@localhost.local')
WHERE email IS NULL OR email = '';

-- Step 3: Ubah kolom email jadi NOT NULL
ALTER TABLE users
MODIFY COLUMN email VARCHAR(120) NOT NULL;

-- Step 4: Tambah UNIQUE constraint
ALTER TABLE users
ADD UNIQUE KEY unique_email (email);

-- Step 5: Verifikasi hasilnya
SELECT 'Migration completed successfully!' AS Status;
SELECT id, username, email FROM users LIMIT 10;
