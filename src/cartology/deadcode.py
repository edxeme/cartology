"""Heuristic search for functions nothing in the package references."""

from __future__ import annotations

from dataclasses import dataclass

from cartology.scanner import ModuleInfo


@dataclass(frozen=True)
class UnusedSymbol:
    module: str
    name: str
    lineno: int


def find_unused(modules: dict[str, ModuleInfo]) -> list[UnusedSymbol]:
    """Flag package functions whose name is never referenced anywhere.

    The check is name-based on purpose: a function counts as used when its
    name shows up in any module's names or attribute accesses, which covers
    plain calls, re-exports, string references and dispatch patterns. Only
    functions are reported; classes and dunder entries are skipped.
    """
    referenced = {name for info in modules.values() for name in info.references}
    unused = []
    for info in sorted(modules.values(), key=lambda m: m.name):
        for function in info.functions:
            if function.name.startswith("__") and function.name.endswith("__"):
                continue
            if function.name not in referenced:
                unused.append(UnusedSymbol(info.name, function.name, function.lineno))
    return unused
