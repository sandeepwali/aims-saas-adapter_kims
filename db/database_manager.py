import os
import sqlite3
from modules.common.common import set_logger

logger = set_logger()


class DatabaseManager:
    """SQLite DB for articles."""

    def __init__(self, db_path: str):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._initialize_database()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _initialize_database(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id TEXT UNIQUE,
                Bezeichnung TEXT,
                VKNetto1 TEXT,
                VKBrutto1 TEXT,
                ean TEXT,
                hash_code TEXT,
                aims_flag INTEGER DEFAULT 1,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        )
        conn.commit()
        conn.close()

    def get_article(self, article_id: str):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT article_id, ean, hash_code 
            FROM articles 
            WHERE article_id=?
        """,
            (article_id,),
        )
        row = cursor.fetchone()
        conn.close()
        return row

    def upsert_article(
        self, article_id: str, name: str, vknetto: str, vkbrutto: str, ean: str, hash_code: str
    ) -> int:
        existing = self.get_article(article_id)
        conn = self._get_connection()
        cursor = conn.cursor()

        if not existing:
            cursor.execute(
                """
                INSERT INTO articles (article_id, Bezeichnung, VKNetto1, VKBrutto1, ean, hash_code, aims_flag)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """,
                (article_id, name, vknetto, vkbrutto, ean, hash_code),
            )
            updated = 1

        elif existing[2] != hash_code:
            cursor.execute(
                """
                UPDATE articles
                SET Bezeichnung=?, VKNetto1=?, VKBrutto1=?, ean=?, hash_code=?, aims_flag=1, last_updated=CURRENT_TIMESTAMP
                WHERE article_id=?
            """,
                (name, vknetto, vkbrutto, ean, hash_code, article_id),
            )
            updated = 1

        else:
            updated = 0

        conn.commit()
        conn.close()
        return updated

    def get_pending_for_aims(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT article_id, Bezeichnung, VKNetto1, VKBrutto1, ean
            FROM articles
            WHERE aims_flag=1
        """
        )
        rows = cursor.fetchall()
        conn.close()
        return rows

    def mark_aims_sent(self, article_ids: list):
        if not article_ids:
            return
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.executemany(
            "UPDATE articles SET aims_flag=0 WHERE article_id=?",
            [(aid,) for aid in article_ids],
        )
        conn.commit()
        conn.close()
