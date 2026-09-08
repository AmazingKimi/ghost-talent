from pathlib import Path


def test_ui_has_bilingual_and_theme_controls():
    html = (Path(__file__).resolve().parents[1] / "web" / "index.html").read_text(encoding="utf-8")
    assert "ghostTalentLang" in html
    assert "ghostTalentTheme" in html
    assert "中文" in html
    assert "Find the next generation of AI builders." in html
    assert "找到下一代 AI 建设者。" in html
    assert "prefers-color-scheme: dark" in html
    assert "data-theme=\"dark\"" in html or "dataset.theme" in html


def test_ui_keeps_reliability_views_and_server_watchlist():
    html = (Path(__file__).resolve().parents[1] / "web" / "index.html").read_text(encoding="utf-8")
    for view in ("discover", "watchlist", "dossiers", "evidence", "validation", "analytics", "settings"):
        assert view in html
    assert "/api/watchlist" in html
    assert "/api/validation" in html
    assert "no snapshot written" in html
