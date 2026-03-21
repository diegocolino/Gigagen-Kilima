"""Interactive terminal console for Gigagen."""

from __future__ import annotations

import sys
from typing import TextIO

from gigagen.core.entity import Character, Faction, Location
from gigagen.core.relation import Relation, harmonic_affinity
from gigagen.core.world_state import WorldState
from gigagen.io.export_world_state import export_world_state


HELP_TEXT = """\
Commands:
  show world          — world state summary
  list characters     — the 12 with status
  list factions       — factions with state
  list locations      — locations with state
  inspect <id>        — full entity detail + relations
  inspect rel.<id>    — relations of an entity
  export [path]       — export world_state.json
  help                — show this help
  quit / exit         — exit console
"""


def _show_world(ws: WorldState, out: TextIO) -> None:
    chars = [e for e in ws.entities.values() if e.entity_type == "character"]
    facs = [e for e in ws.entities.values() if e.entity_type == "faction"]
    locs = [e for e in ws.entities.values() if e.entity_type == "location"]
    out.write(f"\n  World: {ws.world_id}\n")
    out.write(f"  Seed:  {ws.seed}\n")
    out.write(f"  Phase: {ws.phase}\n")
    out.write(f"  Characters: {len(chars)}  Factions: {len(facs)}  Locations: {len(locs)}\n")
    out.write(f"  Relations:  {len(ws.relations)}\n")
    out.write(f"  Tags: {', '.join(ws.tags) if ws.tags else '(none)'}\n\n")


def _list_characters(ws: WorldState, out: TextIO) -> None:
    chars = sorted(
        (e for e in ws.entities.values() if isinstance(e, Character)),
        key=lambda c: c.civil_name,
    )
    out.write(f"\n  {'Name':<12} {'Archetype':<6} {'Note':<4} {'Status':<14} {'Location':<16} {'Emotion'}\n")
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

    # Type-specific fields
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

    # Relations
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

        # Harmonic affinity for character pairs
        if isinstance(ent, Character):
            char_rels = [
                r for r in rels
                if ws.entities.get(
                    r.target_id if r.source_id == entity_id else r.source_id,
                ) is not None
                and isinstance(
                    ws.entities.get(
                        r.target_id if r.source_id == entity_id else r.source_id
                    ),
                    Character,
                )
            ]
            if char_rels:
                out.write(f"\n  Harmonic affinities:\n")
                seen = set()
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


def _handle_command(ws: WorldState, line: str, out: TextIO, output_dir: str) -> bool:
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
        _show_world(ws, out)
        return True

    if cmd == "list" and len(parts) >= 2:
        target = parts[1].lower()
        if target == "characters":
            _list_characters(ws, out)
        elif target == "factions":
            _list_factions(ws, out)
        elif target == "locations":
            _list_locations(ws, out)
        else:
            out.write(f"  Unknown list target: '{target}'. Try: characters, factions, locations\n")
        return True

    if cmd == "inspect" and len(parts) >= 2:
        target = parts[1]
        if target.startswith("rel."):
            # "inspect rel.char.rebel" → show relations of char.rebel
            entity_id = target[4:]  # strip "rel."
            _inspect_relations(ws, entity_id, out)
        else:
            _inspect_entity(ws, target, out)
        return True

    if cmd == "export":
        path = parts[1] if len(parts) >= 2 else f"{output_dir}/{ws.world_id}_seed_{ws.seed:03d}.json"
        result = export_world_state(ws, path)
        out.write(f"  Exported to {result}\n\n")
        return True

    out.write(f"  Unknown command: '{line.strip()}'. Type 'help' for commands.\n")
    return True


def run_console(
    ws: WorldState,
    output_dir: str = "outputs",
    *,
    input_stream: TextIO | None = None,
    output_stream: TextIO | None = None,
) -> None:
    """Run the interactive console loop."""
    inp = input_stream or sys.stdin
    out = output_stream or sys.stdout

    out.write(f"\n  Gigagen Console — {ws.world_id} (seed {ws.seed})\n")
    out.write(f"  Type 'help' for commands.\n\n")

    interactive = inp is sys.stdin and inp.isatty()

    while True:
        if interactive:
            try:
                line = input("gigagen> ")
            except (EOFError, KeyboardInterrupt):
                out.write("\n")
                break
        else:
            line = inp.readline()
            if not line:
                break

        if not _handle_command(ws, line, out, output_dir):
            break
