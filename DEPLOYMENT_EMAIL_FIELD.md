# 🚀 Panduan Deployment ke Server

## 📋 Ringkasan Perubahan

Perubahan terbaru menambahkan **field Email yang WAJIB** di user management:

### File yang Berubah:
1. ✅ `models.py` - Email field menjadi NOT NULL
2. ✅ `routes.py` - Validasi email wajib di add & edit user
3. ✅ `templates/admin/users.html` - Tampilkan kolom email di tabel
4. ✅ `templates/admin/user_form.html` - Form email required
5. ✅ File migration SQL untuk update database

---

## 📤 STEP 1: Upload ke GitHub

```bash
# Di local (Windows)
cd C:\laragon\www\spse\vpython

# Add semua perubahan
git add .

# Commit dengan pesan yang jelas
git commit -m "feat: Add required email field to user management

- Update User model: email field now required (NOT NULL)
- Add email validation in admin user add/edit routes
- Display email column in users table
- Add email input field in user form (required)
- Create migration scripts for database update"

# Push ke GitHub
git push origin main
# atau: git push origin master (tergantung branch utama)
```

---

## 📥 STEP 2: Pull di Server

```bash
# Login ke server via SSH
ssh user@your-server.com

# Masuk ke direktori project
cd /path/to/vpython

# Pull perubahan dari GitHub
git pull origin main

# Verifikasi file yang berubah
git log -1
git diff HEAD~1 HEAD --name-only
```

---

## 🗄️ STEP 3: Migration Database

### A. Backup Database Dulu! (PENTING!)

```bash
# MySQL/MariaDB
mysqldump -u root -p database_name > backup_$(date +%Y%m%d_%H%M%S).sql

# PostgreSQL
pg_dump -U postgres database_name > backup_$(date +%Y%m%d_%H%M%S).sql

# SQLite
cp database.db database_backup_$(date +%Y%m%d_%H%M%S).db
```

### B. Jalankan Migration

**Opsi 1: Menggunakan file SQL yang sudah ada**

```bash
# MySQL/MariaDB
mysql -u root -p database_name < migration_email_required_mysql.sql

# PostgreSQL
psql -U postgres -d database_name -f migration_email_required_postgresql.sql

# SQLite
sqlite3 database.db < migration_email_required_sqlite.sql
```

**Opsi 2: Manual via MySQL Console**

```bash
# Login ke MySQL
mysql -u root -p database_name

# Jalankan query berikut:
```

```sql
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

-- Verifikasi hasilnya
SELECT id, username, email FROM users;
```

---

## 🔄 STEP 4: Restart Aplikasi

```bash
# Jika menggunakan systemd
sudo systemctl restart vpython

# Jika menggunakan supervisor
sudo supervisorctl restart vpython

# Jika manual dengan screen/tmux
# Stop aplikasi (Ctrl+C di screen/tmux)
# Start ulang
python app.py

# Jika menggunakan gunicorn
sudo systemctl restart gunicorn
# atau
pkill gunicorn
gunicorn --bind 0.0.0.0:5000 app:app
```

---

## ✅ STEP 5: Verifikasi

1. **Cek Database:**
   ```sql
   DESCRIBE users;
   -- Pastikan kolom email ada dengan type VARCHAR(120) NOT NULL UNIQUE

   SELECT id, username, email FROM users LIMIT 5;
   -- Pastikan semua user punya email
   ```

2. **Test di Browser:**
   - Buka halaman admin users
   - Coba tambah user baru (email harus diisi)
   - Coba edit user (email harus diisi)
   - Pastikan email muncul di tabel

3. **Test Login dengan Email:**
   - Logout
   - Login menggunakan email (bukan username)
   - Harus berhasil login

---

## 🐛 Troubleshooting

### Error: Column 'email' cannot be null

**Penyebab:** Ada user yang belum punya email

**Solusi:**
```sql
-- Cek user yang email-nya NULL
SELECT id, username, email FROM users WHERE email IS NULL OR email = '';

-- Update dengan default email
UPDATE users
SET email = CONCAT(username, '@localhost.local')
WHERE email IS NULL OR email = '';
```

### Error: Duplicate entry for key 'unique_email'

**Penyebab:** Ada 2 atau lebih user dengan email yang sama

**Solusi:**
```sql
-- Cari email yang duplikat
SELECT email, COUNT(*) as count
FROM users
GROUP BY email
HAVING count > 1;

-- Update email yang duplikat
UPDATE users
SET email = CONCAT(username, '@localhost.local')
WHERE email = 'duplicate@email.com' AND id != 1;
```

### Error saat git pull

**Conflict:**
```bash
# Lihat file yang conflict
git status

# Stash perubahan lokal dulu
git stash

# Pull ulang
git pull origin main

# Apply stash kembali (jika perlu)
git stash pop
```

---

## 📝 Catatan Penting

1. **SELALU BACKUP** database sebelum migration
2. Field email sekarang **WAJIB** diisi
3. Email harus **UNIQUE** (tidak boleh duplikat)
4. User yang sudah ada akan otomatis dapat email default: `username@localhost.local`
5. Admin bisa edit email user kapan saja
6. Login bisa pakai **username ATAU email**

---

## 🔗 File Migration yang Tersedia

- `migration_email_required_mysql.sql` - Untuk MySQL/MariaDB
- `migration_email_required_postgresql.sql` - Untuk PostgreSQL
- `migration_email_required_sqlite.sql` - Untuk SQLite
- `migration_email_required.py` - Script generator (jika perlu regenerate)

---

## 📞 Bantuan

Jika ada masalah saat deployment:
1. Cek log error aplikasi
2. Cek log database
3. Pastikan semua file sudah ter-pull dengan benar
4. Restore dari backup jika terjadi masalah serius

Good luck! 🚀
