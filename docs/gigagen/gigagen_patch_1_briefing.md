# PATCH 1 — Harmonic Faction & Location System

> **Priority:** This is the FIRST major patch since the consolidation phase.
> **Read order:** This file first, then PATCH_ROADMAP.md, then the engine docs.
> **Tone:** Build it solid. This is the harmonic backbone of the entire simulation.

---

## What you're building

Gigagen's simulation currently moves characters between locations and changes their factions — but factions are just labels and locations are just strings. This patch gives them **harmonic identity**: factions become musical modes, locations get tonic notes, and every interaction between characters, factions, and locations produces calculable harmonic relationships.

After this patch:
- A faction IS a musical scale (e.g. Anti Group = Phrygian mode)
- A location HAS a tonic note and inherits modal color from its controlling faction
- A character's note interacts with faction scales and location tonics to produce affinity scores
- The simulator uses these scores during event processing
- The UI shows harmonic data to the user

---

## Read these files IN THIS ORDER

### 1. Understand the engine design
- `docs/gigagen/gigagen_faction_system.md` — how factions work as note subsets
- `docs/gigagen/gigagen_location_system.md` — how locations work with tonic + modal influence

### 2. Understand the Kilima implementation
- `docs/kilima/kilima_factions.md` — the 10 factions, their modes, subdivisions, character assignments
- `docs/kilima/kilima_locations.md` — locations with faction control, character bonds, hierarchy

### 3. Understand the patch plan
- `docs/PATCH_ROADMAP.md` — the master plan (5 phases, dependencies, success criteria)
- `docs/FACTION_ROADMAP.md` — faction-specific tasks and decisions
- `docs/LOCATION_ROADMAP.md` — location-specific tasks and decisions

### 4. Understand current code
- `docs/gigagen/gigagen_ontology.md` — current data models (what you're extending)
- `src/gigagen/core/entity.py` — current Faction, Location, Character models
- `src/gigagen/core/simulator.py` — current event processing (what you're integrating into)
- `src/gigagen/core/relation.py` — current relation system (harmonic affinity already defined here)
- `src/gigagen/io/load_worldpack.py` — current loader (needs to load new fields)

### 5. Understand the data
- `docs/kilima/data/factions.json` — UPDATED: 10 factions with mode, intervals, subdivisions
- `docs/kilima/data/characters.json` — UPDATED: 12 characters with correct faction IDs
- `docs/kilima/data/locations.json` — UPDATED: 15 locations with new faction IDs, tonic (null for now), parent hierarchy, secondary factions
- `docs/kilima/data/relations.json` — UPDATED: correct faction IDs, no fac.ai
- `worlds/kilima/` — SYNC THIS with docs/kilima/data/ before starting. docs/ is source of truth.

---

## Critical rules

### Don't break what works
There are 103 passing tests. Every single one must still pass after your changes. Run tests after every phase.

### Identity vs State
Every field in every model is either **identity** (fixed, never changes between seeds) or **state** (changes during simulation). Mode, intervals, tonic = identity. Controlling faction, tension, affinity scores = state. Never mix them.

### Factions don't have tonics
This is the most important conceptual point. A faction has a MODE (interval pattern) but NO root note. The tonic belongs to SUBDIVISIONS (from their leader's note) and to LOCATIONS (from their founding history). The faction is a template; subdivisions and locations are instances.

### Flai is NOT a faction
The AI entity (Flai) is an omnipresent character, not a faction. It has no mode, no scale, no subdivisions. It operates THROUGH Union Corp and Agency SL. Do not create a faction for it. The Net has `controlling_faction_id: null` because Flai controls it outside the faction system.

### The harmonic engine is GENERIC
All harmonic functions go in a new file: `src/gigagen/core/harmony.py`. They take notes and intervals as input, not faction names or Kilima-specific data. The engine doesn't know what "Anti Group" is — it only knows Phrygian mode applied from root B.

### Events and locations are coupled
Every event happens at a location. When a character moves to a location, their harmonic affinity to that location must be calculated. When a faction takes control of a location (like the Cave invasion at H52-H56), the modal influence changes and every character present must be recalculated. See Phase 4 in PATCH_ROADMAP.md.

---

## Phase execution order

```
Phase 1: Data models (entity.py updates, Subdivision model, worldpack loader)
    ↓
Phase 2: Harmonic engine (harmony.py — pure functions, no side effects)
    ↓
Phase 3: Kilima data (locations.json tonics — SKIP for now, leave as null)
    ↓
Phase 4: Simulator integration (events trigger harmonic calculations)
    ↓
Phase 5: Console/TUI updates (show harmonic data to user)
```

**Do Phase 1 → 2 → 4 → 5 in sequence.** Phase 3 (tonic assignment) is blocked on author decisions — leave tonic fields as null and make the code handle nulls gracefully (no tonic = no harmonic calculation for that location, but everything else still works).

---

## New files to create

| File | Purpose |
|------|---------|
| `src/gigagen/core/harmony.py` | All harmonic functions (scale generation, affinity, compatibility, instability) |
| `tests/test_harmony.py` | Unit tests for harmonic functions |

## Files to modify

| File | Changes |
|------|---------|
| `src/gigagen/core/entity.py` | Add mode/intervals/note_count/scale_family to Faction. Add tonic/parent_location_id/secondary_faction_ids to Location. Create Subdivision model. |
| `src/gigagen/io/load_worldpack.py` | Load new faction fields, subdivisions, new location fields |
| `src/gigagen/core/simulator.py` | Phase 4: events trigger harmonic calculations, modal influence changes |
| `src/gigagen/cli/console.py` | Phase 5: show harmonic info |
| `src/gigagen/cli/tui/` | Phase 5: show harmonic info in TUI |
| `tests/test_data_integrity.py` | New cross-reference checks for subdivisions, faction-location links |
| `tests/test_models.py` | Tests for new model fields |

## Data files to sync FIRST

Copy from `docs/kilima/data/` to `worlds/kilima/`:
- `factions.json`
- `characters.json`
- `locations.json`
- `relations.json`

`docs/kilima/data/` is the source of truth. These were updated during the design session.

---

## Success criteria

After this patch, running the simulator should:

1. Load all 10 factions with their modes, intervals, and subdivisions
2. Load all locations with faction control, parent hierarchy, and (null) tonics
3. Load all characters with correct faction assignments
4. Calculate character-faction affinity for every character
5. Calculate character-location modal affinity when characters move
6. Recalculate modal influence when faction control changes during events
7. Display harmonic data in the console/TUI
8. Pass all 103 existing tests + new harmonic tests
9. Handle null tonics gracefully (no crash, just skip harmonic calc)

---

## What NOT to do

- Don't assign tonic notes to locations — that's the author's job (Phase 3)
- Don't create new secondary characters for empty subdivision leader slots
- Don't rename factions or subdivisions — names are final
- Don't create a faction for Flai/The AI
- Don't hardcode Kilima-specific logic in harmony.py — keep it generic
- Don't refactor the existing simulator architecture — extend it
