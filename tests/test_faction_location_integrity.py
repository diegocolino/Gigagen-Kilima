"""FL-3 — Faction ↔ Location cross-reference integrity tests.

Validates coherence between factions.json and locations.json:
- Every faction base points to a level 5 location
- Every faction root_note matches its leader's archetype note
- Relations of kind based_in point faction → level 5 location
"""

from __future__ import annotations

import json
import pathlib

import pytest

WORLDS_DIR = pathlib.Path(__file__).resolve().parent.parent / "worlds" / "kilima"
DOCS_DIR = pathlib.Path(__file__).resolve().parent.parent / "docs" / "kilima" / "data"


def _load_docs_json(name: str):
    return json.loads((DOCS_DIR / name).read_text(encoding="utf-8"))


class TestFactionLocationIntegrity:
    """Cross-reference validation between factions and locations."""

    @pytest.fixture(scope="class")
    def factions_data(self):
        data = _load_docs_json("factions.json")
        return data

    @pytest.fixture(scope="class")
    def locations_data(self):
        data = _load_docs_json("locations.json")
        return data["locations"]

    @pytest.fixture(scope="class")
    def characters_data(self):
        data = _load_docs_json("characters.json")
        return data["characters"]

    @pytest.fixture(scope="class")
    def relations_data(self):
        data = _load_docs_json("relations.json")
        return data["relations"]

    def test_macro_faction_count(self, factions_data) -> None:
        assert len(factions_data["macro_factions"]) == 10

    def test_faction_count(self, factions_data) -> None:
        assert len(factions_data["factions"]) >= 34

    def test_faction_bases_are_level_5(self, factions_data, locations_data) -> None:
        """Every faction with base_location_id → location exists at level 5."""
        level5 = {
            loc["id"]
            for loc in locations_data
            if loc.get("level") == "location"
        }
        bad = []
        for f in factions_data["factions"]:
            bid = f.get("base_location_id")
            if bid and bid not in level5:
                bad.append((f["id"], bid))
        assert not bad, f"Factions with bad base locations: {bad}"

    def test_root_note_matches_leader(self, factions_data, characters_data) -> None:
        """Every faction with a leader has root_note == leader's archetype note."""
        char_notes = {c["id"]: c["note"] for c in characters_data}
        mismatches = []
        for f in factions_data["factions"]:
            lid = f.get("leader_id")
            rn = f.get("root_note")
            if lid and rn:
                cn = char_notes.get(lid)
                if cn and cn != rn:
                    mismatches.append((f["id"], lid, rn, cn))
        assert not mismatches, f"Root note mismatches: {mismatches}"

    def test_based_in_relations_valid(self, relations_data, locations_data, factions_data) -> None:
        """Relations of kind based_in point faction → level 5 location."""
        fac_ids = {f["id"] for f in factions_data["factions"]}
        level5 = {
            loc["id"]
            for loc in locations_data
            if loc.get("level") == "location"
        }
        bad = []
        for r in relations_data:
            if r["kind"] == "based_in":
                if r["source_id"] not in fac_ids:
                    bad.append((r["id"], "bad source", r["source_id"]))
                if r["target_id"] not in level5:
                    bad.append((r["id"], "bad target", r["target_id"]))
        assert not bad, f"Bad based_in relations: {bad}"

    def test_no_member_of_to_macro_faction(self, relations_data, factions_data) -> None:
        """member_of and leader_of should point to factions, not macro-factions."""
        mfac_ids = {mf["id"] for mf in factions_data["macro_factions"]}
        bad = []
        for r in relations_data:
            if r["kind"] in ("member_of", "leader_of"):
                if r["target_id"] in mfac_ids:
                    bad.append((r["id"], r["kind"], r["target_id"]))
        assert not bad, f"Relations pointing to macro-faction: {bad}"
