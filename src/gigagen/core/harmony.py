"""Harmonic engine — pure functions for musical-relational calculations.

All functions operate on notes (str) and intervals (list[int]).
No faction names, no worldpack-specific data. The engine doesn't know
what "Anti Group" or "Phrygian" means — it only knows note sets.

The universal foundation is `harmonic_affinity(note_a, note_b)` from
relation.py. Functions here add scale-aware context on top of it.
"""

from __future__ import annotations

from .relation import _NOTE_TO_SEMITONE, harmonic_affinity

# Canonical note names in chromatic order
CHROMATIC_NOTES: list[str] = [
    "C", "C#", "D", "D#", "E", "F",
    "F#", "G", "G#", "A", "A#", "B",
]


def _note_to_semitone(note: str) -> int:
    """Convert a note name to its semitone index (0-11)."""
    val = _NOTE_TO_SEMITONE.get(note)
    if val is None:
        raise ValueError(f"Unknown note: '{note}'")
    return val


def _semitone_to_note(semitone: int) -> str:
    """Convert a semitone index (0-11) to its canonical note name."""
    return CHROMATIC_NOTES[semitone % 12]


# ---------------------------------------------------------------------------
# Scale generation
# ---------------------------------------------------------------------------

def build_scale(root_note: str, intervals: list[int]) -> list[str]:
    """Build a scale from a root note and interval pattern.

    Example: build_scale("B", [1,2,2,2,1,2,2]) → ["B","C","D","E","F#","G","A"]
    (Phrygian from B)

    Returns a list of note names with length == len(intervals).
    """
    if not intervals:
        return []
    root = _note_to_semitone(root_note)
    notes: list[str] = [_semitone_to_note(root)]
    current = root
    for i in intervals[:-1]:  # last interval returns to root, skip it
        current = (current + i) % 12
        notes.append(_semitone_to_note(current))
    return notes


# ---------------------------------------------------------------------------
# Character-faction affinity
# ---------------------------------------------------------------------------

def character_faction_affinity(
    character_note: str,
    macro_faction_intervals: list[int],
    faction_root: str | None,
) -> float:
    """Calculate a character's affinity with a faction.

    Uses harmonic_affinity(char, root) as base, then applies a bonus if
    the character's note falls inside the faction's scale, or a penalty
    if outside.

    Returns a float in [-1.0, 1.0]. Returns 0.0 if faction_root is None.
    """
    if faction_root is None or not macro_faction_intervals:
        return 0.0

    base = harmonic_affinity(character_note, faction_root)
    in_scale = character_note in build_scale(faction_root, macro_faction_intervals)

    if in_scale:
        return min(1.0, base + 0.2) if base >= 0 else base * 0.5
    else:
        return max(-1.0, base - 0.2) if base <= 0 else base * 0.5


# ---------------------------------------------------------------------------
# Character-location affinity
# ---------------------------------------------------------------------------

def character_location_affinity(
    character_note: str,
    location_tonic: str | None,
    controlling_macro_faction_intervals: list[int] | None,
    structural_weight: float = 0.3,
    modal_weight: float = 0.7,
) -> float | None:
    """Calculate a character's total affinity with a location.

    Combined structural (harmonic_affinity vs tonic) + modal (in/out of scale).

    Returns None if location has no tonic (no harmonic calculation possible).
    Returns float in [-1.0, 1.0] otherwise.
    """
    if location_tonic is None:
        return None

    structural = harmonic_affinity(character_note, location_tonic)

    if not controlling_macro_faction_intervals:
        return structural

    scale = build_scale(location_tonic, controlling_macro_faction_intervals)
    modal = 0.5 if character_note in scale else -0.5

    return max(-1.0, min(1.0,
        structural_weight * structural + modal_weight * modal
    ))


# ---------------------------------------------------------------------------
# Location instability
# ---------------------------------------------------------------------------

def location_instability(
    location_tonic: str | None,
    macro_faction_intervals_list: list[list[int]],
) -> float:
    """Calculate instability for a disputed location.

    Measures overlap between stacked faction scales projected from the
    location's tonic. Less overlap → more instability.

    Returns 0.0 for stable (single/no faction) or no tonic.
    Returns float in [0.0, 1.0] for disputed locations.
    """
    if location_tonic is None:
        return 0.0

    if len(macro_faction_intervals_list) < 2:
        return 0.0

    scales = []
    for intervals in macro_faction_intervals_list:
        if intervals:
            scale_set = {_note_to_semitone(n) for n in build_scale(location_tonic, intervals)}
            scales.append(scale_set)

    if len(scales) < 2:
        return 0.0

    total_disagreement = 0.0
    pairs = 0
    for i in range(len(scales)):
        for j in range(i + 1, len(scales)):
            overlap = len(scales[i] & scales[j])
            union = len(scales[i] | scales[j])
            total_disagreement += 1.0 - (overlap / union) if union else 0.0
            pairs += 1

    return total_disagreement / pairs if pairs else 0.0


# ---------------------------------------------------------------------------
# Faction weight
# ---------------------------------------------------------------------------

def faction_weight(
    faction_root: str,
    other_roots: list[str],
) -> float:
    """Calculate a faction's political weight within its macro-faction.

    Uses harmonic_affinity with each other root. A faction whose root
    forms perfect fifths with many others is the political center.

    Returns a float in [0.0, 1.0]. Higher = more central.
    """
    if not other_roots:
        return 1.0

    total = sum(harmonic_affinity(faction_root, other) for other in other_roots)
    avg = total / len(other_roots)
    return max(0.0, min(1.0, (avg + 1.0) / 2.0))


# ---------------------------------------------------------------------------
# Faction compatibility
# ---------------------------------------------------------------------------

def faction_compatibility(
    intervals_a: list[int],
    intervals_b: list[int],
) -> float:
    """Calculate structural compatibility between two macro-factions' modes.

    Compares interval patterns directly (no root needed).
    Identical patterns → 1.0. Completely different → 0.0.

    Returns a float in [0.0, 1.0].
    """
    if not intervals_a or not intervals_b:
        return 0.0

    len_a = len(intervals_a)
    len_b = len(intervals_b)

    if len_a != len_b:
        max_notes = max(len_a, len_b)
        min_notes = min(len_a, len_b)
        return min_notes / max_notes * 0.5

    matches = sum(1 for a, b in zip(intervals_a, intervals_b) if a == b)
    return matches / len_a
