"""WorldState container. Matches ontology.md exactly."""

from __future__ import annotations

from pydantic import BaseModel, Field

from .entity import BaseEntity, Character, MacroFaction, Location, Item, Anima
from .lifepack import LifePack
from .relation import Relation


class WorldState(BaseModel):
    world_id: str
    seed: int
    phase: str
    description: str = ""

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
