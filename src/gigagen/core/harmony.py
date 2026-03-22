"""Harmonic engine — pure functions for musical-relational calculations.

All functions operate on notes (str) and intervals (list[int]).
No faction names, no worldpack-specific data. The engine doesn't know
what "Anti Group" or "Phrygian" means — it only knows note sets.
"""

from __future__ import annotations

from .relation import _NOTE_TO_SEMITONE, _INTERVAL_AFFINITY

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


def _interval_affinity(semitones: int) -> float:
    """Get the affinity value for a given interval in semitones."""
    return _INTERVAL_AFFINITY[semitones % 12]


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
    faction_intervals: list[int],
    subdivision_root: str | None,
) -> float:
    """Calculate a character's affinity with a faction subdivision.

    If subdivision_root is None, returns 0.0 (no calculation possible).

    The affinity is the interval-based score between the character's note
    and the subdivision root. If the character's note falls inside the
    subdivision's scale, the score is boosted; outside the scale, it's penalized.

    Returns a float in [-1.0, 1.0].
    """
    if subdivision_root is None or not faction_intervals:
        return 0.0

    # Base: interval affinity between character note and subdivision root
    char_semi = _note_to_semitone(character_note)
    root_semi = _note_to_semitone(subdivision_root)
    interval = (char_semi - root_semi) % 12
    base = _interval_affinity(interval)

    # Bonus/penalty: is the character's note in the subdivision's scale?
    scale = build_scale(subdivision_root, faction_intervals)
    scale_semitones = {_note_to_semitone(n) for n in scale}

    if char_semi in scale_semitones:
        # In scale: boost toward positive (min +0.1 push)
        return min(1.0, base + 0.2) if base >= 0 else base * 0.5
    else:
        # Out of scale: push toward negative (min -0.1 push)
        return max(-1.0, base - 0.2) if base <= 0 else base * 0.5


# ---------------------------------------------------------------------------
# Character-location affinity
# ---------------------------------------------------------------------------

def character_location_affinity(
    character_note: str,
    location_tonic: str | None,
    controlling_faction_intervals: list[int] | None,
    structural_weight: float = 0.3,
    modal_weight: float = 0.7,
) -> float | None:
    """Calculate a character's total affinity with a location.

    Combined structural (note vs tonic) + modal (note vs location scale).

    Returns None if location has no tonic (no harmonic calculation possible).
    Returns float in [-1.0, 1.0] otherwise.
    """
    if location_tonic is None:
        return None

    # Structural: interval between character note and location tonic
    structural = _interval_affinity(
        (_note_to_semitone(character_note) - _note_to_semitone(location_tonic)) % 12
    )

    # Modal: does the character's note fall in the location's current scale?
    if controlling_faction_intervals:
        scale = build_scale(location_tonic, controlling_faction_intervals)
        scale_semitones = {_note_to_semitone(n) for n in scale}
        char_semi = _note_to_semitone(character_note)
        # In scale → positive, out → negative
        modal = 0.5 if char_semi in scale_semitones else -0.5
    else:
        # No controlling faction → neutral ground, only structural matters
        return structural

    return max(-1.0, min(1.0,
        structural_weight * structural + modal_weight * modal
    ))


# ---------------------------------------------------------------------------
# Dual membership cost
# ---------------------------------------------------------------------------

def dual_membership_cost(
    faction_a_intervals: list[int],
    sub_a_root: str | None,
    faction_b_intervals: list[int],
    sub_b_root: str | None,
) -> float:
    """Calculate the tension of belonging to two factions simultaneously.

    Based on scale overlap: high overlap → low cost, low overlap → high cost.

    Returns a float in [0.0, 1.0] where 0 = no tension, 1 = maximum tension.
    """
    if sub_a_root is None or sub_b_root is None:
        return 0.5  # unknown — moderate default

    if not faction_a_intervals or not faction_b_intervals:
        return 0.5

    scale_a = set(build_scale(sub_a_root, faction_a_intervals))
    scale_b = set(build_scale(sub_b_root, faction_b_intervals))

    if not scale_a or not scale_b:
        return 0.5

    overlap = len(scale_a & scale_b)
    max_possible = min(len(scale_a), len(scale_b))

    # High overlap → low cost
    return 1.0 - (overlap / max_possible)


# ---------------------------------------------------------------------------
# Location instability
# ---------------------------------------------------------------------------

def location_instability(
    location_tonic: str | None,
    faction_intervals_list: list[list[int]],
) -> float:
    """Calculate instability for a disputed location.

    Measures overlap between stacked faction scales projected from the
    location's tonic. Less overlap → more instability.

    Returns 0.0 for stable (single/no faction) or no tonic.
    Returns float in [0.0, 1.0] for disputed locations.
    """
    if location_tonic is None:
        return 0.0

    if len(faction_intervals_list) < 2:
        return 0.0

    # Build all scales from the location's tonic
    scales = []
    for intervals in faction_intervals_list:
        if intervals:
            scale_set = {_note_to_semitone(n) for n in build_scale(location_tonic, intervals)}
            scales.append(scale_set)

    if len(scales) < 2:
        return 0.0

    # Pairwise overlap — average the disagreement
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
# Subdivision weight
# ---------------------------------------------------------------------------

def subdivision_weight(
    subdivision_root: str,
    other_roots: list[str],
) -> float:
    """Calculate a subdivision's political weight within its faction.

    Based on consonance with other subdivisions. A subdivision whose root
    forms perfect fifths with many others is the political center.

    Returns a float in [0.0, 1.0]. Higher = more central.
    """
    if not other_roots:
        return 1.0  # only subdivision → maximum weight

    sub_semi = _note_to_semitone(subdivision_root)
    total_affinity = 0.0
    for other in other_roots:
        other_semi = _note_to_semitone(other)
        interval = (other_semi - sub_semi) % 12
        aff = _interval_affinity(interval)
        total_affinity += aff

    # Normalize from [-1, 1] average to [0, 1]
    avg = total_affinity / len(other_roots)
    return max(0.0, min(1.0, (avg + 1.0) / 2.0))


# ---------------------------------------------------------------------------
# Faction compatibility
# ---------------------------------------------------------------------------

def faction_compatibility(
    intervals_a: list[int],
    intervals_b: list[int],
) -> float:
    """Calculate structural compatibility between two factions' modes.

    Compares interval patterns directly (no root needed).
    Identical patterns → 1.0. Completely different → 0.0.

    Returns a float in [0.0, 1.0].
    """
    if not intervals_a or not intervals_b:
        return 0.0

    # Normalize to same length for comparison
    len_a = len(intervals_a)
    len_b = len(intervals_b)

    if len_a != len_b:
        # Different scale families — base compatibility is lower
        # Compare note counts as a rough measure
        max_notes = max(len_a, len_b)
        min_notes = min(len_a, len_b)
        return min_notes / max_notes * 0.5

    # Same length: compare how many intervals match position by position
    # No rotation — modes are compared as-is. Ionian [2,2,1,2,2,2,1]
    # vs Mixolydian [2,2,1,2,2,1,2] differ at positions 5,6 → 5/7 ≈ 0.71.
    matches = sum(1 for a, b in zip(intervals_a, intervals_b) if a == b)
    return matches / len_a
