
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
