"""Static scanning of a Python package using the standard-library AST.

The scanner never imports or executes the code under analysis. It builds a
``ModuleInfo`` per source file, with the internal imports it references
(relative imports are resolved to absolute module names) and a cyclomatic
complexity estimate for every function.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path

_BRANCH_NODES = (
    ast.If,
    ast.For,
    ast.AsyncFor,
    ast.While,
    ast.IfExp,
    ast.ExceptHandler,
    ast.With,
    ast.AsyncWith,
)
_FUNCTION_NODES = (ast.FunctionDef, ast.AsyncFunctionDef)


@dataclass(frozen=True)
class FunctionInfo:
    name: str
    lineno: int
    complexity: int


@dataclass
class ModuleInfo:
    name: str
    path: Path
    imports: set[str] = field(default_factory=set)
    functions: list[FunctionInfo] = field(default_factory=list)


def scan_package(root: Path) -> dict[str, ModuleInfo]:
    """Scan every ``.py`` file below ``root`` and return modules keyed by dotted name.

    ``root`` is the package directory itself; its name becomes the top-level
    module prefix (``root=/x/sample_app`` yields ``sample_app.models`` etc.).
    """
    root = root.resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"not a directory: {root}")

    modules: dict[str, ModuleInfo] = {}
    for path in sorted(root.rglob("*.py")):
        relative = path.relative_to(root)
        if any(part.startswith(".") or part == "__pycache__" for part in relative.parts):
            continue
        name = _module_name(root.name, relative)
        is_package = relative.name == "__init__.py"
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

        info = ModuleInfo(name=name, path=path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                info.imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                info.imports.update(_resolve_from_import(name, is_package, node))
            elif isinstance(node, _FUNCTION_NODES):
                info.functions.append(
                    FunctionInfo(node.name, node.lineno, _cyclomatic_complexity(node))
                )
        modules[name] = info
    return modules


def _module_name(package: str, relative: Path) -> str:
    parts = list(relative.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join([package, *parts])


def _resolve_from_import(module: str, is_package: bool, node: ast.ImportFrom) -> set[str]:
    """Turn ``from ..x import y`` inside ``module`` into absolute dotted names.

    Besides the imported-from module, every ``module.name`` combination is
    recorded so ``from sample_app import orders`` can be matched against the
    ``sample_app.orders`` module when the graph is built. Names that turn out
    to be plain objects are dropped there.
    """
    if node.level == 0:
        base = node.module.split(".") if node.module else []
    else:
        package_parts = module.split(".") if is_package else module.split(".")[:-1]
        ascend = node.level - 1
        if ascend > len(package_parts):
            return set()
        base = package_parts[: len(package_parts) - ascend]
        if node.module:
            base = [*base, *node.module.split(".")]
    if not base:
        return set()
    candidates = {".".join(base)}
    candidates.update(".".join([*base, alias.name]) for alias in node.names)
    return candidates


def _cyclomatic_complexity(function: ast.AST) -> int:
    """1 + number of decision points. Nested functions are counted into their parent."""
    score = 1
    for node in ast.walk(function):
        if isinstance(node, _BRANCH_NODES):
            score += 1
        elif isinstance(node, ast.BoolOp):
            score += len(node.values) - 1
        elif isinstance(node, ast.comprehension):
            score += 1 + len(node.ifs)
        elif isinstance(node, ast.Match):
            score += len(node.cases)
    return score
