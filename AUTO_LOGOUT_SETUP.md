# Auto Logout - Idle Timeout Setup

## Ringkasan Perubahan

Sistem sekarang memiliki **auto logout otomatis** setelah user idle (tidak aktif) selama **30 menit**.

## Komponen yang Diupdate

### 1. Backend (`app.py`)
- ✅ `MAX_IDLE_MINUTES` diubah dari 15 menjadi **30 menit**
- Middleware `check_user_session` memeriksa idle timeout setiap request
- Session expired → auto redirect ke login

### 2. API Endpoint Baru (`routes.py`)
- ✅ **`/api/check-session`** - Endpoint untuk cek validitas session
  - Cek `session_id` di database vs cookie
  - Cek `active_until` (subscription)
  - Cek idle timeout (30 menit)

### 3. Frontend Auto-Detect (`static/js/session_check.js`)
- ✅ Cek session setiap **60 detik** secara otomatis
- ✅ Cek saat user **switch tab** (visibilitychange)
- ✅ Cek saat user **interaksi** setelah idle lama
- ✅ Auto redirect ke `/login` jika session expired

### 4. Template yang Diupdate
- ✅ `templates/tender.html`
- ✅ `templates/non-tender.html`
- ✅ `templates/favorites.html`

Semua template sekarang include `session_check.js` untuk auto-detect session expire.

## Cara Kerja

### Skenario 1: User Idle 30 Menit
1. User membuka halaman tender dan idle (tidak interaksi)
2. Setelah 30 menit, `last_activity` di database outdated
3. JavaScript `session_check.js` cek `/api/check-session` setiap 60 detik
4. API return `{valid: false, reason: 'idle_timeout'}`
5. Alert muncul: "Sesi Anda idle lebih dari 30 menit. Silakan login kembali."
6. Auto redirect ke `/login`

### Skenario 2: Cleanup Script Jalan
1. `cleanup_sessions.py` berjalan via cron/scheduler
2. Script set `user.session_id = None` untuk user yang idle > 30 menit
3. User di browser masih punya cookie `session_id`
4. Pada next request atau saat `session_check.js` cek:
   - Middleware/API detect `session_id` tidak cocok
   - Return `{valid: false, reason: 'session_mismatch'}`
5. Alert: "Akun Anda login di perangkat lain."
6. Auto redirect ke `/login`

### Skenario 3: Account Expired
1. User `active_until` sudah lewat
2. API return `{valid: false, reason: 'account_expired'}`
3. Alert: "Akun Anda sudah kadaluarsa. Silakan perpanjang langganan."
4. Auto redirect ke `/login`

## Konfigurasi Timeout

File: `config.py`
```python
SESSION_TIMEOUT_MINUTES = 30  # Dari .env atau default 30
```

File: `app.py`
```python
MAX_IDLE_MINUTES = 30  # Sekarang konsisten dengan config
```

File: `routes.py` - Endpoint `/api/check-session`
```python
if idle_minutes > 30:  # 30 minutes idle timeout
    return jsonify({'valid': False, 'reason': 'idle_timeout'})
```

File: `static/js/session_check.js`
```javascript
const CHECK_INTERVAL = 60 * 1000; // Cek setiap 60 detik
```

## Testing

### Test Manual:
1. Login ke aplikasi
2. Tunggu idle > 30 menit (atau ubah sementara `MAX_IDLE_MINUTES = 1` untuk testing)
3. Refresh page atau tunggu auto-check (60 detik)
4. Seharusnya auto redirect ke login dengan alert

### Test Cleanup Script:
1. Login ke aplikasi
2. Jalankan `python cleanup_sessions.py` secara manual
3. Tunggu 60 detik (auto-check interval)
4. Atau buka tab/window baru dan navigate ke halaman lain
5. Seharusnya auto redirect ke login

## Catatan Penting

⚠️ **Admin** tidak terpengaruh oleh:
- Session mismatch (bisa login multiple devices)
- Beberapa validasi di middleware

✅ **User biasa** affected by:
- Idle timeout (30 menit)
- Session mismatch (login di device lain)
- Account expiration

🔒 **Security**:
- Session check dilakukan di client-side (JavaScript) + server-side (middleware)
- Server tetap authoritative - JavaScript hanya untuk UX
- Cookie session tetap aman karena server validate setiap request
