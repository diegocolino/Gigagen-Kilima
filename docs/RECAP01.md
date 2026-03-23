# RECAP 01 — Estado del proyecto Gigagen / Kilima

> Snapshot a 22 de marzo de 2026. 205 tests passing.

---

## Qué es esto

**Gigagen** es un motor/framework en Python para compilar universos relacionales. **Kilima** es el primer worldpack: una distopía techno-política organizada alrededor de La Montaña, con 12 personajes, 10 facciones, 15 locations y una timeline de 62 horas.

```
Gigagen = gramática / motor / framework
Kilima  = poema / mundo / instancia concreta
```

---

## Arquitectura

```
src/gigagen/
├── core/                   # Motor puro (0 dependencias de Kilima)
│   ├── entity.py           # Modelos Pydantic: Character, Faction, Location, Item, Anima, Subdivision
│   ├── world_state.py      # Contenedor: entities + relations + seed + phase
│   ├── relation.py         # Modelo Relation + harmonic_affinity() + RELATION_KINDS
│   ├── harmony.py          # Motor armónico puro: 8 funciones matemáticas
│   ├── simulator.py        # Procesador de timeline: avance por horas, event rules, outcomes
│   ├── seed.py             # Variación determinística por seed
│   └── invariants.py       # Validación contra invariants.json
├── io/
│   ├── load_worldpack.py   # Carga cualquier worldpack desde directorio
│   └── export_world_state.py  # Exporta WorldState a JSON, save_worldpack()
├── cli/
│   ├── console.py          # Consola clásica (REPL)
│   └── tui/                # God Mode TUI (Textual)
│       ├── app.py          # App principal: 28 bindings, layout, modal dispatch
│       ├── bridge.py       # SimulatorBridge: snapshots por hora, rewind O(1)
│       ├── screens.py      # 16 screens modales (editores, mapa, timeline, dashboard)
│       ├── widgets.py      # 7 widgets (tablas, paneles, barras)
│       ├── map_widget.py   # Mapa jerárquico por zonas con posiciones de personajes
│       └── styles.tcss     # Estilos CSS del TUI
└── __main__.py             # Entry point: --tui (default) | --classic

worlds/kilima/              # Worldpack de Kilima
├── world.json              # Metadata + catalogs (archetypes, notes, statuses)
├── characters.json         # 12 personajes con subdivisión asignada
├── factions.json           # 10 facciones con modos armónicos y subdivisiones
├── locations.json          # 15 locations con jerarquía parent
├── relations.json          # 26 relaciones fijas
├── invariants.json         # Reglas de integridad + 3 variables
├── event_rules.json        # Reglas condicionales por evento
├── timeline_maps.json      # Mapeo nombres↔IDs para el timeline
└── timelines/bn1.yaml      # Timeline NB1: 45 eventos en 62 horas
```

---

## Sistemas implementados

### 1. Motor armónico (`harmony.py`)
Matemáticas puras. Sin referencia a Kilima.

| Función | Input | Output |
|---------|-------|--------|
| `build_scale` | root + intervals | Lista de notas |
| `character_faction_affinity` | char note + faction intervals + sub root | Float [-1, 1] |
| `character_location_affinity` | char note + loc tonic + faction intervals | Float [-1, 1] |
| `location_instability` | loc tonic + faction intervals list | Float [0, 1] |
| `faction_compatibility` | intervals A + intervals B | Float [0, 1] |
| `subdivision_weight` | sub root + other roots | Float [0, 1] |
| `dual_membership_cost` | two faction/sub combos | Float [0, 1] |

### 2. Simulador (`simulator.py`)
Procesador de timeline data-driven. Sin lógica hardcoded.

- `build_simulator()` → inicializa state desde WorldState
- `advance_to()` → procesa eventos hora a hora
- Event rules: mover personajes, resolver variables, cambiar status, set emociones, faction changes
- Harmonic enrichment: cada evento registra tonic, modal influence, afinidades
- `max_hour` cargado desde worldpack (no hardcoded)

### 3. God Mode TUI
Editor interactivo completo para cualquier worldpack.

**28 bindings organizados en categorías:**

| Categoría | Teclas |
|-----------|--------|
| Tiempo | ←/→, Shift+←/→, Home, End, Space, +/- |
| Paneles | c, f, l, e, Tab |
| Inspección | Enter, r, R, o |
| Edición | Enter (en tablas), a/d (subdivisiones), n (relaciones) |
| Global | Ctrl+S, v, h, m, t, s, x, ?, q |

