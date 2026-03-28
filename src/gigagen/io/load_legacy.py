"""Legacy worldpack loader for worldpacks without x.json/y.json.

This module will be deprecated once all worldpacks migrate to the
Escalera de Descendencia architecture.
"""

from __future__ import annotations

import json
import pathlib

from gigagen.core.entity import Character, MacroFaction, Location
from gigagen.core.lifepack import LifePack, populate_octave_7
from gigagen.core.relation import Relation
from gigagen.core.seed import apply_seed_variation
from gigagen.core.world_state import DescendenceStep, WorldState
from gigagen.layers.contempo import _load_json, _load_factions, _normalize_location


def load_legacy_worldpack(
    root: pathlib.Path,
    seed: int,
    phase: DescendenceStep,
    apply_variation: bool,
) -> WorldState:
    """Load a legacy worldpack without x.json/y.json."""
    meta = json.loads((root / "world.json").read_text(encoding="utf-8"))
    structure = meta.get("structure", {})
    entities: dict = {}
    relations: list = []

    # Load entities
    for etype, fname in [
        ("character", structure.get("characters_file", "characters.json")),
        ("macro_faction", structure.get("factions_file", "factions.json")),
        ("location", structure.get("locations_file", "locations.json")),
    ]:
        path = root / fname
        if not path.exists():
            continue
        cls = {"character": Character, "macro_faction": MacroFaction, "location": Location}[etype]
        raw_list = _load_factions(path) if etype == "macro_faction" else _load_json(path)
        for raw in raw_list:
            if etype == "location":
                raw = _normalize_location(raw)
            entities[raw["id"]] = cls(**raw)

    # Load relations
    rel_path = root / structure.get("relations_file", "relations.json")
    if rel_path.exists():
        relations = [Relation(**r) for r in _load_json(rel_path)]

    # Load lifepacks
    lifepacks: dict = {}
    lp_dir = root / "lifepacks"
    if lp_dir.is_dir():
        for lp_path in sorted(lp_dir.glob("*.json")):
            lp = LifePack.model_validate(json.loads(lp_path.read_text(encoding="utf-8")))
            if lp.meta.entity_id:
                lifepacks[lp.meta.entity_id] = lp
        all_chars = [(eid, e.name, e.note) for eid, e in entities.items() if isinstance(e, Character)]
        for lp in lifepacks.values():
            populate_octave_7(lp, all_chars)

    ws = WorldState(
        world_id=meta["world_id"],
        seed=seed,
        phase=phase,
        description=meta.get("description", ""),
        entities=entities,
        relations=relations,
        active_macro_faction_ids=[
            eid for eid, e in entities.items()
            if e.entity_type == "macro_faction" and getattr(e, "status", "") != "dissolved"
        ],
        active_location_ids=[eid for eid, e in entities.items() if e.entity_type == "location"],
        tags=meta.get("tags", []),
        lifepacks=lifepacks,
    )

    if apply_variation:
        inv_path = root / structure.get("invariants_file", "invariants.json")
        apply_seed_variation(
            ws,
            invariants_path=inv_path if inv_path.exists() else None,
            catalogs=meta.get("catalogs"),
        )

    return ws
