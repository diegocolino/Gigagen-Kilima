"""Canonical entity models for Gigagen.

All worldpack-specific values (archetype codes, notes, elements, statuses)
are loaded from the worldpack's world.json catalogs section at runtime.
The models use plain `str` for these fields — validation happens against
the loaded catalogs, not hardcoded constants.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


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

    # Identity
    archetype: str
    note: str
    hero_type: str
    civil_name: str
    role_name: str
    lineage: str | None = None

    # State (varies by seed/simulation)
    status: str = "active"
    current_location_id: str
    current_faction_id: str | None = None
    current_subdivision_id: str | None = None  # name of subdivision within current faction
    emotional_load: str = "neutral"


class Subdivision(BaseModel):
    """A concrete instantiation of a faction's mode from a specific root note."""
    name: str | None = None
    note: str | None = None       # root note (typically leader's archetype note)
    leader_id: str | None = None
    type: str | None = None       # e.g. "real" | "simulated" (Union Corp ministries)
    notes: str | None = None      # freeform design notes


class Faction(BaseEntity):
    entity_type: Literal["faction"] = "faction"

    # Identity — harmonic
    mode: str = ""                                          # e.g. "ionian", "phrygian", "whole_tone"
    intervals: list[int] = Field(default_factory=list)      # e.g. [2,2,1,2,2,2,1]
    note_count: int = 0                                     # len(intervals)
    scale_family: str = ""                                  # "greek" | "symmetric" | "pentatonic"
    subdivisions: list[Subdivision] = Field(default_factory=list)

    # Identity — structural
    doctrine_tags: list[str] = Field(default_factory=list)
    base_location_id: str | None = None

    # State
    status: str = "active"
    power: float = Field(ge=0.0, le=1.0, default=0.5)
    cohesion: float = Field(ge=0.0, le=1.0, default=0.5)
    leader_id: str | None = None


class Location(BaseEntity):
    entity_type: Literal["location"] = "location"

    # Identity
    tonic: str | None = None      # harmonic tonic note (from founding lineage)
    zone_level: str               # e.g. "high", "mid", "low", "external", "hidden", "virtual"
    parent_location_id: str | None = None   # hierarchy — which location contains this one
    biome_tags: list[str] = Field(default_factory=list)

    # State
    status: str = "stable"
    controlling_faction_id: str | None = None
    secondary_faction_ids: list[str] = Field(default_factory=list)
    tension: float = Field(ge=0.0, le=1.0, default=0.0)
    access: str = "open"          # e.g. "open", "restricted", "sealed", "clandestine"


class Item(BaseEntity):
    entity_type: Literal["item"] = "item"

    # Identity
    item_kind: str                # e.g. "weapon", "artifact", "document", "key", "symbol"
    slot: str | None = None       # e.g. "hand", "body", "mind"
    symbol_tags: list[str] = Field(default_factory=list)
    rarity: str = "common"        # e.g. "common", "rare", "unique"

    # State
    owner_id: str | None = None
    sealed: bool = False


class Anima(BaseEntity):
    entity_type: Literal["anima"] = "anima"

    # Identity
    element: str
    temperament_tags: list[str] = Field(default_factory=list)
    visibility_class: str = "visible"  # e.g. "visible", "sensitive_only", "supreme_only", "hidden"
    personality: str = ""

    # State
    bonded_character_id: str | None = None
    stability: float = Field(ge=0.0, le=1.0, default=1.0)
    manifestation_level: float = Field(ge=0.0, le=1.0, default=0.0)
    current_plane: str = "dormant"  # e.g. "physical", "red", "dormant"
