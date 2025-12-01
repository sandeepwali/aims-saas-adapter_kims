import os
import time
from dotenv import load_dotenv

from db.database_manager import DatabaseManager
from services.csv_process import CSVLoader
from services.load_artciles import AIMSSyncService
from modules.lib import append_timestamp
from pid import ensure_single_instance

from modules.common.maintenance import MaintenanceManager
from modules.common.common import set_logger


# Load environment
load_dotenv()
logger = set_logger()

# Directories
BASE_DIR = os.path.join(os.getcwd(), "data")
INPUT_DIR = os.path.join(BASE_DIR, os.getenv("CSV_INPUT_DIR", "input"))
ARCHIVED_DIR = os.path.join(BASE_DIR, os.getenv("CSV_ARCHIVE_DIR", "archived"))
FAILED_DIR = os.path.join(BASE_DIR, os.getenv("CSV_FAILED_DIR", "failed"))

# DB
DB_PATH = os.getenv("DB_PATH", os.path.join(BASE_DIR, "db", "aims.db"))
# default scan interval: 5 minutes (300 seconds)
SCAN_INTERVAL = int(os.getenv("SCAN_INTERVAL", "300"))

# Ensure directories exist
for folder in [INPUT_DIR, ARCHIVED_DIR, FAILED_DIR, os.path.dirname(DB_PATH)]:
    os.makedirs(folder, exist_ok=True)

# Ensure only one instance is running
PID_FILE = os.path.join(BASE_DIR, "sync_daemon.pid")
ensure_single_instance(PID_FILE)


def run_sync_daemon():
    logger.info("Starting Automated Article Delta Sync Service")

    db = DatabaseManager(DB_PATH)
    csv_loader = CSVLoader(
        db=db, input_dir=INPUT_DIR, archive_dir=ARCHIVED_DIR, failed_dir=FAILED_DIR
    )
    aims_sync = AIMSSyncService(db=db, failed_dir=FAILED_DIR)

    maintenance = MaintenanceManager(archived_dir=ARCHIVED_DIR, zip_retention_days=60)

    try:
        while True:

            # Run daily maintenance tasks
            maintenance.run_daily_tasks()

            # Scan CSV files
            csv_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".csv")]
            if not csv_files:
                logger.info("No new CSV files found.")

            for filename in csv_files:
                file_path = os.path.join(INPUT_DIR, filename)
                logger.info(f"Processing CSV file: {filename}")

                updated = csv_loader.process_csv(file_path)
                timestamped_filename = append_timestamp(filename)

                # Only attempt sync if CSV processing succeeded
                if updated:
                    try:
                        logger.info(
                            f"Syncing articles from CSV: {timestamped_filename}"
                        )
                        sync_success = aims_sync.sync_all_pending_articles()

                        if sync_success:
                            # Only archive if sync succeeds
                            today_folder = os.path.join(
                                ARCHIVED_DIR, time.strftime("%d%m%Y")
                            )
                            os.makedirs(today_folder, exist_ok=True)
                            target_path = os.path.join(
                                today_folder, timestamped_filename
                            )
                            os.rename(file_path, target_path)
                            logger.info(f"CSV archived successfully: {target_path}")
                        else:
                            # Move to failed folder
                            failed_path = os.path.join(FAILED_DIR, timestamped_filename)
                            os.rename(file_path, failed_path)
                            logger.warning(
                                f"CSV moved to failed folder due to sync failure: {failed_path}"
                            )

                    except Exception as e:
                        logger.error(f"Unexpected error during sync: {e}")
                        failed_path = os.path.join(FAILED_DIR, timestamped_filename)
                        os.rename(file_path, failed_path)
                        logger.warning(
                            f"CSV moved to failed folder due to exception: {failed_path}"
                        )
                else:
                    # Move invalid CSV to failed folder
                    failed_path = os.path.join(FAILED_DIR, timestamped_filename)
                    os.rename(file_path, failed_path)
                    logger.warning(
                        f"CSV moved to failed folder due to invalid data: {failed_path}"
                    )

            logger.info(f"Sleeping for {SCAN_INTERVAL} seconds before next check...")
            time.sleep(SCAN_INTERVAL)

    except KeyboardInterrupt:
        logger.info("Daemon interrupted by user. Exiting...")
    except Exception as e:
        logger.error(f"Daemon stopped unexpectedly: {e}")
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
            logger.info(f"PID file {PID_FILE} removed on exit.")


if __name__ == "__main__":
    run_sync_daemon()
