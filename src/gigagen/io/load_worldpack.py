"""Load a worldpack directory into a WorldState."""

from __future__ import annotations

import json
import pathlib
from typing import Any

import yaml

from gigagen.core.entity import BaseEntity, Character, MacroFaction, Location
from gigagen.core.lifepack import LifePack, populate_octave_7
from gigagen.core.relation import Relation
from gigagen.core.world_state import WorldState
from gigagen.core.seed import apply_seed_variation


_ENTITY_LOADERS: dict[str, type[BaseEntity]] = {
    "character": Character,
    "macro_faction": MacroFaction,
    "location": Location,
}


def _load_json(path: pathlib.Path) -> list[dict[str, Any]]:
    """Load a JSON file, handling both plain arrays and object wrappers."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return raw
    # Object wrapper — find the data array
    if isinstance(raw, dict):
        for key in ("characters", "relations", "locations", "factions"):
            if key in raw:
                return raw[key]
        # Plain dict (e.g., world.json) — not an entity list
        return []
    return []


def _load_factions(path: pathlib.Path) -> list[dict[str, Any]]:
    """Load factions, handling both embedded and split formats."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        # Old flat format: list of MacroFaction dicts with embedded factions
        return raw
    if isinstance(raw, dict) and "macro_factions" in raw:
        # New split format: {macro_factions: [...], factions: [...]}
        mfacs = raw["macro_factions"]
        # Group factions by macro_faction_id
        facs_by_mfac: dict[str, list[dict]] = {}
        for f in raw.get("factions", []):
            mfid = f.get("macro_faction_id", "")
            facs_by_mfac.setdefault(mfid, []).append(f)
        # Embed factions into each macro-faction
        result = []
        for mf in mfacs:
            mf_copy = dict(mf)
            mf_copy["factions"] = facs_by_mfac.get(mf_copy["id"], [])
            result.append(mf_copy)
        return result
    return _load_json(path)


def _normalize_location(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize new-format location fields to match the Location model."""
    d = dict(raw)
    # level → zone_level
    if "level" in d and "zone_level" not in d:
        d["zone_level"] = d.pop("level")
    # parent → parent_location_id
    if "parent" in d and "parent_location_id" not in d:
        d["parent_location_id"] = d.pop("parent")
    # faction_control → controlling_macro_faction_id
    if "faction_control" in d and "controlling_macro_faction_id" not in d:
        d["controlling_macro_faction_id"] = d.pop("faction_control")
    # Ensure entity_type
    if "entity_type" not in d:
        d["entity_type"] = "location"
    # Ensure canon_level
    if "canon_level" not in d:
        d["canon_level"] = "fixed"
    # Ensure name
    if "name" not in d:
        d["name"] = d.get("id", "")
    # Strip extra fields the model doesn't know (tonic_type, zone_tag, etc.)
    # These are handled by Location's extra="forbid" — actually Location doesn't
    # have extra="forbid", but unknown fields will cause validation errors.
    # Keep them safe by not stripping — Pydantic BaseEntity doesn't allow extras
    # unless we add them. For now, remove non-model fields.
    known = {
        "id", "entity_type", "name", "tags", "canon_level", "description",
        "tonic", "zone_level", "parent_location_id", "biome_tags",
        "status", "controlling_macro_faction_id", "secondary_macro_faction_ids",
        "tension", "access",
    }
    return {k: v for k, v in d.items() if k in known}


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
        "macro_faction": structure.get("factions_file", "factions.json"),
        "location": structure.get("locations_file", "locations.json"),
    }

    for entity_type, filename in file_map.items():
        path = root / filename
        if not path.exists():
            continue
        cls = _ENTITY_LOADERS[entity_type]
        if entity_type == "macro_faction":
            raw_list = _load_factions(path)
        else:
            raw_list = _load_json(path)
        for raw in raw_list:
            if entity_type == "location":
                raw = _normalize_location(raw)
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
    active_macro_faction_ids = [
        eid for eid, e in entities.items()
        if e.entity_type == "macro_faction" and getattr(e, "status", "") != "dissolved"
    ]
    active_location_ids = [
        eid for eid, e in entities.items()
        if e.entity_type == "location"
    ]

    # -- tags from meta --
    tags: list[str] = meta.get("tags", [])

    # -- lifepacks --
    lifepacks: dict[str, LifePack] = {}
    lifepacks_dir = root / "lifepacks"
    if lifepacks_dir.is_dir():
        for lp_path in sorted(lifepacks_dir.glob("*.json")):
            raw = json.loads(lp_path.read_text(encoding="utf-8"))
            lp = LifePack.model_validate(raw)
            char_id = lp.meta.entity_id
            if char_id:
                lifepacks[char_id] = lp

    # -- auto-populate octave 7 for each lifepack --
    if lifepacks:
        all_chars = [
            (eid, ent.name, ent.note)
            for eid, ent in entities.items()
            if isinstance(ent, Character)
        ]
        for lp in lifepacks.values():
            populate_octave_7(lp, all_chars)

    ws = WorldState(
        world_id=world_id,
        seed=seed,
        phase=phase,
        description=description,
        entities=entities,
        relations=relations,
        active_macro_faction_ids=active_macro_faction_ids,
        active_location_ids=active_location_ids,
        tags=tags,
        lifepacks=lifepacks,
    )

    # -- Apply seed-based variation --
    if apply_variation:
        invariants_file = structure.get("invariants_file", "invariants.json")
        inv_path = root / invariants_file
        catalogs = meta.get("catalogs")
        apply_seed_variation(
            ws,
            invariants_path=inv_path if inv_path.exists() else None,
            catalogs=catalogs,
        )

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
