# Patch Roadmap — Location & Faction System Integration

> This is the master roadmap for the next major code patch.
> Locations and Factions are being implemented TOGETHER as a single integrated system.
> This document lives in docs/ root so Claude Code reads it first.

---

## Why one patch, not two

Factions and Locations are harmonically coupled. A faction's mode projects onto a location's tonic to create a modal influence. A character's affinity to a location depends on which faction controls it. You can't implement one without the other — they're two sides of the same harmonic coin.

---

## What exists now (pre-patch)

### In code
- `entity.py`: Faction model has `doctrine_tags`, `power`, `cohesion`, `leader_id`. No harmonic fields.
- `entity.py`: Location model has `zone_level`, `biome_tags`, `controlling_faction_id`, `tension`, `access`. No tonic.
- `relation.py`: Relation model supports faction-location bonds (`based_in`, `controls`, etc.)
- `simulator.py`: Moves characters between locations. Changes factions via `set_factions`. No harmonic calculations.
- No Subdivision model exists.

### In data
- `factions.json`: UPDATED — 10 factions with mode, intervals, note_count, scale_family, subdivisions.
- `characters.json`: UPDATED — all 12 characters assigned to new factions.
- `relations.json`: UPDATED — faction IDs corrected. No fac.ai.
- `locations.json`: OUTDATED — still uses old faction IDs, no tonic notes.

### In docs
- `gigagen/gigagen_faction_system.md`: Generic faction/harmonic engine. DONE.
- `gigagen/gigagen_location_system.md`: Generic location/harmonic engine. DONE.
- `kilima/kilima_factions.md`: 10 factions with subdivisions, character assignments. DONE.
- `kilima/kilima_locations.md`: Locations with faction control, character bonds. DONE (tonics pending).

---

## Patch phases

### Phase 1 — Data model updates

**Goal:** Entity models reflect the harmonic system. No simulation changes yet.

#### 1.1 Update Faction model in entity.py

Add to identity (fixed):
```python
mode: str                    # e.g. "ionian", "phrygian", "whole_tone"
intervals: list[int]         # e.g. [2,2,1,2,2,2,1]
note_count: int              # derived from len(intervals)
scale_family: str            # "greek" | "symmetric" | "pentatonic"
```

Keep existing state fields (`status`, `power`, `cohesion`, `leader_id`).
Remove or deprecate `doctrine_tags` (replaced by mode-based identity).

#### 1.2 Create Subdivision model in entity.py

New entity type or nested model:
```python
class Subdivision:
    id: str                          # e.g. "sub.direnis_cell"
    name: str
    parent_faction_id: str
    root_note: str | None            # leader's archetype note
    leader_id: str | None
    location_id: str | None          # base location
```

Decision: Is Subdivision a full entity (in WorldState.entities) or a nested object inside Faction? Recommendation: nested inside Faction for now, promote to entity later if needed.

#### 1.3 Update Location model in entity.py

Add to identity (fixed):
```python
tonic: str | None                    # harmonic tonic note (from founding lineage)
parent_location_id: str | None       # hierarchy — which location contains this one
```

Add to state:
```python
secondary_faction_ids: list[str]     # for disputed locations
```

Keep existing fields (`zone_level`, `biome_tags`, `controlling_faction_id`, `tension`, `access`, `status`).

#### 1.4 Update locations.json

- Add `tonic` field to all locations (null for now, filled in Phase 3 or later).
- Add `parent_location_id` for hierarchy.
- Update `controlling_faction_id` to new faction IDs.
- Add `secondary_faction_ids: []` for all.

#### 1.5 Tests

- Validate all 10 factions load correctly with new fields.
- Validate subdivisions load and reference valid factions/characters/locations.
- Validate locations load with new fields.
- Cross-reference: every `controlling_faction_id` in locations.json exists in factions.json.
- Cross-reference: every `leader_id` in subdivisions exists in characters.json.
- Cross-reference: every `location_id` in subdivisions exists in locations.json.

---

### Phase 2 — Harmonic engine

**Goal:** Pure functions that calculate harmonic relationships. No simulation side effects.

#### 2.1 Scale generation

```python
def build_scale(root_note: str, intervals: list[int]) -> list[str]
```

Already partially exists in concept. Formalize and test.

#### 2.2 Character-faction affinity

```python
def character_faction_affinity(
    character_note: str, 
    faction_intervals: list[int], 
    subdivision_root: str
) -> float
```

Does the character's note fall in the subdivision's scale? Returns affinity score.

#### 2.3 Character-location affinity

```python
def character_location_affinity(
    character_note: str,
    location_tonic: str | None,
    controlling_faction_intervals: list[int] | None,
    structural_weight: float = 0.3,
    modal_weight: float = 0.7
) -> float
```

Combined structural (note vs tonic) + modal (note vs location scale) affinity.

#### 2.4 Dual membership cost

```python
def dual_membership_cost(
    faction_a_intervals: list[int],
    sub_a_root: str,
    faction_b_intervals: list[int],
    sub_b_root: str
) -> float
```

Scale overlap between two factions from their subdivision roots.

#### 2.5 Location instability

```python
def location_instability(
    location_tonic: str,
    faction_modes: list[list[int]]
) -> float
```

For disputed locations. Measures overlap between stacked faction scales.

#### 2.6 Subdivision weight

```python
def subdivision_weight(
    subdivision_root: str,
    other_roots: list[str]
) -> float
```

Consonance of a subdivision's root relative to other subdivisions in the same faction.

#### 2.7 Faction compatibility

```python
def faction_compatibility(
    intervals_a: list[int],
    intervals_b: list[int]
) -> float
```

How similar are two factions' modes? Interval pattern comparison (no root needed).

#### 2.8 Tests

