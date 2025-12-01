import os
import shutil
import zipfile
import datetime
from modules.common.common import set_logger

logger = set_logger()


class MaintenanceManager:
    """
    Handles:
      - Zipping previous day folder inside 'archived'
      - Removing the raw folder immediately after ZIP creation
      - Purging old ZIPs
    """

    def __init__(self, archived_dir: str, zip_retention_days: int = 60):
        self.archived_dir = archived_dir
        self.zip_retention_days = zip_retention_days
        os.makedirs(self.archived_dir, exist_ok=True)
        self.last_run_date = None  # to ensure run once per day

    def run_daily_tasks(self):
        """Run once per day (even if daemon sleeps every SCAN_INTERVAL seconds)."""
        today = datetime.date.today()
        if self.last_run_date == today:
            return
        self.last_run_date = today
        self._zip_previous_day_folder()
        self._purge_old_zips()

    def _zip_previous_day_folder(self):
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        folder_name = yesterday.strftime("%d%m%Y")
        folder_path = os.path.join(self.archived_dir, folder_name)
        if not os.path.isdir(folder_path):
            logger.info(f"No folder to ZIP for yesterday: {folder_name}")
            return
        zip_path = os.path.join(self.archived_dir, f"{folder_name}.zip")
        try:
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for root, _, files in os.walk(folder_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, folder_path)
                        zf.write(full_path, rel_path)
            logger.info(f"Created ZIP: {zip_path}")
            shutil.rmtree(folder_path)
            logger.info(f"Deleted raw folder after ZIP: {folder_path}")
        except Exception as e:
            logger.error(f"Error zipping/removing folder {folder_path}: {e}")

    def _purge_old_zips(self):
        """Delete ZIP files older than retention period inside archived folder."""
        now = datetime.datetime.now()
        cutoff = now - datetime.timedelta(days=self.zip_retention_days)
        for file in os.listdir(self.archived_dir):
            if not file.lower().endswith(".zip"):
                continue
            file_path = os.path.join(self.archived_dir, file)
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            if mtime < cutoff:
                try:
                    os.remove(file_path)
                    logger.info(f"Deleted old ZIP: {file}")
                except Exception as e:
                    logger.error(f"Failed to delete old ZIP {file}: {e}")
