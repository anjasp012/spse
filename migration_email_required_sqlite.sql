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