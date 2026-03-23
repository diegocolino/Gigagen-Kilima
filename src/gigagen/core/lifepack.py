"""Life Pack model — the full existential spectrum of a character.

Organized by octaves (infrasonidos → 0–8 → ultrasonidos).
Each octave contains slots determined by harmonic intervals from the
character's tonic note. Generic Gigagen model — no Kilima-specific data.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from .harmony import CHROMATIC_NOTES

# ---------------------------------------------------------------------------
# Note resolution
# ---------------------------------------------------------------------------

_NOTE_TO_SEMITONE: dict[str, int] = {n: i for i, n in enumerate(CHROMATIC_NOTES)}


# Mode-sensitive degrees: 3rd, 6th, 7th
# Maps degree name → (minor_semitones, major_semitones)
_MODE_DEGREES: dict[str, tuple[int, int]] = {
    "3rd": (3, 4),
    "6th": (8, 9),
    "7th": (10, 11),
}

# Slot key pairs affected by mode change (minor_key, major_key)
_MODE_SLOT_PAIRS: list[tuple[str, str]] = [
    ("3_tercera_menor", "4_tercera_mayor"),
    ("8_sexta_menor", "9_sexta_mayor"),
    ("10_septima_menor", "11_septima_mayor"),
]

# Chord octave field names
_CHORD_OCTAVE_FIELDS = (
    "octave_3_locations",
    "octave_4_objetos",
    "octave_5_skills",
)


def get_interval_semitones(degree: str, mode: str) -> int:
    """Get the semitone count for a scale degree in a given mode.

    >>> get_interval_semitones("3rd", "minor")
    3
    >>> get_interval_semitones("3rd", "major")
    4
    """
    pair = _MODE_DEGREES.get(degree)
    if pair is None:
        raise ValueError(f"Unknown degree: '{degree}'. Use: {list(_MODE_DEGREES)}")
    minor_semi, major_semi = pair
    if mode == "minor":
        return minor_semi
    elif mode == "major":
        return major_semi
    raise ValueError(f"Unknown mode: '{mode}'. Use 'major' or 'minor'.")


def resolve_note(tonic_semitone: int, interval_semitones: int) -> str:
    """Calculate the concrete note for a slot given the tonic and interval.

    >>> resolve_note(3, 7)   # D# + 5J = A#
    'A#'
    >>> resolve_note(0, 0)   # C + unison = C
    'C'
    """
    return CHROMATIC_NOTES[(tonic_semitone + interval_semitones) % 12]


# ---------------------------------------------------------------------------
# Slot model
# ---------------------------------------------------------------------------

OctaveLogic = Literal[
    "fixed_12_archetypes",  # octave 0: lore
    "variable_by_elements",  # octave 1: animas
    "single_slot",  # octave 2: lineage
    "internal_chord",  # octaves 3, 4, 5: locations, objects, skills
    "full_12_by_interval",  # octave 7: characters
    "tbd_hybrid",  # octave 8: events (template)
    "invariants_and_variables",  # octave 8: events (filled lifepacks)
    "tbd",  # octave 6: reserved
]

Alteration = Literal["perfect", "major", "minor", "augmented", "diminished"]

DescendenceStep = Literal["genesis", "theogony", "chronica", "contempo", "existence"]


class LifePackSlot(BaseModel, extra="allow"):
    """A single slot in a Life Pack octave.

    Fields are optional because slot structure varies by octave type:
    - Lore (oct 0): archetype, note, semitone, definition
    - Animas (oct 1): element, element_tier, anima_archetype, ...
    - Lineage (oct 2): lineage_id, lineage_name, note, semitone
    - Chord (oct 3-5): interval, semitones, role, entity_id, ...
    - Characters (oct 7): interval, semitones, role, entity_id, ...
    - Events (oct 8): interval, semitones, role, entity_id, ...
    """

    # Common to chord/character/event slots
    interval: str | None = None
    semitones: int | None = None
    role: str | None = None
    role_desc: str | None = None

    # Entity binding
    entity_id: str | None = None
    entity_name: str | None = None
    entity_note: str | None = None

    # Resolved note (calculated from tonic + semitones)
    resolved_note: str | None = None

    # State
    alteration: Alteration | None = None
    locked: bool = False
    unlocked: bool = True

    # Lore-specific
    archetype: str | None = None
    note: str | None = None
    semitone: int | None = None
    definition: str | None = None

    # Anima-specific
    element: str | None = None
    element_tier: str | None = None
    anima_archetype: str | None = None
    anima_note: str | None = None
    anima_semitone: int | None = None
    dominated: bool | None = None

    # Lineage-specific
    lineage_id: str | None = None
    lineage_name: str | None = None

    # Event-specific (octave 8)
    event_type: str | None = None  # "invariant" | "variable" | ""
    resolved: bool = False

    # Handle JSON field "type" → event_type, "semitones_from_tonic" → semitones
    @model_validator(mode="before")
    @classmethod
    def _normalize_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "type" in data and "event_type" not in data:
                data["event_type"] = data.pop("type")
            if "semitones_from_tonic" in data and "semitones" not in data:
                data["semitones"] = data.pop("semitones_from_tonic")
        return data


# ---------------------------------------------------------------------------
# Octave model
# ---------------------------------------------------------------------------


class LifePackOctave(BaseModel, extra="allow"):
    """A single octave in a Life Pack."""

    unlocked_at: DescendenceStep | None = None
    logic: OctaveLogic | None = None
    slots: dict[str, LifePackSlot | Any] = Field(default_factory=dict)

    # Anima-specific fields (octave 1)
    innate_elements: list[str] | None = None
    dominated_elements: list[str] | None = None
    unlocked_fusions: list[str] | None = None


# ---------------------------------------------------------------------------
# Meta model
# ---------------------------------------------------------------------------


class LifePackMeta(BaseModel):
    """Life Pack metadata — identifies the owning character."""

    entity_id: str = ""
    entity_name: str = ""
    collection: str = ""
    tonic: str = ""
    tonic_semitone: int | None = None
    mode: Literal["major", "minor"] | None = None


# ---------------------------------------------------------------------------
# Life Pack model
# ---------------------------------------------------------------------------


class LifePack(BaseModel, extra="allow"):
    """The full existential spectrum of a character.

    Contains metadata, 9 named octaves (0–8), and edge bands
    (infrasonidos, ultrasonidos).
    """

    meta: LifePackMeta = Field(default_factory=LifePackMeta)

    infrasonidos: LifePackOctave = Field(default_factory=LifePackOctave)
    octave_0_lore: LifePackOctave = Field(default_factory=LifePackOctave)
    octave_1_animas: LifePackOctave = Field(default_factory=LifePackOctave)
    octave_2_linajes: LifePackOctave = Field(default_factory=LifePackOctave)
    octave_3_locations: LifePackOctave = Field(default_factory=LifePackOctave)
    octave_4_objetos: LifePackOctave = Field(default_factory=LifePackOctave)
    octave_5_skills: LifePackOctave = Field(default_factory=LifePackOctave)
    octave_6_reservada: LifePackOctave = Field(default_factory=LifePackOctave)
    octave_7_personajes: LifePackOctave = Field(default_factory=LifePackOctave)
    octave_8_eventos: LifePackOctave = Field(default_factory=LifePackOctave)
    ultrasonidos: LifePackOctave = Field(default_factory=LifePackOctave)

    def get_octave(self, index: int) -> LifePackOctave:
        """Get an octave by numeric index (0–8)."""
        attr = f"octave_{index}_" if index <= 8 else None
        if attr is None:
            raise ValueError(f"Octave index must be 0–8, got {index}")
        for name in self.__class__.model_fields:
            if name.startswith(attr):
                return getattr(self, name)
        raise ValueError(f"No octave found for index {index}")


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

# Interval definitions for chord-based octaves (3, 4, 5)
_CHORD_INTERVALS: list[tuple[str, int, str]] = [
    ("0_tonica", 0, "unison"),
    ("1_segunda_menor", 1, "2m"),
    ("2_segunda_mayor", 2, "2M"),
    ("3_tercera_menor", 3, "3m"),
    ("4_tercera_mayor", 4, "3M"),
    ("5_cuarta_justa", 5, "4J"),
    ("6_tritono", 6, "tritone"),
    ("7_quinta_justa", 7, "5J"),
    ("8_sexta_menor", 8, "6m"),
    ("9_sexta_mayor", 9, "6M"),
    ("10_septima_menor", 10, "7m"),
    ("11_septima_mayor", 11, "7M"),
]

# Initial unlocked slots for chord octaves (tonic, 3m, 3M, 5J)
_INITIAL_UNLOCKED = {0, 3, 4, 7}


def build_empty_lifepack(tonic: str, mode: str = "minor") -> LifePack:
    """Generate an empty Life Pack template with all notes resolved.

    All slots are created with resolved_note calculated from the tonic.
    Chord octaves (3, 4, 5) have 4 initially unlocked slots and 8 locked.
    Octave 7 (characters) has all 12 slots unlocked.
    """
    tonic_semi = _NOTE_TO_SEMITONE.get(tonic)
    if tonic_semi is None:
        raise ValueError(f"Unknown tonic note: '{tonic}'")

    meta = LifePackMeta(
        tonic=tonic,
        tonic_semitone=tonic_semi,
        mode=mode,
    )

    # Octave 0: lore (12 fixed archetype slots, not rotated by tonic)
    lore_slots: dict[str, LifePackSlot] = {}
    for i, note in enumerate(CHROMATIC_NOTES):
        key = f"{i}_{note.replace('#', 's')}"
        lore_slots[key] = LifePackSlot(
            note=note,
            semitone=i,
            definition="",
        )

    # Chord octaves (3, 4, 5): 12 slots, 4 initially unlocked
    def _build_chord_slots() -> dict[str, LifePackSlot]:
        slots: dict[str, LifePackSlot] = {}
        for key, semi, interval_name in _CHORD_INTERVALS:
            slots[key] = LifePackSlot(
                interval=interval_name,
                semitones=semi,
                resolved_note=resolve_note(tonic_semi, semi),
                locked=semi not in _INITIAL_UNLOCKED,
                unlocked=semi in _INITIAL_UNLOCKED,
            )
        return slots

    # Octave 7: characters (12 slots, all unlocked)
    char_slots: dict[str, LifePackSlot] = {}
    for key, semi, interval_name in _CHORD_INTERVALS:
        char_slots[key] = LifePackSlot(
            interval=interval_name,
            semitones=semi,
            resolved_note=resolve_note(tonic_semi, semi),
        )

    # Octave 8: events (12 slots, only tonic unlocked)
    event_slots: dict[str, LifePackSlot] = {}
    for key, semi, interval_name in _CHORD_INTERVALS:
        event_slots[key] = LifePackSlot(
            interval=interval_name,
            semitones=semi,
            resolved_note=resolve_note(tonic_semi, semi),
            locked=semi != 0,
            unlocked=semi == 0,
        )

    return LifePack(
        meta=meta,
        infrasonidos=LifePackOctave(unlocked_at="genesis"),
        octave_0_lore=LifePackOctave(
            unlocked_at="genesis",
            logic="fixed_12_archetypes",
            slots=lore_slots,
        ),
        octave_1_animas=LifePackOctave(
            unlocked_at="theogony",
            logic="variable_by_elements",
            innate_elements=[],
            dominated_elements=[],
            unlocked_fusions=[],
        ),
        octave_2_linajes=LifePackOctave(
            unlocked_at="theogony",
            logic="single_slot",
            slots={
                "0_tonica": LifePackSlot(
                    note=tonic,
                    semitone=tonic_semi,
                ),
            },
        ),
        octave_3_locations=LifePackOctave(
            unlocked_at="contempo",
            logic="internal_chord",
            slots=_build_chord_slots(),
        ),
        octave_4_objetos=LifePackOctave(
            unlocked_at="contempo",
            logic="internal_chord",
            slots=_build_chord_slots(),
        ),
        octave_5_skills=LifePackOctave(
            unlocked_at="contempo",
            logic="internal_chord",
            slots=_build_chord_slots(),
        ),
        octave_6_reservada=LifePackOctave(logic="tbd"),
        octave_7_personajes=LifePackOctave(
            unlocked_at="chronica",
            logic="full_12_by_interval",
            slots=char_slots,
        ),
        octave_8_eventos=LifePackOctave(
            unlocked_at="chronica",
            logic="tbd_hybrid",
            slots=event_slots,
        ),
        ultrasonidos=LifePackOctave(),
    )


# ---------------------------------------------------------------------------
# Mode change
# ---------------------------------------------------------------------------


def change_mode(lifepack: LifePack, new_mode: str) -> LifePack:
    """Change a Life Pack's mode (major ↔ minor), recalculating resolved notes.

    For chord octaves (3, 4, 5), the mode-sensitive slot pairs (3rd, 6th, 7th)
    swap their semitone values and resolved notes. Entities stay in their slots —
    only the harmonic interpretation changes.

    Returns a new LifePack (does not mutate the original).
    """
    if new_mode not in ("major", "minor"):
        raise ValueError(f"Mode must be 'major' or 'minor', got '{new_mode}'")

    old_mode = lifepack.meta.mode
    if old_mode == new_mode:
        return lifepack.model_copy(deep=True)

    lp = lifepack.model_copy(deep=True)
    lp.meta.mode = new_mode

    tonic_semi = lp.meta.tonic_semitone
    if tonic_semi is None:
        tonic_semi = _NOTE_TO_SEMITONE.get(lp.meta.tonic, 0)

    # For each chord octave, swap the mode-sensitive pairs
    for octave_name in _CHORD_OCTAVE_FIELDS:
        octave: LifePackOctave = getattr(lp, octave_name)
        for minor_key, major_key in _MODE_SLOT_PAIRS:
            minor_slot = octave.slots.get(minor_key)
            major_slot = octave.slots.get(major_key)
            if minor_slot is None or major_slot is None:
                continue

            # Swap semitones between the pair
            minor_slot.semitones, major_slot.semitones = (
                major_slot.semitones,
                minor_slot.semitones,
            )

            # Recalculate resolved notes
            if minor_slot.semitones is not None:
                minor_slot.resolved_note = resolve_note(tonic_semi, minor_slot.semitones)
            if major_slot.semitones is not None:
                major_slot.resolved_note = resolve_note(tonic_semi, major_slot.semitones)

            # Swap alterations
            minor_slot.alteration, major_slot.alteration = (
                major_slot.alteration,
                minor_slot.alteration,
            )

    return lp


# ---------------------------------------------------------------------------
# Octave 7 auto-population
# ---------------------------------------------------------------------------


def populate_octave_7(
    lifepack: LifePack,
    all_characters: list[tuple[str, str, str]],
) -> None:
    """Fill octave 7 (characters) from the available roster.

    For each character, calculates the interval from the lifepack's tonic
    and places the character in the corresponding slot.

    Parameters
    ----------
    lifepack:
        The Life Pack to populate (mutated in place).
    all_characters:
        List of (entity_id, name, note) tuples for all characters.
        The lifepack owner is included — they land on slot 0 (unison/mirror).
    """
    tonic_semi = lifepack.meta.tonic_semitone
    if tonic_semi is None:
        tonic_semi = _NOTE_TO_SEMITONE.get(lifepack.meta.tonic)
        if tonic_semi is None:
            return

    # Build a map: semitone interval → slot key
    slot_by_semi: dict[int, str] = {}
    for key, slot in lifepack.octave_7_personajes.slots.items():
        if isinstance(slot, LifePackSlot) and slot.semitones is not None:
            slot_by_semi[slot.semitones] = key

    for char_id, char_name, char_note in all_characters:
        char_semi = _NOTE_TO_SEMITONE.get(char_note)
        if char_semi is None:
            continue
        interval = (char_semi - tonic_semi) % 12
        slot_key = slot_by_semi.get(interval)
        if slot_key is None:
            continue
        slot = lifepack.octave_7_personajes.slots[slot_key]
        if isinstance(slot, LifePackSlot):
            slot.entity_id = char_id
            slot.entity_name = char_name
            slot.entity_note = char_note


# ---------------------------------------------------------------------------
# Octave 8: invariants and variables
# ---------------------------------------------------------------------------


def resolve_octave_8_invariants(lifepack: LifePack) -> int:
    """Mark all invariant slots in octave 8 as resolved.

    Invariant events always happen — they are pre-resolved on load.
    Returns the number of slots resolved.
    """
    count = 0
    for slot in lifepack.octave_8_eventos.slots.values():
        if isinstance(slot, LifePackSlot) and slot.event_type == "invariant":
            if not slot.resolved:
                slot.resolved = True
                slot.locked = False
                slot.unlocked = True
                count += 1
    return count


def resolve_octave_8_variable(
    lifepack: LifePack,
    var_id: str,
    resolution: str,
) -> bool:
    """Resolve a variable slot in octave 8.

    Finds the first unresolved variable slot and fills it with the
    resolution outcome. Returns True if a slot was resolved.
    """
    for slot in lifepack.octave_8_eventos.slots.values():
        if not isinstance(slot, LifePackSlot):
            continue
        if slot.event_type == "variable" and not slot.resolved:
            slot.resolved = True
            slot.locked = False
            slot.unlocked = True
            slot.entity_id = var_id
            slot.entity_name = resolution
            return True
    return False


# ---------------------------------------------------------------------------
# Octave 1: Ánimas — element-based slot computation
# ---------------------------------------------------------------------------


class ElementConfig(BaseModel):
    """A character's element configuration for octave 1."""

    innate_elements: list[str] = Field(default_factory=list)
    dominated_elements: list[str] = Field(default_factory=list)
    latent_elements: list[str] = Field(default_factory=list)
    unlocked_fusions: list[str] = Field(default_factory=list)


