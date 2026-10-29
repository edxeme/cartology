from pathlib import Path

import pytest

from cartology.metrics import line_counts, summary, top_functions
from cartology.scanner import scan_package

FIXTURE = Path(__file__).parent / "fixtures" / "sample_app" / "sample_app"


@pytest.fixture(scope="module")
def modules():
    return scan_package(FIXTURE)


def test_line_counts_are_positive_per_module(modules):
    counts = line_counts(modules)
    assert set(counts) == set(modules)
    assert all(lines > 0 for lines in counts.values())


def test_top_functions_orders_by_complexity_desc(modules):
    ranking = top_functions(modules)
    complexities = [h.complexity for h in ranking]
    assert complexities == sorted(complexities, reverse=True)
    assert ranking[0].module == "sample_app.pricing"
    assert ranking[0].function == "discount_for"


def test_limit_is_respected(modules):
    assert len(top_functions(modules, limit=2)) == 2


def test_summary_totals(modules):
    totals = summary(modules)
    assert totals["modules"] == 7
    assert totals["functions"] >= 6
    assert totals["lines"] > 0
    assert 0 < totals["avg_complexity"] < 10
