# Roadmap — Life Pack Integration

> Milestones para integrar el sistema Life Pack en Gigagen.
> Prerequisito: leer `lifepack_estructura.md` y `lifepack_template.json`.

---

## Contexto

El Life Pack es el espectro completo de existencia de un personaje, organizado por octavas (0–8 + infrasonidos/ultrasonidos). Cada octava contiene un tipo de entidad distinto (lore, ánimas, linajes, locations, objetos, skills, personajes, eventos). El sistema se activa progresivamente por escalón de la Escalera de Descendencia (Genesis → Theogony → Chronica → Contempo).

### Impacto en el código existente

- `entity.py` necesita un modelo LifePack + refactor de nomenclatura (subdivision → faction)
- `harmony.py` necesita funciones nuevas para calcular Life Pack slots
- `load_worldpack.py` necesita cargar lifepacks desde JSON
- `simulator.py` necesita leer/escribir slots del Life Pack durante la simulación
- `characters.json` necesita campo `lifepack_file` o embebido
- Nomenclatura global: `subdivision` → `faction`, `faction` → `macro_faction`

### Nomenclatura (renombrado global)

Antes de tocar nada, renombrar en todo el proyecto:

| Antes | Después | Razón |
|-------|---------|-------|
| `faction` | `macro_faction` | La facción era el modo, ahora es la macro-facción |
| `subdivision` | `faction` | La subdivisión era la escala concreta, ahora es la facción real |
| `kilima_rebel` | `kilima_in12_rebel` | Prefijo de colección para evitar conflictos futuros |
| (todos los character ids) | `kilima_in12_{archetype}` | Consistencia de colección |

---

## LP-0: Nomenclatura y preparación — DONE

**Objetivo:** Renombrar sin romper nada. 0 features nuevas.

- [x] Renombrar `subdivision` → `faction` y `faction` → `macro_faction` en todos los modelos Pydantic
- [x] Renombrar en todos los JSON de Kilima (characters, factions, locations, invariants)
- [x] Renombrar character IDs: `char.rebel` → `kilima_in12_rebel` (y los 11 restantes)
- [x] Actualizar timeline_maps.json con IDs nuevos
- [x] Actualizar todos los tests
- [x] Verificar: 205 tests passing con nombres nuevos

**Criterio de éxito:** `pytest` pasa al 100%. Grep de "subdivision" en src/ y worlds/ devuelve 0 hits. ✓

---

## LP-1: Modelo LifePack en Gigagen (core) — DONE

**Objetivo:** Modelo Pydantic genérico para Life Pack. Sin datos de Kilima.

- [x] Crear `src/gigagen/core/lifepack.py`
- [x] Modelo `LifePackSlot`: interval, semitones, role, entity_id, entity_name, resolved_note, unlocked, locked, alteration (optional). Extra fields allowed for octave-specific data.
- [x] Modelo `LifePackOctave`: unlocked_at, logic (enum: fixed_12_archetypes, variable_by_elements, single_slot, internal_chord, full_12_by_interval, invariants_and_variables, tbd_hybrid, tbd), slots dict
- [x] Modelo `LifePack`: meta (tonic, mode, collection), 11 named octave fields (infrasonidos, octave_0–8, ultrasonidos)
- [x] Función `resolve_note(tonic_semitone, interval_semitones) → note_name`
- [x] Función `build_empty_lifepack(tonic, mode) → LifePack`: 12 lore slots, 12×3 chord slots (4 unlocked each), 12 character slots, 12 event slots
- [x] 27 tests: model instantiation, serialization round-trip, template JSON validation, Kive lifepack validation, resolve_note for all 12 semitones

**Criterio de éxito:** `LifePack.model_validate(json.load(open("lifepack_template.json")))` pasa. ✓

---

## LP-2: Loader de Life Packs — DONE

**Objetivo:** Cargar lifepacks desde el worldpack.

- [x] Crear directorio `worlds/kilima/lifepacks/`
- [x] Copiar `kilima_in12_rebel_lifepack.json` a `worlds/kilima/lifepacks/kilima_in12_rebel.json`
- [x] Extender `load_worldpack.py`: buscar `lifepacks/` dir, cargar cada JSON como LifePack, vincular a Character por entity_id
- [x] WorldState: campo `lifepacks: dict[str, LifePack]` + método `get_lifepack(character_id)`
- [x] 7 tests: loading, missing lifepack, meta match, serialization roundtrip

**Criterio de éxito:** `ws.get_lifepack("kilima_in12_rebel").octave_7_personajes.slots["7_quinta_justa"].entity_name == "Cris"` ✓

**Nota:** lifepacks viven en `WorldState.lifepacks` dict, no embebidos en Character. Acceso via `ws.get_lifepack(id)`.

---

## LP-3: Modo global del Life Pack — DONE

**Objetivo:** Implementar el modo (mayor/menor) como propiedad global que afecta a todas las octavas.

