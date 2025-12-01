import os
import shutil
import time
from modules.aims_saas.aims_saas_api_client import AIMSSaaSAPIClient
from modules.common.common import set_logger

logger = set_logger()

STORE_ID = os.getenv("AIMS_SAAS_STORE", "KL001")
COMPANY_ID = os.getenv("AIMS_SAAS_COMPANY", "KIM")


class AIMSSyncService:
    """Sync pending articles to AIMS SaaS."""

    def __init__(self, db, failed_dir: str):
        self.db = db
        self.failed_dir = failed_dir
        os.makedirs(self.failed_dir, exist_ok=True)

        self.client = AIMSSaaSAPIClient()
        logger.info("AIMS SaaS client initialized.")

    def _prepare_articles_payload(self, rows):
        """
        rows: list of tuples (article_id, Bezeichnung, VKNetto1, VKBrutto1, ean)
        """
        articles = []

        for article_id, name, vknetto, vkbrutto, ean in rows:
            data_fields = {
                "STORE_ID": STORE_ID,
                "ArtikelNr": article_id,
                "Bezeichnung": name,
                "VKNetto1": vknetto,
                "VKBrutto1": vkbrutto,
                "EAN1": ean or "",
            }

            articles.append(
                {
                    "store": STORE_ID,
                    "articleId": article_id,
                    "articleName": name,
                    "eans": [ean] if ean else [],
                    "data": data_fields,
                }
            )

        return articles

    def _send_payload(self, articles):
        max_attempts = 5
        attempt = 1

        while attempt <= max_attempts:
            try:
                response = self.client.add_articles(STORE_ID, articles, 5000)

                if getattr(response, "status_code", None) in (200, 202):
                    return True

                if getattr(response, "status_code", None) == 401:
                    logger.info(
                        f"Attempt {attempt}: Token expired or unauthorized. Refreshing..."
                    )
                    attempt += 1
                    time.sleep(1)
                    continue  # retry once

                # Other errors
                logger.error(f"AIMS SaaS error: {getattr(response, 'text', repr(response))}")
                return False

            except Exception as e:
                logger.error(f"AIMS SaaS API call failed on attempt {attempt}: {e}")
                attempt += 1
                time.sleep(1)

        logger.error("Failed to send articles after 5 attempts.")
        return False

    def sync_all_pending_articles(self):
        logger.info("Checking DB for pending article updates...")
        rows = self.db.get_pending_for_aims()
        if not rows:
            logger.info("No pending articles.")
            return False  # indicate sync did not succeed

        articles_payload = self._prepare_articles_payload(rows)
        success = self._send_payload(articles_payload)

        if success:
            article_ids = [r[0] for r in rows]
            self.db.mark_aims_sent(article_ids)
            logger.info(f"Marked {len(article_ids)} articles as synced.")
        else:
            logger.error("Failed to send articles to AIMS API.")

        return success

    def _move_to_failed(self, file_path):
        """Move file to failed folder if AIMS sync fails."""
        try:
            shutil.move(
                file_path, os.path.join(self.failed_dir, os.path.basename(file_path))
            )
            logger.info(f"CSV moved to failed folder: {file_path}")
        except Exception as e:
            logger.error(f"Failed moving file to failed dir: {e}")
