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

from .entity import Character, MacroFaction, Location, BaseEntity
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
    # Harmonic enrichment (Phase 4)
    location_id: str | None = None
    location_tonic: str | None = None
    modal_influence: str | None = None          # controlling faction id
    character_affinities: dict[str, float] = field(default_factory=dict)


@dataclass
class CharacterOutcome:
    character_id: str
    name: str
    life_state: str = "alive"
    bond_state: str = "unresolved"
    political_alignment: str = "aligned"
    location: str = ""
    location_affinity: float | None = None      # current location affinity


@dataclass
class SimulatorState:
    """Tracks simulation progress."""
    current_hour: int = 0
    max_hour: int = 0
    cohesion: float = 0.0
    event_log: list[EventLogEntry] = field(default_factory=list)
    outcomes: dict[str, CharacterOutcome] = field(default_factory=dict)
    resolved_variables: dict[str, str] = field(default_factory=dict)
    # Loaded data
    char_map: dict[str, str] = field(default_factory=dict)
    loc_map: dict[str, str] = field(default_factory=dict)
    event_rules: dict[str, dict[str, Any]] = field(default_factory=dict)
    # Harmonic state (Phase 4)
    character_affinities: dict[str, float | None] = field(default_factory=dict)


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
        life = "dead" if ent.status == "dead" else "alive"
        pol = "aligned"
        if ent.current_macro_faction_id is None:
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


def _calc_character_location_affinity(
    char: Character,
    loc: Location,
    ws: WorldState,
) -> float | None:
    """Calculate a character's affinity with a location using the harmonic engine.

    Returns None if no tonic is set on the location (graceful null handling).
    """
    from .harmony import character_location_affinity

    if loc.tonic is None:
        return None

    # Get controlling faction's intervals
    faction_intervals = None
    if loc.controlling_macro_faction_id:
        fac = ws.entities.get(loc.controlling_macro_faction_id)
        if isinstance(fac, MacroFaction) and fac.intervals:
            faction_intervals = fac.intervals

    return character_location_affinity(
        char.note, loc.tonic, faction_intervals,
    )


def _update_character_affinity(
    char_id: str,
    ws: WorldState,
    sim: SimulatorState,
) -> None:
    """Recalculate and store a character's affinity with their current location."""
    char = ws.entities.get(char_id)
    if not isinstance(char, Character):
        return
    loc = ws.entities.get(char.current_location_id)
    if not isinstance(loc, Location):
        return
    aff = _calc_character_location_affinity(char, loc, ws)
    sim.character_affinities[char_id] = aff
    if char_id in sim.outcomes:
        sim.outcomes[char_id].location_affinity = aff


def _update_location_affinities(
    loc_id: str,
    ws: WorldState,
    sim: SimulatorState,
) -> None:
    """Recalculate affinity for ALL characters currently at a location."""
    for eid, ent in ws.entities.items():
        if isinstance(ent, Character) and ent.current_location_id == loc_id:
            _update_character_affinity(eid, ws, sim)


def _get_event_harmonic_data(
    loc_id: str | None,
    ws: WorldState,
    sim: SimulatorState,
    char_ids: list[str],
) -> tuple[str | None, str | None, str | None, dict[str, float]]:
    """Extract harmonic metadata for an event log entry.

    Returns (location_id, tonic, modal_influence_faction_id, character_affinities).
    """
    if not loc_id:
        return None, None, None, {}

    loc = ws.entities.get(loc_id)
    if not isinstance(loc, Location):
        return loc_id, None, None, {}

    tonic = loc.tonic
    modal = loc.controlling_macro_faction_id

    affinities: dict[str, float] = {}
    for cid in char_ids:
        aff = sim.character_affinities.get(cid)
        if aff is not None:
            affinities[cid] = aff

    return loc_id, tonic, modal, affinities


def build_simulator(
    ws: WorldState,
    timeline_events: list[dict[str, Any]],
    *,
    char_map: dict[str, str] | None = None,
    loc_map: dict[str, str] | None = None,
    event_rules: dict[str, dict[str, Any]] | None = None,
    max_hour: int | None = None,
) -> SimulatorState:
    """Create a SimulatorState initialized from the WorldState."""
    sim = SimulatorState()
    sim.outcomes = _init_outcomes(ws)
    sim.char_map = char_map or {}
    sim.loc_map = loc_map or {}
    sim.event_rules = event_rules or {}

    # Derive max_hour from timeline events if not explicitly provided
    if max_hour is not None:
        sim.max_hour = max_hour
    elif timeline_events:
        sim.max_hour = max(e.get("hour", 0) for e in timeline_events)
    # else stays at 0

    # Calculate initial harmonic affinities for all characters
    for eid, ent in ws.entities.items():
        if isinstance(ent, Character):
            _update_character_affinity(eid, ws, sim)

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
                _update_character_affinity(cid, ws, sim)

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
                    _update_character_affinity(cid, ws, sim)

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
                c.current_macro_faction_id = fac_id

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
            if "controlling_macro_faction_id" in changes:
                loc.controlling_macro_faction_id = changes["controlling_macro_faction_id"]
            # Recalculate affinities for all characters at this location
            _update_location_affinities(loc_id, ws, sim)

    # -- Unlock lifepack slots --
    for unlock in rule.get("unlock_lifepack_slot", []):
        _cname = unlock.get("character")
        _octave = unlock.get("octave")
        _slot_key = unlock.get("slot_key")
        if _cname and _octave and _slot_key:
            _cid = sim.char_map.get(_cname)
            if _cid:
                _unlock_lifepack_slot(ws, sim, _cid, _octave, _slot_key)

    return variable_resolved


def _unlock_lifepack_slot(
    ws: WorldState,
    sim: SimulatorState,
    char_id: str,
    octave_name: str,
    slot_key: str,
) -> None:
    """Unlock a specific slot in a character's Life Pack."""
    from .lifepack import LifePackSlot

    lp = ws.lifepacks.get(char_id)
    if lp is None:
        return
    octave = getattr(lp, octave_name, None)
    if octave is None:
        return
    slot = octave.slots.get(slot_key)
    if slot is None or not isinstance(slot, LifePackSlot):
        return
    if slot.locked:
        slot.locked = False
        slot.unlocked = True
        # Record in outcomes
        char_name = ""
        char = ws.entities.get(char_id)
        if isinstance(char, Character):
            char_name = char.civil_name
        if char_id not in sim.outcomes:
            return
        entity_desc = slot.entity_name or slot_key
        sim.outcomes[char_id].bond_state = (
            f"unlocked {entity_desc} ({octave_name}, {slot_key})"
        )


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
                    _update_character_affinity(char_id, ws, sim)

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

        # Resolve event location for harmonic enrichment
        location_raw = event.get("location")
        event_loc_id = _resolve_location(location_raw, sim.loc_map)
        h_loc_id, h_tonic, h_modal, h_affs = _get_event_harmonic_data(
            event_loc_id, ws, sim, char_ids,
        )

        entry = EventLogEntry(
            hour=event["hour"],
            event_id=event.get("id", "?"),
            name=event.get("name", ""),
            description=event.get("description", ""),
            characters=char_ids,
            phase=event.get("phase", ""),
            variable_resolved=var_resolved,
            location_id=h_loc_id,
            location_tonic=h_tonic,
            modal_influence=h_modal,
            character_affinities=h_affs,
        )
        new_entries.append(entry)
        sim.event_log.append(entry)

    sim.current_hour = target
    return new_entries
