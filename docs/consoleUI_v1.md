# Console UI v1 — God Mode TUI

## Overview

A terminal-based "god mode" dashboard for observing and controlling the Gigagen/Kilima simulation in real-time. Built with [Textual](https://textual.textualize.io/).

## Entry Points

```bash
# Launch TUI (default)
python -m gigagen

# Explicit TUI
python -m gigagen --tui

# Classic text console
python -m gigagen --classic

# With options
python -m gigagen worlds/kilima --seed 42 --tui
```

## Architecture

```
src/gigagen/cli/tui/
    __init__.py       # exports run_tui()
    app.py            # GigagenApp(App) — main class, layout, hotkeys
    bridge.py         # SimulatorBridge — wraps simulator with snapshot/rewind
    widgets.py        # TimelineBar, CharacterTable, FactionPanel, etc.
    screens.py        # Inspector modal, seed picker, help overlay
    styles.tcss       # Textual CSS stylesheet
```

The old console (`cli/console.py`) remains untouched and accessible via `--classic`.

## Layout

```
+--------------------------------------------------------------+
|  GIGAGEN · kilima · seed 001     H14/H62     Cohesion: +2.3  |  Header
+--------------------------------------------------------------+
|  ▶ [████████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒] H14/H62  1.0s   |  Timeline
+--------------------------------------------------------------+
|  CHARACTERS (12)               |  EVENT LOG                  |
|  Name   Arch  Status   Loc    |  H14 [E05] Funeral ends     |
|  Kive   REB   alive    cage   |  H12 [E04B] Nora discovers  |
|  ...                          |  ...                         |
+-------------------------------+------------------------------+
|  FACTIONS     |  LOCATIONS     |  VARIABLES                  |
|  Resistencia  |  The Cage      |  ☑ VAR_BRAIS: lies          |
|  Agencia      |  The Cave      |  ☐ VAR_DEV: unresolved      |
+---------------+----------------+-----------------------------+
|  Footer: keybinding hints                                    |
+--------------------------------------------------------------+
```

## Hotkeys

### Time Control
| Key | Action |
|-----|--------|
| `→` | Step forward 1 hour |
| `Shift+→` | Step forward 5 hours |
| `←` | Step backward 1 hour |
| `Shift+←` | Step backward 5 hours |
| `Home` | Jump to H00 |
| `End` | Jump to H62 |
| `Space` / `p` | Toggle auto-play |
| `+` / `-` | Speed up / slow down (0.1s–5.0s) |

### Panels
| Key | Action |
|-----|--------|
| `c` | Focus Characters |
| `f` | Focus Factions |
| `l` | Focus Locations |
| `e` | Focus Event Log |
| `Tab` | Cycle focus |

### Inspection
| Key | Action |
|-----|--------|
| `Enter` | Inspect selected entity (modal) |
| `r` | Show relations of selected entity |
| `o` | Show outcomes summary |

### Global
| Key | Action |
|-----|--------|
| `s` | Change seed (modal) |
| `x` | Export world state JSON |
| `?` | Help overlay |
| `q` | Quit |

## Rewind Strategy

The simulator is forward-only. The bridge solves this with **per-hour snapshots**:

- Before each hour advance, a `Snapshot(hour, deepcopy(ws), deepcopy(sim))` is saved
- Max 63 snapshots (H00–H62), ~2 MB total
- Rewind = restore snapshot via deepcopy, O(1)
- Seed switch = reload worldpack + clear snapshots + reset to H00

## Dependencies

- `textual` (pip install textual) — ~2 MB, pure Python, works on Windows 10
