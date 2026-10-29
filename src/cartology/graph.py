"""Directed import graph between the modules of a package."""

from __future__ import annotations

from dataclasses import dataclass, field

from cartology.scanner import ModuleInfo


@dataclass(frozen=True)
class ImportEdge:
    source: str
    target: str


@dataclass
class ImportGraph:
    edges: set[ImportEdge] = field(default_factory=set)

    def fan_in(self, module: str) -> int:
        return sum(1 for edge in self.edges if edge.target == module)

    def fan_out(self, module: str) -> int:
        return sum(1 for edge in self.edges if edge.source == module)

    def cycles(self) -> list[list[str]]:
        """Strongly connected components containing more than one module."""
        return [component for component in _strongly_connected(self.edges) if len(component) > 1]


def build_graph(modules: dict[str, ModuleInfo]) -> ImportGraph:
    """Keep only imports that point at modules inside the scanned package."""
    graph = ImportGraph()
    for name, info in modules.items():
        for target in info.imports:
            resolved = _resolve_to_internal(target, modules)
            if resolved and resolved != name:
                graph.edges.add(ImportEdge(name, resolved))
    return graph


def _resolve_to_internal(target: str, modules: dict[str, ModuleInfo]) -> str | None:
    if target in modules:
        return target
    # `from pkg import sub` records `pkg`; a unique submodule under it is still a dependency.
    prefix = f"{target}."
    candidates = [name for name in modules if name.startswith(prefix)]
    if len(candidates) == 1:
        return candidates[0]
    return None


def _strongly_connected(edges: set[ImportEdge]) -> list[list[str]]:
    """Iterative Tarjan SCC, so deep import chains cannot hit the recursion limit."""
    adjacency: dict[str, list[str]] = {}
    for edge in edges:
        adjacency.setdefault(edge.source, []).append(edge.target)

    counter = 0
    index: dict[str, int] = {}
    lowlink: dict[str, int] = {}
    on_stack: set[str] = set()
    stack: list[str] = []
    components: list[list[str]] = []

    for start in sorted(adjacency):
        if start in index:
            continue
        index[start] = lowlink[start] = counter
        counter += 1
        stack.append(start)
        on_stack.add(start)
        work = [(start, iter(sorted(adjacency.get(start, []))))]
        while work:
            node, neighbours = work[-1]
            descended = False
            for neighbour in neighbours:
                if neighbour not in index:
                    index[neighbour] = lowlink[neighbour] = counter
                    counter += 1
                    stack.append(neighbour)
                    on_stack.add(neighbour)
                    work.append((neighbour, iter(sorted(adjacency.get(neighbour, [])))))
                    descended = True
                    break
                if neighbour in on_stack:
                    lowlink[node] = min(lowlink[node], index[neighbour])
            if descended:
                continue
            work.pop()
            if work:
                parent = work[-1][0]
                lowlink[parent] = min(lowlink[parent], lowlink[node])
            if lowlink[node] == index[node]:
                component: list[str] = []
                while True:
                    member = stack.pop()
                    on_stack.discard(member)
                    component.append(member)
                    if member == node:
                        break
                components.append(sorted(component))
    return components
