"""Timeline simulator — fully data-driven.

Processes events hour by hour, updating character states, resolving
variables at correct hours, and tracking cohesion. All worldpack-specific
data (ID mappings, event rules) is loaded from JSON files, not hardcoded.
"""

from __future__ import annotations

import json
import pathlib
import random
from dataclasses import dataclass, field
from typing import Any

from .entity import Character, Faction, Location, BaseEntity
from .world_state import WorldState


@dataclass
class EventLogEntry:
    hour: int
    event_id: str
    name: str
    description: str
    characters: list[str]
    phase: str = ""
    variable_resolved: str | None = None


@dataclass
class CharacterOutcome:
    character_id: str
    name: str
    life_state: str = "alive"
    bond_state: str = "unresolved"
    political_alignment: str = "aligned"
    location: str = ""


@dataclass
class SimulatorState:
    """Tracks simulation progress."""
    current_hour: int = 0
    max_hour: int = 62
    cohesion: float = 0.0
    event_log: list[EventLogEntry] = field(default_factory=list)
    outcomes: dict[str, CharacterOutcome] = field(default_factory=dict)
    resolved_variables: dict[str, str] = field(default_factory=dict)
    # Loaded data
    char_map: dict[str, str] = field(default_factory=dict)
    loc_map: dict[str, str] = field(default_factory=dict)
    event_rules: dict[str, dict[str, Any]] = field(default_factory=dict)


def _resolve_location(loc_raw: Any, loc_map: dict[str, str]) -> str | None:
    """Convert a timeline location to an entity id."""
    if loc_raw is None or loc_raw == "~":
        return None
    if isinstance(loc_raw, list):
        for loc in loc_raw:
            mapped = loc_map.get(str(loc))
            if mapped:
                return mapped
        return None
    return loc_map.get(str(loc_raw))


def _init_outcomes(ws: WorldState) -> dict[str, CharacterOutcome]:
    """Initialize outcomes from current character states."""
    outcomes: dict[str, CharacterOutcome] = {}
    for eid, ent in ws.entities.items():
        if not isinstance(ent, Character):
            continue
        life = "alive"
        if ent.status == "digitalized":
            life = "digitalized"
        elif ent.status == "dead":
            life = "dead"
        pol = "aligned"
        if ent.current_faction_id is None:
            pol = "conflicted"
        outcomes[eid] = CharacterOutcome(
            character_id=eid,
            name=ent.civil_name,
            life_state=life,
            location=ent.current_location_id,
            political_alignment=pol,
        )
    return outcomes


def load_timeline_maps(
    worldpack_dir: str | pathlib.Path,
) -> tuple[dict[str, str], dict[str, str]]:
    """Load character and location ID maps from the worldpack."""
    root = pathlib.Path(worldpack_dir)
    maps_path = root / "timeline_maps.json"
    if maps_path.exists():
        data = json.loads(maps_path.read_text(encoding="utf-8"))
        return data.get("character_map", {}), data.get("location_map", {})
    return {}, {}


def load_event_rules(
    worldpack_dir: str | pathlib.Path,
) -> dict[str, dict[str, Any]]:
    """Load event-specific transition rules from the worldpack."""
    root = pathlib.Path(worldpack_dir)
    rules_path = root / "event_rules.json"
    if rules_path.exists():
        raw = json.loads(rules_path.read_text(encoding="utf-8"))
        return {r["event_id"]: r for r in raw}
    return {}


def build_simulator(
    ws: WorldState,
    timeline_events: list[dict[str, Any]],
    *,
    char_map: dict[str, str] | None = None,
    loc_map: dict[str, str] | None = None,
    event_rules: dict[str, dict[str, Any]] | None = None,
) -> SimulatorState:
    """Create a SimulatorState initialized from the WorldState."""
    sim = SimulatorState()
    sim.outcomes = _init_outcomes(ws)
    sim.char_map = char_map or {}
    sim.loc_map = loc_map or {}
    sim.event_rules = event_rules or {}
    return sim


