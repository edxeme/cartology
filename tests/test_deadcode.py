from pathlib import Path

import pytest

from cartology.deadcode import find_unused
from cartology.scanner import scan_package

FIXTURE = Path(__file__).parent / "fixtures" / "sample_app" / "sample_app"


@pytest.fixture(scope="module")
def unused():
    return find_unused(scan_package(FIXTURE))


def test_functions_without_callers_are_flagged(unused):
    flagged = {(s.module, s.name) for s in unused}
    assert ("sample_app.pricing", "discount_for") in flagged
    assert ("sample_app.pricing", "total_for") in flagged
    assert ("sample_app.reports.summary", "render") in flagged


def test_functions_used_via_attribute_access_are_kept(unused):
    flagged = {(s.module, s.name) for s in unused}
    # subtotal() is only ever reached as order.subtotal()
    assert ("sample_app.models", "subtotal") not in flagged


def test_used_functions_are_never_flagged(unused):
    flagged = {s.name for s in unused}
    assert "price_with_tax" not in flagged
    assert "grand_total" not in flagged


def test_results_are_sorted_by_module(unused):
    modules = [s.module for s in unused]
    assert modules == sorted(modules)
