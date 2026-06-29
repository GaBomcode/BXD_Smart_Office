"""Validation rules for AI Draft final validation."""

from __future__ import annotations

from collections import Counter
from typing import Any
import re

PLACEHOLDER_PATTERN = re.compile(r"(\{\{[^}]+\}\}|\[\[[^\]]+\]\]|<[^>]+>)")
CITATION_PATTERN = re.compile(r"\[(\d+)\]")
NUMBERED_HEADING_PATTERN = re.compile(r"^\s*(\d+)\.\s+(.+)")


class ValidationRules:
    """Pure validation helpers used by the draft validator service."""

    REQUIRED_METADATA = ("title", "document_type")

    @staticmethod
    def text(draft: dict[str, Any]) -> str:
        """Return draft content as plain text."""
        return str(draft.get("draft_content") or draft.get("body") or "")

    @staticmethod
    def title(draft: dict[str, Any]) -> str:
        """Return draft title."""
        return str(draft.get("title") or "").strip()

    @classmethod
    def missing_metadata(cls, draft: dict[str, Any]) -> list[str]:
        """Return missing mandatory metadata fields."""
        return [field for field in cls.REQUIRED_METADATA if not str(draft.get(field) or "").strip()]

    @staticmethod
    def invalid_placeholders(text: str) -> list[str]:
        """Return unresolved placeholder tokens that must fail validation."""
        return PLACEHOLDER_PATTERN.findall(text)

    @staticmethod
    def citation_markers(text: str) -> list[int]:
        """Return numeric citation markers used in draft text."""
        return [int(value) for value in CITATION_PATTERN.findall(text)]

    @staticmethod
    def duplicate_citation_keys(citations: list[dict[str, Any]]) -> list[str]:
        """Return duplicate citation keys after normalizing source identity."""
        keys = [ValidationRules.citation_key(citation) for citation in citations]
        counts = Counter(keys)
        return [key for key, count in counts.items() if key and count > 1]

    @staticmethod
    def deduplicate_citations(citations: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Return citations with duplicate source references removed."""
        seen: set[str] = set()
        unique: list[dict[str, Any]] = []
        for citation in citations:
            key = ValidationRules.citation_key(citation)
            if key in seen:
                continue
            seen.add(key)
            unique.append(citation)
        return unique

    @staticmethod
    def citation_key(citation: dict[str, Any]) -> str:
        """Build a stable citation identity key."""
        return "|".join(
            str(citation.get(field) or "")
            for field in ("source_document_id", "source_chunk_id", "checksum", "document_number")
        )

    @staticmethod
    def empty_paragraphs(text: str) -> list[int]:
        """Return line numbers for whitespace-only paragraph lines."""
        return [index for index, line in enumerate(text.splitlines(), start=1) if line and not line.strip()]

    @staticmethod
    def has_body(text: str) -> bool:
        """Return true when a body section is present and populated."""
        normalized = text.lower()
        body_markers = ("noi dung", "nội dung", "tham muu", "tham mưu")
        return any(marker in normalized for marker in body_markers) and len(text.strip()) >= 80

    @staticmethod
    def has_conclusion(text: str) -> bool:
        """Return true when a conclusion or final note section exists."""
        normalized = text.lower()
        markers = ("ket luan", "kết luận", "luu y", "lưu ý", "kien nghi", "kiến nghị")
        return any(marker in normalized for marker in markers)

    @staticmethod
    def has_signature(text: str) -> bool:
        """Return true when a signature block is present."""
        normalized = text.lower()
        markers = ("nguoi ky", "người ký", "truong ban", "trưởng ban", "kt.", "tm.")
        return any(marker in normalized for marker in markers)

    @staticmethod
    def has_references_when_needed(text: str, citations: list[dict[str, Any]]) -> bool:
        """Return true when cited drafts have source references."""
        return not ValidationRules.citation_markers(text) or bool(citations)

    @staticmethod
    def numbered_headings(text: str) -> list[int]:
        """Return numbering sequence from numbered headings."""
        numbers: list[int] = []
        for line in text.splitlines():
            match = NUMBERED_HEADING_PATTERN.match(line)
            if match:
                numbers.append(int(match.group(1)))
        return numbers

    @staticmethod
    def duplicate_headings(text: str) -> list[str]:
        """Return duplicate numbered heading titles."""
        headings: list[str] = []
        for line in text.splitlines():
            match = NUMBERED_HEADING_PATTERN.match(line)
            if match:
                headings.append(match.group(2).strip().lower())
        counts = Counter(headings)
        return [heading for heading, count in counts.items() if count > 1]

    @staticmethod
    def empty_list_items(text: str) -> list[int]:
        """Return line numbers for empty list items."""
        empty: list[int] = []
        for index, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if stripped in {"-", "+", "*"} or re.fullmatch(r"\d+\.", stripped):
                empty.append(index)
        return empty

    @staticmethod
    def missing_numbering(numbers: list[int]) -> list[int]:
        """Return missing numbers in a heading sequence."""
        if not numbers:
            return []
        expected = set(range(min(numbers), max(numbers) + 1))
        return sorted(expected.difference(numbers))
