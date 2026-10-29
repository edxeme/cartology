import json
import subprocess
import sys
from pathlib import Path

import pytest

FIXTURE = Path(__file__).parent / "fixtures" / "sample_app" / "sample_app"


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "cartology", *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_map_json_reports_every_module():
    result = run("map", str(FIXTURE), "--format", "json")
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert set(payload) == {
        "sample_app",
        "sample_app.config",
        "sample_app.demo",
        "sample_app.models",
        "sample_app.orders",
        "sample_app.pricing",
        "sample_app.reports",
        "sample_app.reports.summary",
    }
    assert payload["sample_app.pricing"]["functions"][0]["name"] == "price_with_tax"


def test_cycles_exit_code_signals_findings():
    result = run("cycles", str(FIXTURE), "--format", "json")
    assert result.returncode == 3
    assert json.loads(result.stdout) == [["sample_app.orders", "sample_app.pricing"]]


def test_hotspots_markdown_contains_table_header():
    result = run("hotspots", str(FIXTURE), "--format", "md", "--top", "3")
    assert result.returncode == 0
    assert "| Module | Function | Line | Complexity |" in result.stdout


def test_deadcode_exit_code_signals_findings():
    result = run("deadcode", str(FIXTURE), "--format", "json")
    assert result.returncode == 3
    names = {entry["name"] for entry in json.loads(result.stdout)}
    assert {"discount_for", "total_for", "render"} == names


def test_missing_path_is_a_usage_error():
    result = run("map", "/does/not/exist")
    assert result.returncode == 1
    assert "cartology:" in result.stderr


@pytest.mark.parametrize("command", ["map", "cycles", "hotspots", "deadcode"])
def test_every_command_supports_text_format(command):
    result = run(command, str(FIXTURE))
    assert result.returncode in (0, 3)
    assert result.stdout.startswith("#")
