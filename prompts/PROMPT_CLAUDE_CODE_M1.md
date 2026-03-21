# PROMPT FOR CLAUDE CODE — Milestone 1

Read ALL files in `docs/` before writing any code. Start with `CLAUDE.md`, then `ontology.md`, then `roadmap.md`, then `invariants.md`. Then read the worldpack files in `worlds/kilima/` to understand the data you'll be validating against.

## What this project is

Gigagen is a Python framework that loads canonical universe data (a "worldpack") and generates reproducible world states by seed. Kilima is the specific worldpack — a dystopian universe with 12 central characters, 4 factions, and a 62-hour narrative timeline.

The documentation in `docs/` is extensive and authoritative. Do not invent anything. Every model, every field, every relationship type is defined in `ontology.md`. Every invariant is in `invariants.md`. The 12 characters, their archetypes, notes, hero types, and lineages are in `kilima_characters.md` and `characters.json`. The timeline is in `worlds/kilima/timelines/bn1.yaml`.

## Your task: Milestone 1

Implement the canonical data models in Python using Pydantic v2.

### Deliverables

1. `src/gigagen/core/entity.py` — BaseEntity + Character, Faction, Location, Item, Anima
2. `src/gigagen/core/relation.py` — Relation as first-class object + harmonic_affinity function
3. `src/gigagen/core/world_state.py` — WorldState container
4. `tests/test_models.py` — Validation tests

### Critical rules

- Models MUST match `ontology.md` exactly. Do not add fields. Do not rename fields. Do not skip fields.
- Character has: id, entity_type, name, tags, canon_level, description, archetype, note, hero_type, civil_name, role_name, lineage, status, current_location_id, current_faction_id, emotional_load
- Relation has: id, source_id, target_id, kind, weight, polarity, tags, canon_level, origin_event_id
- The `harmonic_affinity(note_a, note_b)` function calculates musical interval affinity. The interval table is in `ontology.md`. It returns a float between -1.0 and 1.0. This is a CALCULATED property, never stored.
- Relation.kind must be from the closed vocabulary in `ontology.md`. Validate this.
- All 12 archetype codes are: CAR, JES, HER, REB, ORP, LOV, HCK, LEA, INN, EXP, CRE, DEI

### Validation tests should verify

- Can instantiate all 12 characters from `characters.json`
- Can instantiate all 4 factions from `factions.json` (note: factions.json is missing The AI entry — add it in the test or fix the JSON)
- Can instantiate all 15 locations from `locations.json`
- Can instantiate all 27 relations from `relations.json`
- Can build a WorldState from all of the above
- Validation rejects: wrong archetype code, invalid relation kind, missing required fields
- `harmonic_affinity("D#", "E")` returns a value near the "minor 2nd / strong tension" range
- `harmonic_affinity("D#", "B")` returns a value near the "minor 6th / melancholy" range
- Same seed produces same WorldState

### What NOT to do

- Do not implement layers (genesis, theogony, chronica, contempo, existence) yet
- Do not implement the timeline simulator yet
- Do not implement the CLI console yet
- Do not add any Kilima-specific logic to the Gigagen core — Kilima data lives in worldpack JSON files only
- Do not use heavy dependencies. Pydantic v2 + standard library only.

### File structure

```
D:\Gigagen_Kilima\
├── docs/           (already populated — READ THESE)
├── src/
│   └── gigagen/
│       ├── __init__.py
│       └── core/
│           ├── __init__.py
│           ├── entity.py
│           ├── relation.py
│           └── world_state.py
├── worlds/
│   └── kilima/     (already populated — VALIDATE AGAINST THESE)
├── tests/
│   └── test_models.py
└── outputs/
```

### Success criteria

When you're done, I should be able to run `pytest tests/` and see all tests pass. The models should load every JSON in `worlds/kilima/` without error. The harmonic affinity function should return musically correct values. And no Kilima data should be hardcoded in any Gigagen source file.
