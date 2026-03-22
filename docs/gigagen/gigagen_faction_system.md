# Faction System — Gigagen Engine

> Generic faction and harmonic system for Gigagen.
> This document defines the ENGINE. Worldpack-specific assignments live in worldpack docs (e.g. kilima_factions.md).

---

## Core Concept

A faction is a **subset of the 12 chromatic notes**. Nothing more.

The chromatic scale (all 12 notes) is the "null faction" — no filtering, everything included. Defining a faction means **removing notes** from the chromatic set. The pattern of intervals left behind identifies the faction's harmonic character automatically.

```
Chromatic (12 notes):  C C# D D# E F F# G G# A A# B
Remove 5, keep 7:     → Greek mode (Ionian, Dorian, Phrygian, etc.)
Remove 6, keep 6:     → Whole tone, hexatonic, etc.
Remove 7, keep 5:     → Pentatonic (major, minor, etc.)
Remove 0, keep 12:    → Chromatic (omnipresent, no filter)
```

The engine does not know what a "Union Corp" or a "Cult Order" is. It only sees note sets and calculates relationships between them.

---

## Scale Families

Factions are grouped by how many notes they retain. This is their **scale family**.

| Family | Notes kept | Notes removed | Character | Examples |
|--------|-----------|---------------|-----------|----------|
| 7-note | 7 | 5 | Full harmonic color, rich | Greek modes |
| 6-note | 6 | 6 | Symmetric, ambiguous | Whole tone, augmented |
| 5-note | 5 | 7 | Simple, gapped, selective | Pentatonic major/minor |
| 12-note | 12 | 0 | Omnipresent, no filter | Chromatic |

Factions within the same family are **cousins** — they share structural properties even if their interval patterns differ.

A dev building a worldpack can use any combination of families. A world with 4 pentatonic factions is valid. A world with 12 chromatic factions (all identical) is technically valid but useless. The engine doesn't judge.

---

## Faction Definition (Data Model)

A faction in Gigagen is defined by:

```yaml
faction:
  id: string              # e.g. "fac.union_corp"
  name: string            # Display name
  mode: string            # Mode identifier (e.g. "ionian", "whole_tone", "pentatonic_major")
  intervals: list[int]    # Interval pattern in semitones (e.g. [2,2,1,2,2,2,1])
  note_count: int         # Derived: len(intervals)
  # Identity — does not change
  # All other attributes (base_location, leader, etc.) are worldpack-specific
```

The faction does NOT have a tonic/root note. The tonic belongs to **subdivisions**, not the faction itself. The faction is a **mode** — a pattern of intervals that can be applied from any root.

---

## Subdivision Definition

A subdivision is a concrete instantiation of a faction's mode from a specific root note:

```yaml
subdivision:
  id: string                    # e.g. "sub.direnis_cell"
  name: string                  # Display name
  parent_faction_id: string     # Which faction this belongs to
  root_note: string             # The tonic — typically the leader's archetype note
  leader_id: string | null      # Character who leads this subdivision
  location_id: string | null    # Where this subdivision is based
  # The scale is CALCULATED: apply parent faction's intervals from root_note
```

**Key rule**: the root note of a subdivision = the note of its leader's archetype. When leadership changes, the subdivision's harmonic center shifts.

---

## Harmonic Functions

### 1. Generate scale

```
faction_scale(root_note, intervals) → list[str]
```

Apply the faction's interval pattern starting from a given root. Returns the concrete notes in the scale.

Example: Phrygian intervals `[1,2,2,2,1,2,2]` from root B → `[B, C, D, E, F, G, A]`

### 2. Character-faction affinity

```
character_affinity(character_note, faction_intervals, subdivision_root) → float
```

Does the character's note fall inside the subdivision's scale?

- **In scale**: base affinity = positive (0.5 to 1.0, depending on consonance with root)
- **Out of scale**: base affinity = negative (-0.5 to -1.0, depending on dissonance)
- **Unison with root**: maximum affinity (1.0)
- **Tritone from root**: maximum tension (-1.0)

