# RECAP 02 — Estado del proyecto Gigagen / Kilima

> Snapshot a 23 de marzo de 2026. 292 tests passing.
> Cambios respecto a RECAP 01: Life Pack completo, data rework, nomenclatura nueva, armonía universal.

---

## Qué es esto

**Gigagen** es un motor/framework en Python para compilar universos relacionales. **Kilima** es el primer worldpack: una distopía techno-política organizada alrededor de La Montaña, con 12 personajes, 10 macro-facciones (35 facciones), 55 locations y una timeline de 62 horas.

```
Gigagen = gramática / motor / framework
Kilima  = poema / mundo / instancia concreta
```

---

## Qué cambió desde RECAP 01

### Nomenclatura (LP-0)
La nomenclatura antigua (`faction` / `subdivision`) fue reemplazada en todo el proyecto:

| Antes | Después | Scope |
|-------|---------|-------|
| `class Faction` | `class MacroFaction` | Entidad con modo armónico |
| `class Subdivision` | `class Faction` | Escala concreta con líder y base |
| `current_faction_id` | `current_macro_faction_id` | Campo en Character |
| `current_subdivision_id` | `current_faction_id` | Campo en Character |
| `char.rebel` | `kilima_in12_rebel` | IDs de personaje |
| `subdivision_weight()` | `faction_weight()` | Función armónica |

0 ocurrencias de "subdivision" en src/ y worlds/.

### Data Rework (FL-0 a FL-4)
Los datos de Kilima fueron reestructurados:

