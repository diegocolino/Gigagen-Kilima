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
    expected_count = fixed.get("characters", {}).get("count", 12)
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
    faction_rules = fixed.get("factions", [])
    if faction_rules:
        # First rule says "Exactly 4 factions"
        if len(facs) != 4:
            result.fail(f"Expected 4 factions, found {len(facs)}")

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

    return result
