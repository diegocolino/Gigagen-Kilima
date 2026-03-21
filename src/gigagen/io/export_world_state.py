"""Export a WorldState to JSON."""

from __future__ import annotations

import json
import pathlib

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
