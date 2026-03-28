# PATCH 2 ROADMAP — Escalera de Descendencia

> Lee PATCH2_BRIEFING.md antes de este fichero.
> Este es el plan de implementación. Fases, dependencias, criterios de éxito.

---

## Estado pre-parche

- 292 tests pasando
- `load_worldpack.py` — 259 líneas, mezcla responsabilidades
- Sin carpeta `layers/`
- Sin modelo `Lineage`
- Sin ficheros `x.json` / `y.json`
- `WorldState.phase` es un string sin validación
- La seed entra en `apply_seed_variation()` sin estructura de namespaces

---

## Orden de fases

```
Fase 0 (preparación)
    ↓
Fase 1 (Genesis)
    ↓
Fase 2 (Theogony)
    ↓
Fase 3 (Chronica — infraestructura)
    ↓
Fase 4 (Contempo — stub)
    ↓
Fase 5 (pipeline + refactor io/)
```

Cada fase debe pasar todos los tests antes de empezar la siguiente.

---

## Fase 0 — Preparación

**Goal:** crear la estructura de carpetas y mover código existente sin romper nada.

### 0.1 — Crear carpeta layers/

```
src/gigagen/layers/__init__.py
src/gigagen/layers/genesis.py      ← stub
src/gigagen/layers/theogony.py     ← stub
src/gigagen/layers/chronica.py     ← stub
src/gigagen/layers/contempo.py     ← stub
src/gigagen/layers/existence.py    ← stub
```

Cada stub exporta `run(ws: WorldState, config: dict) -> WorldState` que devuelve `ws` sin cambios.

### 0.2 — DescendenceStep en world_state.py

```python
DescendenceStep = Literal["genesis", "theogony", "chronica", "contempo", "existence"]

class WorldState(BaseModel):
    phase: DescendenceStep = "genesis"   # antes era str
    ...
```

### 0.3 — Tests

- `WorldState.phase` solo acepta valores de `DescendenceStep`
- Los 292 tests existentes siguen pasando

**Criterio:** `pytest` verde. Carpeta `layers/` existe. `WorldState.phase` tipado.

---

## Fase 1 — Genesis

**Goal:** `genesis.py` carga `x.json` + `y.json` y produce un `WorldState` base válido.

### 1.1 — Diseñar x.json

Estructura propuesta:

```json
{
  "schema": "gigagen.x.v1",
  "archetypes": [
    { "code": "REB", "name": "Rebel", "note": "D#" }
  ],
  "harmonic_intervals": {
    "unison": { "semitones": 0, "affinity": 1.0, "label": "resonance" },
    "minor_second": { "semitones": 1, "affinity": -0.7, "label": "friction" },
    "tritone": { "semitones": 6, "affinity": -1.0, "label": "nemesis" },
    "perfect_fifth": { "semitones": 7, "affinity": 0.8, "label": "ally" }
  },
  "scale_families": ["greek", "symmetric", "pentatonic"],
  "relation_types": ["ally", "nemesis", "mentor", "rival"],
  "entity_types": ["character", "faction", "location", "item", "anima", "lineage"],
  "canon_levels": ["fixed", "seeded", "derived"]
}
```

### 1.2 — Diseñar y.json

Estructura propuesta:

```json
{
  "schema": "gigagen.y.v1",
  "chromatic_notes": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
  "elements": [
    { "id": "agua", "name": "Agua", "tier": "fundamental", "components": [] },
    { "id": "metal", "name": "Metal", "tier": "mixed", "components": ["fuego", "tierra"] }
  ],
  "character_tiers": ["S", "A", "B"],
  "location_levels": [1, 2, 3, 4, 5, 6],
  "item_tiers": ["S", "A", "B"],
  "skill_tiers": ["S", "A", "B"],
  "harmonic_modes": [
    { "name": "ionian", "intervals": [2,2,1,2,2,2,1], "family": "greek" },
    { "name": "whole_tone", "intervals": [2,2,2,2,2,2], "family": "symmetric" }
  ]
}
```

### 1.3 — Implementar genesis.py

```python
def run(ws: WorldState, config: dict) -> WorldState:
    x = _load_json(config["x_path"])
    y = _load_json(config["y_path"])
    _validate_xy(x, y)           # y respeta las leyes de x
    ws = ws.model_copy(deep=True)
    ws.catalogs = _build_catalogs(x, y)
    ws.entities["loc.world"] = _build_world_location()
    ws.phase = "genesis"
    return ws
```

### 1.4 — Tests

