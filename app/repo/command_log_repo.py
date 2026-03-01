from typing import List, Optional
from core.database import Database
from core.logger import get_logger
from model.command_log import CommandLog

TAG = "CommandLogRepo"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS command_logs (
    id          SERIAL PRIMARY KEY,
    chat_id     BIGINT NOT NULL,
    command     VARCHAR(50) NOT NULL,
    args        TEXT,
    status      VARCHAR(10) DEFAULT 'ok',
    error_msg   TEXT,
    created_at  TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (chat_id) REFERENCES users(chat_id)
)
"""


class CommandLogRepository:
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
            self.logger.info(f"[{TAG}] command_logs table ready")
        except Exception as e:
            conn.rollback()
            self.logger.error(f"[{TAG}] init_schema failed: {e}")
        finally:
            self.db.return_postgres_connection(conn)

    def insert(self, chat_id: int, command: str, args: Optional[str] = None,
               status: str = "ok", error_msg: Optional[str] = None) -> None:
        conn = self.db.get_postgres_connection()
        if not conn:
            return
        sql = """
            INSERT INTO command_logs (chat_id, command, args, status, error_msg)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (chat_id, command, args, status, error_msg))
            conn.commit()
        except Exception as e:
            conn.rollback()
            self.logger.error(f"[{TAG}] insert failed: {e}")
        finally:
            self.db.return_postgres_connection(conn)

    def get_by_chat_id(self, chat_id: int, limit: int = 20) -> List[CommandLog]:
        conn = self.db.get_postgres_connection()
        if not conn:
            return []
        sql = """
            SELECT id, chat_id, command, args, status, error_msg, created_at
            FROM command_logs
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
                results.append(CommandLog(id=row[0], chat_id=row[1], command=row[2],
                                          args=row[3], status=row[4], error_msg=row[5],
                                          created_at=row[6]))
        except Exception as e:
            self.logger.error(f"[{TAG}] get_by_chat_id failed: {e}")
        finally:
            self.db.return_postgres_connection(conn)
        return results
