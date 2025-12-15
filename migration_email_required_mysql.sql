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