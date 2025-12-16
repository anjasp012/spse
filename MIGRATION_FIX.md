# 🔧 FIX: MySQL Migration Error

## ❌ Error yang Terjadi:
```
ERROR 1064 (42000) at line 2: You have an error in your SQL syntax;
check the manual that corresponds to your MySQL server version for
the right syntax to use near 'IF NOT EXISTS email VARCHAR(120) DEFAULT NULL'
```

## 🔍 Penyebab:
- Syntax `IF NOT EXISTS` untuk `ADD COLUMN` hanya tersedia di MySQL **8.0.29+**
- Server kamu kemungkinan pakai MySQL versi lebih lama (5.7 atau 8.0 awal)

## ✅ Solusi: 3 Opsi

---

### **OPSI 1: Pakai File SQL yang Baru (RECOMMENDED)**

File baru sudah dibuat: `migration_email_required_mysql_safe.sql`

```bash
# Di server
mysql -u root -p database_name < migration_email_required_mysql_safe.sql
```

⚠️ **CATATAN**:
- Jika kolom email **sudah ada**, query pertama akan error tapi bisa diabaikan
- Query berikutnya tetap akan jalan dan berhasil

---

### **OPSI 2: Manual Step by Step (PALING AMAN)**

File: `migration_email_step_by_step.sql`

```bash
# 1. Login ke MySQL
mysql -u root -p database_name

# 2. Copy-paste query dari file migration_email_step_by_step.sql
#    SATU PER SATU sesuai urutan
```

**Langkah-langkahnya:**

```sql
-- 1. Cek kolom email ada atau tidak
SELECT COLUMN_NAME
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME = 'users'
  AND COLUMN_NAME = 'email';
```

**Jika TIDAK ada (hasil kosong):**
```sql
-- 2. Tambah kolom email
ALTER TABLE users ADD COLUMN email VARCHAR(120) DEFAULT NULL AFTER username;
```

**Selalu jalankan (meskipun kolom sudah ada):**
```sql
-- 3. Update email yang kosong
UPDATE users
SET email = CONCAT(username, '@localhost.local')
WHERE email IS NULL OR email = '';

-- 4. Verifikasi tidak ada email NULL
SELECT COUNT(*) FROM users WHERE email IS NULL OR email = '';
-- Harus 0 (nol)

-- 5. Ubah kolom jadi NOT NULL
ALTER TABLE users
MODIFY COLUMN email VARCHAR(120) NOT NULL;

-- 6. Tambah UNIQUE constraint
ALTER TABLE users
ADD UNIQUE KEY unique_email (email);

-- 7. Verifikasi
SELECT id, username, email FROM users LIMIT 10;
```

---

### **OPSI 3: One-Liner Manual (Cepat tapi Riskier)**

```bash
# Login MySQL
mysql -u root -p database_name
```

```sql
-- Copy paste semua query ini SEKALIGUS
ALTER TABLE users ADD COLUMN email VARCHAR(120) DEFAULT NULL AFTER username;
UPDATE users SET email = CONCAT(username, '@localhost.local') WHERE email IS NULL OR email = '';
ALTER TABLE users MODIFY COLUMN email VARCHAR(120) NOT NULL;
ALTER TABLE users ADD UNIQUE KEY unique_email (email);
SELECT id, username, email FROM users LIMIT 10;
```

⚠️ **CATATAN**: Query pertama akan error jika kolom sudah ada, tapi query lainnya tetap jalan.

---

## 🔍 Troubleshooting

### Error: "Duplicate column name 'email'"
**Artinya**: Kolom email sudah ada

**Solusi**: Skip query `ADD COLUMN`, langsung jalankan query UPDATE dan seterusnya:
```sql
UPDATE users SET email = CONCAT(username, '@localhost.local') WHERE email IS NULL OR email = '';
ALTER TABLE users MODIFY COLUMN email VARCHAR(120) NOT NULL;
ALTER TABLE users ADD UNIQUE KEY unique_email (email);
```

---

### Error: "Duplicate key name 'unique_email'"
**Artinya**: Constraint unique_email sudah ada

**Solusi**: Skip query `ADD UNIQUE KEY`, migration sudah selesai. Cukup verifikasi:
```sql
DESCRIBE users;
SELECT id, username, email FROM users;
```

---

### Error: "Column 'email' cannot be null"
**Artinya**: Ada user yang emailnya masih NULL

**Solusi**:
```sql
-- Cek user yang email NULL
SELECT id, username, email FROM users WHERE email IS NULL OR email = '';

-- Update dulu
UPDATE users SET email = CONCAT(username, '@localhost.local') WHERE email IS NULL OR email = '';

-- Baru jalankan ALTER TABLE
ALTER TABLE users MODIFY COLUMN email VARCHAR(120) NOT NULL;
```

---

### Error: "Duplicate entry 'xxx@yyy' for key 'unique_email'"
**Artinya**: Ada duplikat email

**Solusi**:
```sql
-- Cari email duplikat
SELECT email, COUNT(*) as count
FROM users
GROUP BY email
HAVING count > 1;

-- Update email duplikat dengan tambahan ID
UPDATE users
SET email = CONCAT(username, '_', id, '@localhost.local')
WHERE email IN (
    SELECT email FROM (
        SELECT email FROM users
        GROUP BY email
        HAVING COUNT(*) > 1
    ) AS dups
);

-- Baru tambah constraint
ALTER TABLE users ADD UNIQUE KEY unique_email (email);
```

---

## ✅ Verifikasi Sukses

Jalankan query ini untuk memastikan migration berhasil:

```sql
-- 1. Cek struktur tabel
DESCRIBE users;
-- Kolom email harus ada dengan:
--   Type: varchar(120)
--   Null: NO
--   Key: UNI

-- 2. Cek data
SELECT id, username, email FROM users;
-- Semua user harus punya email

-- 3. Cek constraint
SHOW INDEX FROM users WHERE Key_name = 'unique_email';
-- Harus ada 1 baris
```

---

## 📝 Setelah Migration Sukses

1. **Restart aplikasi**
   ```bash
   sudo systemctl restart vpython
   # atau
   pkill -f "python app.py"
   python app.py
   ```

2. **Test di browser**
   - Buka `/admin/users` - Lihat kolom email
   - Create user baru - Email wajib
   - Login dengan email - Harus berhasil

---

## 🆘 Masih Error?

Kirim output dari query ini:
```sql
SELECT VERSION();  -- Versi MySQL
DESCRIBE users;     -- Struktur tabel users
SELECT id, username, email FROM users LIMIT 5;  -- Sample data
```

Good luck! 🚀
