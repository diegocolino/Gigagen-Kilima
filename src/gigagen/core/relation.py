"""Relation model and harmonic affinity function. Matches ontology.md exactly."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


RELATION_KINDS = frozenset({
    # Character <-> Character
    "sibling", "partner", "ex_partner", "close_friend", "former_friend",
    "rival", "mentor", "distrust", "childhood_best_friends", "oneiric_bond",
    "maternal_figure", "leadership_succession", "reunited_in_limbo",
    "automaton_of",
    # Character <-> Faction
    "member_of", "leader_of", "allied_with", "opposed_to", "infiltrated_in",
    # Character <-> Location
    "lives_in", "tied_to", "hidden_in",
    # Faction <-> Location
    "based_in", "controls", "influences", "hides_in",
})

CanonLevel = Literal["fixed", "seeded", "derived"]

# --- Note-to-semitone mapping ---

_NOTE_TO_SEMITONE: dict[str, int] = {
    "C": 0, "C#": 1, "Db": 1,
    "D": 2, "D#": 3, "Eb": 3,
    "E": 4,
    "F": 5, "F#": 6, "Gb": 6,
    "G": 7, "G#": 8, "Ab": 8,
    "A": 9, "A#": 10, "Bb": 10,
    "B": 11,
}

# Affinity by semitone interval (0-11), derived from ontology.md interval table
_INTERVAL_AFFINITY: dict[int, float] = {
    0: 1.0,    # Unísono — resonancia total
    1: -0.8,   # Segunda menor — tensión fuerte / fricción
    2: -0.5,   # Segunda mayor — tensión moderada
    3: -0.3,   # Tercera menor — tensión dramática / vínculo emocional tenso
    4: 0.7,    # Tercera mayor — afinidad emocional / armonía cálida
    5: 0.8,    # Cuarta justa — estabilidad / soporte
    6: -1.0,   # Tritono — némesis / tensión máxima / disonancia
    7: 0.9,    # Quinta justa — aliado natural / armonía fuerte
    8: -0.2,   # Sexta menor — melancolía / vínculo agridulce
    9: 0.6,    # Sexta mayor — afinidad dulce / complemento
    10: -0.4,  # Séptima menor — tensión dinámica / empuje
    11: -0.6,  # Séptima mayor — tensión elevada / aspiración
}


def harmonic_affinity(note_a: str, note_b: str) -> float:
    """Calculate the base harmonic affinity between two musical notes.

    Uses the interval table from ontology.md. Returns a float between -1.0
    and 1.0. This is a CALCULATED property, never stored.
    """
    semi_a = _NOTE_TO_SEMITONE.get(note_a)
    semi_b = _NOTE_TO_SEMITONE.get(note_b)
    if semi_a is None:
        raise ValueError(f"Unknown note: '{note_a}'")
    if semi_b is None:
        raise ValueError(f"Unknown note: '{note_b}'")
    interval = (semi_b - semi_a) % 12
    return _INTERVAL_AFFINITY[interval]


class Relation(BaseModel):
    id: str
    source_id: str
    target_id: str
    kind: str
    weight: float = Field(ge=0.0, le=1.0)
    polarity: int = Field(ge=-1, le=1)
    tags: list[str] = Field(default_factory=list)
    canon_level: CanonLevel
    origin_event_id: str | None = None

    def model_post_init(self, __context: object) -> None:
        if self.kind not in RELATION_KINDS:
            raise ValueError(
                f"Invalid relation kind '{self.kind}'. "
                f"Must be one of: {sorted(RELATION_KINDS)}"
            )
