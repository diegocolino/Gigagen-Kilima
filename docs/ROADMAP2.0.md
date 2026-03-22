# ROADMAP 2.0 — God Mode TUI

## Context

La TUI actual es **solo lectura**. Puedes inspeccionar todo pero no cambiar nada. Además, los personajes están vinculados a macro-facciones (`current_faction_id = "fac.anti_group"`) pero no a divisiones concretas (Red Fist Dragons, Direnis Cell, etc.), que son lo realmente importante narrativamente.

Este roadmap rediseña la TUI para dar **control total** sobre facciones, locations, relaciones y personajes — siempre que no se violen los invariantes. Cada edición pasa por `validate_invariants` antes de aplicarse.

---

## Phase 0 — Data Model: Divisiones como ciudadanos

**Problema:** `Character.current_faction_id` apunta a la macro-facción. No hay forma de saber en qué división está cada personaje.

### 0.1 — Añadir `current_subdivision_id` a Character

**Archivo:** `src/gigagen/core/entity.py` (después de `current_faction_id`)

```python
current_subdivision_id: str | None = None  # name of subdivision within current faction
```

Es `str | None` usando el `name` de la subdivisión (único dentro de cada facción). `None` = sin asignar o facción sin subdivisiones.

### 0.2 — Poblar asignaciones en characters.json

**Archivo:** `worlds/kilima/characters.json`

Asignaciones conocidas (de `leader_id` en factions.json):
- char.rebel → `"Red Fist Dragons"` (fac.anti_group)
- char.deity → `"Direnis Cell"` (fac.anti_group)
- char.explorer → `"Dust Parade"` (fac.anti_group)
- char.hero → `"Master Council"` (fac.agency)
- char.leader → `"Interior"` (fac.union_corp)
- char.creator → `"Forno Cell"` (fac.anti_group, miembro, no líder)
- Resto → `null`

### 0.3 — Nuevo invariante: consistencia subdivisión

**Archivo:** `src/gigagen/core/invariants.py`

- Nombres de subdivisión únicos dentro de cada facción
- Si `current_subdivision_id` no es null, debe existir en la facción referida por `current_faction_id`

### 0.4 — Tests

**Archivo:** `tests/test_models.py` — test campo nuevo + invariante subdivisión

### Criterio: `python -m pytest tests/ -v` pasa. Personajes de Kilima cargados con subdivisión.

---

## Phase 1 — Panel de Relaciones Global

**Problema:** Las relaciones solo se ven por entidad (modal RelationsScreen). No hay forma de ver el grafo completo.

### 1.1 — Widget `RelationsTable`

**Archivo:** `src/gigagen/cli/tui/widgets.py`

DataTable con columnas: `Source | Target | Kind | Weight | Polarity | Canon | Tags`

- Color por polaridad: verde (+1), blanco (0), rojo (-1)
- Filas `fixed` en dim (visualmente bloqueadas)
- `cursor_type = "row"`

### 1.2 — Screen `GlobalRelationsScreen`

**Archivo:** `src/gigagen/cli/tui/screens.py`

- Modal 90% × 85%
- Barra de filtro arriba: `[Char↔Char]` `[Char→Fac]` `[Fac→Loc]` (toggles)
- Sort por columna: `w` peso, `k` kind, `s` source
- Resuelve IDs a nombres humanos

### 1.3 — Binding `R` en app

**Archivo:** `src/gigagen/cli/tui/app.py`

`R` (mayúscula o rebind) → abre `GlobalRelationsScreen` global. La `r` per-entity sigue existiendo desde InspectorScreen.

### Criterio: `R` abre panel con 24+ relaciones. Filtros y sort funcionan.

---

## Phase 2 — Faction God Mode

**Problema:** FactionPanel es texto estático. No puedes editar nada ni ver subdivisiones con sus miembros.

### 2.1 — `apply_edit` en Bridge

**Archivo:** `src/gigagen/cli/tui/bridge.py`

```python
def apply_edit(self, mutator: Callable[[WorldState], None]) -> ValidationResult:
    # 1. deep-copy ws
    # 2. apply mutator to copy
    # 3. validate_invariants(copy)
    # 4. if valid: apply to real ws, snapshot, set _dirty=True
    # 5. return result
```

Único punto de entrada para todas las ediciones God Mode. Flag `_dirty` para mostrar `[MODIFIED]` en el header.

### 2.2 — FactionPanel → DataTable interactivo

**Archivo:** `src/gigagen/cli/tui/widgets.py`

`Faction | Mode | Status | Power | Cohesion | Leader | Subs(n)`

`Enter` en fila → abre `FactionEditorScreen`.

### 2.3 — `FactionEditorScreen`

**Archivo:** `src/gigagen/cli/tui/screens.py`

Layout vertical:

1. **Header (locked):** Nombre, mode, intervals, scale_family — greyed out, no editable
2. **Propiedades editables:**
   - Status → `Select` (active/dissolved/underground/dominant)
   - Power → `Input` float 0.0–1.0 + barra visual
   - Cohesion → `Input` float 0.0–1.0 + barra visual
   - Leader → `Select` con miembros de la facción
3. **Subdivisiones:** DataTable anidada
   - `Subdivision | Root Note | Leader | Type | Members(n)`
   - `a` = añadir subdivisión, `d` = eliminar (si no es fixed)
4. **Miembros:** DataTable
   - `Character | Note | Archetype | Subdivision | Affinity`
   - Affinity via `harmony.character_faction_affinity(char.note, faction.intervals, sub.note)`
   - `Enter` en personaje → `Select` para reasignar subdivisión (con scores)
5. **Footer:** `[Save]` `[Cancel]`

Save → `bridge.apply_edit(mutator)`. Si inválido → error rojo, no cierra.

