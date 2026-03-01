from datetime import datetime, date
from typing import List, Optional
from core.database import Database
from core.logger import get_logger
from model.subscription import UserSubscription

TAG = "SubscriptionRepo"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL,
    subscription_type VARCHAR(20) NOT NULL,
    scheduled_time VARCHAR(5) NOT NULL,
    frequency VARCHAR(10) NOT NULL DEFAULT 'daily',
    is_active BOOLEAN DEFAULT TRUE,
    last_sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(chat_id, subscription_type)
)
"""


class SubscriptionRepository:
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
            self.logger.info(f"[{TAG}] user_subscriptions table ready")
        except Exception as e:
            conn.rollback()
            self.logger.error(f"[{TAG}] init_schema failed: {e}")
        finally:
            self.db.return_postgres_connection(conn)

    def upsert(self, chat_id: int, sub_type: str, scheduled_time: str, frequency: str = "daily") -> Optional[UserSubscription]:
        conn = self.db.get_postgres_connection()
        if not conn:
            return None
        sql = """
            INSERT INTO user_subscriptions (chat_id, subscription_type, scheduled_time, frequency, is_active, updated_at)
            VALUES (%s, %s, %s, %s, TRUE, NOW())
            ON CONFLICT (chat_id, subscription_type) DO UPDATE SET
                scheduled_time = EXCLUDED.scheduled_time,
                frequency = EXCLUDED.frequency,
                is_active = TRUE,
                updated_at = NOW()
            RETURNING id, chat_id, subscription_type, scheduled_time, frequency, is_active, last_sent_at, created_at, updated_at
        """
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (chat_id, sub_type, scheduled_time, frequency))
                row = cur.fetchone()
            conn.commit()
            if row:
                return UserSubscription(
                    id=row[0], chat_id=row[1], subscription_type=row[2],
                    scheduled_time=row[3], frequency=row[4], is_active=row[5],
                    last_sent_at=row[6], created_at=row[7], updated_at=row[8]
                )
        except Exception as e:
            conn.rollback()
            self.logger.error(f"[{TAG}] upsert failed: {e}")
        finally:
            self.db.return_postgres_connection(conn)
        return None

    def get_due_subscriptions(self, current_time: str, today: date) -> List[UserSubscription]:
        conn = self.db.get_postgres_connection()
        if not conn:
            return []
        sql = """
            SELECT id, chat_id, subscription_type, scheduled_time, frequency, is_active, last_sent_at, created_at, updated_at
            FROM user_subscriptions
            WHERE is_active = TRUE
              AND scheduled_time = %s
              AND (last_sent_at IS NULL OR last_sent_at::date < %s)
        """
        results = []
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (current_time, today))
                rows = cur.fetchall()
            for row in rows:
                results.append(UserSubscription(
                    id=row[0], chat_id=row[1], subscription_type=row[2],
                    scheduled_time=row[3], frequency=row[4], is_active=row[5],
                    last_sent_at=row[6], created_at=row[7], updated_at=row[8]
                ))
        except Exception as e:
            self.logger.error(f"[{TAG}] get_due_subscriptions failed: {e}")
        finally:
            self.db.return_postgres_connection(conn)
        return results

    def update_last_sent(self, sub_id: int, sent_at: datetime) -> None:
        conn = self.db.get_postgres_connection()
        if not conn:
            return
        sql = "UPDATE user_subscriptions SET last_sent_at = %s, updated_at = NOW() WHERE id = %s"
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (sent_at, sub_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            self.logger.error(f"[{TAG}] update_last_sent failed: {e}")
        finally:
            self.db.return_postgres_connection(conn)

    def get_by_chat_id(self, chat_id: int) -> List[UserSubscription]:
        conn = self.db.get_postgres_connection()
        if not conn:
            return []
        sql = """
            SELECT id, chat_id, subscription_type, scheduled_time, frequency, is_active, last_sent_at, created_at, updated_at
            FROM user_subscriptions
            WHERE chat_id = %s AND is_active = TRUE
            ORDER BY subscription_type
        """
        results = []
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (chat_id,))
                rows = cur.fetchall()
            for row in rows:
                results.append(UserSubscription(
                    id=row[0], chat_id=row[1], subscription_type=row[2],
                    scheduled_time=row[3], frequency=row[4], is_active=row[5],
                    last_sent_at=row[6], created_at=row[7], updated_at=row[8]
                ))
        except Exception as e:
            self.logger.error(f"[{TAG}] get_by_chat_id failed: {e}")
        finally:
            self.db.return_postgres_connection(conn)
        return results

    def deactivate(self, chat_id: int, sub_type: str) -> bool:
        conn = self.db.get_postgres_connection()
        if not conn:
            return False
        sql = """
            UPDATE user_subscriptions SET is_active = FALSE, updated_at = NOW()
            WHERE chat_id = %s AND subscription_type = %s AND is_active = TRUE
        """
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (chat_id, sub_type))
                affected = cur.rowcount
            conn.commit()
            return affected > 0
        except Exception as e:
            conn.rollback()
            self.logger.error(f"[{TAG}] deactivate failed: {e}")
            return False
        finally:
            self.db.return_postgres_connection(conn)
