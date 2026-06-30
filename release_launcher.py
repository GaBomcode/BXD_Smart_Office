"""PyInstaller launcher for BXD Smart Office Streamlit app."""

from __future__ import annotations

from pathlib import Path
import os
import sys


def main() -> None:
    """Launch the Streamlit application from a packaged runtime."""
    base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    app_path = base_dir / "app" / "main.py"
    if not app_path.exists():
        app_path = Path(__file__).resolve().parent / "app" / "main.py"
    os.environ.setdefault("STREAMLIT_SERVER_HEADLESS", "true")
    os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")
    sys.path.insert(0, str(base_dir))
    sys.argv = [
        "streamlit",
        "run",
        str(app_path),
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
    ]
    from streamlit.web import cli as stcli

    stcli.main()


if __name__ == "__main__":
    main()