| Dato | RECAP 01 | RECAP 02 |
|------|----------|----------|
| Factions JSON | Array plano, subdivisions embebidas | Split: `macro_factions[]` + `factions[]` |
| Faction IDs | `fac.anti_group` | `mfac.anti_group` (macro) + `fac.direnis_cell` (facción) |
| Location count | 15 planas | 55 jerárquicas (7 niveles: world→territory→region→area→location→room→locker) |
| Location IDs | `loc.cage`, `loc.capital`, `loc.city` | `golden_cage`, `capitol`, `agora` |
| Location tonics | Todas null | 4 fixed (Workshop D#, Backdoor F#, Cave B, Recess A#), resto seeded |
| Relations | 26 | 30 (7 faction→location añadidas) |
| Character faction refs | Nombres ("Red Fist Dragons") | IDs (`fac.red_fist_dragons`) |

### Life Pack (LP-1 a LP-8)
Sistema completamente nuevo. El Life Pack es el espectro completo de existencia de un personaje, organizado por octavas.

### Armonía Universal
`harmony.py` simplificado. Funciones específicas por tipo ahora delegan a `harmonic_affinity(note_a, note_b)` de `relation.py`. `dual_membership_cost` eliminado (dead code).

### Migración Data
`worlds/kilima/` y `docs/kilima/data/` sincronizados. Una sola fuente de verdad. El loader maneja el nuevo formato split (factions) y jerárquico (locations).

---

## Arquitectura

```
src/gigagen/
├── core/                      # Motor puro (0 dependencias de Kilima)
│   ├── entity.py              # Modelos: Character, MacroFaction, Faction, Location, Item, Anima
│   ├── lifepack.py            # NUEVO — Life Pack: modelos, resolve_note, build, change_mode, populate, elements
│   ├── elements.json          # NUEVO — Catálogo de 16 elementos (4 fund + 6 mix + 4 trunc + 2 supreme)
│   ├── world_state.py         # Contenedor: entities + relations + lifepacks + seed + phase
│   ├── relation.py            # Modelo Relation + harmonic_affinity() universal + RELATION_KINDS
│   ├── harmony.py             # Motor armónico: 6 funciones (simplificado, usa harmonic_affinity)
│   ├── simulator.py           # Procesador de timeline + unlock_lifepack_slot
│   ├── seed.py                # Variación determinística por seed
│   └── invariants.py          # Validación contra invariants.json
├── io/
│   ├── load_worldpack.py      # Loader: split factions, hierarchical locations, lifepacks
│   └── export_world_state.py  # Exporta WorldState + lifepacks a JSON
├── cli/
│   ├── console.py             # Consola clásica (REPL)
│   └── tui/                   # God Mode TUI (Textual)
│       ├── app.py             # 29 bindings (+L para Life Pack)
│       ├── bridge.py          # SimulatorBridge: snapshots por hora, rewind O(1)
│       ├── screens.py         # 17 screens modales (+LifePackInspectorScreen)
│       ├── widgets.py         # 7 widgets
│       ├── map_widget.py      # Mapa jerárquico
│       └── styles.tcss        # Estilos CSS
└── __main__.py                # Entry point

worlds/kilima/                 # Worldpack de Kilima (fuente de verdad)
├── world.json                 # Metadata + catalogs
├── characters.json            # 12 personajes (IDs kilima_in12_*)
├── factions.json              # 10 macro-facciones + 35 facciones (split format)
├── locations.json             # 55 locations (7 niveles jerárquicos)
├── relations.json             # 30 relaciones
├── invariants.json            # Reglas de integridad + 3 variables
├── event_rules.json           # Reglas condicionales por evento
├── timeline_maps.json         # Mapeo nombres↔IDs
├── lifepacks/                 # NUEVO
│   └── kilima_in12_rebel.json # Life Pack de Kive (parcialmente rellenado)
└── timelines/
    └── bn1.yaml               # Timeline NB1: 45 eventos en 62 horas
```

---

## Sistemas implementados

### 1. Motor armónico (`harmony.py` + `relation.py`)

Pilar universal: `harmonic_affinity(note_a, note_b)` en `relation.py`. Todo cálculo armónico parte de esta función.

| Función | Dónde | Qué hace |
|---------|-------|----------|
| `harmonic_affinity` | relation.py | Intervalo entre dos notas → afinidad [-1, 1] |
| `build_scale` | harmony.py | Root + intervals → lista de notas |
| `character_faction_affinity` | harmony.py | Afinidad + bonus/penalty por pertenencia a escala |
| `character_location_affinity` | harmony.py | Structural (vs tonic) + modal (in/out of scale) |
| `location_instability` | harmony.py | Overlap entre escalas de facciones disputando |
| `faction_weight` | harmony.py | Consonancia con otras facciones → peso político |
| `faction_compatibility` | harmony.py | Similitud de interval patterns entre modos |

### 2. Life Pack (`lifepack.py`) — NUEVO

El espectro completo de existencia de un personaje.

**Modelos:**
- `LifePack`: 11 octavas (infrasonidos, 0-8, ultrasonidos) + meta (tonic, mode, collection)
- `LifePackOctave`: unlocked_at, logic, slots dict
- `LifePackSlot`: interval, semitones, role, entity_id, resolved_note, locked, alteration, event_type, resolved
- `LifePackMeta`: entity_id, tonic, tonic_semitone, mode
- `ElementConfig`: innate/dominated/latent elements, unlocked_fusions
- `ElementDef`: id, name, tier, requires
- `AnimaSlotResult`: element_id, tier, status (active/available/future)

**Funciones:**
| Función | Qué hace |
|---------|----------|
| `resolve_note(tonic_semi, interval_semi)` | Calcula nota concreta de un slot |
| `get_interval_semitones(degree, mode)` | Semitonos de 3rd/6th/7th según modo |
| `build_empty_lifepack(tonic, mode)` | Genera plantilla vacía con notas resueltas |
| `change_mode(lp, new_mode)` | Recalcula slots mode-sensitive (3rd/6th/7th × 3 octavas) |
| `populate_octave_7(lp, all_characters)` | Auto-rellena octava de personajes por intervalo |
| `resolve_octave_8_invariants(lp)` | Marca slots invariant como resolved |
| `resolve_octave_8_variable(lp, var_id, resolution)` | Rellena primer slot variable no resuelto |
| `load_elements_catalog()` | Carga 16 elementos desde JSON |
| `compute_available_anima_slots(config, catalog)` | Calcula slots disponibles por elementos |

**Integración:**
- Loader auto-descubre `lifepacks/*.json` y los carga en `WorldState.lifepacks`
- Octava 7 auto-populated tras cargar characters
- Simulador puede desbloquear slots vía event rule `unlock_lifepack_slot`
- `save_worldpack()` persiste lifepacks modificados
- TUI: `L` abre `LifePackInspectorScreen` (colores: verde=filled, amarillo=empty, gris=locked)

### 3. Simulador (`simulator.py`)

Procesador de timeline data-driven. Sin lógica hardcoded.

- `build_simulator()` → inicializa state desde WorldState
- `advance_to()` → procesa eventos hora a hora
- Event rules: mover personajes, resolver variables, cambiar status, set emociones, faction changes
- **NUEVO:** `unlock_lifepack_slot` — desbloquea slots del Life Pack durante la simulación
- Harmonic enrichment: cada evento registra tonic, modal influence, afinidades
- `max_hour` cargado desde worldpack

### 4. God Mode TUI

Editor interactivo completo. 29 bindings, 17 screens modales.

**Bindings nuevos:**
| Tecla | Acción |
|-------|--------|
| `L` | Abre Life Pack Inspector del personaje seleccionado |

**LifePackInspectorScreen:**
- 9 octavas como secciones
- Cada slot: nota resuelta, rol, entidad, estado
- Verde = filled, amarillo = empty/unlocked, gris = locked
- Maneja personajes sin lifepack gracefully

### 5. Sistema de invariantes (`invariants.py`)

- Conteo de characters/macro-factions
- Identidad del roster (archetype, note, name)
- Relaciones fijas presentes
- Faction consistency: valida contra embedded factions O faction IDs (compatible con ambos modelos)
- Parent location validity + detección de ciclos

### 6. Separación Gigagen/Kilima

Desacoplamiento total mantenido.

- **entity.py**: `str` libre. `Faction` con `extra="allow"` para campos nuevos del split format.
- **lifepack.py**: genérico. `LifePackSlot` con `extra="allow"` y normalizer para aliases JSON.
- **load_worldpack.py**: maneja tanto formato antiguo (array plano) como nuevo (split/hierarchical).
- **elements.json**: catálogo genérico en `core/`, no en `worlds/kilima/`.

---

## Datos de Kilima

| Entidad | Count | Detalle |
|---------|-------|---------|
| Characters | 12 | 12 arquetipos × 12 notas. IDs: `kilima_in12_{archetype}` |
| Macro-factions | 10 | 7 griegas + 1 whole_tone + 2 pentatónicas |
| Factions | 35 | 12 ministerios UC + 5 Agency + 3 Anti Group + 4 Amparo + 4 Bohemian + 2 Cult + 4 Guard + 1 Backdoor |
| Locations | 55 | 1 world + 1 territory + 4 regions + 5 areas + 17 locations + 24 rooms + 2 lockers + 1 future_locations catalog |
| Relations | 30 | 17 char↔char + 5 char→fac + 7 fac→loc + 1 char→mfac |
| Timeline events | 45 | H00→H62. 3 variables (VAR_DEV, VAR_BRAIS, VAR_ENDING) |
| Event rules | 17 | Condicionales, movimiento, status changes, lifepack unlocks |
| Life Packs | 1 | Kive (kilima_in12_rebel) — parcialmente rellenado |

---

## Tests

**292 funciones de test, 100% passing.**

| Archivo | Tests | Cubre |
|---------|-------|-------|
| test_lifepack.py | 78 | LP-1 a LP-8: modelos, serialización, mode, octave 7, unlock, octave 8, TUI, ánimas |
| test_models.py | 44 | Modelos Pydantic, worldpack loading, faction invariants, parent hierarchy |
| test_harmony.py | 42 | Todas las funciones armónicas (post-simplificación) |
| test_loader_console.py | 29 | Loader, consola, no-Kilima-in-source check |
| test_bridge.py | 28 | Snapshots, rewind, time navigation |
| test_simulator.py | 28 | Event processing, variables, movement, outcomes, harmonic integration |
| test_seed_variation.py | 16 | Variación determinística |
| test_lifepack_loader.py | 7 | LP-2: carga desde worldpack, meta match, serialización |
| test_data_integrity.py | 7 | Cross-reference entre JSONs (characters→locations, factions→locations, relations) |
| test_generic_worldpack.py | 7 | Worldpack no-Kilima funciona |
| test_faction_location_integrity.py | 6 | FL-3: faction bases level 5, root notes, based_in relations |

---

## Milestones completados en esta sesión

| Milestone | Descripción | Tests añadidos |
|-----------|-------------|----------------|
| FL-0 | Rework factions.json: split macro_factions + factions | — (data) |
| FL-3 | Validación cruzada factions↔locations | +6 |
| FL-4 | Update relations.json con nuevos faction IDs | — (data) |
| LP-0 | Rename: subdivision→faction, faction→macro_faction, char IDs | — (rename) |
| LP-1 | Modelo LifePack Pydantic | +27 |
| LP-2 | Loader de lifepacks desde worldpack | +7 |
| LP-3 | Modo global (major/minor) con change_mode() | +18 |
| LP-4 | Octava 7 auto-populated desde roster | +8 |
| LP-5 | unlock_lifepack_slot en simulador | +5 |
| LP-6 | Octava 8: invariants + variables | +7 |
| LP-7 | TUI LifePackInspectorScreen (L) | +4 |
| LP-8 | Ánimas: ElementConfig + elements.json + compute_slots | +9 |
| Data migration | worlds/ = docs/ (una fuente de verdad) | — (data) |
| Harmony refactor | Simplificación con harmonic_affinity() universal | -4 (dead code removed) |

**Delta:** +87 tests netos (205 → 292)

---

## Lo que NO está implementado

| Sistema | Estado en RECAP 01 | Estado en RECAP 02 |
|---------|--------------------|--------------------|
| **Ánimas** | Modelo existe. Sin loader, sin datos | **Estructura base implementada.** ElementConfig, catálogo de 16 elementos, compute_available_anima_slots(). Sin datos de Kilima aún. |
| **Life Pack** | No existía | **Completo.** Modelo, loader, mode, populate, unlock, events, TUI, elements. |
| Items | Modelo existe. Sin loader, sin datos | Sin cambios |
| Chronica | Layer 3. No implementada | Sin cambios |
| Existence | Layer 5. No implementada | Sin cambios |
| Skills | No definidas | Sin cambios |
| Combate | No definido | Sin cambios |
| Godot | Sin integración | Sin cambios |
| **Tonics** | Todas null | **4 locations con tonic fixed.** Resto seeded. |

---

## Stack

- Python 3.12+
- Pydantic v2 (modelos de datos)
- Textual (TUI framework)
- PyYAML (timelines)
- pytest (tests)
- pip install -e . (pyproject.toml)

---

## Ideas a futuro / próximos pasos naturales

### Inmediato (fundamento)

1. **Primera simulación completa con Life Pack** — Correr BN1 con Kive's Life Pack activo. Conectar `resolve_octave_8_invariants` al loader (auto-resolve on load). Conectar variable resolution del simulador con `resolve_octave_8_variable`. Ver cómo muta el espectro durante la timeline. **Esta es la meta faro del CLAUDE.md.**

2. **Segundo Life Pack** — Crear el lifepack de Len (máximo elemental, Éter de base) o Dev (octava 1 vacía, poder condicional). Valida que el sistema es genérico y no Kive-dependiente.

3. **Poblar octavas 3-5** — Locations, objetos, skills de Kive. El template está, los slots están, pero los datos son vacíos. Esto cierra el circuito del Life Pack.

### Medio plazo (sistema)

4. **RELATION_KINDS dinámico** — Mover el frozenset a catálogos del worldpack. Cada universo define sus tipos de relación.

5. **Integración ánimas con datos de Kilima** — Crear element_configs para los 12 personajes. Poblar octava 1 con ánimas gambleadas por seed.

6. **Character tracker** — Biografía temporal de un personaje (trayectoria completa H00→H62). Qué locations visitó, qué slots desbloqueó, cómo cambió su espectro.

7. **Diff entre snapshots** — Comparar H00 vs H30: qué cambió en el worldstate, en los lifepacks, en las afinidades.

### Largo plazo (visión)

8. **Chronica** — Layer 3: re-simulación del pasado. Resuelve notas seeded de locations, asigna tonics por lineage. El Life Pack se activa completamente aquí.

9. **Harmonía como driver de outcomes** — Que las afinidades influyan en las decisiones del simulador, no solo se registren. Un personaje con alta afinidad a una location resiste más; baja afinidad genera eventos negativos.

10. **Scenario fork** — Guardar checkpoints, comparar escenarios alternativos. Un VAR_DEV="participates" vs "refuses" genera dos universos divergentes con lifepacks distintos.

---

## Inconsistencias conocidas / deuda técnica

| Issue | Severidad | Detalle |
|-------|-----------|---------|
| **worlds/ vs docs/ format wrapper** | Baja | `docs/kilima/data/` usa `{"characters":[...]}` wrappers con `$schema`. `worlds/kilima/` usa arrays planos (characters, relations) o el split format (factions, locations). Loader maneja ambos. |
| **Faction model flexibility** | Baja | `Faction(BaseModel, extra="allow")` acepta campos extras del split format (id, macro_faction_id, etc.) pero no los declara explícitamente. Funciona pero es implícito. |
| **Location model stripping** | Baja | El loader `_normalize_location()` filtra campos desconocidos (tonic_type, zone_tag, modal_influence, bn1_relevance). Estos datos existen en el JSON pero no se cargan en el modelo. |
| **current_macro_faction_id obsoleto** | Baja | El campo existe en Character pero docs/ characters.json no lo usa (es None para todos). El validator tolera ambos modelos. Podría eliminarse en el futuro. |
| **Life Pack no integrado en simulación** | Media | LP-5 añade `unlock_lifepack_slot` pero no hay event rules en bn1.yaml que lo usen. LP-6 tiene resolve functions pero no se llaman automáticamente durante la simulación. Es opt-in, no automático. |
| **TUI zone_level mapping** | Baja | El mapa TUI usa zone_level para categorizar (HIGH/MID/LOW/etc.). El nuevo locations.json usa `level` (world/territory/region/area/location). La normalización convierte level→zone_level pero los valores no mapean 1:1 a las zonas del mapa. |
| **Solo 1 Life Pack** | Media | Solo Kive tiene lifepack. Sin segundo ejemplo, no se puede validar edge cases (personaje sin elementos, personaje con éter, etc.) |
