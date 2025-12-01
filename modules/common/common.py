import os
import logging
import zipfile
import datetime
from logging.handlers import RotatingFileHandler
from env import LOG_LEVEL


LOG_DIR = "./logs"
LOG_NAME = "aims_saas_adapter_kims"


def set_logger(logger_name=LOG_NAME, retention_days=15):
    """
    Set up a daily log with rotation, previous-day ZIP, and purge old logs.
    """
    # Create logs directory
    os.makedirs(LOG_DIR, exist_ok=True)

    # Log file for today
    today_str = datetime.date.today().strftime("%d%m%Y")
    log_file = os.path.join(LOG_DIR, f"{logger_name}_{today_str}.log")

    # Set log level
    log_levels = {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
    }
    log_level = log_levels.get(LOG_LEVEL, logging.INFO)

    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)

    log_format = "%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s"
    formatter = logging.Formatter(log_format)

    # Stream handler (console)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(formatter)

    # Rotating file handler
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=0
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    # Clear existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    # Run maintenance: zip previous day and purge old
    _zip_previous_day_log(logger_name, retention_days)
    _purge_old_logs(logger_name, retention_days)

    return logger


def _zip_previous_day_log(logger_name, retention_days):
    """Zip yesterday's log file if exists"""
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    yesterday_str = yesterday.strftime("%d%m%Y")
    log_file = os.path.join(LOG_DIR, f"{logger_name}_{yesterday_str}.log")
    zip_file = os.path.join(LOG_DIR, f"{logger_name}_{yesterday_str}.zip")

    if os.path.isfile(log_file):
        try:
            with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.write(log_file, arcname=os.path.basename(log_file))
            os.remove(log_file)
        except Exception as e:
            print(f"Error zipping log {log_file}: {e}")


def _purge_old_logs(logger_name, retention_days):
    """Delete old log ZIPs older than retention_days"""
    now = datetime.datetime.now()
    cutoff = now - datetime.timedelta(days=retention_days)

    for f in os.listdir(LOG_DIR):
        if f.startswith(logger_name) and f.endswith(".zip"):
            fpath = os.path.join(LOG_DIR, f)
            if datetime.datetime.fromtimestamp(os.path.getmtime(fpath)) < cutoff:
                try:
                    os.remove(fpath)
                except Exception as e:
                    print(f"Failed to remove old log ZIP {f}: {e}")


if __name__ == "__main__":
    logger = set_logger()
    logger.info("Logger initialized with daily rotation, ZIP, and purge")
