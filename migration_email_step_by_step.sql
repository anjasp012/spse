-- =========================================
-- Migration: Add Required Email Field
-- STEP BY STEP VERSION - Paling Aman!
-- =========================================

-- LANGKAH 1: Cek apakah kolom email sudah ada
-- Jalankan query ini dulu:
SELECT COLUMN_NAME
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME = 'users'
  AND COLUMN_NAME = 'email';


-- Jika hasilnya KOSONG (tidak ada baris), lanjut ke LANGKAH 2
-- Jika hasilnya ADA (ada 1 baris), SKIP ke LANGKAH 3


-- LANGKAH 2: Tambah kolom email (HANYA jika belum ada)
ALTER TABLE users ADD COLUMN email VARCHAR(120) DEFAULT NULL AFTER username;


-- LANGKAH 3: Update email yang kosong
-- (Jalankan ini meskipun kolom sudah ada)
UPDATE users
SET email = CONCAT(username, '@localhost.local')
WHERE email IS NULL OR email = '';


-- LANGKAH 4: Cek apakah ada email yang masih NULL
SELECT COUNT(*) as null_count
FROM users
WHERE email IS NULL OR email = '';

-- Pastikan hasilnya 0 (nol) sebelum lanjut


-- LANGKAH 5: Ubah kolom email jadi NOT NULL
ALTER TABLE users
MODIFY COLUMN email VARCHAR(120) NOT NULL;


-- LANGKAH 6: Cek apakah constraint unique_email sudah ada
SELECT CONSTRAINT_NAME
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME = 'users'
  AND CONSTRAINT_NAME = 'unique_email';

-- Jika hasilnya KOSONG, lanjut ke LANGKAH 7
-- Jika hasilnya ADA, SKIP LANGKAH 7


-- LANGKAH 7: Tambah UNIQUE constraint (HANYA jika belum ada)
ALTER TABLE users
ADD UNIQUE KEY unique_email (email);


-- LANGKAH 8: Verifikasi Final
SELECT 'Migration completed successfully!' AS Status;
DESCRIBE users;
SELECT id, username, email FROM users LIMIT 10;
