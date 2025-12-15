
-- Migration: Menambahkan kolom email ke tabel users (SQLite)
-- SQLite tidak support IF NOT EXISTS untuk ALTER TABLE, jadi cek manual
-- Jika kolom sudah ada, query ini akan error dan bisa diabaikan
ALTER TABLE users ADD COLUMN email VARCHAR(120);
