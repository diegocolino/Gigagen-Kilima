"""Load a worldpack directory into a WorldState."""

from __future__ import annotations

import json
import pathlib
from typing import Any

import yaml

from gigagen.core.entity import BaseEntity, Character, Faction, Location
from gigagen.core.relation import Relation
from gigagen.core.world_state import WorldState
from gigagen.core.seed import apply_seed_variation


_ENTITY_LOADERS: dict[str, type[BaseEntity]] = {
    "character": Character,
    "faction": Faction,
    "location": Location,
}


def _load_json(path: pathlib.Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_world_meta(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_worldpack(
    worldpack_dir: str | pathlib.Path,
    seed: int = 1,
    phase: str = "block_1_start",
    *,
    apply_variation: bool = True,
) -> WorldState:
    """Load all JSONs from a worldpack directory and build a WorldState.

    Parameters
    ----------
    worldpack_dir:
        Path to the worldpack directory.
    seed:
        Deterministic seed for this run.
    phase:
        Starting phase label.
    apply_variation:
        If True, apply seed-based variation to seeded fields.

    Returns
    -------
    WorldState
        Fully populated world state with all entities and relations.
    """
    root = pathlib.Path(worldpack_dir)

    # -- world metadata --
    meta = _load_world_meta(root / "world.json")
    world_id: str = meta["world_id"]
    description: str = meta.get("description", "")

    # -- entities --
    entities: dict[str, BaseEntity] = {}

    structure = meta.get("structure", {})
    file_map = {
        "character": structure.get("characters_file", "characters.json"),
        "faction": structure.get("factions_file", "factions.json"),
        "location": structure.get("locations_file", "locations.json"),
    }

    for entity_type, filename in file_map.items():
        path = root / filename
        if not path.exists():
            continue
        cls = _ENTITY_LOADERS[entity_type]
        for raw in _load_json(path):
            ent = cls(**raw)
            entities[ent.id] = ent

    # -- relations --
    relations_file = structure.get("relations_file", "relations.json")
    relations: list[Relation] = []
    rel_path = root / relations_file
    if rel_path.exists():
        for raw in _load_json(rel_path):
            relations.append(Relation(**raw))

    # -- timeline (loaded but not processed yet — M5) --
    timeline_data: dict[str, Any] | None = None
    timelines_cfg = structure.get("timelines", {})
    for _label, tl_file in timelines_cfg.items():
        tl_path = root / tl_file
        if tl_path.exists():
            timeline_data = yaml.safe_load(tl_path.read_text(encoding="utf-8"))
            break  # only first timeline for now

    # -- build active lists --
    active_faction_ids = [
        eid for eid, e in entities.items()
        if e.entity_type == "faction" and getattr(e, "status", "") != "dissolved"
    ]
    active_location_ids = [
        eid for eid, e in entities.items()
        if e.entity_type == "location"
    ]

    # -- tags from meta --
    tags: list[str] = meta.get("tags", [])

    ws = WorldState(
        world_id=world_id,
        seed=seed,
        phase=phase,
        description=description,
        entities=entities,
        relations=relations,
        active_faction_ids=active_faction_ids,
        active_location_ids=active_location_ids,
        tags=tags,
    )

    # -- Apply seed-based variation --
    if apply_variation:
        invariants_file = structure.get("invariants_file", "invariants.json")
        inv_path = root / invariants_file
        apply_seed_variation(ws, invariants_path=inv_path if inv_path.exists() else None)

    return ws


def load_timeline_events(
    worldpack_dir: str | pathlib.Path,
) -> list[dict[str, Any]]:
    """Load timeline events from the worldpack's YAML timeline.

    Returns a list of event dicts sorted by hour.
    """
    root = pathlib.Path(worldpack_dir)
    meta = _load_world_meta(root / "world.json")
    structure = meta.get("structure", {})
    timelines_cfg = structure.get("timelines", {})

    for _label, tl_file in timelines_cfg.items():
        tl_path = root / tl_file
        if tl_path.exists():
            data = yaml.safe_load(tl_path.read_text(encoding="utf-8"))
            events = data.get("events", [])
            return sorted(
                [e for e in events if e.get("hour") is not None],
                key=lambda e: (e["hour"], e.get("id", "")),
            )
    return []
