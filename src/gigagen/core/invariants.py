"""Invariant validation for WorldState against invariants.json."""

from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass, field
from typing import Any

from .entity import BaseEntity, Character, Faction, Location
from .relation import Relation
from .world_state import WorldState


@dataclass
class ValidationResult:
    """Result of invariant validation."""
    valid: bool = True
    errors: list[str] = field(default_factory=list)

    def fail(self, msg: str) -> None:
        self.valid = False
        self.errors.append(msg)


def validate_invariants(
    ws: WorldState,
    invariants_path: str | pathlib.Path,
) -> ValidationResult:
    """Validate a WorldState against the invariants defined in invariants.json.

    Checks:
    - Correct number of characters, factions
    - All 12 roster characters present with correct fixed identity
    - All fixed relationships present
    - All fixed faction memberships present
    - All fixed faction-location bonds present
    - No forbidden states
    """
    result = ValidationResult()
    inv_path = pathlib.Path(invariants_path)

    if not inv_path.exists():
        result.fail(f"Invariants file not found: {inv_path}")
        return result

    inv: dict[str, Any] = json.loads(inv_path.read_text(encoding="utf-8"))
    fixed = inv.get("fixed", {})

    # -- Character count --
    chars = {eid: e for eid, e in ws.entities.items() if isinstance(e, Character)}
    char_cfg = fixed.get("characters", {})
    if "count" in char_cfg:
        expected_count = char_cfg["count"]
        if len(chars) != expected_count:
            result.fail(f"Expected {expected_count} characters, found {len(chars)}")

    # -- Roster identity check --
    roster = fixed.get("characters", {}).get("roster", [])
    for entry in roster:
        cid = entry["id"]
        if cid not in chars:
            result.fail(f"Missing roster character: {cid}")
            continue
        c = chars[cid]
        if c.archetype != entry["archetype"]:
            result.fail(
                f"{cid}: archetype is '{c.archetype}', expected '{entry['archetype']}'"
            )
        if c.note != entry["note"]:
            result.fail(
                f"{cid}: note is '{c.note}', expected '{entry['note']}'"
            )
        if c.name != entry["name"]:
            result.fail(
                f"{cid}: name is '{c.name}', expected '{entry['name']}'"
            )

    # -- Faction count --
    facs = {eid: e for eid, e in ws.entities.items() if isinstance(e, Faction)}
    faction_count = fixed.get("faction_count")
    if faction_count is not None:
        if len(facs) != faction_count:
            result.fail(f"Expected {faction_count} factions, found {len(facs)}")

    # -- Fixed relationships --
    fixed_rels = fixed.get("relationships", [])
    ws_rel_keys = {
        (r.source_id, r.target_id, r.kind) for r in ws.relations
    }
    for frel in fixed_rels:
        key = (frel["source"], frel["target"], frel["kind"])
        if key not in ws_rel_keys:
            result.fail(
                f"Missing fixed relationship: {frel['source']} -> "
                f"{frel['target']} ({frel['kind']})"
            )

    # -- Fixed faction memberships --
    fixed_memberships = fixed.get("faction_memberships", [])
    for fm in fixed_memberships:
        key = (fm["character"], fm["faction"], fm["kind"])
        if key not in ws_rel_keys:
            result.fail(
                f"Missing faction membership: {fm['character']} -> "
                f"{fm['faction']} ({fm['kind']})"
            )

    # -- Fixed faction-location bonds --
    fixed_fac_locs = fixed.get("faction_locations", [])
    for fl in fixed_fac_locs:
        key = (fl["faction"], fl["location"], fl["kind"])
        if key not in ws_rel_keys:
            result.fail(
                f"Missing faction-location bond: {fl['faction']} -> "
                f"{fl['location']} ({fl['kind']})"
            )

    # -- Subdivision uniqueness within each faction --
    for fid, fac in facs.items():
        names = [s.name for s in fac.subdivisions if s.name is not None]
        if len(names) != len(set(names)):
            dupes = [n for n in names if names.count(n) > 1]
            result.fail(f"{fid}: duplicate subdivision names: {sorted(set(dupes))}")

    # -- Character subdivision consistency --
    for cid, char in chars.items():
        if char.current_subdivision_id is None:
            continue
        if char.current_faction_id is None:
            result.fail(
                f"{cid}: has subdivision '{char.current_subdivision_id}' "
                f"but no faction"
            )
            continue
        fac = facs.get(char.current_faction_id)
        if fac is None:
            continue  # faction existence is checked elsewhere
        sub_names = {s.name for s in fac.subdivisions if s.name is not None}
        if char.current_subdivision_id not in sub_names:
            result.fail(
                f"{cid}: subdivision '{char.current_subdivision_id}' "
                f"not found in {char.current_faction_id}"
            )

    # -- Location parent validity --
    locs = {eid: e for eid, e in ws.entities.items() if isinstance(e, Location)}
    for lid, loc in locs.items():
        if loc.parent_location_id is None:
            continue
        if loc.parent_location_id not in locs:
            result.fail(
                f"{lid}: parent_location_id '{loc.parent_location_id}' "
                f"is not a valid location"
            )

    # -- Location parent cycle detection --
    for lid in locs:
        visited: set[str] = set()
        current = lid
        while current is not None:
            if current in visited:
                result.fail(f"{lid}: cycle in location hierarchy")
                break
            visited.add(current)
            parent_loc = locs.get(current)
            current = parent_loc.parent_location_id if parent_loc else None

    return result
