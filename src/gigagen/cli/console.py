"""Interactive terminal console for Gigagen."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Any, TextIO

from gigagen.core.entity import Character, Faction, Location
from gigagen.core.relation import Relation, harmonic_affinity
from gigagen.core.world_state import WorldState
from gigagen.core.simulator import (
    SimulatorState,
    build_simulator,
    advance_to,
)
from gigagen.io.export_world_state import export_world_state


HELP_TEXT = """\
Commands:
  show world          -- world state summary
  list characters     -- the 12 with status
  list factions       -- factions with state
  list locations      -- locations with state
  inspect <id>        -- full entity detail + relations
  inspect rel.<id>    -- relations of an entity
  advance [N]         -- advance N hours (default 1)
  hour                -- show current hour and active events
  outcomes            -- show dramatic states of the 12
  log [N]             -- show last N event log entries (default 10)
  export [path]       -- export world_state.json
  help                -- show this help
  quit / exit         -- exit console
"""


@dataclass
class ConsoleContext:
    ws: WorldState
    sim: SimulatorState
    timeline_events: list[dict[str, Any]]
    output_dir: str = "outputs"


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def _show_world(ctx: ConsoleContext, out: TextIO) -> None:
    ws = ctx.ws
    chars = [e for e in ws.entities.values() if e.entity_type == "character"]
    facs = [e for e in ws.entities.values() if e.entity_type == "faction"]
    locs = [e for e in ws.entities.values() if e.entity_type == "location"]
    out.write(f"\n  World: {ws.world_id}\n")
    out.write(f"  Seed:  {ws.seed}\n")
    out.write(f"  Phase: {ws.phase}\n")
    out.write(f"  Hour:  H{ctx.sim.current_hour:02d} / H{ctx.sim.max_hour:02d}\n")
    out.write(f"  Cohesion: {ctx.sim.cohesion:+.1f}\n")
    out.write(f"  Characters: {len(chars)}  Factions: {len(facs)}  Locations: {len(locs)}\n")
    out.write(f"  Relations:  {len(ws.relations)}\n")
    # Show resolved variables
    if ctx.sim.resolved_variables:
        vars_str = ", ".join(f"{k}={v}" for k, v in sorted(ctx.sim.resolved_variables.items()))
        out.write(f"  Variables: {vars_str}\n")
    out.write(f"  Tags: {', '.join(ws.tags) if ws.tags else '(none)'}\n\n")


def _list_characters(ws: WorldState, out: TextIO) -> None:
    chars = sorted(
        (e for e in ws.entities.values() if isinstance(e, Character)),
        key=lambda c: c.civil_name,
    )
    out.write(f"\n  {'Name':<12} {'Arch':<6} {'Note':<4} {'Status':<14} {'Location':<16} {'Emotion'}\n")
    out.write(f"  {'-'*12} {'-'*6} {'-'*4} {'-'*14} {'-'*16} {'-'*10}\n")
    for c in chars:
        out.write(
            f"  {c.civil_name:<12} {c.archetype:<6} {c.note:<4} "
            f"{c.status:<14} {c.current_location_id:<16} {c.emotional_load}\n"
        )
    out.write("\n")


def _list_factions(ws: WorldState, out: TextIO) -> None:
    facs = sorted(
        (e for e in ws.entities.values() if isinstance(e, Faction)),
        key=lambda f: f.name,
    )
    out.write(f"\n  {'Name':<20} {'Status':<14} {'Power':>6} {'Cohesion':>9} {'Leader'}\n")
    out.write(f"  {'-'*20} {'-'*14} {'-'*6} {'-'*9} {'-'*16}\n")
    for f in facs:
        leader = f.leader_id or "(none)"
        out.write(
            f"  {f.name:<20} {f.status:<14} {f.power:>6.2f} {f.cohesion:>9.2f} {leader}\n"
        )
    out.write("\n")


def _list_locations(ws: WorldState, out: TextIO) -> None:
    locs = sorted(
        (e for e in ws.entities.values() if isinstance(e, Location)),
        key=lambda loc: loc.name,
    )
    out.write(f"\n  {'Name':<22} {'Zone':<10} {'Status':<12} {'Tension':>8} {'Access':<14} {'Controller'}\n")
    out.write(f"  {'-'*22} {'-'*10} {'-'*12} {'-'*8} {'-'*14} {'-'*16}\n")
    for loc in locs:
        ctrl = loc.controlling_faction_id or "(none)"
        out.write(
            f"  {loc.name:<22} {loc.zone_level:<10} {loc.status:<12} "
            f"{loc.tension:>8.2f} {loc.access:<14} {ctrl}\n"
        )
    out.write("\n")


def _get_entity_relations(ws: WorldState, entity_id: str) -> list[Relation]:
    return [
        r for r in ws.relations
        if r.source_id == entity_id or r.target_id == entity_id
    ]


def _inspect_entity(ws: WorldState, entity_id: str, out: TextIO) -> None:
    ent = ws.entities.get(entity_id)
    if ent is None:
        out.write(f"  Entity '{entity_id}' not found.\n\n")
        return

    out.write(f"\n  === {ent.name} ({ent.id}) ===\n")
    out.write(f"  Type: {ent.entity_type}  Canon: {ent.canon_level}\n")
    if ent.description:
        out.write(f"  {ent.description}\n")

    if isinstance(ent, Character):
        out.write(f"\n  Identity:\n")
        out.write(f"    Archetype:  {ent.archetype}  Note: {ent.note}  Hero: {ent.hero_type}\n")
        out.write(f"    Civil name: {ent.civil_name}  Role: {ent.role_name}\n")
        out.write(f"    Lineage:    {ent.lineage or '(none)'}\n")
        out.write(f"\n  State:\n")
        out.write(f"    Status:   {ent.status}  Emotion: {ent.emotional_load}\n")
        out.write(f"    Location: {ent.current_location_id}\n")
        out.write(f"    Faction:  {ent.current_faction_id or '(none)'}\n")
    elif isinstance(ent, Faction):
        out.write(f"\n  Doctrine: {', '.join(ent.doctrine_tags)}\n")
        out.write(f"  Base: {ent.base_location_id}  Leader: {ent.leader_id or '(none)'}\n")
        out.write(f"  Status: {ent.status}  Power: {ent.power:.2f}  Cohesion: {ent.cohesion:.2f}\n")
    elif isinstance(ent, Location):
        out.write(f"\n  Zone: {ent.zone_level}  Biome: {', '.join(ent.biome_tags)}\n")
        out.write(f"  Status: {ent.status}  Tension: {ent.tension:.2f}  Access: {ent.access}\n")
        out.write(f"  Controller: {ent.controlling_faction_id or '(none)'}\n")

    rels = _get_entity_relations(ws, entity_id)
    if rels:
        out.write(f"\n  Relations ({len(rels)}):\n")
        for r in rels:
            other_id = r.target_id if r.source_id == entity_id else r.source_id
            direction = "->" if r.source_id == entity_id else "<-"
            polarity_sym = {1: "+", 0: "~", -1: "-"}.get(r.polarity, "?")
            out.write(
                f"    {direction} {other_id:<22} {r.kind:<26} "
                f"w={r.weight:.1f} pol={polarity_sym}\n"
            )

        if isinstance(ent, Character):
            char_rels = [
                r for r in rels
                if isinstance(
                    ws.entities.get(
                        r.target_id if r.source_id == entity_id else r.source_id
                    ),
                    Character,
                )
            ]
            if char_rels:
                out.write(f"\n  Harmonic affinities:\n")
                seen: set[str] = set()
                for r in char_rels:
                    other_id = r.target_id if r.source_id == entity_id else r.source_id
                    if other_id in seen:
                        continue
                    seen.add(other_id)
                    other = ws.entities[other_id]
                    if isinstance(other, Character):
                        aff = harmonic_affinity(ent.note, other.note)
                        out.write(
                            f"    {ent.note} -> {other.note} ({other.civil_name}): "
                            f"{aff:+.2f}\n"
                        )
    out.write("\n")


def _inspect_relations(ws: WorldState, entity_id: str, out: TextIO) -> None:
    rels = _get_entity_relations(ws, entity_id)
    if not rels:
        out.write(f"  No relations found for '{entity_id}'.\n\n")
        return
    out.write(f"\n  Relations for {entity_id} ({len(rels)}):\n")
    for r in rels:
        other_id = r.target_id if r.source_id == entity_id else r.source_id
        direction = "->" if r.source_id == entity_id else "<-"
        polarity_sym = {1: "+", 0: "~", -1: "-"}.get(r.polarity, "?")
        out.write(
            f"    {r.id:<42} {direction} {other_id:<22} "
            f"{r.kind:<26} w={r.weight:.1f} pol={polarity_sym}\n"
        )
    out.write("\n")


# ---------------------------------------------------------------------------
# Simulation commands
# ---------------------------------------------------------------------------

def _cmd_advance(ctx: ConsoleContext, parts: list[str], out: TextIO) -> None:
    n = 1
    if len(parts) >= 2:
        try:
            n = int(parts[1])
        except ValueError:
            out.write("  Usage: advance [N]  (N = number of hours)\n")
            return

    if ctx.sim.current_hour >= ctx.sim.max_hour:
        out.write(f"  Already at H{ctx.sim.max_hour:02d}. Timeline complete.\n\n")
        return

    target = min(ctx.sim.current_hour + n, ctx.sim.max_hour)
    new_entries = advance_to(ctx.ws, ctx.sim, target, ctx.timeline_events, ctx.ws.seed)

    out.write(f"\n  Advanced H{ctx.sim.current_hour - n if ctx.sim.current_hour >= n else 0:02d} -> H{ctx.sim.current_hour:02d}")
    out.write(f"  (cohesion: {ctx.sim.cohesion:+.1f})\n")

    if new_entries:
        for entry in new_entries:
            marker = " ***" if entry.variable_resolved else ""
            out.write(f"    H{entry.hour:02d} [{entry.event_id}] {entry.name}{marker}\n")
            if entry.variable_resolved:
                out.write(f"         >> VARIABLE RESOLVED: {entry.variable_resolved}\n")
    else:
        out.write("    (no events in this window)\n")
    out.write("\n")


def _cmd_hour(ctx: ConsoleContext, out: TextIO) -> None:
    out.write(f"\n  Current hour: H{ctx.sim.current_hour:02d} / H{ctx.sim.max_hour:02d}\n")
    out.write(f"  Cohesion: {ctx.sim.cohesion:+.1f}\n")

    # Show events at current hour
    current_events = [
        e for e in ctx.timeline_events
        if e.get("hour") == ctx.sim.current_hour
    ]
    if current_events:
        out.write(f"  Events at H{ctx.sim.current_hour:02d}:\n")
        for ev in current_events:
            chars = ", ".join(str(c) for c in ev.get("characters", []))
            out.write(f"    [{ev.get('id', '?')}] {ev.get('name', '')}  ({chars})\n")
    else:
        out.write(f"  No events at H{ctx.sim.current_hour:02d}.\n")

    # Show resolved variables
    if ctx.sim.resolved_variables:
        out.write(f"  Resolved variables:\n")
        for k, v in sorted(ctx.sim.resolved_variables.items()):
            out.write(f"    {k} = {v}\n")
    out.write("\n")


def _cmd_outcomes(ctx: ConsoleContext, out: TextIO) -> None:
    out.write(f"\n  Outcomes at H{ctx.sim.current_hour:02d}:\n")
    out.write(f"  {'Name':<12} {'Life':<14} {'Bond':<14} {'Politics':<14} {'Location'}\n")
    out.write(f"  {'-'*12} {'-'*14} {'-'*14} {'-'*14} {'-'*16}\n")
    for oc in sorted(ctx.sim.outcomes.values(), key=lambda o: o.name):
        out.write(
            f"  {oc.name:<12} {oc.life_state:<14} {oc.bond_state:<14} "
            f"{oc.political_alignment:<14} {oc.location}\n"
        )
    out.write("\n")


def _cmd_log(ctx: ConsoleContext, parts: list[str], out: TextIO) -> None:
    n = 10
    if len(parts) >= 2:
        try:
            n = int(parts[1])
        except ValueError:
            pass
    entries = ctx.sim.event_log[-n:]
    if not entries:
        out.write("  No events logged yet. Use 'advance' to progress.\n\n")
        return
    out.write(f"\n  Event log (last {len(entries)}):\n")
    for entry in entries:
        marker = " ***" if entry.variable_resolved else ""
        out.write(f"    H{entry.hour:02d} [{entry.event_id:<16}] {entry.name}{marker}\n")
        if entry.variable_resolved:
            out.write(f"         >> {entry.variable_resolved}\n")
    out.write("\n")


# ---------------------------------------------------------------------------
# Command dispatcher
# ---------------------------------------------------------------------------

def _handle_command(ctx: ConsoleContext, line: str, out: TextIO) -> bool:
    """Process one command. Returns False to quit."""
    parts = line.strip().split()
    if not parts:
        return True

    cmd = parts[0].lower()

    if cmd in ("quit", "exit"):
        return False

    if cmd == "help":
        out.write(HELP_TEXT)
        return True

    if cmd == "show" and len(parts) >= 2 and parts[1].lower() == "world":
        _show_world(ctx, out)
        return True

    if cmd == "list" and len(parts) >= 2:
        target = parts[1].lower()
        if target == "characters":
            _list_characters(ctx.ws, out)
        elif target == "factions":
            _list_factions(ctx.ws, out)
        elif target == "locations":
            _list_locations(ctx.ws, out)
        else:
            out.write(f"  Unknown list target: '{target}'. Try: characters, factions, locations\n")
        return True

    if cmd == "inspect" and len(parts) >= 2:
        target = parts[1]
        if target.startswith("rel."):
            entity_id = target[4:]
            _inspect_relations(ctx.ws, entity_id, out)
        else:
            _inspect_entity(ctx.ws, target, out)
        return True

    if cmd == "advance":
        _cmd_advance(ctx, parts, out)
        return True

    if cmd == "hour":
        _cmd_hour(ctx, out)
        return True

    if cmd == "outcomes":
        _cmd_outcomes(ctx, out)
        return True

    if cmd == "log":
        _cmd_log(ctx, parts, out)
        return True

    if cmd == "export":
        path = parts[1] if len(parts) >= 2 else f"{ctx.output_dir}/{ctx.ws.world_id}_seed_{ctx.ws.seed:03d}.json"
        result = export_world_state(ctx.ws, path)
        out.write(f"  Exported to {result}\n\n")
        return True

    out.write(f"  Unknown command: '{line.strip()}'. Type 'help' for commands.\n")
    return True


def run_console(
    ws: WorldState,
    output_dir: str = "outputs",
    *,
    timeline_events: list[dict[str, Any]] | None = None,
    char_map: dict[str, str] | None = None,
    loc_map: dict[str, str] | None = None,
    event_rules: dict[str, dict[str, Any]] | None = None,
    input_stream: TextIO | None = None,
    output_stream: TextIO | None = None,
) -> None:
    """Run the interactive console loop."""
    inp = input_stream or sys.stdin
    out = output_stream or sys.stdout

    sim = build_simulator(
        ws, timeline_events or [],
        char_map=char_map,
        loc_map=loc_map,
        event_rules=event_rules,
    )
    ctx = ConsoleContext(
        ws=ws,
        sim=sim,
        timeline_events=timeline_events or [],
        output_dir=output_dir,
    )

    out.write(f"\n  Gigagen Console -- {ws.world_id} (seed {ws.seed})\n")
    out.write(f"  Timeline: H00 -> H{sim.max_hour:02d} ({len(timeline_events or [])} events)\n")
    out.write(f"  Type 'help' for commands.\n\n")

    interactive = inp is sys.stdin and inp.isatty()

    while True:
        if interactive:
            try:
                prompt = f"H{sim.current_hour:02d}> "
                line = input(prompt)
            except (EOFError, KeyboardInterrupt):
                out.write("\n")
                break
        else:
            line = inp.readline()
            if not line:
                break

        if not _handle_command(ctx, line, out):
            break
