# 🏢 SPSE Scraper & Management System

Aplikasi Flask untuk scraping dan manajemen data tender/non-tender dari SPSE (Sistem Pengadaan Secara Elektronik).

## ✨ Fitur

- 🔐 **Authentication System** - Login/Register dengan session management
- 👥 **Role-based Access Control** - Admin dan User roles
- ⏰ **Time-limited Accounts** - Akun user dengan masa aktif (3 hari, 6 hari, 1 bulan)
- 🔒 **Single Device Login** - Mencegah login simultan (kecuali admin)
- 🕷️ **Async Web Scraping** - Scraping paralel menggunakan aiohttp
- 💾 **Redis Caching** - Caching data untuk performa optimal
- 📊 **Data Management** - Fetch dan filter data tender/non-tender
- 📝 **Logging System** - Comprehensive logging dengan rotating file handler

## 🛠️ Teknologi

- **Backend**: Flask 3.1.2
- **Database**: MySQL (via SQLAlchemy)
- **Caching**: Redis
- **Scraping**: aiohttp, asyncio
- **Auth**: Werkzeug password hashing
- **Timezone**: pytz (Asia/Jakarta)

## 📋 Prerequisites

- Python 3.8+
- MySQL Server
- Redis Server
- pip (Python package manager)

## 🚀 Installation

### 1. Clone repository

```bash
git clone <repository-url>
cd vpython
```

### 2. Create virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup environment variables

Copy `.env.example` ke `.env` dan sesuaikan konfigurasi:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Flask Configuration
SECRET_KEY=your-super-secret-key-here

# Database Configuration
DB_USER=root
DB_PASS=your-password
DB_HOST=localhost
DB_NAME=spse

# Redis Configuration
REDIS_URL=redis://localhost

# SPSE Scraping Configuration
SPSE_BASE_URL=https://spse.inaproc.id

# Session Configuration
SESSION_TIMEOUT_MINUTES=30
```

### 5. Setup database

```bash
# Buat database MySQL
mysql -u root -p
CREATE DATABASE spse;
exit;
```

### 6. Run application

```bash
python app.py
```

Aplikasi akan berjalan di `http://localhost:5000`

## 📁 Struktur Direktori

```
vpython/
├── app.py                  # Main application
├── config.py              # Configuration
├── models.py              # Database models
├── routes.py              # Route handlers
├── utils.py               # Utility functions (decorators)
├── logger.py              # Logging configuration
├── scrape.py              # Web scraping script
├── cleanup_sessions.py    # Session cleanup script
├── modules/
│   ├── fetch_tender.py
│   ├── fetch_nontender.py
│   ├── redis_tender.py
│   └── redis_nontender.py
├── templates/             # HTML templates
├── static/               # Static files (CSS, JS)
├── logs/                 # Application logs
├── .env                  # Environment variables (DO NOT COMMIT)
├── .env.example          # Environment template
├── .gitignore           # Git ignore rules
└── requirements.txt      # Python dependencies
```

## 🔧 Usage

### Running the scraper

```bash
python scrape.py
```

### Cleanup inactive sessions

```bash
python cleanup_sessions.py
```

Atau setup cron job untuk auto cleanup:

```bash
# Windows Task Scheduler
# Jalankan setiap 30 menit

# Linux cron
*/30 * * * * cd /path/to/vpython && python cleanup_sessions.py
```

## 🔐 Default Admin Account

Buat admin account manual di database:

```sql
INSERT INTO users (username, password, role, active_until)
VALUES ('admin', '<hashed-password>', 'admin', NULL);
```

## 📊 API Endpoints

### Authentication

- `GET/POST /register` - User registration
- `GET/POST /login` - User login
- `GET /logout` - User logout

### Dashboard

- `GET /dashboard` - User dashboard
- `GET /admin` - Admin dashboard (admin only)
- `GET /user` - User dashboard (user only)

### Data Fetching

- `GET /fetch-tender` - Fetch tender data
  - Query params: `tahun`, `page`, `per_page`, `instansi`, `kategoriId`
- `POST /redis-tender` - Fetch tender from Redis
- `GET /fetch-non-tender` - Fetch non-tender data
- `POST /redis-non-tender` - Fetch non-tender from Redis

## 🐛 Debugging

Logs tersimpan di `logs/spse.log` dengan format:

```
[2025-11-25 09:00:00] INFO in app: Database tables created/verified
[2025-11-25 09:00:15] INFO in routes: User logged in: john_doe
```

## 🔒 Security Features

- ✅ Password hashing dengan Werkzeug
- ✅ Environment variables untuk credentials
- ✅ Session management dengan UUID
- ✅ Input validation
- ✅ Error handling
- ✅ Single device login enforcement
- ✅ Timezone-aware datetime

## ⚠️ Important Notes

1. **JANGAN commit file `.env`** - Sudah ada di `.gitignore`
2. **Ganti SECRET_KEY** di production dengan key yang kuat
3. **Setup proper MySQL password** untuk production
4. **Enable HTTPS** untuk production deployment
5. **Setup firewall** untuk Redis dan MySQL

## 📝 TODO / Improvements

- [ ] Add CSRF protection (Flask-WTF)
- [ ] Add rate limiting
- [ ] Add API authentication (JWT)
- [ ] Add unit tests
- [ ] Add data export (Excel, CSV)
- [ ] Add email notifications
- [ ] Add password reset functionality
- [ ] Add user profile management
- [ ] Add audit logging
- [ ] Add data visualization dashboard

## 🤝 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

MIT License - feel free to use this project for learning or commercial purposes.

## 👨‍💻 Author

Created with ❤️ by [Your Name]

## 📞 Support

Jika ada pertanyaan atau issue, silakan buat issue di GitHub repository.

---

**Happy Coding! 🚀**
