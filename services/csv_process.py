import os
import csv
import hashlib
import shutil
from db.database_manager import DatabaseManager
from modules.common.common import set_logger

logger = set_logger()


class CSVLoader:
    """Handles CSV reading, hashing rows, and DB upserts."""

    def __init__(
        self, db: DatabaseManager, input_dir: str, archive_dir: str, failed_dir: str
    ):
        self.db = db
        self.input_dir = input_dir
        self.archive_dir = archive_dir
        self.failed_dir = failed_dir

        for d in [self.input_dir, self.archive_dir, self.failed_dir]:
            os.makedirs(d, exist_ok=True)

    def _generate_row_hash(self, row: dict) -> str:
        """Generate SHA256 hash for CSV row. Includes all columns (sorted by key)."""
        content = "||".join(str(v).strip() for _, v in sorted(row.items()))
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _read_csv(self, file_path: str) -> list[dict]:
        with open(file_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f, delimiter=";")
            return [row for row in reader if any(str(v).strip() for v in row.values())]

    def _move_file(self, src: str, dst_dir: str, new_filename: str = None):
        """Move a file to a folder with optional new filename."""
        os.makedirs(dst_dir, exist_ok=True)
        if new_filename is None:
            new_filename = os.path.basename(src)
        dest_path = os.path.join(dst_dir, new_filename)
        shutil.move(src, dest_path)
        return dest_path

    def process_csv(self, file_path: str) -> bool:
        try:
            rows = self._read_csv(file_path)
            if not rows:
                logger.warning(f"No valid rows in CSV: {file_path}")
                return False

            success = False
            for row in rows:
                article_id = row.get("ArtikelNr", "").strip()
                name = row.get("Bezeichnung", "").strip()
                price_net = row.get("VKNetto1", "").strip()
                price_gross = row.get("VKBrutto1", "").strip() if "VKBrutto1" in row else ""
                ean = row.get("EAN1", "").strip() or ""

                if not article_id:
                    logger.warning(f"Skipping invalid row: {row}")
                    continue

                row_hash = self._generate_row_hash(row)

                self.db.upsert_article(article_id, name, price_net, price_gross, ean, row_hash)
                success = True

            return success

        except Exception as e:
            logger.error(f"Error processing CSV {file_path}: {e}")
            return False
