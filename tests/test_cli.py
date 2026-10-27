import json
from pathlib import Path

from austinlab.cli import main


def test_cli_writes_reports_and_exits_successfully(tmp_path: Path, monkeypatch) -> None:
    output = tmp_path / "out"
    example = Path(__file__).resolve().parents[1] / "examples" / "sample_page.html"
    monkeypatch.setattr(
        "sys.argv",
        ["austinlab", "audit", "--input", str(example), "--out", str(output)],
    )
    assert main() == 0
    report = json.loads((output / "report.json").read_text(encoding="utf-8"))
    assert report["source"] == str(example)
    assert (output / "report.md").is_file()


def test_cli_returns_failure_for_error_findings(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "broken.html"
    source.write_text("<body><p>Missing title and H1</p></body>", encoding="utf-8")
    output = tmp_path / "out"
    monkeypatch.setattr(
        "sys.argv",
        ["austinlab", "audit", "--input", str(source), "--out", str(output)],
    )
    assert main() == 1
    report = json.loads((output / "report.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert report["summary"]["errors"] == 2
