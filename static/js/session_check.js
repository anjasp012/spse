// Auto Session Check - Deteksi otomatis jika session expired
(function() {
    // Hanya jalankan jika user sedang login (ada element dengan class 'user-logged-in' atau cek dari body data attribute)
    const isLoggedIn = document.body.dataset.loggedIn === 'true' || document.querySelector('.user-menu') !== null;

    if (!isLoggedIn) {
        return; // Skip jika belum login
    }

    // Interval check setiap 60 detik (1 menit)
    const CHECK_INTERVAL = 60 * 1000; // 60 seconds

    function checkSession() {
        fetch('/api/check-session')
            .then(response => response.json())
            .then(data => {
                if (!data.valid) {
                    // Session expired, redirect to login
                    let message = 'Sesi Anda telah berakhir. Silakan login kembali.';

                    switch(data.reason) {
                        case 'idle_timeout':
                            message = 'Sesi Anda idle lebih dari 30 menit. Silakan login kembali.';
                            break;
                        case 'session_mismatch':
                            message = 'Akun Anda login di perangkat lain. Silakan login kembali.';
                            break;
                        case 'account_expired':
                            message = 'Akun Anda sudah kadaluarsa. Silakan perpanjang langganan.';
                            break;
                    }

                    // Show alert
                    alert(message);

                    // Redirect to login page
                    window.location.href = '/login';
                }
            })
            .catch(error => {
                console.error('Session check error:', error);
            });
    }

    // Start periodic check
    const intervalId = setInterval(checkSession, CHECK_INTERVAL);

    // Also check when page becomes visible (user switches back to tab)
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden) {
            checkSession();
        }
    });

    // Check when user interacts with page after being idle
    let lastActivityCheck = Date.now();
    ['click', 'keypress', 'scroll', 'touchstart'].forEach(eventType => {
        document.addEventListener(eventType, function() {
            const now = Date.now();
            // Only check if more than 5 minutes since last activity check
            if (now - lastActivityCheck > 5 * 60 * 1000) {
                checkSession();
                lastActivityCheck = now;
            }
        }, { passive: true });
    });

    console.log('✅ Auto session check initialized (checking every 60 seconds)');
})();
