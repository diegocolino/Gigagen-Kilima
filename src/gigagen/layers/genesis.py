"""Genesis — Universo Primigenio.

Loads x.json (laws) + y.json (catalog), validates them,
produces a WorldState with catalogs and WORLD (root location level 1).

No seed. Deterministic. Same x + y → same result.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..core.entity import Location
from ..core.world_state import Catalogs, ElementDef, ModeDef, WorldState


class GenesisError(Exception):
    """Raised when Genesis validation fails."""


def run(ws: WorldState, config: dict) -> WorldState:
    """Execute Genesis layer.

    Args:
        ws: Input WorldState (typically empty).
        config: Must contain 'x_path' and 'y_path'.

    Returns:
        WorldState with phase='genesis', catalogs loaded, WORLD location created.

    Raises:
        GenesisError: If validation fails.
    """
    x_path = Path(config["x_path"])
    y_path = Path(config["y_path"])

    x = _load_json(x_path)
    y = _load_json(y_path)

    _validate_x(x)
    _validate_y(y)
    _validate_cross(x, y)

    catalogs = _build_catalogs(x, y)
    world_location = _build_world_location()

    ws = ws.model_copy(deep=True)
    ws.catalogs = catalogs
    ws.entities[world_location.id] = world_location
    ws.active_location_ids.append(world_location.id)
    ws.phase = "genesis"

    return ws


def _load_json(path: Path) -> dict[str, Any]:
    """Load a JSON file."""
    if not path.exists():
        raise GenesisError(f"File not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_x(x: dict[str, Any]) -> None:
    """Validate x.json structure and laws."""
    # Required keys
    required = ["archetypes", "modes", "scale_families", "entity_types", "canon_levels", "element_tiers"]
    for key in required:
        if key not in x:
            raise GenesisError(f"x.json missing required key: {key}")

    # Archetypes must be a list
    if not isinstance(x["archetypes"], list):
        raise GenesisError("x.json archetypes must be a list")

    # Each archetype must have code and name
    for arch in x["archetypes"]:
        if "code" not in arch or "name" not in arch:
            raise GenesisError(f"Archetype missing code or name: {arch}")

    # Modes must have intervals that sum to 12
    modes = x.get("modes", {})
    for name, mode_data in modes.items():
        if name.startswith("$"):  # Skip $doc fields
            continue
        intervals = mode_data.get("intervals", [])
        if sum(intervals) != 12:
            raise GenesisError(
                f"Mode '{name}' intervals sum to {sum(intervals)}, expected 12"
            )


def _validate_y(y: dict[str, Any]) -> None:
    """Validate y.json structure and catalog."""
    # Required keys
    required = ["chromatic_notes", "archetypes", "elements", "character_tiers", "item_tiers", "skill_tiers"]
    for key in required:
        if key not in y:
            raise GenesisError(f"y.json missing required key: {key}")

    # Exactly 12 chromatic notes
    notes = y["chromatic_notes"]
    if len(notes) != 12:
        raise GenesisError(f"y.json must have exactly 12 chromatic notes, got {len(notes)}")

    # Tiers must be non-empty lists
    for tier_key in ["character_tiers", "item_tiers", "skill_tiers"]:
        tiers = y.get(tier_key, [])
        if not tiers:
            raise GenesisError(f"y.json {tier_key} must be non-empty")

    # Elements: validate component references
    elements = y.get("elements", [])
    element_ids = {e["id"] for e in elements}
    for elem in elements:
        for comp in elem.get("components", []):
            if comp not in element_ids:
                raise GenesisError(
                    f"Element '{elem['id']}' references unknown component '{comp}'"
                )


def _validate_cross(x: dict[str, Any], y: dict[str, Any]) -> None:
    """Validate cross-references between x.json and y.json."""
    # All archetypes in y.json must have valid notes
    notes_set = set(y["chromatic_notes"])
    archetypes_x = {a["code"] for a in x["archetypes"]}
    archetypes_y = y.get("archetypes", {})

    # Filter out $doc keys
    archetypes_y = {k: v for k, v in archetypes_y.items() if not k.startswith("$")}

    for code, note in archetypes_y.items():
        if note not in notes_set:
            raise GenesisError(
                f"Archetype '{code}' has invalid note '{note}' (not in chromatic_notes)"
            )
        if code not in archetypes_x:
            raise GenesisError(
                f"Archetype '{code}' in y.json not defined in x.json"
            )

    # All archetype codes in x.json should have a note in y.json
    for code in archetypes_x:
        if code not in archetypes_y:
            raise GenesisError(
                f"Archetype '{code}' defined in x.json has no note assignment in y.json"
            )

    # Element tiers in y.json must match element_tiers in x.json
    valid_tiers = set(x.get("element_tiers", {}).keys())
    if not valid_tiers:
        # element_tiers might be a dict with descriptions
        valid_tiers = set(x.get("element_tiers", {}).keys())

    for elem in y.get("elements", []):
        tier = elem.get("tier")
        if valid_tiers and tier not in valid_tiers:
            raise GenesisError(
                f"Element '{elem['id']}' has tier '{tier}' not in x.json element_tiers"
            )


def _build_catalogs(x: dict[str, Any], y: dict[str, Any]) -> Catalogs:
    """Build Catalogs from x.json and y.json."""
    # Build elements dict
    elements: dict[str, ElementDef] = {}
    for elem in y.get("elements", []):
        elements[elem["id"]] = ElementDef(
            id=elem["id"],
            name=elem["name"],
            tier=elem["tier"],
            components=elem.get("components", []),
        )

    # Build modes dict
    modes: dict[str, ModeDef] = {}
    for name, mode_data in x.get("modes", {}).items():
        if name.startswith("$"):  # Skip $doc fields
            continue
        modes[name] = ModeDef(
            intervals=mode_data["intervals"],
            family=mode_data.get("family", ""),
            character=mode_data.get("character", ""),
        )

    # Build archetypes dict (filter $doc)
    archetypes = {
        k: v for k, v in y.get("archetypes", {}).items()
        if not k.startswith("$")
    }

    # Extract element_tiers keys
    element_tiers_raw = x.get("element_tiers", {})
    if isinstance(element_tiers_raw, dict):
        element_tiers = list(element_tiers_raw.keys())
    else:
        element_tiers = element_tiers_raw

    # Extract canon_levels keys
    canon_levels_raw = x.get("canon_levels", {})
    if isinstance(canon_levels_raw, dict):
        canon_levels = list(canon_levels_raw.keys())
    else:
        canon_levels = canon_levels_raw

    return Catalogs(
        notes=y["chromatic_notes"],
        archetypes=archetypes,
        elements=elements,
        modes=modes,
        scale_families=x.get("scale_families", []),
        entity_types=x.get("entity_types", []),
        canon_levels=canon_levels,
        element_tiers=element_tiers,
        character_tiers=y.get("character_tiers", []),
        location_levels=y.get("location_levels", ["world", "territory", "region", "area", "location", "room", "locker"]),
        item_tiers=y.get("item_tiers", []),
        skill_tiers=y.get("skill_tiers", []),
    )


def _build_world_location() -> Location:
    """Build the WORLD root location (level 1)."""
    return Location(
        id="loc.world",
        entity_type="location",
        name="WORLD",
        canon_level="fixed",
        tonic=None,  # WORLD has no tonic — it contains all
        zone_level="world",
        parent_location_id=None,
        description="The root location. Contains all other locations.",
        tags=["root"],
    )
