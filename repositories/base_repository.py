from typing import Any
from database.connection import get_connection


class BaseRepository:
    def fetch_all(self, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        with get_connection() as conn:
            return [dict(row) for row in conn.execute(query, params).fetchall()]

    def fetch_one(self, query: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        with get_connection() as conn:
            row = conn.execute(query, params).fetchone()
            return dict(row) if row else None

    def execute(self, query: str, params: tuple[Any, ...] = ()) -> int:
        with get_connection() as conn:
            cur = conn.execute(query, params)
            return int(cur.lastrowid or cur.rowcount)
