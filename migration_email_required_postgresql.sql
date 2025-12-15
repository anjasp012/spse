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