**16 screens modales:**
- Editores: CharacterEditor, FactionEditor, LocationEditor, SubdivisionPicker, AddSubdivision, NewRelation
- Inspección: Inspector, Relations, Outcomes, GlobalRelations
- Visualización: Map, Timeline, HarmonicDashboard, ValidationResult
- Utilidad: Help, SeedPicker

**Mapa (`m`):**
- Paneles por zona (HIGH / MID / LOW / HIDDEN / EXTERNAL / VIRTUAL)
- Personajes posicionados con color por facción
- Indicador de movimiento (→) al avanzar horas
- Bordes de location coloreados por facción controladora
- Event log inline, auto-play con Space
- ←/→ avanza horas sin salir del mapa

**Timeline (`t`):**
- Todos los eventos H00→H62 en DataTable
- Variables marcadas con ★
- Enter salta a la hora del evento seleccionado

### 4. Sistema de invariantes
Validación contra `invariants.json` del worldpack.

- Conteo de characters/factions (numérico, sin defaults)
- Identidad del roster (archetype, note, name)
- Relaciones fijas presentes
- Subdivisión consistency (existe en la facción del character)
- Parent location validity + detección de ciclos

### 5. Separación Gigagen/Kilima
Desacoplamiento total.

- **entity.py**: `str` libre para todos los campos (archetype, status, emotion). Sin frozensets.
- **world.json catalogs**: cada worldpack define sus vocabularios
- **simulator.py**: `max_hour` desde worldpack, sin status hardcoded
- **seed.py**: emociones desde catálogos
- **invariants.py**: conteos numéricos desde invariants.json, sin regex
- **Test de verificación**: `test_generic_worldpack.py` carga un worldpack con archetypes "WARRIOR"/"MAGE"

---

## Datos de Kilima

| Entidad | Count | Detalle |
|---------|-------|---------|
| Characters | 12 | 12 arquetipos × 12 notas. 6 con subdivisión asignada |
| Factions | 10 | 7 griegas + 1 whole_tone + 2 pentatónicas. 38 subdivisiones total |
| Locations | 15 | 9 top-level + 6 con parent. Zonas: high/mid/low/hidden/external/virtual |
| Relations | 26 | 17 char↔char + 5 char→fac + 3 fac→loc. Todas fixed |
| Timeline events | 45 | H00→H62. 3 variables (VAR_DEV, VAR_BRAIS, VAR_ENDING) |
| Event rules | ~15 | Condicionales, movimiento, status changes |

---

## Tests

**205 funciones de test, 100% passing.**

| Archivo | Tests | Cubre |
|---------|-------|-------|
| test_harmony.py | 46 | Todas las funciones armónicas |
| test_models.py | 44 | Modelos Pydantic, worldpack loading, subdivisión invariants, parent hierarchy |
| test_loader_console.py | 29 | Loader, consola, no-Kilima-in-source check |
| test_bridge.py | 28 | Snapshots, rewind, time navigation |
| test_simulator.py | 28 | Event processing, variables, movement, outcomes |
| test_seed_variation.py | 16 | Variación determinística |
| test_data_integrity.py | 7 | Cross-reference entre JSONs |
| test_generic_worldpack.py | 7 | Worldpack no-Kilima funciona |

---

## Lo que NO está implementado

Según CLAUDE.md, fuera de scope para Act 1:

| Sistema | Estado |
|---------|--------|
| Ánimas | Modelo existe. Sin loader, sin datos, sin mecánicas |
| Items | Modelo existe. Sin loader, sin datos |
| Chronica | Layer 3 (re-simulación del pasado). No implementada |
| Existence | Layer 5 (introducción del jugador). No implementada |
| Skills | No definidas |
| Combate | No definido |
| Godot | Sin integración |
| Tonics | Todas las locations tienen tonic=null (pendiente decisión autoral) |

---

## Stack

- Python 3.11+
- Pydantic v2 (modelos de datos)
- Textual (TUI framework)
- PyYAML (timelines)
- pytest (tests)
- pip install -e . (pyproject.toml)

---

## Próximos pasos posibles

1. **Tonics de locations** — Asignar notas tónicas a las 15 locations para activar el cálculo de afinidades char↔loc
2. **Ánimas** — Crear animas.json en Kilima, loader, visualización en TUI
3. **Simulador armónico** — Que las afinidades influyan en los outcomes (no solo se muestren)
4. **Character tracker** — Biografía temporal de un personaje (trayectoria completa)
5. **Diff entre snapshots** — Comparar H00 vs H30: qué cambió
6. **Scenario fork** — Guardar checkpoints, comparar escenarios alternativos
7. **RELATION_KINDS dinámico** — Mover el frozenset a catálogos del worldpack
