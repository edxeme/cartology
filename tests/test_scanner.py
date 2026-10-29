from pathlib import Path

import pytest

from cartology.scanner import scan_package

FIXTURE = Path(__file__).parent / "fixtures" / "sample_app" / "sample_app"


@pytest.fixture(scope="module")
def modules():
    return scan_package(FIXTURE)


def test_module_names_are_dotted_and_package_init_is_collapsed(modules):
    assert "sample_app" in modules
    assert "sample_app.reports" in modules
    assert "sample_app.reports.summary" in modules


def test_relative_imports_are_resolved_to_absolute_names(modules):
    imports = modules["sample_app.reports.summary"].imports
    assert "sample_app.config" in imports
    assert "sample_app.models" in imports


def test_external_imports_are_kept_as_written(modules):
    assert "dataclasses" in modules["sample_app.models"].imports


def test_complexity_counts_branches_and_boolean_operators(modules):
    functions = {f.name: f for f in modules["sample_app.pricing"].functions}
    # 1 base + 3 if-statements (one per elif) + 1 extra operand of `and`
    assert functions["discount_for"].complexity == 5
    assert functions["price_with_tax"].complexity == 1


def test_missing_directory_raises(tmp_path):
    with pytest.raises(NotADirectoryError):
        scan_package(tmp_path / "does-not-exist")
