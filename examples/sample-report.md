# Sample report — examples/inventory

Generated with cartology 0.1.0 (`map`, `cycles`, `hotspots`, `deadcode`)
against `examples/inventory/inventory`.
# Map (5 modules)

## inventory · 1 lines

No functions.
Imports: —

## inventory.audit · 11 lines

Functions: audit_trail(), archive()
Imports: —

## inventory.models · 15 lines

Functions: total_quantity()
Imports: —

## inventory.storage · 10 lines

Functions: receive(), pick()
Imports: inventory, inventory.models, inventory.warehouse

## inventory.warehouse · 10 lines

Functions: put_away(), transfer()
Imports: inventory, inventory.models, inventory.storage


# Import cycles (1)

- inventory.storage → inventory.warehouse → inventory.storage

# Complexity hotspots

| Module | Function | Line | Complexity |
|---|---|---|---|
| inventory.audit | audit_trail | 1 | 4 |
| inventory.models | total_quantity | 14 | 2 |
| inventory.audit | archive | 10 | 1 |
| inventory.storage | receive | 5 | 1 |
| inventory.storage | pick | 9 | 1 |
| inventory.warehouse | put_away | 5 | 1 |
| inventory.warehouse | transfer | 9 | 1 |

# Possibly dead functions

| Module | Function | Line |
|---|---|---|
| inventory.audit | audit_trail | 1 |
| inventory.audit | archive | 10 |
| inventory.storage | receive | 5 |
| inventory.warehouse | transfer | 9 |

Name-based heuristic — verify each hit before deleting.
