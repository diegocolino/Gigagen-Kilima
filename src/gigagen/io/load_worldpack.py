"""Load a worldpack directory into a WorldState.

Thin coordinator: delegates to Escalera de Descendencia pipeline when
x.json/y.json exist, fallback to legacy loader otherwise.
"""

from __future__ import annotations

import json
import pathlib
from typing import Any

import yaml

from gigagen.core.world_state import DescendenceStep, WorldState
from gigagen.layers import run_pipeline

from .load_legacy import load_legacy_worldpack


def load_worldpack(
    worldpack_dir: str | pathlib.Path,
    seed: int = 1,
    phase: DescendenceStep = "contempo",
    *,
    apply_variation: bool = True,
) -> WorldState:
    """Load worldpack and build a WorldState.

    Uses the new pipeline if x.json/y.json exist, else falls back to legacy.
    """
    root = pathlib.Path(worldpack_dir)

    # New architecture: Escalera de Descendencia
    if (root / "x.json").exists() and (root / "y.json").exists():
        return run_pipeline(root, seed=seed)

    # Legacy: worldpacks without x.json/y.json
    return load_legacy_worldpack(root, seed, phase, apply_variation)


def load_timeline_events(worldpack_dir: str | pathlib.Path) -> list[dict[str, Any]]:
    """Load timeline events from the worldpack's YAML timeline."""
    root = pathlib.Path(worldpack_dir)
    meta = json.loads((root / "world.json").read_text(encoding="utf-8"))
    for _label, tl_file in meta.get("structure", {}).get("timelines", {}).items():
        tl_path = root / tl_file
        if tl_path.exists():
            data = yaml.safe_load(tl_path.read_text(encoding="utf-8"))
            events = data.get("events", [])
            return sorted(
                [e for e in events if e.get("hour") is not None],
                key=lambda e: (e["hour"], e.get("id", "")),
            )
    return []
