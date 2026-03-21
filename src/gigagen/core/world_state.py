"""WorldState container. Matches ontology.md exactly."""

from __future__ import annotations

from pydantic import BaseModel, Field

from .entity import BaseEntity, Character, Faction, Location, Item, Anima
from .relation import Relation


class WorldState(BaseModel):
    world_id: str
    seed: int
    phase: str
    description: str = ""

    entities: dict[str, BaseEntity] = Field(default_factory=dict)
    relations: list[Relation] = Field(default_factory=list)

    active_faction_ids: list[str] = Field(default_factory=list)
    active_location_ids: list[str] = Field(default_factory=list)

    tags: list[str] = Field(default_factory=list)