class ElementDef(BaseModel):
    """An element from the catalog."""

    id: str
    name: str
    tier: str  # "fundamental" | "mixed" | "truncated" | "supreme"
    requires: list[str] = Field(default_factory=list)


class AnimaSlotResult(BaseModel):
    """Result of computing available anima slots."""

    element_id: str
    element_name: str
    tier: str
    status: str  # "active" (dominated), "available" (innate, not dominated), "future" (fusion unlockable)


def load_elements_catalog(path: str | None = None) -> list[ElementDef]:
    """Load the element catalog from JSON."""
    import json
    import pathlib

    if path is None:
        path = str(pathlib.Path(__file__).parent / "elements.json")
    raw = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    return [ElementDef(**e) for e in raw["elements"]]


def compute_available_anima_slots(
    config: ElementConfig,
    catalog: list[ElementDef],
) -> list[AnimaSlotResult]:
    """Compute which anima slots a character can have based on their elements.

    - dominated elements → "active" slots (anima assigned, fully usable)
    - innate but not dominated → "available" slots (can be activated)
    - fusions whose requirements are met by innate elements → "future" slots

    Returns a list of AnimaSlotResult sorted by tier priority.
    """
    innate_set = set(config.innate_elements)
    dominated_set = set(config.dominated_elements)
    fusion_set = set(config.unlocked_fusions)

    catalog_map = {e.id: e for e in catalog}
    results: list[AnimaSlotResult] = []

    # Active: dominated elements
    for eid in config.dominated_elements:
        elem = catalog_map.get(eid)
        if elem:
            results.append(AnimaSlotResult(
                element_id=eid, element_name=elem.name,
                tier=elem.tier, status="active",
            ))

    # Available: innate but not dominated
    for eid in config.innate_elements:
        if eid in dominated_set:
            continue
        elem = catalog_map.get(eid)
        if elem:
            results.append(AnimaSlotResult(
                element_id=eid, element_name=elem.name,
                tier=elem.tier, status="available",
            ))

    # Future: fusions whose requirements are all in innate_elements
    seen = innate_set | dominated_set
    for elem in catalog:
        if elem.id in seen:
            continue
        if elem.tier in ("mixed", "truncated", "supreme"):
            if elem.requires and all(r in innate_set for r in elem.requires):
                results.append(AnimaSlotResult(
                    element_id=elem.id, element_name=elem.name,
                    tier=elem.tier, status="future",
                ))

    return results
