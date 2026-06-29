"""Final validation service for AI Draft documents."""

from __future__ import annotations

from typing import Any
import logging

from models.draft_validation_result import DraftValidationResult
from repositories.ai_draft_repository import AIDraftRepository
from repositories.document_library_repository import DocumentLibraryRepository
from services.document_validation.validation_report import ValidationReport
from services.document_validation.validation_rules import ValidationRules

logger = logging.getLogger(__name__)


class DraftValidator:
    """Validate AI Draft structure and evidence before export."""

    def __init__(
        self,
        *,
        repository: AIDraftRepository | None = None,
        library_repository: DocumentLibraryRepository | None = None,
    ) -> None:
        self.repository = repository or AIDraftRepository()
        self.library_repository = library_repository or DocumentLibraryRepository()

    def validate(
        self,
        draft: dict[str, Any],
        *,
        citations: list[dict[str, Any]] | None = None,
    ) -> DraftValidationResult:
        """Run all final validation rules for one draft."""
        draft_citations = citations if citations is not None else self._load_citations(draft)
        unique_citations = ValidationRules.deduplicate_citations(draft_citations)
        text = ValidationRules.text(draft)

        errors: list[str] = []
        warnings: list[str] = []
        missing_sections: list[str] = []
        invalid_citations: list[str] = []
        empty_fields: list[str] = []

        self._validate_required_fields(draft, text, errors, missing_sections, empty_fields)
        self._validate_placeholders(text, errors)
        self._validate_document_format(text, warnings, missing_sections)
        self._validate_citations(text, unique_citations, errors, warnings, invalid_citations)

        duplicates = ValidationRules.duplicate_citation_keys(draft_citations)
        if duplicates:
            warnings.append(f"Duplicate citations removed: {len(duplicates)}")

        score = self._score(errors, warnings)
        passed = not errors
        recommendations = self._recommendations(errors, warnings, missing_sections, invalid_citations)
        report = ValidationReport.build(
            passed=passed,
            errors=errors,
            warnings=warnings,
            score=score,
            recommendations=recommendations,
        )
        logger.info("AI draft validation passed=%s score=%s", passed, score)
        return DraftValidationResult(
            passed=passed,
            errors=errors,
            warnings=warnings,
            score=score,
            missing_sections=missing_sections,
            invalid_citations=invalid_citations,
            empty_fields=empty_fields,
            report=report,
        )

    def _load_citations(self, draft: dict[str, Any]) -> list[dict[str, Any]]:
        result_id = draft.get("id")
        if not result_id:
            return []
        return self.repository.list_citations(result_id=int(result_id))

    def _validate_required_fields(
        self,
        draft: dict[str, Any],
        text: str,
        errors: list[str],
        missing_sections: list[str],
        empty_fields: list[str],
    ) -> None:
        for field in ValidationRules.missing_metadata(draft):
            errors.append(f"Mandatory metadata missing: {field}")
            empty_fields.append(field)
        if not ValidationRules.title(draft):
            errors.append("Title is required")
            empty_fields.append("title")
        if not text.strip():
            errors.append("Body is required")
            empty_fields.append("draft_content")
            missing_sections.append("body")
            return
        if not ValidationRules.has_body(text):
            errors.append("Body section is missing or incomplete")
            missing_sections.append("body")
        if not ValidationRules.has_conclusion(text):
            errors.append("Conclusion section is required")
            missing_sections.append("conclusion")
        if not ValidationRules.has_signature(text):
            errors.append("Signature block is required")
            missing_sections.append("signature")

    @staticmethod
    def _validate_placeholders(text: str, errors: list[str]) -> None:
        placeholders = ValidationRules.invalid_placeholders(text)
        if placeholders:
            errors.append("Invalid placeholders found: " + ", ".join(sorted(set(placeholders))))

    @staticmethod
    def _validate_document_format(
        text: str,
        warnings: list[str],
        missing_sections: list[str],
    ) -> None:
        numbers = ValidationRules.numbered_headings(text)
        missing_numbers = ValidationRules.missing_numbering(numbers)
        duplicate_headings = ValidationRules.duplicate_headings(text)
        empty_lists = ValidationRules.empty_list_items(text)
        empty_paragraphs = ValidationRules.empty_paragraphs(text)
        if numbers and numbers[0] != 1:
            warnings.append("Heading hierarchy should start at 1")
        if missing_numbers:
            warnings.append("Missing numbering: " + ", ".join(str(number) for number in missing_numbers))
            missing_sections.append("numbering")
        if duplicate_headings:
            warnings.append("Duplicate headings: " + ", ".join(duplicate_headings))
        if empty_lists:
            warnings.append("Empty list items at line(s): " + ", ".join(str(line) for line in empty_lists))
        if empty_paragraphs:
            warnings.append("Empty paragraphs at line(s): " + ", ".join(str(line) for line in empty_paragraphs))

    def _validate_citations(
        self,
        text: str,
        citations: list[dict[str, Any]],
        errors: list[str],
        warnings: list[str],
        invalid_citations: list[str],
    ) -> None:
        markers = ValidationRules.citation_markers(text)
        if not ValidationRules.has_references_when_needed(text, citations):
            errors.append("References are required when evidence citations are used")
        if markers and max(markers) > len(citations):
            errors.append("Citation marker points to a missing reference")
            invalid_citations.append(f"[{max(markers)}]")
        if citations and not markers:
            warnings.append("Evidence exists but no citation markers were found in draft text")
        for citation in citations:
            source_document_id = citation.get("source_document_id")
            if not source_document_id or not self.library_repository.get_document(int(source_document_id)):
                label = str(citation.get("document_number") or citation.get("title") or source_document_id or "unknown")
                invalid_citations.append(label)
        if invalid_citations:
            errors.append("Every citation must point to an existing document")

    @staticmethod
    def _score(errors: list[str], warnings: list[str]) -> float:
        score = 1.0 - (len(errors) * 0.2) - (len(warnings) * 0.05)
        return round(max(score, 0.0), 2)

    @staticmethod
    def _recommendations(
        errors: list[str],
        warnings: list[str],
        missing_sections: list[str],
        invalid_citations: list[str],
    ) -> list[str]:
        recommendations: list[str] = []
        if missing_sections:
            recommendations.append("Complete missing draft sections before approval/export.")
        if invalid_citations:
            recommendations.append("Replace or remove citations that do not map to existing documents.")
        if any("placeholder" in error.lower() for error in errors):
            recommendations.append("Resolve all placeholders before export.")
        if warnings:
            recommendations.append("Review warnings to improve document quality.")
        return recommendations
