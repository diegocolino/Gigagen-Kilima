"""Modal screens for the Gigagen TUI."""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal, Center
from textual.screen import ModalScreen
from textual.widgets import Static, Label, Input, Button, DataTable

from gigagen.core.entity import Character, Faction, Location
from gigagen.core.relation import harmonic_affinity
from gigagen.core.world_state import WorldState
from gigagen.core.simulator import SimulatorState


class HelpScreen(ModalScreen[None]):
    """Help overlay showing all hotkeys."""

    BINDINGS = [("escape", "dismiss", "Close"), ("question_mark", "dismiss", "Close")]

    DEFAULT_CSS = """
    HelpScreen {
        align: center middle;
    }
    #help-dialog {
        width: 70;
        height: auto;
        max-height: 80%;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }
    """

    HELP_TEXT = """\
[b]GIGAGEN TUI — GOD MODE[/b]

[b]Time Control[/b]
  →          Step forward 1 hour
  Shift+→    Step forward 5 hours
  ←          Step backward 1 hour
  Shift+←    Step backward 5 hours
  Home       Jump to H00
  End        Jump to H62
  Space      Pause / Resume auto-play
  p          Toggle auto-play
  +/-        Speed up / slow down (0.1s–5.0s)

[b]Panels[/b]
  c          Focus Characters
  f          Focus Factions
  l          Focus Locations
  e          Focus Event Log
  Tab        Cycle focus

[b]Inspection[/b]
  Enter      Inspect selected entity
  r          Show relations
  o          Show outcomes

[b]Global[/b]
  s          Change seed
  x          Export world state JSON
  ?          Help (this screen)
  q          Quit
"""

    def compose(self) -> ComposeResult:
        with Vertical(id="help-dialog"):
            yield Static(self.HELP_TEXT)
            with Center():
                yield Button("Close", variant="primary", id="help-close")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "help-close":
            self.dismiss(None)


