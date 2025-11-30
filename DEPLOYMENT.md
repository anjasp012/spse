# Panduan Deployment ke VPS (Ubuntu/Debian)

Panduan ini menjelaskan cara men-deploy aplikasi Flask SPSE Monitor ke server VPS Linux.

## 1. Persiapan Server

Update sistem dan install paket yang dibutuhkan:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv redis-server mysql-server nginx git -y
```

Pastikan Redis berjalan:
```bash
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

## 2. Setup Database (MySQL)

Masuk ke MySQL:
```bash
sudo mysql
```

Jalankan query berikut (ganti password sesuai keinginan):
```sql
CREATE DATABASE spse_vpython;
CREATE USER 'spse_user'@'localhost' IDENTIFIED BY 'password_rahasia';
GRANT ALL PRIVILEGES ON spse_vpython.* TO 'spse_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## 3. Setup Aplikasi

Upload kodingan Anda ke server (misal ke folder `/var/www/spse`).

```bash
# Buat direktori
sudo mkdir -p /var/www/spse
sudo chown -R $USER:$USER /var/www/spse

# Masuk ke direktori (upload file Anda ke sini)
cd /var/www/spse
```

Buat virtual environment dan install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn  # Server production untuk Flask
```

## 4. Konfigurasi Aplikasi

Edit file `config.py` atau sesuaikan environment variables. Pastikan koneksi database sesuai dengan yang dibuat di langkah 2.

```python
# Contoh config.py
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://spse_user:password_rahasia@localhost/spse_vpython'
REDIS_URL = 'redis://localhost:6379/0'
```

## 5. Setup Systemd (Agar jalan otomatis)

Buat file service agar aplikasi jalan di background dan auto-start saat restart.

```bash
sudo nano /etc/systemd/system/spse.service
```

Isi dengan (sesuaikan path user dan project):

```ini
[Unit]
Description=Gunicorn instance to serve SPSE App
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/spse
Environment="PATH=/var/www/spse/venv/bin"
ExecStart=/var/www/spse/venv/bin/gunicorn --workers 3 --bind unix:spse.sock -m 007 app:app

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl start spse
sudo systemctl enable spse
```

## 6. Setup Nginx (Web Server)

Buat konfigurasi Nginx:
```bash
sudo nano /etc/nginx/sites-available/spse
```

Isi dengan:

```nginx
server {
    listen 80;
    server_name alamat_ip_atau_domain_anda;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/spse/spse.sock;
    }
}
```

Aktifkan konfigurasi:
```bash
sudo ln -s /etc/nginx/sites-available/spse /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

## 7. Setup Cron Job (PENTING!)

Untuk fitur **Single Device Login** dan **Auto Cleanup**, Anda WAJIB memasang cron job untuk membersihkan sesi yang expired.

Buka crontab:
```bash
crontab -e
```

Tambahkan baris ini (jalan setiap 10 menit):

```bash
# Cleanup Session (Agar user yang lupa logout bisa login lagi setelah timeout)
*/10 * * * * cd /var/www/spse && /var/www/spse/venv/bin/python cleanup_sessions.py >> /var/www/spse/cron.log 2>&1
```

## 8. Maintenance

- **Lihat Log Aplikasi**: `journalctl -u spse -f`
- **Lihat Log Nginx**: `tail -f /var/log/nginx/error.log`
- **Restart Aplikasi**: `sudo systemctl restart spse`
