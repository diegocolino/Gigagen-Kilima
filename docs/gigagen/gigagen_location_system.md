# Location System — Gigagen Engine

> Generic location system for Gigagen with harmonic integration.
> This document defines the ENGINE. Worldpack-specific locations live in worldpack docs.
> Depends on: gigagen_faction_system.md, gigagen_ontology.md

---

## Core Concept

A location has a **fixed tonic note** — its harmonic identity. This note comes from the location's origin (who built it, who discovered it, what lineage founded it). The tonic never changes. Factions come and go; the land remembers.

A location does NOT have a mode. It has a single note. The modal color of a location comes from the **faction that controls it** — this is the location's **modal influence**.

---

## Modal Influence

When a faction controls a location, the location acquires that faction's mode as an ambient harmonic field. This creates a **location scale**: the faction's intervals applied from the location's tonic note.

```
Location tonic: D
Controlling faction mode: Phrygian [1,2,2,2,1,2,2]
Location scale: D Phrygian → D Eb F G A Bb C
```

Any character in that location is inside this harmonic field. Their note either falls in the location scale (comfort) or outside it (tension).

### Key distinction
- The **location tonic** is identity (fixed, historical, never changes).
- The **modal influence** is state (changes when faction control changes).

This follows the same identity/state separation used in all Gigagen entities.

---

## Tonic-Faction Consonance

