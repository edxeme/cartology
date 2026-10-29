# cartology

Code cartography for Python projects — static maps of imports, complexity hotspots, dead code and runtime behaviour, with zero third-party dependencies.

Every codebase tells a story: which modules everything leans on, where the branching logic piles up, which functions nothing calls anymore. `cartology` reads that story with the standard library alone (`ast`, `sys.settrace`, `runpy`) and renders it as text, Markdown or JSON.

## Install

```console
pip install -e '.[dev]'      # local
docker build -t cartology .  # container
```

Requires Python 3.11+.

## Usage

All commands take the path of the package directory to scan.

```console
$ cartology map src/myproject              # modules, functions, internal imports
$ cartology cycles src/myproject           # circular imports
$ cartology hotspots src/myproject --top 5 # most complex functions first
$ cartology deadcode src/myproject         # functions nothing references
$ cartology trace src/myproject -m myproject.demo  # what actually runs
```

Every command accepts `--format text|json|md`. A [sample report](examples/sample-report.md) was generated against [`examples/inventory`](examples/inventory), a small package with a deliberate import cycle and a couple of orphans.

### Exit codes

`map`, `hotspots` and `trace` exit `0` when the scan completes. `cycles` and `deadcode` exit `3` when they have findings — convenient for CI:

```yaml
- name: Guard against new import cycles
  run: cartology cycles src/myproject
```

### Runtime traces

`cartology trace` runs a target module in-process under `sys.settrace` and diffs the functions that executed against the static scan:

```console
$ cartology trace examples/inventory/inventory -m inventory.storage
# Runtime trace (4 functions executed, 3 cold)

## Executed
- inventory.storage · receive()
- inventory.storage · pick()
- inventory.warehouse · put_away()

## Cold (defined but never executed)
...
```

Cold functions after a real run are the runtime twin of `deadcode`: defined, referenced, never reached.

### Docker

```console
$ docker build -t cartology .
$ docker run --rm -v "$PWD/src/myproject:/src:ro" cartology cycles /src
```

The image is multi-stage, runs as a non-root user and has no third-party dependencies to attack or patch.

## How it works

- **scanner** parses every file with `ast`, resolving `from … import` statements (including relative ones) to absolute dotted names, and estimates cyclomatic complexity as `1 + decision points` (branches, boolean operators, comprehensions, match cases).
- **graph** builds the internal import graph and finds cycles with an iterative Tarjan SCC pass, so deep chains cannot hit the recursion limit.
- **deadcode** is deliberately name-based: a function counts as used when its name appears anywhere as a name or attribute access, which avoids false positives from re-exports and dispatch patterns.
- **trace** installs a call-only tracer, runs the module with `runpy`, restores the previous tracer in a `finally`, and never imports the code under analysis at scan time.

## Development

```console
pip install -e '.[dev]'
pytest          # 33 tests
ruff check src tests
```

CI runs the lint-and-test matrix on Python 3.11 – 3.14.

## License

[MIT](LICENSE) © Edwin Martínez
