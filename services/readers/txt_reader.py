"""Reader TXT cho kho văn bản."""

from __future__ import annotations

from pathlib import Path
import logging

from services.readers.base import ReaderResult

logger = logging.getLogger(__name__)


class TxtReader:
    """Đọc text thuần với một số encoding phổ biến."""

    def read(self, path: str | Path) -> ReaderResult:
        file_path = Path(path)
        for encoding in ("utf-8", "utf-8-sig", "cp1258", "cp1252"):
            try:
                text = file_path.read_text(encoding=encoding)
                return ReaderResult(text=text, pages=1, metadata={"encoding": encoding}, status="read")
            except UnicodeDecodeError:
                continue
            except Exception as exc:
                logger.exception("Cannot read TXT file: %s", file_path)
                return ReaderResult(text="", status="failed", error=str(exc))
        return ReaderResult(text="", status="failed", error="Không xác định được encoding TXT")