The location's tonic note may or may not fall inside the controlling faction's scale (when applied from any of the faction's subdivision roots). This creates a control quality metric:

- **Tonic in faction scale** → natural control. The faction "fits" this territory harmonically. Lower maintenance cost, higher stability.
- **Tonic outside faction scale** → forced control. The faction occupies territory that doesn't sound like them. Higher tension, lower cohesion in that location, easier to lose control.

### Formula

```
control_quality(location_tonic, faction_mode, subdivision_root) → float
```

Apply the faction's mode from the subdivision root. Check if the location's tonic falls in the resulting scale. If yes → high quality. If no → check interval between tonic and nearest scale note for tension degree.

---

## Stacked Influences (Disputed Locations)

A location can be influenced by multiple factions simultaneously. Each faction projects its mode onto the location's tonic, creating overlapping scales.

```
Location tonic: D
Faction A (Ionian): D E F# G A B C# → 7 notes
Faction B (Phrygian): D Eb F G A Bb C → 7 notes
Overlap: D, G, A → only 3 shared notes
Conflict zones: 4 notes where the scales disagree → high instability
```

### Instability calculation

```
location_instability(tonic, faction_a_mode, faction_b_mode) → float
```

The fewer notes the overlapping scales share, the more unstable the location. Maximum instability = 0 shared notes (theoretically impossible with 7-note scales from the same root, but possible with different root-mode combinations).

Stacked influences also affect characters: a character in a disputed location must resolve their note against BOTH scales. A note that falls in both → comfortable anywhere. A note that falls in neither → alien to everyone, maximum vulnerability.

---

## Character-Location Affinity

A character's note interacts with a location in two independent ways:

### 1. Structural affinity (permanent)

The interval between the character's note and the location's tonic. This is the character's "natural" relationship with the place, independent of who controls it.

```
structural_affinity(character_note, location_tonic) → float
```

Uses the same interval-to-affinity table defined in gigagen_ontology.md:
- Unison (0 semitones): this is home ground → 1.0
- Perfect fifth (7 semitones): natural ally → 0.9
- Tritone (6 semitones): maximally alien → -1.0

### 2. Modal affinity (dynamic)

Does the character's note fall in the location's current modal influence (faction mode applied from location tonic)?

```
modal_affinity(character_note, location_tonic, controlling_faction_mode) → float
```

- Note in scale → positive (comfort, integration, invisibility)
- Note outside scale → negative (tension, detection risk, friction)

The controlling faction changes → the modal affinity changes for every character in that location, even though the location itself didn't change and the structural affinity remains the same.

### Combined affinity

```
total_affinity = (structural_weight * structural_affinity) + (modal_weight * modal_affinity)
```

Default weights: structural = 0.3, modal = 0.7. The current power dynamics matter more than ancient history, but ancient history never fully disappears.

---

## Location Hierarchy

Locations can contain other locations (parent-child). A child location inherits the parent's modal influence UNLESS it has its own controlling faction that overrides it.

```
Parent (tonic: C, controlled by Faction A → Ionian)
  ├── Child 1 (tonic: E, controlled by Faction B → Aeolian) ← overrides parent
  ├── Child 2 (tonic: G, no faction override) ← inherits parent's Ionian influence
  └── Child 3 (tonic: F#, disputed by Faction A and C) ← stacked influences
```

### Inheritance rules
- If a child has `controlling_faction_id = null`, it inherits the parent's modal influence.
- If a child has its own controlling faction, that faction's mode overrides the parent's.
- A child can be disputed (multiple factions) even if the parent is stable.
- Zone-level locations (e.g. "The Capital") set the default influence for all children without overrides.

---

## Location Data Model

```yaml
location:
  id: string                          # e.g. "loc.cave"
  name: string
  entity_type: "location"
  
  # Identity (fixed)
  tonic: string | null                # The location's harmonic note (e.g. "B")
  zone_level: string                  # "high" | "mid" | "low" | "external" | "hidden" | "virtual"
  parent_location_id: string | null   # Hierarchy — which location contains this one
  biome_tags: list[str]
  founded_by_lineage: string | null   # Which lineage built/discovered this place (source of tonic)
  
  # State (changes)
  controlling_faction_id: string | null
  secondary_faction_ids: list[str]    # For disputed locations — additional factions with influence
  status: string                      # "stable" | "tense" | "fragile" | "unstable" | "breached" | "besieged"
  tension: float                      # 0.0 to 1.0
  access: string                      # "open" | "restricted" | "sealed" | "clandestine"
  
  # Derived (calculated at runtime)
  # modal_influence → from controlling_faction.mode + self.tonic
  # instability → from overlapping faction scales if disputed
  # character affinities → calculated per character present
```

---

## Harmonic Functions

### 1. Location scale

```
location_scale(location_tonic, controlling_faction_intervals) → list[str]
```

Apply the faction's mode from the location's tonic. Returns the concrete notes of the location's current harmonic field. If no controlling faction → no modal influence (neutral ground).

### 2. Control quality

```
control_quality(location_tonic, faction_intervals, subdivision_root) → float
```

How naturally does this faction control this territory? Based on whether the tonic falls in the faction's scale from its nearest subdivision root.

### 3. Location instability

```
location_instability(location_tonic, list[faction_intervals]) → float
```

For disputed locations. Measures overlap between the scales of all factions projecting influence. Less overlap → more instability.

### 4. Character structural affinity

```
structural_affinity(character_note, location_tonic) → float
```

Permanent relationship between character and place. Interval-based.

### 5. Character modal affinity

```
modal_affinity(character_note, location_scale) → float
```

Current comfort level. Does the character's note fall in the active scale?

### 6. Character total affinity

```
total_location_affinity(character_note, location_tonic, controlling_faction_intervals, weights) → float
```

Combined structural + modal affinity.

---

## Simulation Implications

- **Movement:** Characters naturally drift toward high-affinity locations. Low affinity = higher cost to stay, higher detection risk.
- **Conquest:** Faction takes a location → modal influence changes → all characters' modal affinities recalculate → some become comfortable, others become tense.
- **Territory defense:** Locations whose tonic fits the controlling faction's scale are easier to defend. Mismatched tonics = structural weakness.
- **Disputed zones:** Multiple modal influences create instability. Characters in disputed zones resolve against multiple scales simultaneously.
- **Safe houses:** A location with no controlling faction has no modal influence. Only structural affinity matters. Neutral ground.

---

## Implementation Notes

### For the engine (Gigagen core)
- Locations are tonic notes with optional modal overlays from factions.
- All harmonic functions work with notes, intervals, and scales.
- The engine provides: scale generation, affinity calculation, instability scores.
- The engine does NOT provide: narrative interpretation of why a location has a specific tonic.

### For worldpacks
- Worldpacks assign tonic notes based on lore (founding lineages, narrative need, etc.).
- Worldpacks define the parent-child hierarchy.
- Worldpacks can leave tonic as null for locations without harmonic identity (purely functional spaces).
- Not every location needs a tonic — minor/background locations can be harmonically neutral.

### For the simulator
- Location modal influence feeds into character comfort calculations.
- Faction conquest events trigger modal influence recalculation.
- Location instability feeds into event probability (unstable locations generate more events).
- Character affinity to current location affects detection, escape, and social interaction probabilities.
