# Faction System — Implementation Roadmap

> Roadmap for implementing the harmonic faction system.
> Part of the Location & Faction patch. See PATCH_ROADMAP.md for the integrated plan.
> Engine docs: gigagen/gigagen_faction_system.md
> Kilima data: kilima/kilima_factions.md

---

## Current state

### What works
- 10 factions defined with modes, intervals, subdivisions in kilima_factions.md.
- `factions.json` updated with all 10 factions and harmonic fields.
- `characters.json` updated with correct faction assignments.
- `relations.json` updated with new faction IDs.
- 12 character-faction assignments documented and in data.

### What's broken or missing
- Faction model in `entity.py` has no harmonic fields (mode, intervals, note_count, scale_family).
- No Subdivision model exists in code.
- No harmonic functions exist (scale generation, affinity, compatibility).
- Simulator doesn't use harmonic data — faction changes are event-driven only, no harmonic consequences.
- `load_worldpack.py` doesn't load subdivision data from factions.json.
- Tests don't validate harmonic fields.
- `worlds/kilima/factions.json` may diverge from `docs/kilima/data/factions.json` — need to sync.

---

## Tasks

### Data model (Phase 1 of patch)

- [ ] Add to Faction model: `mode`, `intervals`, `note_count`, `scale_family`
- [ ] Create Subdivision model (nested in Faction or standalone)
- [ ] Decide: keep `doctrine_tags` alongside new fields or deprecate?
- [ ] Decide: keep `power` and `cohesion` as manual values or derive from harmonic data?

### Worldpack loader update (Phase 1)

- [ ] `load_worldpack.py` reads new faction fields from factions.json
- [ ] `load_worldpack.py` loads subdivisions as nested objects
- [ ] `load_worldpack.py` validates: every subdivision leader_id exists, every location_id exists

### Harmonic engine (Phase 2)

- [ ] `build_scale(root, intervals)` — generate scale from any root + mode
- [ ] `character_faction_affinity(char_note, faction_intervals, sub_root)` — does note fit in scale?
- [ ] `dual_membership_cost(faction_a, sub_a_root, faction_b, sub_b_root)` — scale overlap
- [ ] `subdivision_weight(sub_root, other_roots)` — political weight within faction
- [ ] `faction_compatibility(intervals_a, intervals_b)` — structural similarity between modes

### Kilima data completion (Phase 3)

- [ ] Name for Anti Group's Forno cell
- [ ] Leader for Forno cell (secondary character — note determines subdivision root)
- [ ] Name for Amparo Foundation's refuge subdivision
- [ ] Cult Order: finalize 2 remaining subdivisions (supernatural research + spiritual movement)
- [ ] Subdivisions for Kilima Lines
- [ ] Subdivisions for Kilima Mail
- [ ] Leaders for all TBD subdivisions (secondary characters, each with archetype note)
- [ ] Root notes for Agency SL subdivisions (pending leader assignments)
- [ ] Len's specific subdivision within Agency SL

### Simulator integration (Phase 4)

- [ ] When character changes faction → calculate affinity with new faction
- [ ] When character changes faction → impact on old faction's cohesion
- [ ] When character changes faction → impact on new faction's cohesion
- [ ] Dual membership cost calculated for characters in 2 factions (Len, Freya)
- [ ] Luka's desertion at H20 → harmonic consequences computed

### Event-Faction integration (Phase 4 — critical)

Events that change faction state must trigger harmonic recalculations:
- [ ] H16: Kive declares war → Anti Group's modal influence solidifies in The Forno
- [ ] H18: Saarah breaks with Union Corp → cohesion loss in Interior ministry, location modal shift at La Sede
- [ ] H20: Luka turns → Agency SL loses D note from Master Council, Anti Group gains it. Faction composition changes → affinity recalculation for all characters in both factions
- [ ] H20: Brais dies → Guard Force loses G# from Arena Corps. Brais-automaton inherits the note but in a different faction context
- [ ] H52-H56: Cave invasion → Guard Force projects Dorian onto Cave's tonic, replacing Anti Group's Phrygian. Every character present recalculates modal affinity
- [ ] All faction change events (`set_factions` in event_rules.json) must propagate to: character affinities, location modal influences, faction cohesion scores

### Console/TUI (Phase 5)

- [ ] Show faction mode and scale family
- [ ] Show subdivision list per faction
- [ ] Show character affinity to current faction
- [ ] Show dual membership cost for multi-faction characters

---

## Decisions needed from author

1. Keep `doctrine_tags` or replace with mode-based identity?
2. Keep `power`/`cohesion` as manual or derive from harmonic composition?
3. Subdivision as full entity in WorldState or nested in Faction?
4. Forno cell name and leader (secondary character)
5. Amparo Foundation refuge subdivision name
6. Cult Order remaining 2 subdivisions
7. Kilima Lines subdivisions
8. Kilima Mail subdivisions
9. Brais subdivision confirmation — Wall Command, Arena Corps, or other?

---

## Sync check

Before starting implementation, verify these files are consistent:

```
docs/kilima/data/factions.json  ←→  worlds/kilima/factions.json
docs/kilima/data/characters.json ←→ worlds/kilima/characters.json
docs/kilima/data/relations.json  ←→  worlds/kilima/relations.json
```

If they diverge, `docs/kilima/data/` is the source of truth (updated in this session).
Copy to `worlds/kilima/` before starting code work.
