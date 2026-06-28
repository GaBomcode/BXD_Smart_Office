"""Trích xuất metadata văn bản hành chính Đảng theo rule-based."""

from __future__ import annotations

from datetime import date
import logging
import re

logger = logging.getLogger(__name__)

DOCUMENT_TYPE_PATTERNS = {
    "Công văn": r"\bCÔNG VĂN\b|\bCV\b",
    "Kế hoạch": r"\bKẾ HOẠCH\b|\bKH\b",
    "Báo cáo": r"\bBÁO CÁO\b|\bBC\b",
    "Thông báo": r"\bTHÔNG BÁO\b|\bTB\b",
    "Tờ trình": r"\bTỜ TRÌNH\b|\bTTr\b",
    "Quyết định": r"\bQUYẾT ĐỊNH\b|\bQĐ\b",
}

FIELD_KEYWORDS = {
    "Tổ chức": ["tổ chức", "cán bộ", "đảng viên", "chi bộ"],
    "Tuyên giáo": ["tuyên giáo", "nghị quyết", "tuyên truyền", "học tập"],
    "Dân vận": ["dân vận", "dân tộc", "tôn giáo", "mặt trận"],
    "Tổng hợp": ["báo cáo", "tổng hợp", "chuyển đổi số", "phối hợp"],
    "Lãnh đạo điều hành": ["chỉ đạo", "điều hành", "lãnh đạo"],
}


class DocumentMetadataExtractor:
    """Trích metadata sơ bộ, chưa dùng AI và luôn cho phép người dùng duyệt lại."""

    def extract(self, text: str, *, file_name: str = "") -> dict[str, str | None]:
        normalized = self._normalize_text(text)
        lines = [line.strip() for line in normalized.splitlines() if line.strip()]
        document_number = self._extract_document_number(normalized)
        issued_date = self._extract_date(normalized)
        document_type = self._extract_document_type(normalized, document_number, file_name)
        issuing_agency = self._extract_issuing_agency(lines)
        signer = self._extract_signer(lines)
        summary = self._extract_summary(lines, document_type, file_name)
        field = self._extract_field(normalized)
        keywords = self._extract_keywords(normalized, file_name)
        title = summary or PathSafe.stem(file_name) or document_type or "Văn bản chưa đặt tên"
        return {
            "title": title,
            "document_type": document_type,
            "document_number": document_number,
            "issued_date": issued_date,
            "issuing_agency": issuing_agency,
            "signer": signer,
            "summary": summary,
            "keywords": ", ".join(keywords),
            "field": field,
        }

    @staticmethod
    def _normalize_text(text: str) -> str:
        return re.sub(r"[ \t]+", " ", text.replace("\r\n", "\n").replace("\r", "\n"))

    @staticmethod
    def _extract_document_number(text: str) -> str | None:
        match = re.search(r"Số\s*[:：]\s*([0-9A-Za-zÀ-ỹ/.\-]+)", text, flags=re.IGNORECASE)
        return match.group(1).strip() if match else None

    @staticmethod
    def _extract_date(text: str) -> str | None:
        match = re.search(r"ngày\s+(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})", text, flags=re.IGNORECASE)
        if match:
            day, month, year = map(int, match.groups())
            try:
                return date(year, month, day).isoformat()
            except ValueError:
                logger.warning("Ngày văn bản không hợp lệ: %s", match.group(0))
        match = re.search(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", text)
        if match:
            day, month, year = map(int, match.groups())
            try:
                return date(year, month, day).isoformat()
            except ValueError:
                return None
        return None

    @staticmethod
    def _extract_document_type(text: str, document_number: str | None, file_name: str) -> str | None:
        haystack = f"{text}\n{document_number or ''}\n{file_name}"
        for document_type, pattern in DOCUMENT_TYPE_PATTERNS.items():
            if re.search(pattern, haystack, flags=re.IGNORECASE):
                return document_type
        return None

    @staticmethod
    def _extract_issuing_agency(lines: list[str]) -> str | None:
        for line in lines[:12]:
            upper = line.upper()
            if any(signal in upper for signal in ("BAN XÂY DỰNG ĐẢNG", "ĐẢNG ỦY", "TỈNH ỦY", "HUYỆN ỦY")):
                return line
        return None

    @staticmethod
    def _extract_signer(lines: list[str]) -> str | None:
        for index, line in enumerate(lines):
            upper = line.upper()
            if upper in {"TRƯỞNG BAN", "PHÓ TRƯỞNG BAN", "BÍ THƯ", "PHÓ BÍ THƯ"} and index + 1 < len(lines):
                candidate = lines[index + 1].strip()
                if 3 <= len(candidate) <= 80:
                    return candidate
        return None

    @staticmethod
    def _extract_summary(lines: list[str], document_type: str | None, file_name: str) -> str | None:
        for line in lines:
            cleaned = line.strip(" -")
            if len(cleaned) < 12:
                continue
            upper = cleaned.upper()
            if upper.startswith(("CỘNG HÒA", "ĐỘC LẬP", "SỐ:", "ĐẢNG ỦY", "BAN XÂY DỰNG")):
                continue
            if document_type and upper == document_type.upper():
                continue
            if cleaned.lower().startswith(("v/v", "về việc")):
                return cleaned
        return PathSafe.stem(file_name) if file_name else None

    @staticmethod
    def _extract_field(text: str) -> str | None:
        lower = text.lower()
        scores = {
            field: sum(1 for keyword in keywords if keyword in lower)
            for field, keywords in FIELD_KEYWORDS.items()
        }
        best = max(scores.items(), key=lambda item: item[1])
        return best[0] if best[1] > 0 else None

    @staticmethod
    def _extract_keywords(text: str, file_name: str) -> list[str]:
        words = re.findall(r"[0-9A-Za-zÀ-ỹ]{3,}", f"{text} {file_name}".lower())
        ignored = {
            "của",
            "cho",
            "các",
            "văn",
            "bản",
            "ngày",
            "tháng",
            "năm",
            "được",
            "theo",
            "trong",
            "với",
            "trên",
            "dưới",
            "nơi",
            "nhận",
        }
        unique: list[str] = []
        for word in words:
            if word not in ignored and word not in unique:
                unique.append(word)
            if len(unique) >= 12:
                break
        return unique


class PathSafe:
    """Tiện ích tránh import pathlib trong các test extractor đơn giản."""

    @staticmethod
    def stem(file_name: str) -> str:
        if not file_name:
            return ""
        return re.sub(r"\.[^.]+$", "", file_name).replace("_", " ").replace("-", " ").strip()
