from pathlib import Path

import pytest

from austinlab.audit import audit_file, audit_html


def test_good_html_passes_without_findings() -> None:
    html = """
    <html><head><title>Catalog</title>
    <meta name="description" content="A product catalog"></head>
    <body><h1>Catalog</h1><img src="item.png" alt="Item">
    <a href="/products">Products</a>
    <label for="email">Email</label><input id="email" type="email"></body></html>
    """
    report = audit_html(html)
    assert report["status"] == "PASS"
    assert report["summary"] == {"errors": 0, "warnings": 0, "findings": 0}


def test_detects_missing_title_h1_and_accessibility_issues() -> None:
    report = audit_html('<html><body><img src="x.png"><a href="#"></a><input id="q"></body></html>')
    rule_ids = {item["rule_id"] for item in report["findings"]}
    assert report["status"] == "FAIL"
    assert {"SEO001", "SEO002", "STR001", "A11Y001", "A11Y002", "A11Y003", "LINK001"} <= rule_ids


def test_detects_javascript_placeholder_links_case_insensitively() -> None:
    report = audit_html('<title>Page</title><h1>Page</h1><a href="JAVASCRIPT:void(0)">Action</a>')
    assert any(item["rule_id"] == "LINK001" for item in report["findings"])


def test_multiple_h1_is_warning_not_error() -> None:
    report = audit_html("<title>Page</title><h1>One</h1><h1>Two</h1>")
    assert report["status"] == "PASS"
    assert any(item["rule_id"] == "STR002" for item in report["findings"])


def test_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Input HTML file not found"):
        audit_file(tmp_path / "missing.html")


def test_rejects_non_html_extension(tmp_path: Path) -> None:
    source = tmp_path / "page.txt"
    source.write_text("<title>Page</title>", encoding="utf-8")
    with pytest.raises(ValueError, match="Input must be an HTML file"):
        audit_file(source)


def test_rejects_invalid_utf8_input(tmp_path: Path) -> None:
    source = tmp_path / "page.html"
    source.write_bytes(b"<title>\xff</title>")
    with pytest.raises(UnicodeDecodeError):
        audit_file(source)
