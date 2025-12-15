# Login dengan Username atau Email

## 📋 Perubahan yang Dilakukan

Sistem login telah diupdate untuk mendukung login menggunakan **username** atau **email**.

### 1. **Perubahan Database (models.py)**
- Menambahkan kolom `email` (VARCHAR 120, UNIQUE, NULLABLE) pada tabel `users`
- Field email bersifat opsional untuk backward compatibility

### 2. **Perubahan Logic Login (routes.py)**
- Login sekarang menerima input username **atau** email
- System akan mencari user berdasarkan kedua field (username OR email)
- Validasi tetap sama: cek password, cek akun aktif, cek session

### 3. **Perubahan Interface (login.html)**
- Label form berubah dari "Username" menjadi "Username / Email"
- Placeholder: "Masukkan username atau email"

## 🚀 Cara Menjalankan Migration

### Opsi 1: Menggunakan Script Python (Otomatis)
```bash
python run_migration.py
```

### Opsi 2: Manual SQL Query

**Untuk MySQL/MariaDB:**
```sql
ALTER TABLE users ADD COLUMN email VARCHAR(120) UNIQUE AFTER username;
```

**Untuk PostgreSQL:**
```sql
ALTER TABLE users ADD COLUMN email VARCHAR(120) UNIQUE;
```

**Untuk SQLite:**
```sql
ALTER TABLE users ADD COLUMN email VARCHAR(120);
```

### Opsi 3: Menggunakan File SQL Migration
File migration sudah tersedia:
- `migration_add_email_mysql.sql` - untuk MySQL/MariaDB
- `migration_add_email_postgresql.sql` - untuk PostgreSQL
- `migration_add_email_sqlite.sql` - untuk SQLite

Jalankan dengan:
```bash
# MySQL
mysql -u username -p database_name < migration_add_email_mysql.sql

# PostgreSQL
psql -U username -d database_name -f migration_add_email_postgresql.sql

# SQLite
sqlite3 database_name.db < migration_add_email_sqlite.sql
```

## 📝 Cara Menggunakan

### Login dengan Username (seperti biasa):
```
Username/Email: admin
Password: ******
```

### Login dengan Email (fitur baru):
```
Username/Email: admin@example.com
Password: ******
```

## ⚠️ Catatan Penting

1. **Email bersifat opsional** - user lama yang belum punya email tetap bisa login dengan username
2. **Email harus UNIQUE** - tidak boleh ada 2 user dengan email yang sama
3. **Backward Compatible** - user yang sudah ada tidak perlu melakukan apa-apa

## 🔄 Update User dengan Email

Untuk menambahkan email ke user yang sudah ada, bisa dilakukan via:

### 1. Admin Panel (jika tersedia)
Edit user dan tambahkan email

### 2. Manual via SQL
```sql
UPDATE users SET email = 'user@example.com' WHERE username = 'username';
```

### 3. Via Python Script
```python
from app import app, db
from models import User

with app.app_context():
    user = User.query.filter_by(username='admin').first()
    if user:
        user.email = 'admin@example.com'
        db.session.commit()
        print("Email updated!")
```

## 🧪 Testing

### Test Login dengan Username:
1. Buka halaman login
2. Masukkan username yang sudah ada
3. Masukkan password
4. Klik Login
5. Harus berhasil ✅

### Test Login dengan Email:
1. Update user dengan email (via SQL atau admin panel)
2. Buka halaman login
3. Masukkan email user
4. Masukkan password
5. Klik Login
6. Harus berhasil ✅

### Test Validasi:
- Username/email tidak ditemukan → Error "User tidak ditemukan"
- Password salah → Error "Password salah"
- Akun expired → Error "Akun sudah kadaluarsa"

## 📂 File yang Dimodifikasi

1. `models.py` - Model User dengan kolom email
2. `routes.py` - Logic login dengan username OR email
3. `templates/login.html` - UI form login
4. `run_migration.py` - Script migration otomatis
5. `generate_email_migration_sql.py` - Generator file SQL
6. `migration_add_email_*.sql` - File SQL migration
7. `LOGIN_WITH_EMAIL.md` - Dokumentasi ini

## 🎯 Benefit

✅ User lebih fleksibel dalam login
✅ Bisa menggunakan email yang mudah diingat
✅ Tetap support username untuk user lama
✅ Meningkatkan user experience

## 🐛 Troubleshooting

### Error: "Can't connect to MySQL server"
- Pastikan MySQL/MariaDB sedang running
- Cek konfigurasi database di file `.env`
- Start MySQL dengan: `mysql.server start` atau via Laragon

### Error: "Duplicate column name 'email'"
- Kolom email sudah ada, migration tidak perlu dijalankan lagi
- Sistem sudah siap digunakan

### Error: "column not found" saat login
- Migration belum dijalankan
- Jalankan migration dengan script `run_migration.py`

---

**Update:** Desember 15, 2025
**Version:** 1.0
**Status:** ✅ Ready to Deploy
