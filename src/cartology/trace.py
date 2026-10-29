"""Runtime tracing of a module to see which package functions really execute."""

from __future__ import annotations

import runpy
import sys
import threading
from dataclasses import dataclass, field
from pathlib import Path

from cartology.scanner import ModuleInfo


@dataclass(frozen=True)
class FunctionHit:
    module: str
    function: str


@dataclass
class TraceResult:
    executed: list[FunctionHit] = field(default_factory=list)
    cold: list[FunctionHit] = field(default_factory=list)


def run_traced(modules: dict[str, ModuleInfo], module_name: str, package_dir: Path) -> TraceResult:
    """Run ``module_name`` in-process and diff executed functions against the scan.

    The package directory's parent is appended to ``sys.path`` so the module
    can be imported, and the trace function is restored afterwards even if
    the module raises or calls ``sys.exit()``.
    """
    package_dir = package_dir.resolve()
    parent = str(package_dir.parent)
    if parent not in sys.path:
        sys.path.insert(0, parent)

    file_to_module = {str(info.path): info.name for info in modules.values()}
    executed: set[tuple[str, str]] = set()

    def _tracer(frame, event, arg):
        if event == "call":
            module = file_to_module.get(frame.f_code.co_filename)
            if module:
                executed.add((module, frame.f_code.co_name))
        return _tracer

    previous = sys.gettrace()
    previous_thread = threading.gettrace()
    sys.settrace(_tracer)
    threading.settrace(_tracer)
    try:
        runpy.run_module(module_name, run_name="__main__", alter_sys=True)
    except SystemExit:
        pass
    finally:
        sys.settrace(previous)
        threading.settrace(previous_thread)

    hits = {FunctionHit(module, name) for module, name in executed}
    cold = [
        FunctionHit(info.name, function.name)
        for info in modules.values()
        for function in info.functions
        if FunctionHit(info.name, function.name) not in hits
    ]
    return TraceResult(executed=sorted(hits, key=lambda h: (h.module, h.function)), cold=cold)
