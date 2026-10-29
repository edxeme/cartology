"""Rendering of scan results as JSON or Markdown."""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import asdict

from cartology.graph import ImportGraph
from cartology.metrics import Hotspot
from cartology.scanner import ModuleInfo


def to_json(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, default=str)


def map_payload(modules: dict[str, ModuleInfo], graph: ImportGraph) -> dict:
    out = {}
    for name in sorted(modules):
        info = modules[name]
        out[name] = {
            "path": str(info.path),
            "imports": sorted(info.imports),
            "internal_imports": sorted(
                edge.target for edge in graph.edges if edge.source == name
            ),
            "functions": [
                {"name": f.name, "lineno": f.lineno, "complexity": f.complexity}
                for f in info.functions
            ],
        }
    return out


def render_map(
    modules: dict[str, ModuleInfo], graph: ImportGraph, counts: dict[str, int] | None = None
) -> str:
    lines = [f"# Map ({len(modules)} modules)", ""]
    for name in sorted(modules):
        info = modules[name]
        internal = sorted(edge.target for edge in graph.edges if edge.source == name)
        suffix = f" · {counts[name]} lines" if counts else ""
        lines.append(f"## {name}{suffix}")
        lines.append("")
        if info.functions:
            lines.append("Functions: " + ", ".join(f"{f.name}()" for f in info.functions))
        else:
            lines.append("No functions.")
        if internal:
            lines.append("Imports: " + ", ".join(internal))
        else:
            lines.append("Imports: —")
        lines.append("")
    return "\n".join(lines)


def cycles_payload(cycles: Iterable[Iterable[str]]) -> list[list[str]]:
    return sorted(list(cycle) for cycle in cycles)


def render_cycles(cycles: list[list[str]]) -> str:
    lines = [f"# Import cycles ({len(cycles)})", ""]
    if not cycles:
        lines.append("None found.")
    for cycle in cycles:
        lines.append("- " + " → ".join([*cycle, cycle[0]]))
    return "\n".join(lines)


def hotspots_payload(hotspots: list[Hotspot]) -> list[dict]:
    return [asdict(hotspot) for hotspot in hotspots]


def render_hotspots(hotspots: list[Hotspot]) -> str:
    rows = [(h.module, h.function, str(h.lineno), str(h.complexity)) for h in hotspots]
    body = _markdown_table(("Module", "Function", "Line", "Complexity"), rows)
    return f"# Complexity hotspots\n\n{body}"


def deadcode_payload(unused: list) -> list[dict]:
    return [asdict(symbol) for symbol in unused]


def render_deadcode(unused: list) -> str:
    rows = [(s.module, s.name, str(s.lineno)) for s in unused]
    body = _markdown_table(("Module", "Function", "Line"), rows)
    return f"# Possibly dead functions\n\n{body}\n\nName-based heuristic — verify each hit before deleting."


def _markdown_table(header: tuple, rows: list[tuple]) -> str:
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(out)