- Genesis carga `x.json` + `y.json` sin error
- Validación: `y.json` con nota inválida falla limpio
- `WorldState` post-genesis tiene `loc.world` en entities
- `WorldState.phase == "genesis"`
- Sin datos de Kilima hardcodeados en genesis.py

**Criterio:** `pytest tests/test_genesis.py` verde.

---

## Fase 2 — Theogony

**Goal:** `theogony.py` instancia ánimas, linajes y locations nivel 2. Sin seed.

### 2.1 — Modelo Lineage en entity.py

```python
class Lineage(BaseEntity):
    entity_type: Literal["lineage"] = "lineage"

    # Identity — fixed
    note: str
    tier: Literal["founder", "leader", "notary"]
    element_pool: list[str]          # elementos posibles para este linaje

    # Seeded — Chronica los resuelve
    element: str | None = None
    founding_era: str | None = None
    origin_location_id: str | None = None
```

### 2.2 — Crear lineages.json en Kilima

Mínimo viable: los linajes de los 12 principales.

```json
[
  {
    "id": "lineage.radbot",
    "name": "Radbot",
    "archetype": "REB",
    "note": "D#",
    "tier": "founder",
    "element_pool": ["fuego", "metal", "lava"],
    "canon_level": "fixed"
  }
]
```

### 2.3 — Implementar theogony.py

```python
def run(ws: WorldState, config: dict) -> WorldState:
    ws = ws.model_copy(deep=True)
    ws = _load_animas(ws, config)       # 16 elementos como entidades Anima
    ws = _load_lineages(ws, config)     # linajes con campos fixed instanciados
    ws = _load_locations_l2(ws, config) # locations nivel 2
    ws = _load_items_tier_s(ws, config)
    ws = _load_skills_tier_s(ws, config)
    ws.phase = "theogony"
    return ws
```

### 2.4 — Tests

- Theogony instancia 16 ánimas
- Todos los linajes tienen `element_pool` válido (elementos en y.json)
- Los campos seeded (`element`, `founding_era`, `origin_location_id`) son None post-theogony
- Locations nivel 2 cargadas
- `WorldState.phase == "theogony"`

**Criterio:** `pytest tests/test_theogony.py` verde.

---

## Fase 3 — Chronica (infraestructura)

**Goal:** `chronica.py` con RNG namespaces y resolución de linajes. Las partes más complejas (macro-events, 2gen) son stubs documentados.

### 3.1 — SeedEngine en chronica.py

```python
class SeedEngine:
    def __init__(self, seed: int):
        self._seed = seed

    def rng(self, namespace: str) -> Random:
        return Random(f"{self._seed}:{namespace}")
```

### 3.2 — Resolver linajes

```python
def _resolve_lineages(ws: WorldState, engine: SeedEngine) -> WorldState:
    rng = engine.rng("elements")
    for entity in ws.entities.values():
        if isinstance(entity, Lineage):
            entity.element = rng.choice(entity.element_pool)
    return ws
```

### 3.3 — Stubs documentados

```python
def _resolve_macrofactions(ws, engine):
    # TODO Fase 3.2: agrupar linajes por elementos compatibles
    # → macrofactions emergen con modo heredado del linaje fundador
    return ws

def _resolve_macro_events(ws, engine):
    # TODO Fase 3.3: gamblear resolución de eventos históricos canónicos
    # → Capitol Foundation, First Revolution, etc. en Kilima
    return ws

def _resolve_locations_l3_l6(ws, engine):
    # TODO Fase 3.4: locations que nacen de la historia
    # → tonic derivado del linaje fundador
    return ws

def _resolve_characters_1gen(ws, engine):
    # TODO Fase 3.5: Founders (Tier S), Leaders (Tier A), Notaries (Tier B)
    return ws

def _resolve_characters_2gen(ws, engine):
    # TODO Fase 3.6: NPCs y secundarios
    return ws
```

### 3.4 — Tests

- `SeedEngine` produce RNGs reproducibles (misma seed + namespace = mismo resultado)
- `SeedEngine` produce RNGs independientes (namespace A no afecta namespace B)
- Linajes tienen `element` asignado post-chronica
- `element` está en el `element_pool` del linaje
- Misma seed → mismo elemento asignado (reproducible)
- Seeds distintas → resultados distintos
- `WorldState.phase == "chronica"`

**Criterio:** `pytest tests/test_chronica.py` verde.

---

## Fase 4 — Contempo (stub)

**Goal:** `contempo.py` stub que carga IN12 y avanza el estado al presente. Base para BN1.

