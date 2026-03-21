"""Canonical entity models for Gigagen. Matches ontology.md exactly."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


ARCHETYPE_CODES = frozenset({
    "CAR", "JES", "HER", "REB", "ORP", "LOV",
    "HCK", "LEA", "INN", "EXP", "CRE", "DEI",
})

NOTES = frozenset({
    "C", "C#", "D", "D#", "E", "F",
    "F#", "G", "G#", "A", "A#", "B",
})

ELEMENTS = frozenset({
    "Agua", "Fuego", "Tierra", "Aire",
    "Nube", "Barro", "Hielo", "Metal", "Humo", "Polvo",
    "Lava", "Humedad", "Ceniza", "Tormenta",
    "Éter Natural", "Éter Sintético",
})


EntityType = Literal["character", "faction", "location", "item", "anima"]
CanonLevel = Literal["fixed", "seeded", "derived"]


class BaseEntity(BaseModel):
    id: str
    entity_type: EntityType
    name: str
    tags: list[str] = Field(default_factory=list)
    canon_level: CanonLevel
    description: str = ""


class Character(BaseEntity):
    entity_type: Literal["character"] = "character"

    # Identity (fixed for the 12 principals in Kilima)
    archetype: str
    note: str
    hero_type: str
    civil_name: str
    role_name: str
    lineage: str | None = None

    # State (varies by seed/simulation)
    status: Literal[
        "active", "dead", "missing", "captive",
        "digitalized", "transferred", "automaton",
    ] = "active"
    current_location_id: str
    current_faction_id: str | None = None
    emotional_load: Literal[
        "neutral", "grief", "rage", "hope", "fear",
    ] = "neutral"

    def model_post_init(self, __context: object) -> None:
        if self.archetype not in ARCHETYPE_CODES:
            raise ValueError(
                f"Invalid archetype '{self.archetype}'. "
                f"Must be one of: {sorted(ARCHETYPE_CODES)}"
            )
        if self.note not in NOTES:
            raise ValueError(
                f"Invalid note '{self.note}'. Must be one of: {sorted(NOTES)}"
            )


class Faction(BaseEntity):
    entity_type: Literal["faction"] = "faction"

    # Identity
    doctrine_tags: list[str] = Field(default_factory=list)
    base_location_id: str

    # State
    status: Literal["active", "dissolved", "underground", "dominant"] = "active"
    power: float = Field(ge=0.0, le=1.0)
    cohesion: float = Field(ge=0.0, le=1.0)
    leader_id: str | None = None


class Location(BaseEntity):
    entity_type: Literal["location"] = "location"

    # Identity
    zone_level: Literal["high", "mid", "low", "external", "hidden", "virtual"]
    biome_tags: list[str] = Field(default_factory=list)

    # State
    status: Literal[
        "stable", "tense", "fragile", "unstable",
        "hidden", "active", "breached", "besieged",
    ] = "stable"
    controlling_faction_id: str | None = None
    tension: float = Field(ge=0.0, le=1.0, default=0.0)
    access: Literal["open", "restricted", "sealed", "clandestine"] = "open"


class Item(BaseEntity):
    entity_type: Literal["item"] = "item"

    # Identity
    item_kind: Literal["weapon", "artifact", "document", "key", "symbol"]
    slot: Literal["hand", "body", "mind"] | None = None
    symbol_tags: list[str] = Field(default_factory=list)
    rarity: Literal["common", "rare", "unique"] = "common"

    # State
    owner_id: str | None = None
    sealed: bool = False


class Anima(BaseEntity):
    entity_type: Literal["anima"] = "anima"

    # Identity
    element: str
    temperament_tags: list[str] = Field(default_factory=list)
    visibility_class: Literal[
        "visible", "sensitive_only", "supreme_only", "hidden",
    ] = "visible"
    personality: str = ""

    # State
    bonded_character_id: str | None = None
    stability: float = Field(ge=0.0, le=1.0, default=1.0)
    manifestation_level: float = Field(ge=0.0, le=1.0, default=0.0)
    current_plane: Literal["physical", "red", "dormant"] = "dormant"

    def model_post_init(self, __context: object) -> None:
        if self.element not in ELEMENTS:
            raise ValueError(
                f"Invalid element '{self.element}'. "
                f"Must be one of: {sorted(ELEMENTS)}"
            )