### 2.4 — Harmonic display

Usar `harmony.py` (ya existe, funciones puras):
- `character_faction_affinity` → color: verde ≥0.3, amarillo -0.3..0.3, rojo ≤-0.3
- `subdivision_weight` → peso político de cada subdivisión

### Criterio: Enter en facción abre editor. Puedes cambiar status/power/cohesion/leader. Puedes reasignar personajes a subdivisiones con scores armónicos. Invariantes bloquean cambios ilegales.

---

## Phase 3 — Location God Mode

**Problema:** LocationPanel es texto estático. No puedes cambiar control de facciones, tensión, acceso.

### 3.1 — LocationPanel → DataTable interactivo

**Archivo:** `src/gigagen/cli/tui/widgets.py`

`Location | Zone | Status | Tension | Access | Controller | Secondary`

`Enter` → abre `LocationEditorScreen`.

### 3.2 — `LocationEditorScreen`

**Archivo:** `src/gigagen/cli/tui/screens.py`

Layout:

1. **Header (locked):** Nombre, zone_level, tonic, biome_tags, parent — identity, no editable
2. **Editables:**
   - Status → `Select`
   - Tension → `Input` float 0.0–1.0 + barra
   - Access → `Select` (open/restricted/sealed/clandestine)
   - Controlling Faction → `Select` con todas las facciones
   - Secondary Factions → lista de checkboxes (toggle por facción)
3. **Residentes:** DataTable de characters en esta location
   - `Character | Note | Faction | Affinity`
   - Affinity via `harmony.character_location_affinity`
4. **Instabilidad:** `harmony.location_instability` en vivo como barra coloreada
5. **Footer:** `[Save]` `[Cancel]`

### Criterio: Enter en location abre editor. Puedes cambiar controller/secondary/tension/access/status. Invariantes protegen bonds fijos.

---

## Phase 4 — Integración y Persistencia

### 4.1 — Persistir a JSON

**Archivo:** `src/gigagen/io/export_world_state.py`

```python
def save_worldpack(ws: WorldState, worldpack_dir: Path) -> None:
```

Escribe characters.json, factions.json, locations.json, relations.json.

**Binding:** `Ctrl+S` en app → guarda + limpia `_dirty`.

### 4.2 — Character editor

**Archivo:** `src/gigagen/cli/tui/screens.py`

`CharacterEditorScreen` accesible desde InspectorScreen con `e`:
- Editables: status, emotional_load, current_location_id, current_faction_id, current_subdivision_id
- Locked: name, archetype, note, hero_type, civil_name, role_name, lineage
- Muestra afinidades al cambiar facción/location
- Valida vía `bridge.apply_edit`

### 4.3 — Crear relaciones dinámicas

En `GlobalRelationsScreen`, binding `n` → formulario `NewRelationScreen`:
- Source/Target → `Select` con todas las entidades
- Kind, Weight, Polarity → inputs
- Canon level forzado a `"derived"`

### 4.4 — Validación global bajo demanda

Binding `v` → `ValidationResultScreen` mostrando resultado de `validate_invariants` completo.

### 4.5 — Dashboard armónico

Binding `h` → `HarmonicDashboardScreen`:
- Matriz de compatibilidad entre facciones (`faction_compatibility`)
- Ranking de instabilidad de locations
- Resumen de afinidad personaje↔facción (flaggear afinidades negativas)

### 4.6 — Help actualizado

Actualizar `HelpScreen` con todos los bindings nuevos.

### Criterio: Ctrl+S guarda. `v` valida. `h` muestra dashboard armónico. Personajes editables. Relaciones creables.

---

## Orden de implementación

```
Phase 0 (modelo)
    │
    ├──► Phase 1 (relaciones)     ← independiente
    │
    └──► Phase 2 (facciones)      ← independiente, pero implementa apply_edit
              │
              ▼
         Phase 3 (locations)      ← reutiliza apply_edit de Phase 2
              │
              ▼
         Phase 4 (integración)    ← depende de todo lo anterior
```

Phase 1 y 2 pueden desarrollarse en paralelo tras Phase 0.

---

## Archivos tocados (resumen)

| Archivo | Phases | Cambios |
|---------|--------|---------|
| `src/gigagen/core/entity.py` | 0 | `current_subdivision_id` en Character |
| `worlds/kilima/characters.json` | 0 | Asignaciones de subdivisión |
| `src/gigagen/core/invariants.py` | 0, 2, 3 | Checks subdivisión + edición |
| `tests/test_models.py` | 0 | Tests campo + invariante |
| `src/gigagen/cli/tui/widgets.py` | 1, 2, 3 | RelationsTable, FactionPanel y LocationPanel → DataTable |
| `src/gigagen/cli/tui/screens.py` | 1, 2, 3, 4 | 7 screens nuevas |
| `src/gigagen/cli/tui/app.py` | 1, 2, 3, 4 | Bindings, wiring, save, validate |
| `src/gigagen/cli/tui/bridge.py` | 2, 4 | `apply_edit`, `_dirty` flag |
| `src/gigagen/cli/tui/styles.tcss` | 1, 2, 3 | Estilos nuevas screens |
| `src/gigagen/io/export_world_state.py` | 4 | `save_worldpack` |

## Funciones existentes a reutilizar

- `harmony.character_faction_affinity()` — `src/gigagen/core/harmony.py`
- `harmony.character_location_affinity()` — `src/gigagen/core/harmony.py`
- `harmony.location_instability()` — `src/gigagen/core/harmony.py`
- `harmony.faction_compatibility()` — `src/gigagen/core/harmony.py`
- `harmony.subdivision_weight()` — `src/gigagen/core/harmony.py`
- `validate_invariants()` — `src/gigagen/core/invariants.py`