### 4.1 — Implementar contempo.py

```python
def run(ws: WorldState, config: dict) -> WorldState:
    ws = ws.model_copy(deep=True)
    ws = _load_in12(ws, config)         # los 12 principales con estado H00
    ws = _load_relations(ws, config)    # relaciones del presente
    ws = _load_timeline(ws, config)     # BN1 / actos futuros
    ws.phase = "contempo"
    return ws
```

La lógica de IN12 es en gran parte lo que ya hace `load_worldpack.py` — se mueve aquí.

### 4.2 — Tests

- Contempo carga IN12 sin error
- Los 292 tests existentes siguen pasando (regresión)
- `WorldState.phase == "contempo"`

**Criterio:** `pytest` verde completo.

---

## Fase 5 — Pipeline + refactor io/

**Goal:** conectar todas las fases en un pipeline limpio. `load_worldpack.py` pasa a ser un coordinador ligero.

### 5.1 — Pipeline principal en __main__.py o cli/

```python
def build_world(worldpack_dir: Path, seed: int) -> WorldState:
    config = _load_config(worldpack_dir)

    ws = WorldState()
    ws = genesis.run(ws, config)
    ws = theogony.run(ws, config)
    ws = chronica.run(ws, config, seed=seed)
    ws = contempo.run(ws, config)
    return ws
```

### 5.2 — Refactor load_worldpack.py

`load_worldpack.py` queda como lector de disco puro — solo parsea JSON/YAML y devuelve dicts. Toda la lógica de transformación pasa a las layers.

### 5.3 — Tests de integración

- Pipeline completo produce WorldState válido
- Misma seed → mismo WorldState (reproducibilidad end-to-end)
- Seeds distintas → WorldStates distintos
- Todos los 292 tests originales siguen pasando

**Criterio:** `pytest` verde completo. Pipeline ejecutable desde CLI.

---

## Ficheros nuevos

| Fichero | Fase | Propósito |
|---------|------|-----------|
| `src/gigagen/layers/__init__.py` | 0 | Package |
| `src/gigagen/layers/genesis.py` | 1 | Carga x.json + y.json |
| `src/gigagen/layers/theogony.py` | 2 | Ánimas, linajes, L2 |
| `src/gigagen/layers/chronica.py` | 3 | Seed, pasado generado |
| `src/gigagen/layers/contempo.py` | 4 | IN12, presente, BN1 |
| `src/gigagen/layers/existence.py` | 0 | Stub vacío |
| `worlds/kilima/x.json` | 1 | Leyes del universo Kilima |
| `worlds/kilima/y.json` | 1 | Catálogo de materia Kilima |
| `worlds/kilima/lineages.json` | 2 | Linajes de Kilima |
| `tests/test_genesis.py` | 1 | Tests de Genesis |
| `tests/test_theogony.py` | 2 | Tests de Theogony |
| `tests/test_chronica.py` | 3 | Tests de Chronica |

---

## Ficheros modificados

| Fichero | Fase | Cambios |
|---------|------|---------|
| `src/gigagen/core/world_state.py` | 0 | `phase: DescendenceStep` |
| `src/gigagen/core/entity.py` | 2 | Añadir modelo `Lineage` |
| `src/gigagen/io/load_worldpack.py` | 5 | Refactor → coordinador ligero |
| `src/gigagen/__main__.py` | 5 | Pipeline principal |

---

## Criterios de éxito del parche completo

1. `pytest` verde — los 292 tests originales + los nuevos
2. `python -m gigagen` carga Kilima sin errores pasando por los 5 escalones
3. Dos seeds distintas producen WorldStates distintos
4. La misma seed siempre produce el mismo WorldState
5. Cada layer es importable y testeable en aislamiento
6. `load_worldpack.py` tiene menos de 80 líneas (solo io)
7. No hay lógica de Kilima hardcodeada en ninguna layer

---

## Fuera de scope

- `animas.json` — las ánimas como entidades plenas (personalidad, apariencia, nombre propio, vínculos con linajes). Theogony en este parche instancia ánimas mínimas desde `y.json`. Los datos ricos de Kilima vienen en **Patch 3**.
- Datos concretos de Kilima para Chronica (macro-events, characters 2gen, locations L3-L6)
- Implementación real de Existence
- God Mode TUI
- Minor Wheel en Contempo
- Árbol de eventos de BN1
- Items y Skills con datos de Kilima

Este parche construye el caño. Los siguientes lo llenan.
