import logging
import sys
from logging.handlers import RotatingFileHandler
import os

def setup_logger(app):
    """
    Setup logging configuration untuk aplikasi Flask
    """
    # Create logs directory jika belum ada
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Set log level
    log_level = logging.DEBUG if app.debug else logging.INFO

    # Format log
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )

    # File handler - rotating file (max 10MB, keep 10 backup files)
    file_handler = RotatingFileHandler(
        'logs/spse.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    # Add handlers to app logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(log_level)

    # Log startup
    app.logger.info('=' * 50)
    app.logger.info('SPSE Application Starting')
    app.logger.info('=' * 50)

    return app.logger
