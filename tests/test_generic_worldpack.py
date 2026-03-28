"""Test that Gigagen works with a non-Kilima worldpack.

Proves the engine is worldpack-agnostic: custom archetypes, notes,
statuses, and entity counts all work without touching Kilima data.
"""

from __future__ import annotations

from gigagen.core.entity import BaseEntity, Character, MacroFaction, Location
from gigagen.core.relation import Relation
from gigagen.core.world_state import WorldState
from gigagen.core.simulator import SimulatorState, build_simulator


def _build_mini_worldpack() -> tuple[WorldState, list[dict]]:
    """Build a minimal worldpack with non-Kilima data."""
    chars = [
        Character(
            id="char.warrior",
            entity_type="character",
            name="Arak",
            canon_level="fixed",
            archetype="WARRIOR",
            note="X1",
            hero_type="brute",
            civil_name="Arak",
            role_name="The Warrior",
            status="healthy",
            current_location_id="loc.village",
            current_macro_faction_id="fac.guild",
            emotional_load="calm",
        ),
        Character(
            id="char.mage",
            entity_type="character",
            name="Syra",
            canon_level="fixed",
            archetype="MAGE",
            note="X2",
            hero_type="sage",
            civil_name="Syra",
            role_name="The Mage",
            status="healthy",
            current_location_id="loc.tower",
            current_macro_faction_id="fac.guild",
            emotional_load="focused",
        ),
    ]
    facs = [
        MacroFaction(
            id="fac.guild",
            entity_type="macro_faction",
            name="Adventurers Guild",
            canon_level="fixed",
            status="active",
            base_location_id="loc.village",
        ),
    ]
    locs = [
        Location(
            id="loc.village",
            entity_type="location",
            name="Thornvale",
            canon_level="fixed",
            zone_level="low",
            status="peaceful",
            controlling_macro_faction_id="fac.guild",
        ),
        Location(
            id="loc.tower",
            entity_type="location",
            name="Arcane Tower",
            canon_level="fixed",
            zone_level="high",
            parent_location_id="loc.village",
            status="mystical",
        ),
    ]
    entities: dict[str, BaseEntity] = {}
    for ent in [*chars, *facs, *locs]:
        entities[ent.id] = ent

    ws = WorldState(
        world_id="world.testlands",
        seed=7,
        phase="contempo",
        description="A tiny test worldpack",
        entities=entities,
        relations=[],
        active_macro_faction_ids=["fac.guild"],
        active_location_ids=["loc.village", "loc.tower"],
    )

    # Minimal timeline: 2 events over 10 hours
    timeline = [
        {"id": "E01", "hour": 3, "name": "Goblin raid", "characters": ["warrior"]},
        {"id": "E02", "hour": 8, "name": "Ritual complete", "characters": ["mage"]},
    ]
    return ws, timeline


class TestMiniWorldpack:
    """Prove Gigagen works with completely non-Kilima data."""

    def test_worldstate_creates(self) -> None:
        ws, _ = _build_mini_worldpack()
        assert ws.world_id == "world.testlands"
        assert len(ws.entities) == 5  # 2 chars + 1 fac + 2 locs

    def test_custom_archetypes_accepted(self) -> None:
        ws, _ = _build_mini_worldpack()
        warrior = ws.entities["char.warrior"]
        assert isinstance(warrior, Character)
        assert warrior.archetype == "WARRIOR"
        assert warrior.note == "X1"

    def test_custom_statuses_accepted(self) -> None:
        ws, _ = _build_mini_worldpack()
        warrior = ws.entities["char.warrior"]
        assert isinstance(warrior, Character)
        assert warrior.status == "healthy"
        assert warrior.emotional_load == "calm"

    def test_build_simulator(self) -> None:
        ws, timeline = _build_mini_worldpack()
        sim = build_simulator(ws, timeline, max_hour=10)
        assert sim.max_hour == 10
        assert sim.current_hour == 0
        assert len(sim.outcomes) == 2

    def test_simulator_derives_max_hour_from_events(self) -> None:
        ws, timeline = _build_mini_worldpack()
        sim = build_simulator(ws, timeline)
        assert sim.max_hour == 8  # max hour from events

    def test_location_parent_hierarchy(self) -> None:
        ws, _ = _build_mini_worldpack()
        tower = ws.entities["loc.tower"]
        assert isinstance(tower, Location)
        assert tower.parent_location_id == "loc.village"

    def test_faction_with_custom_status(self) -> None:
        ws, _ = _build_mini_worldpack()
        guild = ws.entities["fac.guild"]
        assert isinstance(guild, MacroFaction)
        assert guild.status == "active"
