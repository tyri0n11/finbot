from typing import Optional
from core.database import Database
from core.logger import get_logger
from model.user import User

TAG = "UserRepo"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id          SERIAL PRIMARY KEY,
    chat_id     BIGINT UNIQUE NOT NULL,
    username    VARCHAR(100),
    full_name   VARCHAR(200),
    language    VARCHAR(5) DEFAULT 'vi',
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
)
"""


class UserRepository:
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
            self.logger.info(f"[{TAG}] users table ready")
        except Exception as e:
            conn.rollback()
            self.logger.error(f"[{TAG}] init_schema failed: {e}")
        finally:
            self.db.return_postgres_connection(conn)

    def upsert(self, chat_id: int, username: Optional[str] = None,
               full_name: Optional[str] = None) -> Optional[User]:
        conn = self.db.get_postgres_connection()
        if not conn:
            return None
        sql = """
            INSERT INTO users (chat_id, username, full_name, updated_at)
            VALUES (%s, %s, %s, NOW())
            ON CONFLICT (chat_id) DO UPDATE SET
                username   = COALESCE(EXCLUDED.username, users.username),
                full_name  = COALESCE(EXCLUDED.full_name, users.full_name),
                updated_at = NOW()
            RETURNING id, chat_id, username, full_name, language, is_active, created_at, updated_at
        """
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (chat_id, username, full_name))
                row = cur.fetchone()
            conn.commit()
            if row:
                return User(id=row[0], chat_id=row[1], username=row[2],
                            full_name=row[3], language=row[4], is_active=row[5],
                            created_at=row[6], updated_at=row[7])
        except Exception as e:
            conn.rollback()
            self.logger.error(f"[{TAG}] upsert failed: {e}")
        finally:
            self.db.return_postgres_connection(conn)
        return None

    def get_by_chat_id(self, chat_id: int) -> Optional[User]:
        conn = self.db.get_postgres_connection()
        if not conn:
            return None
        sql = """
            SELECT id, chat_id, username, full_name, language, is_active, created_at, updated_at
            FROM users WHERE chat_id = %s
        """
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (chat_id,))
                row = cur.fetchone()
            if row:
                return User(id=row[0], chat_id=row[1], username=row[2],
                            full_name=row[3], language=row[4], is_active=row[5],
                            created_at=row[6], updated_at=row[7])
        except Exception as e:
            self.logger.error(f"[{TAG}] get_by_chat_id failed: {e}")
        finally:
            self.db.return_postgres_connection(conn)
        return None