- [x] Campo `mode: Literal["major", "minor"]` en LifePack.meta (ya existía desde LP-1)
- [x] Función `get_interval_semitones(degree, mode) → int`: 3rd, 6th, 7th → semitones por modo
- [x] Función `change_mode(lifepack, new_mode) → LifePack`: swaps semitones/resolved_notes/alterations de los 3 pares mode-sensitive × 3 chord octaves. Entities preserved.
- [x] 18 tests: interval lookup, mode swap, resolved note recalculation, entity preservation, double-change roundtrip

**Criterio de éxito:** `change_mode(lp, "major")` recalcula 3×3 slot pairs sin perder entidades. ✓

---

## LP-4: Octava 7 auto-calculada — DONE

**Objetivo:** La octava de personajes se rellena sola cuando hay datos suficientes.

- [x] Función `populate_octave_7(lifepack, all_characters)`: calcula intervalo desde tónica, rellena entity_id/name/note
- [x] Integrado en `load_worldpack.py`: auto-popula después de cargar characters + lifepacks
- [x] Slots vacíos manejados (no crash si faltan personajes)
- [x] 8 tests: 12 chars complete, 6 chars partial, Kive↔Len/Dev/Cris slots, owner at unison, loader integration

**Criterio de éxito:** Kive tiene Len en slot 1, Dev en slot 3, Cris en slot 7 (automáticamente). ✓

---

## LP-5: Unlock de slots en simulación — DONE

**Objetivo:** El simulador puede desbloquear slots del Life Pack durante la timeline.

- [x] Nuevo event rule type: `unlock_lifepack_slot` (lista de {character, octave, slot_key})
- [x] Handler `_unlock_lifepack_slot` en simulator.py: locked→unlocked, outcome recorded
- [x] Already-unlocked slots = no-op, missing lifepack = no-op
- [x] 5 tests: lock→unlock, no-op on unlocked, outcome recording, full event rule integration, missing lifepack

**Criterio de éxito:** Event rule con `unlock_lifepack_slot` → slot pasa de locked a unlocked. ✓

---

## LP-6: Octava 8 — Eventos como invariantes/variables — DONE

**Objetivo:** Los slots de eventos respetan la lógica invariant/variable del sistema existente.

- [x] `LifePackSlot.event_type`: "invariant" | "variable" | "" (aliased from JSON "type")
- [x] `LifePackSlot.resolved`: bool field + `semitones_from_tonic` → `semitones` normalizer
- [x] `resolve_octave_8_invariants(lp)`: marks invariant slots as resolved, returns count
- [x] `resolve_octave_8_variable(lp, var_id, resolution)`: fills first unresolved variable slot
- [x] 7 tests: invariant pre-resolve, variable resolve, noop on re-resolve, Kive JSON loads with event_type

**Criterio de éxito:** Kive's lifepack loads with `event_type == "invariant"`, `resolve_octave_8_invariants` marks them resolved. ✓

---

## LP-7: TUI — Visualización del Life Pack — DONE

**Objetivo:** Poder inspeccionar el Life Pack de un personaje desde God Mode.

- [x] `LifePackInspectorScreen` en screens.py — modal con scroll, 9 octavas
- [x] Cada slot: nota resuelta, rol, entidad vinculada, estado (unlocked/locked)
- [x] Color por estado: green = filled, yellow = empty/unlocked, dim = locked
- [x] Binding `L` (shift+l) en app.py → abre inspector del personaje seleccionado
- [x] Maneja personajes sin lifepack (muestra "No Life Pack loaded")
- [x] 4 tests: content builds, no-lifepack fallback, green/dim color output

**Criterio de éxito:** `L` sobre un character → Life Pack completo con colores. ✓

---

## LP-8: Ánimas (octava 1) — Estructura base — DONE

**Objetivo:** Implementar la lógica variable de ánimas. Sin mecánicas de combate, solo estructura.

- [x] Modelo `ElementConfig`: innate_elements, dominated_elements, latent_elements, unlocked_fusions
- [x] Modelo `ElementDef` + catálogo `elements.json`: 16 elementos (4 fundamental, 6 mixed, 4 truncated, 2 supreme)
- [x] `load_elements_catalog()`: carga el JSON de elementos
- [x] `compute_available_anima_slots(config, catalog)`: active/available/future por elemento
- [x] 9 tests: catalog loads, Kive (1 active + 1 available + metal future), Dev (0), Len (4 active + 12 future), fusions

**Criterio de éxito:** Kive config → fuego active, tierra available, metal future. ✓

---

## Orden recomendado

```
LP-0 (renombrado) → LP-1 (modelo) → LP-2 (loader) → LP-3 (modo) → LP-4 (octava 7 auto)
     → LP-5 (unlock en simulación) → LP-6 (eventos) → LP-7 (TUI) → LP-8 (ánimas)
```

LP-0 a LP-4 son el fundamento. LP-5 y LP-6 conectan con el simulador. LP-7 es visualización. LP-8 es el sistema más complejo y puede esperar.

---

## Archivos de referencia

| Archivo | Qué contiene |
|---------|-------------|
| `lifepack_estructura.md` | Definición conceptual de todas las entidades y relaciones |
| `lifepack_template.json` | Plantilla JSON vacía con todos los slots |
| `kilima_in12_rebel_lifepack.json` | Life Pack de Kive parcialmente rellenado (primer ejemplo) |