class SeedPickerScreen(ModalScreen[int | None]):
    """Modal for entering a new seed."""

    BINDINGS = [("escape", "dismiss_none", "Cancel")]

    DEFAULT_CSS = """
    SeedPickerScreen {
        align: center middle;
    }
    #seed-dialog {
        width: 40;
        height: auto;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }
    #seed-input {
        margin: 1 0;
    }
    """

    def __init__(self, current_seed: int) -> None:
        super().__init__()
        self.current_seed = current_seed

    def compose(self) -> ComposeResult:
        with Vertical(id="seed-dialog"):
            yield Label(f"Current seed: {self.current_seed}")
            yield Label("Enter new seed (integer):")
            yield Input(
                placeholder="e.g. 42",
                id="seed-input",
                type="integer",
            )
            with Horizontal():
                yield Button("OK", variant="primary", id="seed-ok")
                yield Button("Cancel", id="seed-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "seed-ok":
            self._submit()
        elif event.button.id == "seed-cancel":
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._submit()

    def _submit(self) -> None:
        inp = self.query_one("#seed-input", Input)
        try:
            val = int(inp.value)
            self.dismiss(val)
        except ValueError:
            inp.value = ""
            inp.placeholder = "Must be an integer!"

    def action_dismiss_none(self) -> None:
        self.dismiss(None)


class InspectorScreen(ModalScreen[None]):
    """Full entity detail inspector."""

    BINDINGS = [("escape", "dismiss", "Close")]

    DEFAULT_CSS = """
    InspectorScreen {
        align: center middle;
    }
    #inspector-dialog {
        width: 80;
        height: auto;
        max-height: 85%;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
        overflow-y: auto;
    }
    """

    def __init__(self, entity_id: str, ws: WorldState, sim: SimulatorState) -> None:
        super().__init__()
        self.entity_id = entity_id
        self.ws = ws
        self.sim = sim

    def compose(self) -> ComposeResult:
        content = self._build_content()
        with Vertical(id="inspector-dialog"):
            yield Static(content, id="inspector-content")
            with Center():
                yield Button("Close", variant="primary", id="inspector-close")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "inspector-close":
            self.dismiss(None)

    def _build_content(self) -> str:
        ent = self.ws.entities.get(self.entity_id)
        if ent is None:
            return f"Entity '{self.entity_id}' not found."

        lines: list[str] = []
        lines.append(f"[b]=== {ent.name} ({ent.id}) ===[/b]")
        lines.append(f"Type: {ent.entity_type}  Canon: {ent.canon_level}")
        if ent.description:
            lines.append(f"[dim]{ent.description}[/dim]")

        if isinstance(ent, Character):
            lines.append("")
            lines.append("[b]Identity[/b]")
            lines.append(f"  Archetype: {ent.archetype}  Note: {ent.note}  Hero: {ent.hero_type}")
            lines.append(f"  Civil: {ent.civil_name}  Role: {ent.role_name}")
            lines.append(f"  Lineage: {ent.lineage or '(none)'}")
            lines.append("")
            lines.append("[b]State[/b]")
            lines.append(f"  Status:   {ent.status}  Emotion: {ent.emotional_load}")
            lines.append(f"  Location: {ent.current_location_id}")
            lines.append(f"  Faction:  {ent.current_faction_id or '(none)'}")

            # Outcome
            oc = self.sim.outcomes.get(self.entity_id)
            if oc:
                lines.append("")
                lines.append("[b]Outcome[/b]")
                lines.append(f"  Life: {oc.life_state}  Bond: {oc.bond_state}")
                lines.append(f"  Politics: {oc.political_alignment}  Location: {oc.location}")

        elif isinstance(ent, Faction):
            lines.append("")
            lines.append(f"Doctrine: {', '.join(ent.doctrine_tags)}")
            lines.append(f"Base: {ent.base_location_id}  Leader: {ent.leader_id or '(none)'}")
            lines.append(f"Status: {ent.status}  Power: {ent.power:.2f}  Cohesion: {ent.cohesion:.2f}")

        elif isinstance(ent, Location):
            lines.append("")
            lines.append(f"Zone: {ent.zone_level}  Biome: {', '.join(ent.biome_tags)}")
            lines.append(f"Status: {ent.status}  Tension: {ent.tension:.2f}  Access: {ent.access}")
            lines.append(f"Controller: {ent.controlling_faction_id or '(none)'}")

        # Relations
        rels = [
            r for r in self.ws.relations
            if r.source_id == self.entity_id or r.target_id == self.entity_id
        ]
        if rels:
            lines.append("")
            lines.append(f"[b]Relations ({len(rels)})[/b]")
            for r in rels:
                other_id = r.target_id if r.source_id == self.entity_id else r.source_id
                direction = "\u2192" if r.source_id == self.entity_id else "\u2190"
                pol_sym = {1: "+", 0: "~", -1: "-"}.get(r.polarity, "?")
                other_name = self.ws.entities[other_id].name if other_id in self.ws.entities else other_id
                lines.append(f"  {direction} {other_name} ({r.kind}) w={r.weight:.1f} pol={pol_sym}")

            # Harmonic affinities for characters
            if isinstance(ent, Character):
                char_others = set()
                for r in rels:
                    oid = r.target_id if r.source_id == self.entity_id else r.source_id
                    other = self.ws.entities.get(oid)
                    if isinstance(other, Character) and oid not in char_others:
                        char_others.add(oid)
                if char_others:
                    lines.append("")
                    lines.append("[b]Harmonic Affinities[/b]")
                    for oid in sorted(char_others):
                        other = self.ws.entities[oid]
                        if isinstance(other, Character):
                            aff = harmonic_affinity(ent.note, other.note)
                            color = "green" if aff > 0 else "red" if aff < 0 else "white"
                            lines.append(
                                f"  {ent.note} \u2192 {other.note} ({other.civil_name}): "
                                f"[{color}]{aff:+.2f}[/{color}]"
                            )

        return "\n".join(lines)


class RelationsScreen(ModalScreen[None]):
    """Shows all relations for a selected entity."""

    BINDINGS = [("escape", "dismiss", "Close")]

    DEFAULT_CSS = """
    RelationsScreen {
        align: center middle;
    }
    #relations-dialog {
        width: 80;
        height: auto;
        max-height: 80%;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
        overflow-y: auto;
    }
    """

    def __init__(self, entity_id: str, ws: WorldState) -> None:
        super().__init__()
        self.entity_id = entity_id
        self.ws = ws

    def compose(self) -> ComposeResult:
        ent = self.ws.entities.get(self.entity_id)
        name = ent.name if ent else self.entity_id
        rels = [
            r for r in self.ws.relations
            if r.source_id == self.entity_id or r.target_id == self.entity_id
        ]

        lines = [f"[b]Relations for {name}[/b] ({len(rels)})\n"]
        for r in rels:
            other_id = r.target_id if r.source_id == self.entity_id else r.source_id
            direction = "\u2192" if r.source_id == self.entity_id else "\u2190"
            pol_sym = {1: "+", 0: "~", -1: "-"}.get(r.polarity, "?")
            other_name = self.ws.entities[other_id].name if other_id in self.ws.entities else other_id
            lines.append(
                f"  {direction} {other_name:<20} {r.kind:<26} "
                f"w={r.weight:.1f} pol={pol_sym} [{r.canon_level}]"
            )

        with Vertical(id="relations-dialog"):
            yield Static("\n".join(lines))
            with Center():
                yield Button("Close", variant="primary", id="rel-close")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "rel-close":
            self.dismiss(None)


class OutcomesScreen(ModalScreen[None]):
    """Shows character outcomes summary."""

    BINDINGS = [("escape", "dismiss", "Close")]

    DEFAULT_CSS = """
    OutcomesScreen {
        align: center middle;
    }
    #outcomes-dialog {
        width: 80;
        height: auto;
        max-height: 80%;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
        overflow-y: auto;
    }
    """

    def __init__(self, sim: SimulatorState, current_hour: int) -> None:
        super().__init__()
        self.sim = sim
        self.current_hour = current_hour

    def compose(self) -> ComposeResult:
        lines = [f"[b]Outcomes at H{self.current_hour:02d}[/b]\n"]
        header = f"  {'Name':<12} {'Life':<14} {'Bond':<14} {'Politics':<14} {'Location'}"
        lines.append(header)
        lines.append(f"  {'-'*12} {'-'*14} {'-'*14} {'-'*14} {'-'*16}")
        for oc in sorted(self.sim.outcomes.values(), key=lambda o: o.name):
            life_color = "red" if oc.life_state == "dead" else "green" if oc.life_state == "alive" else "yellow"
            lines.append(
                f"  {oc.name:<12} [{life_color}]{oc.life_state:<14}[/{life_color}] "
                f"{oc.bond_state:<14} {oc.political_alignment:<14} {oc.location}"
            )

        with Vertical(id="outcomes-dialog"):
            yield Static("\n".join(lines))
            with Center():
                yield Button("Close", variant="primary", id="outcomes-close")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "outcomes-close":
            self.dismiss(None)
