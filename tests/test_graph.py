from pathlib import Path

import pytest

from cartology.graph import ImportEdge, ImportGraph, build_graph
from cartology.scanner import scan_package

FIXTURE = Path(__file__).parent / "fixtures" / "sample_app" / "sample_app"


@pytest.fixture(scope="module")
def graph():
    return build_graph(scan_package(FIXTURE))


def test_external_dependencies_are_excluded(graph):
    targets = {edge.target for edge in graph.edges}
    assert "dataclasses" not in targets
    assert all(target.startswith("sample_app") for target in targets)


def test_relative_imports_produce_edges(graph):
    assert ImportEdge("sample_app.reports.summary", "sample_app.config") in graph.edges
    assert ImportEdge("sample_app.reports.summary", "sample_app.models") in graph.edges


def test_acyclic_graph_has_no_cycles():
    graph = ImportGraph(
        edges={ImportEdge("a", "b"), ImportEdge("b", "c"), ImportEdge("a", "c")}
    )
    assert graph.cycles() == []


def test_disjoint_cycles_are_reported_separately():
    graph = ImportGraph(
        edges={
            ImportEdge("a", "b"),
            ImportEdge("b", "a"),
            ImportEdge("c", "d"),
            ImportEdge("d", "e"),
            ImportEdge("e", "c"),
            ImportEdge("f", "a"),
        }
    )
    assert sorted(graph.cycles()) == [["a", "b"], ["c", "d", "e"]]


def test_fan_in_counts_importers(graph):
    assert graph.fan_in("sample_app.models") >= 2
