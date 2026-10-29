"""Size and complexity hotspots derived from a scan."""

from __future__ import annotations

from dataclasses import dataclass

from cartology.scanner import ModuleInfo


@dataclass(frozen=True)
class Hotspot:
    module: str
    function: str
    lineno: int
    complexity: int


def line_counts(modules: dict[str, ModuleInfo]) -> dict[str, int]:
    """Physical line count per module."""
    return {
        name: len(info.path.read_text(encoding="utf-8").splitlines())
        for name, info in modules.items()
    }


def top_functions(modules: dict[str, ModuleInfo], limit: int = 10) -> list[Hotspot]:
    """The most complex functions, highest cyclomatic complexity first."""
    hotspots = [
        Hotspot(info.name, function.name, function.lineno, function.complexity)
        for info in modules.values()
        for function in info.functions
    ]
    return sorted(hotspots, key=lambda h: (-h.complexity, h.module, h.lineno))[:limit]


def summary(modules: dict[str, ModuleInfo]) -> dict[str, int]:
    """Project-wide totals."""
    functions = [function for info in modules.values() for function in info.functions]
    return {
        "modules": len(modules),
        "functions": len(functions),
        "lines": sum(line_counts(modules).values()),
        "avg_complexity": round(
            sum(f.complexity for f in functions) / len(functions), 2
        )
        if functions
        else 0.0,
    }
