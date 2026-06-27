"""Repository nền cho thao tác SQLite an toàn."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any
import logging

from database.connection import get_connection

logger = logging.getLogger(__name__)


class BaseRepository:
    """Cung cấp các hàm đọc/ghi dùng chung cho repository nghiệp vụ."""

    def fetch_all(self, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        """Trả về nhiều dòng dưới dạng dict."""
        with get_connection() as conn:
            return [dict(row) for row in conn.execute(query, params).fetchall()]

    def fetch_one(self, query: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        """Trả về một dòng dưới dạng dict hoặc None."""
        with get_connection() as conn:
            row = conn.execute(query, params).fetchone()
            return dict(row) if row else None

    def execute(self, query: str, params: tuple[Any, ...] = ()) -> int:
        """Thực thi câu lệnh ghi dữ liệu và trả về lastrowid/rowcount."""
        with get_connection() as conn:
            cur = conn.execute(query, params)
            return int(cur.lastrowid or cur.rowcount)

    def insert(self, table: str, data: Mapping[str, Any]) -> int:
        """Thêm một bản ghi và trả về id mới."""
        cleaned = {key: value for key, value in data.items() if key != "id" and value is not None}
        if not cleaned:
            raise ValueError("Không có dữ liệu để thêm")
        columns = ", ".join(cleaned.keys())
        placeholders = ", ".join("?" for _ in cleaned)
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        logger.debug("Insert into %s: %s", table, cleaned.keys())
        return self.execute(query, tuple(cleaned.values()))

    def update(self, table: str, record_id: int, data: Mapping[str, Any]) -> int:
        """Cập nhật một bản ghi theo id."""
        if record_id <= 0:
            raise ValueError("record_id phải lớn hơn 0")
        cleaned = {key: value for key, value in data.items() if key != "id" and value is not None}
        if not cleaned:
            return 0
        assignments = ", ".join(f"{key}=?" for key in cleaned)
        query = f"UPDATE {table} SET {assignments}, updated_at=CURRENT_TIMESTAMP WHERE id=?"
        logger.debug("Update %s id=%s", table, record_id)
        return self.execute(query, (*cleaned.values(), record_id))

    def delete(self, table: str, record_id: int) -> int:
        """Xóa một bản ghi theo id."""
        if record_id <= 0:
            raise ValueError("record_id phải lớn hơn 0")
        return self.execute(f"DELETE FROM {table} WHERE id=?", (record_id,))

    def find(self, table: str, record_id: int) -> dict[str, Any] | None:
        """Tìm một bản ghi theo id."""
        if record_id <= 0:
            raise ValueError("record_id phải lớn hơn 0")
        return self.fetch_one(f"SELECT * FROM {table} WHERE id=?", (record_id,))

    def list(
        self,
        table: str,
        *,
        order_by: str = "id DESC",
        limit: int | None = None,
        where: str | None = None,
        params: Sequence[Any] = (),
    ) -> list[dict[str, Any]]:
        """Liệt kê bản ghi của một bảng với điều kiện đơn giản."""
        query = f"SELECT * FROM {table}"
        if where:
            query += f" WHERE {where}"
        if order_by:
            query += f" ORDER BY {order_by}"
        query_params: tuple[Any, ...] = tuple(params)
        if limit is not None:
            if limit <= 0:
                raise ValueError("limit phải lớn hơn 0")
            query += " LIMIT ?"
            query_params = (*query_params, limit)
        return self.fetch_all(query, query_params)
