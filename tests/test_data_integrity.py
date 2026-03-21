"""C2 — Cross-reference validation tests for worldpack data integrity.

Ensures every entity reference in the Kilima worldpack resolves to a real
entity. If someone edits a JSON and introduces an orphan ID, these tests
catch it.
"""

from __future__ import annotations

import json
import pathlib
from typing import Any

import pytest
import yaml


WORLDS_DIR = pathlib.Path(__file__).resolve().parent.parent / "worlds" / "kilima"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_json(name: str) -> list[dict] | dict:
    return json.loads((WORLDS_DIR / name).read_text(encoding="utf-8"))


def _load_yaml(rel_path: str) -> dict:
    path = WORLDS_DIR / rel_path
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _all_entity_ids() -> set[str]:
    """Collect every entity ID across characters, factions, and locations."""
    ids: set[str] = set()
    for name in ("characters.json", "factions.json", "locations.json"):
        for entry in _load_json(name):
            ids.add(entry["id"])
    return ids


# ---------------------------------------------------------------------------
# Character location references
# ---------------------------------------------------------------------------

class TestCharacterLocations:
    def test_all_character_locations_exist(self) -> None:
        """Every current_location_id in characters.json resolves to a
        location in locations.json."""
        location_ids = {loc["id"] for loc in _load_json("locations.json")}
        characters = _load_json("characters.json")
        missing = []
        for c in characters:
            loc_id = c.get("current_location_id")
            if loc_id and loc_id not in location_ids:
                missing.append((c["id"], loc_id))
        assert not missing, f"Characters reference unknown locations: {missing}"


# ---------------------------------------------------------------------------
# Faction base location references
# ---------------------------------------------------------------------------

class TestFactionBases:
    def test_all_faction_bases_exist(self) -> None:
        """Every base_location_id in factions.json resolves to a location
        in locations.json."""
        location_ids = {loc["id"] for loc in _load_json("locations.json")}
        factions = _load_json("factions.json")
        missing = []
        for f in factions:
            base = f.get("base_location_id")
            if base and base not in location_ids:
                missing.append((f["id"], base))
        assert not missing, f"Factions reference unknown base locations: {missing}"


# ---------------------------------------------------------------------------
# Relation entity references
# ---------------------------------------------------------------------------

class TestRelationEntities:
    def test_all_relation_entities_exist(self) -> None:
        """Every source_id and target_id in relations.json exists in
        characters, factions, or locations."""
        all_ids = _all_entity_ids()
        relations = _load_json("relations.json")
        missing = []
        for r in relations:
            if r["source_id"] not in all_ids:
                missing.append((r["id"], "source_id", r["source_id"]))
            if r["target_id"] not in all_ids:
                missing.append((r["id"], "target_id", r["target_id"]))
        assert not missing, f"Relations reference unknown entities: {missing}"


# ---------------------------------------------------------------------------
# Event rules ↔ bn1.yaml cross-validation
# ---------------------------------------------------------------------------

class TestEventRules:
    @pytest.fixture(scope="class")
    def timeline_event_ids(self) -> set[str]:
        data = _load_yaml("timelines/bn1.yaml")
        return {e["id"] for e in data.get("events", [])}

    @pytest.fixture(scope="class")
    def event_rules(self) -> list[dict[str, Any]]:
        return _load_json("event_rules.json")

    @pytest.fixture(scope="class")
    def char_map(self) -> dict[str, str]:
        maps = _load_json("timeline_maps.json")
        return maps["character_map"]

    @pytest.fixture(scope="class")
    def location_ids(self) -> set[str]:
        return {loc["id"] for loc in _load_json("locations.json")}

    @pytest.fixture(scope="class")
    def faction_ids(self) -> set[str]:
        return {f["id"] for f in _load_json("factions.json")}

    def test_event_rules_reference_valid_events(
        self,
        event_rules: list[dict[str, Any]],
        timeline_event_ids: set[str],
    ) -> None:
        """Every event_id in event_rules.json exists in bn1.yaml."""
        missing = []
        for rule in event_rules:
            eid = rule["event_id"]
            if eid not in timeline_event_ids:
                missing.append(eid)
        assert not missing, f"Event rules reference unknown timeline events: {missing}"

    def test_event_rules_reference_valid_characters(
        self,
        event_rules: list[dict[str, Any]],
        char_map: dict[str, str],
    ) -> None:
        """Every character short name used in event_rules.json actions
        exists in timeline_maps.json character_map."""
        char_fields = (
            "move_characters", "set_emotions", "set_factions",
            "set_political", "set_status", "set_life_state", "set_bond_state",
        )
        missing = []
        for rule in event_rules:
            eid = rule["event_id"]
            for field in char_fields:
                if field in rule and isinstance(rule[field], dict):
                    for name in rule[field]:
                        if name not in char_map:
                            missing.append((eid, field, name))
            # set_captive and rescue are lists of char short names
            for field in ("set_captive", "rescue"):
                if field in rule and isinstance(rule[field], list):
                    for name in rule[field]:
                        if name not in char_map:
                            missing.append((eid, field, name))
            # move_active.characters
            if "move_active" in rule:
                for name in rule["move_active"].get("characters", []):
                    if name not in char_map:
                        missing.append((eid, "move_active.characters", name))
            # on_choice nested effects
            if "on_choice" in rule:
                for _choice, effects in rule["on_choice"].items():
                    if isinstance(effects, dict):
                        if "kill" in effects and effects["kill"] not in char_map:
                            missing.append((eid, "on_choice.kill", effects["kill"]))
                        for field in char_fields:
                            if field in effects and isinstance(effects[field], dict):
                                for name in effects[field]:
                                    if name not in char_map:
                                        missing.append((eid, f"on_choice.{field}", name))
        assert not missing, f"Event rules reference unknown characters: {missing}"

    def test_event_rules_reference_valid_locations(
        self,
        event_rules: list[dict[str, Any]],
        location_ids: set[str],
    ) -> None:
        """Every location ID used in event_rules.json exists in
        locations.json."""
        missing = []
        for rule in event_rules:
            eid = rule["event_id"]
            # move_characters values are loc.* IDs
            if "move_characters" in rule:
                for loc in rule["move_characters"].values():
                    if isinstance(loc, str) and loc not in location_ids:
                        missing.append((eid, "move_characters", loc))
            # move_active.location
            if "move_active" in rule:
                loc = rule["move_active"].get("location")
                if loc and loc not in location_ids:
                    missing.append((eid, "move_active.location", loc))
            # set_location_status keys are loc.* IDs
            if "set_location_status" in rule:
                for loc in rule["set_location_status"]:
                    if loc not in location_ids:
                        missing.append((eid, "set_location_status", loc))
        assert not missing, f"Event rules reference unknown locations: {missing}"

    def test_event_rules_reference_valid_factions(
        self,
        event_rules: list[dict[str, Any]],
        faction_ids: set[str],
    ) -> None:
        """Every faction ID used in set_factions actions exists in
        factions.json (null means 'remove from faction')."""
        missing = []
        for rule in event_rules:
            eid = rule["event_id"]
            if "set_factions" in rule:
                for fac in rule["set_factions"].values():
                    if fac is not None and fac not in faction_ids:
                        missing.append((eid, "set_factions", fac))
        assert not missing, f"Event rules reference unknown factions: {missing}"