The interval between the character's note and the subdivision root determines the specific value, using the same interval-to-affinity table already defined in ontology.md for character-character relationships.

### 3. Dual membership cost

```
dual_membership_cost(faction_a_intervals, sub_a_root, faction_b_intervals, sub_b_root) → float
```

How much tension does it create to belong to two factions simultaneously?

Calculated by comparing the two scales:
- **High overlap** (many shared notes): low cost, comfortable dual membership
- **Low overlap** (few shared notes): high cost, constant friction
- **Subset** (one scale contained in the other): very low cost

A character in two factions with 6/7 notes in common barely feels it. A character in two factions with 2/7 notes in common is being torn apart.

### 4. Subdivision weight

```
subdivision_weight(subdivision_root, faction_mode, other_subdivision_roots) → float
```

How much political weight does a subdivision carry within its faction?

Based on the consonance of the subdivision's root note relative to other subdivisions in the same faction. A subdivision whose root forms a perfect fifth (7 semitones) with the most subdivisions is the political center. A subdivision whose root forms tritones with others is the outlier.

### 5. Inter-faction compatibility

```
faction_compatibility(intervals_a, intervals_b) → float
```

How similar are two factions' modes? Calculated by comparing their interval patterns directly (no root needed, since factions don't have tonics).

- **Identical intervals shifted**: maximum compatibility (e.g. Ionian vs Ionian = same faction family)
- **Differ by 1 interval**: close (e.g. Ionian vs Mixolydian — only the 7th degree differs)
- **Differ by many intervals**: distant (e.g. Ionian vs Locrian — almost opposite)

This gives the **structural** political relationship between factions, independent of which characters are in them.

---

## Membership Rules

### Single membership
A character belongs to one faction with one role (member, leader, infiltrated, allied, opposed).

### Dual membership
A character can belong to two factions simultaneously. The system calculates:
1. Affinity with each faction (how well their note fits each scale)
2. Cost of dual membership (how different the two factions are)
3. Primary vs secondary: the faction where affinity is higher is primary

### Membership changes
When a character changes faction (e.g. desertion), the system recalculates:
- Their affinity with the new faction
- Impact on the old faction's cohesion (losing a consonant member hurts more)
- Impact on the new faction's cohesion (gaining a dissonant member creates tension)

---

## Implementation Notes

### For the engine (Gigagen core)
- Factions are note sets. No names, no lore, no politics.
- All harmonic functions work with intervals and note names only.
- The engine provides: scale generation, affinity calculation, compatibility scores.
- The engine does NOT provide: narrative interpretation, event triggers, political consequences.

### For worldpacks
- Worldpacks assign meaning to factions: names, lore, locations, characters.
- Worldpacks define which modes to use and how many factions exist.
- Worldpacks can use any combination of scale families.
- The standard configuration removes 5 notes (keeping 7) for Greek modes, but this is a worldpack choice, not an engine constraint.

### For the simulator
- Faction affinity feeds into relationship weight calculations.
- Cohesion changes when members join/leave/die.
- Dual membership cost feeds into desertion probability.
- Subdivision weight feeds into internal faction politics.

---

## Reserved / Future

The engine supports any interval pattern. Some patterns not yet used in any worldpack:

| Pattern | Notes | Name | Potential use |
|---------|-------|------|---------------|
| 2-1-2-2-1-3-1 | 7 | Harmonic minor | Dramatic, exotic factions |
| 1-3-1-2-1-2-2 | 7 | Phrygian dominant | Oppressive, sinister factions |
| 1-1-1-1-1-1-1-1-1-1-1-1 | 12 | Chromatic | Omnipresent entities |
| 2-1-2-1-2-1-2-1 | 8 | Octatonic/diminished | Unstable, shifting factions |
| 3-1-1-3-1-1-2 | 7 | Hungarian minor | Exotic, isolated factions |

The engine accepts any `intervals` list. If a dev invents a new scale, it works.
