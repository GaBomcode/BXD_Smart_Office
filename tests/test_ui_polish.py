from __future__ import annotations

from core.config import RESOURCE_DIR
from modules.dashboard.widgets import metric_card


def test_dashboard_css_asset_exists() -> None:
    """Verify the offline dashboard stylesheet is bundled."""
    css_path = RESOURCE_DIR / "static" / "css" / "dashboard.css"

    assert css_path.exists()
    css = css_path.read_text(encoding="utf-8")
    assert ".bxd-kpi-card" in css
    assert ".bxd-sidebar-brand" in css
    assert "--bxd-blue" in css


def test_dashboard_metric_card_imports() -> None:
    """Verify the styled KPI helper remains importable."""
    assert callable(metric_card)
