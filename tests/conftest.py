"""Cấu hình kiểm thử cho BXD Smart Office.

Mỗi test dùng một database SQLite sạch để tránh lỗi trùng dữ liệu
khi chạy lại nhiều lần trên cùng một thư mục source.
"""

from collections.abc import Iterator
from pathlib import Path
import shutil
import sys

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.config import DB_PATH, UPLOAD_DIR, EXPORT_DIR  # noqa: E402


@pytest.fixture(autouse=True)
def clean_runtime_data() -> Iterator[None]:
    """Xóa dữ liệu runtime trước mỗi test để test có thể chạy lặp lại."""
    if DB_PATH.exists():
        DB_PATH.unlink()
    if UPLOAD_DIR.exists():
        shutil.rmtree(UPLOAD_DIR)
    if EXPORT_DIR.exists():
        shutil.rmtree(EXPORT_DIR)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    yield
