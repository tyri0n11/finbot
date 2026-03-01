from typing import List
from core.database import Database
from core.logger import get_logger
from model.message import Message

TAG = "MessageRepo"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS messages (
    id           SERIAL PRIMARY KEY,
    chat_id      BIGINT NOT NULL,
    direction    VARCHAR(4) NOT NULL,
    content      TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text',
    created_at   TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (chat_id) REFERENCES users(chat_id)
)
"""


class MessageRepository:
    def __init__(self, db: Database):
        self.db = db
        self.logger = get_logger()

    def init_schema(self) -> None:
        conn = self.db.get_postgres_connection()
        if not conn:
            self.logger.error(f"[{TAG}] Cannot init schema: no DB connection")
            return
        try:
            with conn.cursor() as cur:
                cur.execute(CREATE_TABLE_SQL)
            conn.commit()
            self.logger.info(f"[{TAG}] messages table ready")
        except Exception as e:
            conn.rollback()
            self.logger.error(f"[{TAG}] init_schema failed: {e}")
        finally:
            self.db.return_postgres_connection(conn)

    def insert(self, chat_id: int, direction: str, content: str,
               message_type: str = "text") -> None:
        conn = self.db.get_postgres_connection()
        if not conn:
            return
        sql = """
            INSERT INTO messages (chat_id, direction, content, message_type)
            VALUES (%s, %s, %s, %s)
        """
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (chat_id, direction, content, message_type))
            conn.commit()
        except Exception as e:
            conn.rollback()
            self.logger.error(f"[{TAG}] insert failed: {e}")
        finally:
            self.db.return_postgres_connection(conn)

    def get_history(self, chat_id: int, limit: int = 20) -> List[Message]:
        conn = self.db.get_postgres_connection()
        if not conn:
            return []
        sql = """
            SELECT id, chat_id, direction, content, message_type, created_at
            FROM messages
            WHERE chat_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        results = []
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (chat_id, limit))
                rows = cur.fetchall()
            for row in rows:
                results.append(Message(id=row[0], chat_id=row[1], direction=row[2],
                                       content=row[3], message_type=row[4], created_at=row[5]))
        except Exception as e:
            self.logger.error(f"[{TAG}] get_history failed: {e}")
        finally:
            self.db.return_postgres_connection(conn)
        return results