- Unit tests for every function above.
- Edge cases: null tonics, empty interval lists, whole tone symmetry, pentatonic gaps.
- Verify known Kilima relationships produce expected results (e.g. Kive D# in Phrygian scale).

---

### Phase 3 — Kilima data completion

**Goal:** Fill in all the blanks in the worldpack data.

#### 3.1 Assign tonic notes to key locations

Requires decision session (author). Strategy: founding lineage → location tonic.
At minimum, assign tonics to the 15 Act 1 locations.

#### 3.2 Update locations.json with tonics

Fill `tonic` field for all assigned locations.

#### 3.3 Update locations.json with hierarchy

Fill `parent_location_id` for all child locations.

#### 3.4 Verify faction-location consonance

Run harmonic functions on the assigned data. Check that the results make narrative sense:
- Anti Group should feel natural in The Cave.
- Agency SL should feel natural in The Tower.
- The City should be harmonically disputed.

#### 3.5 Tests

- Data integrity: every tonic is a valid note.
- Hierarchy: no circular parent references.
- Narrative validation: spot-check affinity scores against lore expectations.

---

### Phase 4 — Simulator integration

**Goal:** The simulator uses harmonic data during event processing. Events and locations are tightly coupled — every event happens somewhere, and that somewhere now has harmonic consequences.

#### 4.1 Events must reference locations

Every event in the timeline (bn1.yaml) has a `location` field. The simulator must resolve this to a location entity with tonic + controlling faction. Events that currently use raw location strings need to map to `loc.*` IDs so the harmonic system can engage.

#### 4.2 Character movement triggers affinity calculation

When an event moves a character to a location, calculate their affinity on arrival. Store as a modifier on the character's state. This affects:
- Detection risk (low affinity in enemy territory = easier to spot)
- Emotional load (entering a dissonant location adds stress)
- Action effectiveness (high affinity = home advantage)

#### 4.3 Events that change location control

Some events change which faction controls a location. The most critical in NB1:
- **H52-H56: Army invades The Cave** — Guard Force takes Anti Group's base. Modal influence shifts from Phrygian to Dorian. Every character in The Cave feels the harmonic shift.
- **H16: Kive declares war** — The Forno becomes openly Anti Group. Modal influence crystallizes.
- **H18: Saarah breaks with Union Corp** — La Sede loses a leader. Cohesion impact.
- **H20: Luka turns** — The Tower loses a Council member. Faction composition changes.

When control changes: recalculate modal influence → recalculate affinity for all characters present → update location tension → log harmonic shift as event metadata.

#### 4.4 Faction control changes trigger recalculation

When `set_factions` or conquest events fire, recalculate modal influence for affected locations and all characters present.

#### 4.5 Cohesion affected by harmonic fit

Faction cohesion in a location is modified by tonic-faction consonance. Occupying territory that doesn't fit your scale lowers cohesion there.

#### 4.6 Disputed locations generate instability events

Locations with multiple faction influences have instability scores. High instability → higher probability of conflict events.

#### 4.7 Event log enrichment

Each event log entry should include:
- `location_id`: where it happened
- `location_tonic`: the tonic of that location
- `modal_influence`: which faction's mode was active
- `character_affinities`: dict of character_id → affinity score at that location
- This data is derived, not stored in the timeline — calculated at simulation time.

#### 4.8 Timeline-location mapping

`bn1.yaml` uses location names that don't always match `loc.*` IDs. The `timeline_maps.json` needs a complete location mapping so every event resolves to a harmonically-active location entity.

#### 4.9 Tests

- Simulate NB1 timeline with harmonic data active.
- Verify no regression in existing 103 tests.
- New tests: character affinity changes when location control changes.
- New tests: cohesion impact from harmonic mismatch.
- New tests: Cave invasion (H52-H56) triggers modal shift from Phrygian to Dorian.
- New tests: every event in bn1.yaml resolves to a valid location ID.

---

### Phase 5 — Console/TUI updates

**Goal:** The user interface shows harmonic information.

- Display faction mode and scale family in faction info.
- Display subdivision root notes.
- Display location tonic and current modal influence.
- Display character affinity to current location.
- Color-code or tag consonant vs dissonant relationships.

---

## Dependencies

```
Phase 1 (data models) → Phase 2 (harmonic engine) → Phase 3 (Kilima data)
                                                   → Phase 4 (simulator)
                                                   → Phase 5 (UI)
```

Phase 2 and Phase 3 can run in parallel once Phase 1 is complete.
Phase 4 depends on both Phase 2 and Phase 3.
Phase 5 depends on Phase 4.

---

## Success criteria

- All 10 factions load with harmonic data.
- All subdivisions reference valid entities.
- All locations have faction control with new IDs.
- Key locations have tonic notes assigned.
- Harmonic functions produce correct, tested results.
- Simulator uses harmonic data without breaking existing tests.
- A dev can run `python -m gigagen` and see harmonic info in the console.

---

## Files touched

### New files
- `src/gigagen/core/harmony.py` — all harmonic functions (Phase 2)
- `tests/test_harmony.py` — harmonic function tests

### Modified files
- `src/gigagen/core/entity.py` — Faction + Location + Subdivision models
- `worlds/kilima/factions.json` — already updated, may need subdivision tweaks
- `worlds/kilima/locations.json` — needs full rewrite (new fields, new faction IDs)
- `worlds/kilima/relations.json` — already updated
- `worlds/kilima/characters.json` — already updated
- `src/gigagen/core/simulator.py` — Phase 4 integration
- `src/gigagen/io/load_worldpack.py` — load new fields
- `src/gigagen/cli/` — Phase 5 UI updates
- `tests/test_data_integrity.py` — new cross-reference checks
