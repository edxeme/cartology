"""Command-line interface for cartology."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from cartology import __version__
from cartology.deadcode import find_unused
from cartology.graph import build_graph
from cartology.metrics import line_counts, top_functions
from cartology.report import (
    cycles_payload,
    deadcode_payload,
    hotspots_payload,
    map_payload,
    render_cycles,
    render_deadcode,
    render_hotspots,
    render_map,
    render_trace,
    to_json,
    trace_payload,
)
from cartology.scanner import scan_package
from cartology.trace import run_traced

EXIT_OK = 0
EXIT_USAGE = 1
EXIT_FINDINGS = 3


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        modules = scan_package(Path(args.path))
    except (NotADirectoryError, SyntaxError) as error:
        print(f"cartology: {error}", file=sys.stderr)
        return EXIT_USAGE

    graph = build_graph(modules)
    emit = _emitter(args.format)

    if args.command == "map":
        counts = line_counts(modules)
        print(emit(map_payload(modules, graph), render_map(modules, graph, counts)))
        return EXIT_OK

    if args.command == "cycles":
        cycles = graph.cycles()
        print(emit(cycles_payload(cycles), render_cycles(cycles)))
        return EXIT_FINDINGS if cycles else EXIT_OK

    if args.command == "hotspots":
        hotspots = top_functions(modules, limit=args.top)
        print(emit(hotspots_payload(hotspots), render_hotspots(hotspots)))
        return EXIT_OK

    if args.command == "deadcode":
        unused = find_unused(modules)
        print(emit(deadcode_payload(unused), render_deadcode(unused)))
        return EXIT_FINDINGS if unused else EXIT_OK

    if args.command == "trace":
        result = run_traced(modules, args.module, Path(args.path))
        print(emit(trace_payload(result), render_trace(result)))
        return EXIT_OK

    parser.error(f"unknown command: {args.command}")  # pragma: no cover


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cartology",
        description="Static maps of a Python package: imports, cycles, hotspots, dead code.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_target(command: str, help_text: str) -> None:
        child = sub.add_parser(command, help=help_text)
        child.add_argument("path", help="path to the package directory to scan")
        child.add_argument(
            "--format", choices=("text", "json", "md"), default="text", help="output format"
        )

    add_target("map", "modules with their functions and internal imports")
    add_target("cycles", "circular imports between modules")
    trace = sub.add_parser("trace", help="run a module and report executed functions")
    trace.add_argument("path", help="path to the package directory to scan")
    trace.add_argument("-m", "--module", required=True, help="module to run (e.g. pkg.demo)")
    trace.add_argument("--format", choices=("text", "json", "md"), default="text")
    hotspots = sub.add_parser("hotspots", help="most complex functions first")
    hotspots.add_argument("path", help="path to the package directory to scan")
    hotspots.add_argument("--format", choices=("text", "json", "md"), default="text")
    hotspots.add_argument("--top", type=int, default=10, help="how many functions to show")
    add_target("deadcode", "functions never referenced in the package")
    return parser


def _emitter(fmt: str):
    if fmt == "json":
        return lambda payload, _: to_json(payload)
    if fmt == "md":
        return lambda _, rendered: rendered
    return _text_fallback


def _text_fallback(payload: object, rendered: str) -> str:
    """Text mode reuses the Markdown renderer; it reads fine on a terminal."""
    return rendered


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
