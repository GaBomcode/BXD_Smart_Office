"""Release verification for BXD Smart Office V1.0."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import json
import sys

from core.config import BACKUP_DIR, DB_PATH, EXPORT_DIR, LOG_DIR, WORKSPACE_DIR
from database.connection import get_connection
from database.init_db import init_database
from repositories.task_repository import TaskRepository
from services.document_library_service import DocumentLibraryService
from services.document_validation.draft_validator import DraftValidator
from services.embedding_service import OllamaEmbeddingBackend
from services.knowledge_service import KnowledgeService
from services.report_service import ReportService
from services.search_service import SearchService
from models.report_request import ReportRequest
from models.search_request import SearchRequest


@dataclass(slots=True)
class VerificationResult:
    """One release verification check result."""

    name: str
    passed: bool
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize result."""
        return {"name": self.name, "passed": self.passed, "detail": self.detail}


@dataclass(slots=True)
class VerificationSummary:
    """Release verification summary."""

    results: list[VerificationResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """Return true when every check passed."""
        return all(result.passed for result in self.results)

    def add(self, name: str, passed: bool, detail: str = "") -> None:
        """Append one check result."""
        self.results.append(VerificationResult(name=name, passed=passed, detail=detail))

    def to_dict(self) -> dict[str, Any]:
        """Serialize summary."""
        return {
            "passed": self.passed,
            "results": [result.to_dict() for result in self.results],
        }


def run_verification() -> VerificationSummary:
    """Run all release verification checks."""
    summary = VerificationSummary()
    _check(summary, "database initialization", _verify_database_initialization)
    _check(summary, "migration execution", _verify_migrations)
    _check(summary, "Ollama configuration loading", _verify_ollama_config)
    _check(summary, "document library initialization", _verify_document_library)
    _check(summary, "workspace creation", _verify_workspace_creation)
    _check(summary, "runtime directories", _verify_runtime_directories)
    _check(summary, "application startup imports", _verify_application_imports)
    _check(summary, "knowledge engine loads", _verify_knowledge_engine)
    _check(summary, "search smoke", _verify_search)
    _check(summary, "draft validation smoke", _verify_draft_validation)
    _check(summary, "advisory report loads", _verify_advisory_report)
    return summary


def _check(summary: VerificationSummary, name: str, func: Any) -> None:
    try:
        detail = func()
        summary.add(name, True, str(detail or "ok"))
    except Exception as exc:
        summary.add(name, False, str(exc))


def _verify_database_initialization() -> str:
    init_database()
    if not DB_PATH.exists():
        raise RuntimeError(f"Database file was not created: {DB_PATH}")
    return str(DB_PATH)


def _verify_migrations() -> str:
    with get_connection() as conn:
        rows = conn.execute("SELECT version FROM schema_migrations").fetchall()
    versions = {str(row[0]) for row in rows}
    required = {"014_advisory_report_engine"}
    missing = required.difference(versions)
    if missing:
        raise RuntimeError("Missing migration(s): " + ", ".join(sorted(missing)))
    return "migrations applied"


def _verify_ollama_config() -> str:
    backend = OllamaEmbeddingBackend()
    if not backend.model or not backend.name:
        raise RuntimeError("Ollama backend configuration is incomplete")
    return f"{backend.name}:{backend.model}"


def _verify_document_library() -> str:
    service = DocumentLibraryService()
    counts = service.status_counts()
    return f"{len(counts)} document status group(s)"


def _verify_workspace_creation() -> str:
    repository = TaskRepository()
    existing = repository.fetch_one("SELECT id FROM workspaces WHERE name=?", ("Release Verification",))
    if existing:
        return f"workspace {existing['id']}"
    workspace_id = repository.create_workspace(
        {
            "name": "Release Verification",
            "description": "V1.0 release verification workspace",
            "field": "Release",
            "status": "Verified",
        }
    )
    return f"workspace {workspace_id}"


def _verify_runtime_directories() -> str:
    required = [LOG_DIR, EXPORT_DIR, BACKUP_DIR, WORKSPACE_DIR]
    missing: list[Path] = []
    for path in required:
        path.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            missing.append(path)
    if missing:
        raise RuntimeError("Missing runtime directories: " + ", ".join(str(path) for path in missing))
    return "directories ready"


def _verify_application_imports() -> str:
    from app.router import PAGES

    if not PAGES:
        raise RuntimeError("Application router has no pages")
    return f"{len(PAGES)} page(s)"


def _verify_knowledge_engine() -> str:
    service = KnowledgeService()
    if not service.embedding_backend.name:
        raise RuntimeError("Knowledge embedding backend did not load")
    return service.embedding_backend.name


def _verify_search() -> str:
    response = SearchService().search(SearchRequest(query="release verification", mode="keyword"))
    if not response.get("valid"):
        raise RuntimeError(str(response.get("errors")))
    return "search valid"


def _verify_draft_validation() -> str:
    draft = {
        "title": "Release validation draft",
        "document_type": "Cong van",
        "draft_content": "\n".join(
            [
                "DU THAO",
                "Noi dung tham muu:",
                "1. Noi dung kiem tra release co du than bai va can cu noi bo.",
                "Ket luan:",
                "Kinh de nghi xem xet theo tham quyen.",
                "Nguoi ky",
            ]
        ),
    }
    result = DraftValidator().validate(draft, citations=[])
    if not result.passed:
        raise RuntimeError("; ".join(result.errors))
    return "draft validation passed"


def _verify_advisory_report() -> str:
    service = ReportService()
    result = service.generate_report(
        ReportRequest(report_type="topic", title="Release advisory smoke", topic="release")
    )
    if result.report_id is None:
        raise RuntimeError("Advisory report did not store history")
    return f"report {result.report_id}"


def main() -> int:
    """Run release verification CLI."""
    summary = run_verification()
    print(json.dumps(summary.to_dict(), ensure_ascii=False, indent=2))
    return 0 if summary.passed else 1


if __name__ == "__main__":
    sys.exit(main())
