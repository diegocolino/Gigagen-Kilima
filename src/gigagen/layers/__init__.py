"""Escalera de Descendencia — pipeline layers.

Each layer transforms a WorldState into a richer one:
    Genesis    → laws + catalogs + WORLD location
    Theogony   → animas, lineages, L2 locations (no seed)
    Chronica   → seed enters here → generates the past
    Contempo   → present state, IN12, BN1
    Existence  → player enters (future)
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from . import genesis
from . import theogony
from . import chronica
from . import contempo
from . import existence

if TYPE_CHECKING:
    from ..core.world_state import WorldState

__all__ = [
    "genesis",
    "theogony",
    "chronica",
    "contempo",
    "existence",
    "run_pipeline",
]


def run_pipeline(
    worldpack_dir: str | Path,
    seed: int = 1,
) -> "WorldState":
    """Run the complete Escalera de Descendencia pipeline.

    Args:
        worldpack_dir: Path to the worldpack directory.
        seed: Deterministic seed for Chronica.

    Returns:
        WorldState with phase='contempo', fully populated.
    """
    from ..core.world_state import WorldState
    import json

    root = Path(worldpack_dir)
    meta = json.loads((root / "world.json").read_text(encoding="utf-8"))
    structure = meta.get("structure", {})

    # Initial WorldState
    ws = WorldState(
        world_id=meta["world_id"],
        seed=seed,
        phase="genesis",
        description=meta.get("description", ""),
        tags=meta.get("tags", []),
    )

    # Genesis: load x.json + y.json
    genesis_config = {
        "x_path": str(root / "x.json"),
        "y_path": str(root / "y.json"),
    }
    ws = genesis.run(ws, genesis_config)

    # Theogony: load lineages, animas, L2 locations
    theogony_config = {
        "lineages_path": str(root / "lineages.json"),
        "locations_path": str(root / structure.get("locations_file", "locations.json")),
    }
    ws = theogony.run(ws, theogony_config)

    # Chronica: seed enters, generate the past
    chronica_config = {}
    ws = chronica.run(ws, chronica_config, seed=seed)

    # Contempo: present state
    contempo_config = {
        "characters_path": str(root / structure.get("characters_file", "characters.json")),
        "factions_path": str(root / structure.get("factions_file", "factions.json")),
        "locations_path": str(root / structure.get("locations_file", "locations.json")),
        "relations_path": str(root / structure.get("relations_file", "relations.json")),
        "lifepacks_dir": str(root / "lifepacks"),
        "invariants_path": str(root / structure.get("invariants_file", "invariants.json")),
        "catalogs": meta.get("catalogs"),
    }
    ws = contempo.run(ws, contempo_config)

    return ws
