
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
