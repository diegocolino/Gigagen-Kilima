# Roadmap — Gigagen / Kilima

> Concrete milestones. No smoke.

---

## Current state

- Clean start (previous code discarded)
- Context documentation in `docs/` — reviewed and updated
- Ontological models defined conceptually
- Kilima worldpack defined conceptually
- **NB1 fully defined** — 62-hour timeline, 12 characters, ~30 events, 3 variables, lore, relationships (see `kilima_timeline_bn1.yaml` v5.0)
- **Nothing programmed yet**

---

## Milestone 1 — Canonical models in code ✱ NEXT

**Goal:** Data models implemented and validatable.

**Deliverables:**
- [ ] `src/gigagen/core/entity.py` — BaseEntity + Character, Faction, Location, Item, Anima
- [ ] `src/gigagen/core/relation.py` — Relation as first-class object
- [ ] `src/gigagen/core/world_state.py` — WorldState
- [ ] Minimal validation tests

**Stack:** Python 3.11+ with Pydantic v2

**Success criteria:** Can instantiate a Character, a Relation, and a WorldState without error. Validation rejects malformed data.

---

## Milestone 2 — Kilima worldpack in JSON

**Goal:** Canonical Kilima data ready to load.

**Deliverables:**
- [ ] `worlds/kilima/world.json` — Worldpack metadata
- [ ] `worlds/kilima/characters.json` — The 12 principals (with hero types)
- [ ] `worlds/kilima/factions.json` — 4 factions (with corrected leadership)
- [ ] `worlds/kilima/locations.json` — Locations (including The Limbo, The Forno)
- [ ] `worlds/kilima/relations.json` — 15-25 core relations (updated with all NB1 discoveries)
- [ ] `worlds/kilima/invariants.json` — Rules of what cannot break
- [ ] `worlds/kilima/timelines/bn1.yaml` — The 62-hour NB1 master file (already done: v5.0)

**Success criteria:** JSONs validate against Pydantic models without error.

---

## Milestone 3 — Loader, world_state, and interactive console

**Goal:** Gigagen loads Kilima, builds a valid world_state, displays it in an interactive console.

**Deliverables:**
- [ ] `src/gigagen/io/load_worldpack.py` — Reads worldpack JSONs + YAML timelines
- [ ] `src/gigagen/io/export_world_state.py` — Exports world_state.json
- [ ] `src/gigagen/cli/console.py` — Interactive terminal loop
- [ ] First `outputs/kilima_seed_001.json` generated

**Minimal console commands:**
```
show world          → world state summary
list characters     → the 12 with status
list factions       → factions with state
list locations      → locations with state
inspect char.rebel  → full character detail + relations
inspect rel.*       → relations of an entity
export              → export world_state.json
quit                → exit
```

**Success criteria:**
1. Clean separation (no Kilima data hardcoded in Gigagen)
2. Identity and state clearly separated on entities
3. Relations as first-class citizens
4. Reproducible export (same seed = same output)
5. Can load Kilima and see the world in terminal legibly

---

## Milestone 4 — Seed with controlled variation

**Goal:** Different seeds produce different valid states of Kilima.

**Deliverables:**
- [ ] Seed logic that varies seeded fields without touching fixed
- [ ] Validation against invariants.json
- [ ] Visible comparison between seed 1 and seed 2
- [ ] The 3 NB1 variables (VAR_DEV, VAR_BRAIS, VAR_ENDING) resolved per seed

**Success criteria:** Two seeds produce different states but both respect all invariants.

---

## Milestone 5 — Temporal simulation (the 62-hour NB1)

**Goal:** The console advances through the 62-hour NB1 timeline, step by step.

**Data source:** `kilima_timeline_bn1.yaml` (v5.0)

**Deliverables:**
- [ ] Command `advance` / `advance N` — advance N hours
- [ ] Command `hour` — show current hour and active events
- [ ] Command `outcomes` — show dramatic states of the 12
- [ ] Minimal event log
- [ ] Outcome variables: life_state, bond_state, political_alignment, location
- [ ] Minimal transition rules (what can change per hour step)
- [ ] Cohesion score tracking
- [ ] Variable resolution at correct hours (E07B at H16, E09 at H35, E24 at H62)

**Success criteria:** Can load Kilima, advance hour by hour through the 62-hour NB1, see character states change, variables resolve, and outcomes emerge — all without breaking invariants.

---

## Future milestones (DO NOT implement yet)

- **Milestone 6:** Chronica (past with real consequences feeding into NB1)
- **Milestone 7:** Strong Contempo (complete visible present)
- **Milestone 8:** Animas and elements system
- **Milestone 9:** Hero arc tracking (map events to arc steps, detect trigger chains)
- **Milestone 10:** Topological viewer in Godot (level 1: map + points + colors)
- **Milestone 11:** Gameplay (archetype selection, player intervention)

---

## Advancement rule

No milestone starts until the previous one is closed and validated.

Each milestone must be:
- Programmable
- Verifiable
- Ontology-respecting
- Free of arbitrariness

---

## File structure (updated)

```
D:\Gigagen_Kilima\
├── docs/
│   ├── CLAUDE.md                  # Master context
│   ├── ontology.md                # Formal data models
│   ├── kilima_bible.md            # INDEX pointing to all kilima_ files
│   ├── kilima_lore.md             # World background, ether, elements, etc.
│   ├── kilima_characters.md       # The 12 principals
│   ├── kilima_locations.md        # All locations
│   ├── kilima_factions.md         # The 4 factions
│   ├── kilima_hero_rebel.md       # Hero arc: Tragic hero (Kive)
│   ├── kilima_hero_orphan.md      # Hero arc: Mythological hero (Len)
│   ├── kilima_hero_hacker.md      # Hero arc: Action hero (Dev)
│   ├── kilima_hero_leader.md      # Hero arc: Anti-villain (Saarah)
│   ├── kilima_hero_creator.md     # Hero arc: Urban hero (Cris)
│   ├── kilima_hero_innocent.md    # Hero arc: Redemption hero (Brais)
│   ├── kilima_hero_lover.md       # Hero arc: Romantic hero (Ali)
│   ├── kilima_hero_jester.md      # Hero arc: Fantasy hero (Pau)
│   ├── kilima_hero_hero.md        # Hero arc: Archetypal hero (Luka)
│   ├── kilima_hero_explorer.md    # Hero arc: Post-apocalyptic (Yeri)
│   ├── kilima_hero_caregiver.md   # Hero arc: Protector hero (Nora)
│   ├── kilima_hero_deity.md       # Hero arc: Criminal hero (Freya)
│   ├── invariants.md              # Fixed / seeded / derived / forbidden
│   └── roadmap.md                 # This file
├── src/
│   └── gigagen/
│       ├── core/
│       │   ├── entity.py
│       │   ├── relation.py
│       │   └── world_state.py
│       ├── catalogs/
│       │   ├── archetypes.json
│       │   ├── notes.json
│       │   ├── elements.json
│       │   └── relation_types.json
│       ├── layers/
│       │   ├── genesis.py
│       │   ├── theogony.py
│       │   ├── chronica.py
│       │   ├── contempo.py
│       │   └── existence.py
│       └── io/
│           ├── load_worldpack.py
│           └── export_world_state.py
├── worlds/
│   └── kilima/
│       ├── world.json
│       ├── characters.json
│       ├── factions.json
│       ├── locations.json
│       ├── relations.json
│       ├── invariants.json
│       └── timelines/
│           └── bn1.yaml           # ← The 62-hour NB1 master (v5.0)
└── outputs/
```
