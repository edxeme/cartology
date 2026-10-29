import json
import subprocess
import sys
from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures" / "sample_app" / "sample_app"


def run_trace(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "cartology", "trace", str(FIXTURE), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_trace_reports_executed_functions():
    result = run_trace("-m", "sample_app.demo", "--format", "json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    executed = {(hit["module"], hit["function"]) for hit in payload["executed"]}
    assert ("sample_app.demo", "main") in executed
    assert ("sample_app.orders", "grand_total") in executed
    assert ("sample_app.models", "subtotal") in executed


def test_trace_reports_cold_functions():
    result = run_trace("-m", "sample_app.demo", "--format", "json")
    payload = json.loads(result.stdout)
    cold = {(hit["module"], hit["function"]) for hit in payload["cold"]}
    assert ("sample_app.pricing", "discount_for") in cold
    assert ("sample_app.reports.summary", "render") in cold
    assert ("sample_app.pricing", "price_with_tax") not in cold


def test_trace_text_output_has_both_sections():
    result = run_trace("-m", "sample_app.demo")
    assert result.returncode == 0, result.stderr
    assert "## Executed" in result.stdout
    assert "## Cold (defined but never executed)" in result.stdout