def _apply_rule(
    rule: dict[str, Any],
    ws: WorldState,
    sim: SimulatorState,
    rng: random.Random,
) -> str | None:
    """Apply a single event rule. Returns variable resolution string if any."""
    variable_resolved = None

    # -- Conditional check --
    cond = rule.get("conditional")
    if cond:
        var_id = cond["var_id"]
        expected = cond["value"]
        if sim.resolved_variables.get(var_id) != expected:
            return None

    # -- Resolve variable --
    var_cfg = rule.get("resolve_variable")
    if var_cfg:
        var_id = var_cfg["var_id"]
        options = var_cfg["options"]
        choice = rng.choice(options)
        sim.resolved_variables[var_id] = choice
        variable_resolved = f"{var_id}={choice}"
        # Apply choice-specific effects
        on_choice = rule.get("on_choice", {})
        choice_effects = on_choice.get(choice, {})
        if "set_emotions" in choice_effects:
            _apply_emotions(choice_effects["set_emotions"], ws, sim)
        if "set_bond_state" in choice_effects:
            for cname, state in choice_effects["set_bond_state"].items():
                cid = sim.char_map.get(cname)
                if cid and cid in sim.outcomes:
                    sim.outcomes[cid].bond_state = state
        if "kill" in choice_effects:
            cname = choice_effects["kill"]
            cid = sim.char_map.get(cname)
            if cid and cid in ws.entities:
                c = ws.entities[cid]
                if isinstance(c, Character):
                    c.status = "dead"
                    if cid in sim.outcomes:
                        sim.outcomes[cid].life_state = "dead"

    # -- Move characters to specific locations --
    for cname, loc_id in rule.get("move_characters", {}).items():
        cid = sim.char_map.get(cname)
        if cid and cid in ws.entities:
            c = ws.entities[cid]
            if isinstance(c, Character):
                c.current_location_id = loc_id
                if cid in sim.outcomes:
                    sim.outcomes[cid].location = loc_id

    # -- Move active characters --
    move_active = rule.get("move_active")
    if move_active:
        loc_id = move_active["location"]
        for cname in move_active["characters"]:
            cid = sim.char_map.get(cname)
            if cid and cid in ws.entities:
                c = ws.entities[cid]
                if isinstance(c, Character) and c.status == "active":
                    c.current_location_id = loc_id
                    if cid in sim.outcomes:
                        sim.outcomes[cid].location = loc_id

    # -- Set status --
    for cname, status in rule.get("set_status", {}).items():
        cid = sim.char_map.get(cname)
        if cid and cid in ws.entities:
            c = ws.entities[cid]
            if isinstance(c, Character):
                c.status = status

    # -- Set captive --
    for cname in rule.get("set_captive", []):
        cid = sim.char_map.get(cname)
        if cid and cid in ws.entities:
            c = ws.entities[cid]
            if isinstance(c, Character):
                c.status = "captive"

    # -- Set emotions --
    _apply_emotions(rule.get("set_emotions", {}), ws, sim)

    # -- Set factions --
    for cname, fac_id in rule.get("set_factions", {}).items():
        cid = sim.char_map.get(cname)
        if cid and cid in ws.entities:
            c = ws.entities[cid]
            if isinstance(c, Character):
                c.current_faction_id = fac_id

    # -- Set political alignment --
    for cname, pol in rule.get("set_political", {}).items():
        cid = sim.char_map.get(cname)
        if cid and cid in sim.outcomes:
            sim.outcomes[cid].political_alignment = pol

    # -- Set life_state --
    for cname, state in rule.get("set_life_state", {}).items():
        cid = sim.char_map.get(cname)
        if cid and cid in sim.outcomes:
            sim.outcomes[cid].life_state = state

    # -- Set bond_state --
    for cname, state in rule.get("set_bond_state", {}).items():
        cid = sim.char_map.get(cname)
        if cid and cid in sim.outcomes:
            sim.outcomes[cid].bond_state = state

    # -- Rescue --
    for cname in rule.get("rescue", []):
        cid = sim.char_map.get(cname)
        if cid and cid in ws.entities:
            c = ws.entities[cid]
            if isinstance(c, Character) and c.status == "captive":
                c.status = "active"
                if cid in sim.outcomes:
                    sim.outcomes[cid].life_state = "alive"

    # -- Set location status --
    for loc_id, changes in rule.get("set_location_status", {}).items():
        loc = ws.entities.get(loc_id)
        if isinstance(loc, Location):
            if "status" in changes:
                loc.status = changes["status"]
            if "tension" in changes:
                loc.tension = changes["tension"]

    return variable_resolved


def _apply_emotions(
    emotions: dict[str, str],
    ws: WorldState,
    sim: SimulatorState,
) -> None:
    for cname, emotion in emotions.items():
        cid = sim.char_map.get(cname)
        if cid and cid in ws.entities:
            c = ws.entities[cid]
            if isinstance(c, Character):
                c.emotional_load = emotion


def _apply_event_state_changes(
    event: dict[str, Any],
    ws: WorldState,
    sim: SimulatorState,
    rng: random.Random,
) -> str | None:
    """Apply state changes for a specific event."""
    eid = event.get("id", "")
    hour = event.get("hour")
    if hour is None:
        return None

    characters = event.get("characters", [])
    location_raw = event.get("location")
    loc_id = _resolve_location(location_raw, sim.loc_map)

    # -- Move characters to event location --
    if loc_id and characters:
        for char_name in characters:
            char_id = sim.char_map.get(str(char_name))
            if char_id and char_id in ws.entities:
                char = ws.entities[char_id]
                if isinstance(char, Character) and char.status == "active":
                    char.current_location_id = loc_id
                    if char_id in sim.outcomes:
                        sim.outcomes[char_id].location = loc_id

    # -- Cohesion changes --
    cohesion_delta = event.get("cohesion", 0)
    if cohesion_delta:
        sim.cohesion += cohesion_delta

    # -- Apply event rule if one exists --
    rule = sim.event_rules.get(eid)
    if rule:
        return _apply_rule(rule, ws, sim, rng)

    return None


def advance_to(
    ws: WorldState,
    sim: SimulatorState,
    target_hour: int,
    timeline_events: list[dict[str, Any]],
    seed: int,
) -> list[EventLogEntry]:
    """Advance the simulation from current_hour to target_hour.

    Processes all events with hours in (current_hour, target_hour].
    Returns list of new log entries.
    """
    rng = random.Random(seed)
    # Advance RNG state for consistency
    for _ in range(sim.current_hour):
        rng.random()

    target = min(target_hour, sim.max_hour)
    new_entries: list[EventLogEntry] = []

    pending = [
        e for e in timeline_events
        if e.get("hour") is not None
        and sim.current_hour < e["hour"] <= target
    ]
    pending.sort(key=lambda e: (e["hour"], e.get("id", "")))

    for event in pending:
        var_resolved = _apply_event_state_changes(event, ws, sim, rng)

        chars_in_event = event.get("characters", [])
        char_ids = [sim.char_map.get(str(c), str(c)) for c in chars_in_event]

        entry = EventLogEntry(
            hour=event["hour"],
            event_id=event.get("id", "?"),
            name=event.get("name", ""),
            description=event.get("description", ""),
            characters=char_ids,
            phase=event.get("phase", ""),
            variable_resolved=var_resolved,
        )
        new_entries.append(entry)
        sim.event_log.append(entry)

    sim.current_hour = target
    return new_entries
