import sqlite3
import uuid

from config import LONG_TERM_DB_PATH


class LongTermMemory:
    """
    Persistent user-level memory stored in SQLite.
    """

    def __init__(
        self,
        db_path=LONG_TERM_DB_PATH,
    ):
        self.db_path = db_path
        self._create_table()


    def _connect(self):
        return sqlite3.connect(
            self.db_path
        )


    def _create_table(self):
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    memory_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            connection.commit()


    def add_memory(
        self,
        user_id: str,
        content: str,
    ):
        memory_id = str(
            uuid.uuid4()
        )

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO memories (
                    memory_id,
                    user_id,
                    content
                )
                VALUES (?, ?, ?)
                """,
                (
                    memory_id,
                    user_id,
                    content,
                )
            )

            connection.commit()

        return memory_id


    def get_memories(
        self,
        user_id: str,
    ):
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT content
                FROM memories
                WHERE user_id = ?
                ORDER BY created_at, memory_id
                """,
                (user_id,)
            ).fetchall()

        return [
            row[0]
            for row in rows
        ]


    def delete_user_memories(
        self,
        user_id: str,
    ):
        with self._connect() as connection:
            connection.execute(
                """
                DELETE FROM memories
                WHERE user_id = ?
                """,
                (user_id,)
            )

            connection.commit()


long_term_memory = LongTermMemory()
