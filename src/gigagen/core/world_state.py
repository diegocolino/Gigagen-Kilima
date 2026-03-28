"""WorldState container. Matches ontology.md exactly."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from .entity import BaseEntity, Character, MacroFaction, Location, Item, Anima
from .lifepack import LifePack
from .relation import Relation

# The five steps of the Descendence Ladder
DescendenceStep = Literal["genesis", "theogony", "chronica", "contempo", "existence"]


class ElementDef(BaseModel):
    """Element definition from y.json."""

    id: str
    name: str
    tier: str
    components: list[str] = Field(default_factory=list)


class ModeDef(BaseModel):
    """Mode definition from x.json."""

    intervals: list[int]
    family: str
    character: str = ""


class Catalogs(BaseModel):
    """Universe catalogs built from x.json + y.json during Genesis.

    Contains both the abstract laws (from x.json) and the concrete
    assignments (from y.json) needed by subsequent layers.
    """

    # From y.json — concrete matter
    notes: list[str]
    archetypes: dict[str, str]  # code -> note
    elements: dict[str, ElementDef]  # id -> element definition

    # From x.json — abstract laws
    modes: dict[str, ModeDef]  # mode name -> definition
    scale_families: list[str]
    entity_types: list[str]
    canon_levels: list[str]
    element_tiers: list[str]

    # From y.json — tier lists
    character_tiers: list[str]
    location_levels: list[str]
    item_tiers: list[str]
    skill_tiers: list[str]


class WorldState(BaseModel):
    world_id: str
    seed: int
    phase: DescendenceStep
    description: str = ""

    # Catalogs from Genesis (x.json + y.json)
    catalogs: Catalogs | None = None

    entities: dict[str, BaseEntity] = Field(default_factory=dict)
    relations: list[Relation] = Field(default_factory=list)

    active_macro_faction_ids: list[str] = Field(default_factory=list)
    active_location_ids: list[str] = Field(default_factory=list)

    tags: list[str] = Field(default_factory=list)

    # Life Packs — keyed by character entity_id
    lifepacks: dict[str, "LifePack"] = Field(default_factory=dict)

    def get_lifepack(self, character_id: str) -> "LifePack | None":
        """Get a character's Life Pack, or None if not loaded."""
        return self.lifepacks.get(character_id)
