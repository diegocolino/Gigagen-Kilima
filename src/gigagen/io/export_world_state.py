"""Export a WorldState to JSON."""

from __future__ import annotations

import json
import pathlib

from gigagen.core.entity import Character, Faction, Location
from gigagen.core.world_state import WorldState


def export_world_state(
    ws: WorldState,
    output_path: str | pathlib.Path,
    *,
    indent: int = 2,
) -> pathlib.Path:
    """Serialize a WorldState to a JSON file.

    Returns the resolved output path.
    """
    path = pathlib.Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(ws.model_dump_json(indent=indent), encoding="utf-8")
    return path.resolve()


def save_worldpack(
    ws: WorldState,
    worldpack_dir: str | pathlib.Path,
    *,
    indent: int = 2,
) -> None:
    """Write modified entities back to their source JSON files.

    Saves characters.json, factions.json, locations.json, and relations.json.
    """
    wp = pathlib.Path(worldpack_dir)

    chars = [
        e.model_dump(mode="json")
        for e in sorted(ws.entities.values(), key=lambda e: e.id)
        if isinstance(e, Character)
    ]
    facs = [
        e.model_dump(mode="json")
        for e in sorted(ws.entities.values(), key=lambda e: e.id)
        if isinstance(e, Faction)
    ]
    locs = [
        e.model_dump(mode="json")
        for e in sorted(ws.entities.values(), key=lambda e: e.id)
        if isinstance(e, Location)
    ]
    rels = [r.model_dump(mode="json") for r in ws.relations]

    for name, data in [
        ("characters.json", chars),
        ("factions.json", facs),
        ("locations.json", locs),
        ("relations.json", rels),
    ]:
        (wp / name).write_text(
            json.dumps(data, indent=indent, ensure_ascii=False),
            encoding="utf-8",
        )
