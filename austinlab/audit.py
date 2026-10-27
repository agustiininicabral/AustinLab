"""Deterministic static HTML checks; no network requests or JavaScript execution."""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_text = ""
        self.in_title = False
        self.meta_description = ""
        self.h1_count = 0
        self.images_without_alt: list[str] = []
        self.empty_links: list[str] = []
        self.placeholder_links: list[str] = []
        self.form_controls: list[tuple[str, str]] = []
        self.label_targets: set[str] = set()
        self.current_link_href = ""
        self.current_link_text = ""
        self.in_link = False
        self.current_h1_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "title":
            self.in_title = True
        elif tag == "meta" and (values.get("name") or "").lower() == "description":
            self.meta_description = (values.get("content") or "").strip()
        elif tag == "h1":
            self.h1_count += 1
            self.current_h1_depth += 1
        elif tag == "img" and "alt" not in values:
            self.images_without_alt.append(values.get("src") or "(src missing)")
        elif tag == "a":
            self.current_link_href = (values.get("href") or "").strip()
            self.current_link_text = ""
            self.in_link = True
        elif tag == "label":
            target = (values.get("for") or "").strip()
            if target:
                self.label_targets.add(target)
        elif tag in {"input", "select", "textarea"}:
            if tag == "input" and (values.get("type") or "").lower() in {"hidden", "submit", "button", "reset"}:
                return
            self.form_controls.append((tag, (values.get("id") or "").strip()))

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        elif tag == "h1" and self.current_h1_depth:
            self.current_h1_depth -= 1
        elif tag == "a":
            if not self.current_link_text.strip():
                self.empty_links.append(self.current_link_href or "(href missing)")
            normalized_href = self.current_link_href.strip().lower()
            if normalized_href in {"", "#", "javascript:void(0)"}:
                self.placeholder_links.append(self.current_link_href or "(href missing)")
            self.current_link_href = ""
            self.current_link_text = ""
            self.in_link = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_text += data
        if self.in_link:
            self.current_link_text += data


def audit_html(html: str, source: str = "input.html") -> dict[str, object]:
    parser = PageParser()
    parser.current_link_href = ""
    parser.feed(html)
    parser.close()
    findings: list[dict[str, str]] = []

    def add(rule_id: str, severity: str, message: str, element: str) -> None:
        findings.append(
            {"rule_id": rule_id, "severity": severity, "message": message, "element": element}
        )

    if not parser.title_text.strip():
        add("SEO001", "error", "Page title is missing or empty.", "<title>")
    if not parser.meta_description:
        add("SEO002", "warning", "Meta description is missing or empty.", '<meta name="description">')
    if parser.h1_count == 0:
        add("STR001", "error", "No H1 heading was found.", "<h1>")
    elif parser.h1_count > 1:
        add("STR002", "warning", f"Found {parser.h1_count} H1 headings; review heading hierarchy.", "<h1>")
    for src in parser.images_without_alt:
        add("A11Y001", "warning", "Image has no alt attribute.", f'<img src="{src}">')
    for href in parser.empty_links:
        add("A11Y002", "warning", "Link has no discernible text.", f'<a href="{href}">')
    for href in parser.placeholder_links:
        add("LINK001", "warning", "Link has a missing or placeholder destination.", f'<a href="{href}">')
    for tag, element_id in parser.form_controls:
        if not element_id or element_id not in parser.label_targets:
            add("A11Y003", "warning", "Form control has no explicit label association.", f"<{tag} id=\"{element_id}\">")

    errors = sum(item["severity"] == "error" for item in findings)
    warnings = sum(item["severity"] == "warning" for item in findings)
    return {
        "source": source,
        "status": "FAIL" if errors else "PASS",
        "summary": {"errors": errors, "warnings": warnings, "findings": len(findings)},
        "findings": findings,
    }


def audit_file(path: str | Path) -> dict[str, object]:
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"Input HTML file not found: {source}")
    if source.suffix.lower() not in {".html", ".htm"}:
        raise ValueError("Input must be an HTML file (.html or .htm).")
    return audit_html(source.read_text(encoding="utf-8"), str(source))
