from __future__ import annotations


def test_router_and_ai_draft_ui_imports() -> None:
    import app.router as router
    from modules.ai_draft.page import render_ai_draft

    assert "AI Soạn thảo" in router.PAGES
    assert router.PAGES["AI Soạn thảo"] is render_ai_draft
    assert callable(render_ai_draft)
