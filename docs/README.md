# Gigagen — Documentation Index

> General documentation hub for the Gigagen project.

---

## Project Overview

Gigagen is a narrative simulation engine. It generates and simulates fictional worlds where characters, factions, locations, and relationships interact through a deterministic, seed-based system.

The engine is generic — it defines data models, simulation rules, and harmonic systems. Worldpacks provide the specific content (characters, lore, factions, timelines) for a particular universe.

**Current worldpack:** Kilima (within the "Basura Digital" universe).

---

## Directory Structure

```
docs/
├── CLAUDE.md                  # Master context — what the project is, how to work on it
├── README.md                  # This file — documentation index
│
├── gigagen/                   # Engine-level documentation (not worldpack-specific)
│   ├── gigagen_ontology.md        # Formal data models — BaseEntity, Relation, WorldState
│   ├── gigagen_faction_system.md  # Generic faction & harmonic system
│   ├── gigagen_roadmap1.md        # Development milestones M1-M5 (complete)
│   ├── gigagen_roadmap2.md        # Consolidation milestones C1-C6
│   └── gigagen_consoleUI_v1.md    # Console UI specification
│
├── kilima/                    # Kilima worldpack — lore, design, and narrative
│   ├── kilima_bible.md            # Index/map of all Kilima lore documents
│   ├── kilima_lore.md             # World background, history, geography, technology
│   ├── kilima_characters.md       # The 12 principals — identities, bonds, arcs
│   ├── kilima_factions.md         # The 10 factions — modes, subdivisions, assignments
│   ├── kilima_locations.md        # All locations — zones, access, faction control
│   ├── kilima_invariants.md       # What's fixed, variable, derived, forbidden in Kilima
│   ├── kilima_parked_ideas.md     # Good ideas not needed for Act 1
│   ├── kilima_timeline_act1.yaml  # NB1 master timeline — 62 hours, all events
│   │
│   └── data/                      # Kilima JSON data files (loaded by code)
│       ├── characters.json
│       ├── factions.json          # OUTDATED — needs update to match kilima_factions.md
│       ├── locations.json
│       ├── relations.json
│       └── world.json
```

---

## Key Documents

### For understanding the engine
1. **CLAUDE.md** — Start here. Master context for the whole project.
2. **gigagen/gigagen_ontology.md** — The data model law. Entity types, relations, world state.
3. **gigagen/gigagen_faction_system.md** — How factions work as harmonic note sets.

### For understanding Kilima
1. **kilima/kilima_bible.md** — Map of all Kilima lore. Start here for the world.
2. **kilima/kilima_lore.md** — Deep background: history, geography, technology, society.
3. **kilima/kilima_factions.md** — The 10 factions, their subdivisions, and character assignments.
4. **kilima/kilima_characters.md** — The 12 principals in detail.

### For development
1. **gigagen/gigagen_roadmap2.md** — Current milestone tracker (consolidation phase).
2. **kilima/kilima_invariants.md** — Rules the system must never break.

### For the Life Pack system
1. **lifepack_estructura.md** — Conceptual definition of all entities, relationships, and octave logic.
2. **lifepack_template.json** — Empty JSON template with all octaves and all slots.
3. **gigagen_roadmap_lifepack.md** — Implementation milestones LP-0 through LP-8.
4. **kilima_in12_rebel_lifepack.json** — Kive's Life Pack (first example, partially filled).

---

## Conventions

- **Engine docs** use the `gigagen_` prefix and live in `docs/gigagen/`.
- **Worldpack docs** use the `kilima_` prefix and live in `docs/kilima/`.
- **JSON data** loaded by code lives in `docs/kilima/data/` (mirrors `worlds/kilima/`).
- **Life Pack files** live in `worlds/kilima/lifepacks/` (one JSON per character).
- **CLAUDE.md** stays at `docs/` root — it's the entry point for any AI assistant working on the project.

---

## TODO

- [x] Create `gigagen/gigagen_invariants.md` — generic invariant system
- [ ] **LP-0: Rename subdivision → faction, faction → macro_faction globally**
- [ ] **LP-0: Rename character IDs to kilima_in12_{archetype} pattern**
- [ ] Update `kilima/data/factions.json` to match the new 10-faction system in kilima_factions.md
- [ ] Update CLAUDE.md to reflect new directory structure
- [ ] **LP-1: Create `src/gigagen/core/lifepack.py` — Pydantic models for Life Pack**
- [ ] **LP-2: Extend loader to load lifepacks from `worlds/kilima/lifepacks/`**
- [ ] **LP-3: Implement global mode (major/minor) on Life Pack**
- [ ] **LP-4: Auto-populate octave 7 from character roster**
- [ ] **LP-5: Unlock slots during simulation via event rules**
- [ ] **LP-6: Integrate octave 8 events with invariant/variable system**
- [ ] **LP-7: TUI screen for Life Pack inspection**
- [ ] **LP-8: Ánimas octave 1 — element config and slot computation**
- [ ] Create Recess as new location in worldpack (note A#, Ciudad, Kilima)
- [ ] Create remaining 11 Life Packs for kilima_in12 collection
