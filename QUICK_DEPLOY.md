# Quick Reference - Deployment Email Field

## 🚀 RINGKASAN CEPAT

### 1️⃣ Git Push (di Local)
```bash
git add .
git commit -m "feat: Add required email field to user management"
git push origin main
```

### 2️⃣ Git Pull (di Server)
```bash
cd /path/to/vpython
git pull origin main
```

### 3️⃣ Migration Database (di Server)

**WAJIB BACKUP DULU!**
```bash
mysqldump -u root -p database_name > backup_$(date +%Y%m%d).sql
```

**Jalankan Migration:**
```bash
mysql -u root -p database_name < migration_email_required_mysql.sql
```

atau manual:
```bash
mysql -u root -p database_name
```
```sql
ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR(120) DEFAULT NULL;
UPDATE users SET email = CONCAT(username, '@localhost.local') WHERE email IS NULL OR email = '';
ALTER TABLE users MODIFY COLUMN email VARCHAR(120) NOT NULL, ADD UNIQUE KEY unique_email (email);
SELECT id, username, email FROM users;
```

### 4️⃣ Restart App
```bash
# Systemd
sudo systemctl restart vpython

# Manual
pkill -f "python app.py"
nohup python app.py &
```

### 5️⃣ Test
- Buka admin/users
- Coba create user baru (email wajib)
- Coba login pakai email

---

## ⚠️ TROUBLESHOOTING

**Error: Column email cannot be null**
```sql
UPDATE users SET email = CONCAT(username, '@localhost.local') WHERE email IS NULL;
```

**Error: Duplicate entry**
```sql
SELECT email, COUNT(*) FROM users GROUP BY email HAVING COUNT(*) > 1;
UPDATE users SET email = CONCAT(username, '_', id, '@localhost.local') WHERE id IN (SELECT id FROM (...));
```

---

File lengkap: DEPLOYMENT_EMAIL_FIELD.md
