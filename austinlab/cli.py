"""Command-line entry point and report rendering."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .audit import audit_file


def render_markdown(report: dict[str, object]) -> str:
    summary = report["summary"]
    findings = report["findings"]
    lines = [
        "# AustinLab QA Audit Report",
        "",
        f"- Source: `{report['source']}`",
        f"- Status: **{report['status']}**",
        f"- Errors: **{summary['errors']}**",
        f"- Warnings: **{summary['warnings']}**",
        "",
        "## Findings",
        "",
    ]
    if not findings:
        lines.append("No findings.")
    else:
        lines.extend(["| Rule | Severity | Finding | Element |", "|---|---|---|---|"])
        for item in findings:
            message = item["message"].replace("|", "\\|")
            element = item["element"].replace("|", "\\|").replace("`", "'")
            lines.append(f"| {item['rule_id']} | {item['severity']} | {message} | `{element}` |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(prog="austinlab", description="Offline static HTML QA audit")
    subparsers = parser.add_subparsers(dest="command", required=True)
    audit_parser = subparsers.add_parser("audit", help="Audit a local HTML file")
    audit_parser.add_argument("--input", required=True, help="Path to .html or .htm file")
    audit_parser.add_argument("--out", default="outputs", help="Directory for JSON and Markdown reports")
    args = parser.parse_args()

    try:
        report = audit_file(args.input)
    except (FileNotFoundError, ValueError, UnicodeDecodeError) as error:
        parser.error(str(error))

    output_dir = Path(args.out)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (output_dir / "report.md").write_text(render_markdown(report), encoding="utf-8")
    print(f"{report['status']}: {report['summary']['errors']} errors, {report['summary']['warnings']} warnings")
    print(f"Reports written to {output_dir}")
    return 1 if report["status"] == "FAIL" else 0
