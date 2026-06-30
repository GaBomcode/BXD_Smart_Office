from __future__ import annotations

from core.config import RESOURCE_DIR
from modules.dashboard.widgets import metric_card


def test_dashboard_css_asset_exists() -> None:
    """Verify the offline light design system stylesheet is bundled."""
    css_path = RESOURCE_DIR / "static" / "css" / "design_system.css"

    assert css_path.exists()
    css = css_path.read_text(encoding="utf-8")
    assert ".bxd-kpi-card" in css
    assert ".bxd-sidebar-brand" in css
    assert "--bxd-primary" in css
    assert "#2563eb" in css


def test_dashboard_metric_card_imports() -> None:
    """Verify the styled KPI helper remains importable."""
    assert callable(metric_card)
