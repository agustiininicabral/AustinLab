# AustinLab — QA Web Audit CLI

A reproducible, offline-first website quality auditor. It analyzes a saved HTML file, reports deterministic QA findings, and exports JSON and Markdown evidence. The initial version does not crawl websites or send page content to external services.

## What it checks

- **SEO basics:** missing/empty page title and meta description.
- **Structure:** missing H1 or multiple H1 elements.
- **Accessibility basics:** images without an `alt` attribute and form controls without an associated label.
- **Links:** empty links and placeholder destinations such as `#`.
- **Evidence:** each finding includes a stable rule ID, severity, description, and source element.

This is a lightweight static audit, not a substitute for a browser-based accessibility audit, security scanner, or manual QA review.

## Requirements

- Python 3.12+
- Runtime uses only the Python standard library.
- pytest and Ruff are used for development and CI.

## Quick start (Windows PowerShell)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

Save a webpage as HTML, then run:

```powershell
.\.venv\Scripts\python.exe -m austinlab audit --input examples/sample_page.html --out outputs
```

Outputs:
- `outputs/report.md`: human-readable summary and findings.
- `outputs/report.json`: machine-readable report for pipelines.

The command exits with code 1 when error-severity findings are present, code 0 when the audit has no errors, and a non-zero code for invalid input. Warnings alone do not fail the audit.

## Run tests and checks

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff format austinlab tests
.\.venv\Scripts\python.exe -m ruff check austinlab tests
```

GitHub Actions runs these checks on pushes and pull requests.

## Scope and safety

The tool reads local files only. It does not visit URLs, execute JavaScript, submit forms, or access credentials. HTML parsing is static, so content rendered only by JavaScript is outside the audit scope. Findings are heuristic and must be reviewed before being treated as defects.

## Project structure

- `austinlab/audit.py`: HTML parser and rule engine.
- `austinlab/cli.py`: command-line interface and report writers.
- `examples/sample_page.html`: deliberately imperfect fixture for a visible demo.
- `tests/`: deterministic unit and CLI tests.
- `docs/rules.md`: rule IDs, severity, remediation and known limitations.
- `.github/workflows/ci.yml`: automated quality checks.

## License

MIT. See [LICENSE](LICENSE).
