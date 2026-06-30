"""Tests for V1.0 release verification."""

from __future__ import annotations

from core.config import BACKUP_DIR, EXPORT_DIR, LOG_DIR, RESOURCE_DIR
from core.version import APP_VERSION, BUILD_NAME
from verify_release import run_verification


def test_release_version_constants() -> None:
    assert APP_VERSION == "1.0.0"
    assert BUILD_NAME == "V1.0.0 LTS"


def test_resource_directory_points_to_project_assets() -> None:
    assert (RESOURCE_DIR / "database" / "schema.sql").exists()
    assert (RESOURCE_DIR / "database" / "migrations").exists()


def test_release_verification_passes() -> None:
    summary = run_verification()

    assert summary.passed is True
    names = {result.name for result in summary.results}
    assert "database initialization" in names
    assert "migration execution" in names
    assert "advisory report loads" in names
    assert LOG_DIR.exists()
    assert EXPORT_DIR.exists()
    assert BACKUP_DIR.exists()
