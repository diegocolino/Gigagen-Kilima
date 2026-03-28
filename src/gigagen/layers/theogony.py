"""Theogony — Universo Mágico.

Instantiates primordial entities: animas (16 elements), lineages (with element_pool
but no concrete element yet), level 2 locations.

No seed. Defines the rules for gambling but doesn't roll the dice yet.

IMPORTANT: Entities born in Theogony are NOT archetypized.
- No `note` field
- No `archetype` field
- Their relational system is elemental, not harmonic-chromatic
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..core.entity import Anima, Lineage, Location
from ..core.world_state import WorldState


class TheogonyError(Exception):
    """Raised when Theogony fails."""


def run(ws: WorldState, config: dict) -> WorldState:
    """Execute Theogony layer.

    Args:
        ws: WorldState from Genesis (must have catalogs).
        config: Worldpack configuration with paths.

    Returns:
        WorldState with phase='theogony', animas/lineages/L2 locations instantiated.

    Raises:
        TheogonyError: If required data is missing or invalid.
    """
    if ws.catalogs is None:
        raise TheogonyError("Theogony requires catalogs from Genesis")

    ws = ws.model_copy(deep=True)

    # Load animas from elements in catalogs (from y.json)
    ws = _load_animas(ws)

    # Load lineages from worldpack
    lineages_path = config.get("lineages_path")
    if lineages_path:
        ws = _load_lineages(ws, Path(lineages_path))

    # Load level 2 locations (territories) if present
    locations_path = config.get("locations_path")
    if locations_path:
        ws = _load_locations_l2(ws, Path(locations_path))

    # Items tier S and Skills tier S — stub for now
    # No data files exist yet, will be added in future patches

    ws.phase = "theogony"
    return ws


def _load_animas(ws: WorldState) -> WorldState:
    """Create Anima entities from the elements catalog.

    Each element in y.json becomes an Anima entity.
    """
    if ws.catalogs is None:
        return ws

    for element_id, element_def in ws.catalogs.elements.items():
        anima_id = f"anima.{element_id}"

        # Skip if already exists
        if anima_id in ws.entities:
            continue

        anima = Anima(
            id=anima_id,
            entity_type="anima",
            name=element_def.name,
            canon_level="fixed",
            element=element_id,
            tags=[f"tier_{element_def.tier}"],
            description=f"The primordial spirit of {element_def.name}.",
            visibility_class=_visibility_for_tier(element_def.tier),
        )
        ws.entities[anima_id] = anima

    return ws


def _visibility_for_tier(tier: str) -> str:
    """Determine visibility class based on element tier."""
    if tier == "supreme":
        return "supreme_only"
    if tier == "truncated":
        return "sensitive_only"
    return "visible"


def _load_lineages(ws: WorldState, path: Path) -> WorldState:
    """Load lineages from JSON file."""
    if not path.exists():
        return ws

    data = json.loads(path.read_text(encoding="utf-8"))
    lineages_list = data.get("lineages", [])

    if ws.catalogs is None:
        return ws

    valid_elements = set(ws.catalogs.elements.keys())

    for raw in lineages_list:
        lineage_id = raw["id"]

        # Skip if already exists
        if lineage_id in ws.entities:
            continue

        # Validate element_pool references valid elements
        element_pool = raw.get("element_pool", [])
        for elem in element_pool:
            if elem not in valid_elements:
                raise TheogonyError(
                    f"Lineage '{lineage_id}' references unknown element '{elem}'"
                )

        lineage = Lineage(
            id=lineage_id,
            entity_type="lineage",
            name=raw["name"],
            canon_level=raw.get("canon_level", "fixed"),
            tier=raw["tier"],
            element_pool=element_pool,
            status=raw.get("status", "relevant"),
            power=raw.get("power"),
            population=raw.get("population"),
            character_id=raw.get("character_id"),
            note_ref=raw.get("note_ref"),
            tags=raw.get("tags", []),
            description=raw.get("description", ""),
            # Seeded fields are None — Chronica resolves them
            element=None,
            founding_era=None,
            origin_location_id=None,
        )
        ws.entities[lineage_id] = lineage

    return ws


def _load_locations_l2(ws: WorldState, path: Path) -> WorldState:
    """Load level 2 (territory) locations from JSON file.

    Only loads locations with level="territory" — these are primordial,
    existing before history.
    """
    if not path.exists():
        return ws

    data = json.loads(path.read_text(encoding="utf-8"))

    # Handle both array format and object with "locations" key
    if isinstance(data, list):
        locations_list = data
    else:
        locations_list = data.get("locations", [])

    for raw in locations_list:
        level = raw.get("level", "")
        if level != "territory":
            continue

        loc_id = raw["id"]

        # Skip if already exists
        if loc_id in ws.entities:
            continue

        # Normalize parent reference — Genesis creates "loc.world" but JSON may say "world"
        parent = raw.get("parent", "loc.world")
        if parent == "world":
            parent = "loc.world"

        location = Location(
            id=loc_id,
            entity_type="location",
            name=raw.get("name", loc_id),
            canon_level=raw.get("canon_level", "fixed"),
            zone_level="territory",
            parent_location_id=parent,
            tonic=None,  # Tonic assignment happens in Chronica
            tags=raw.get("tags", []),
            description=raw.get("description", ""),
        )
        ws.entities[loc_id] = location
        ws.active_location_ids.append(loc_id)

    return ws
