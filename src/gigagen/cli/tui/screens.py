"""Modal screens for the Gigagen TUI."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal, Center, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Static, Label, Input, Button, DataTable, Select

from gigagen.core.entity import Character, Faction, Location
from gigagen.core.harmony import (
    character_faction_affinity,
    character_location_affinity,
    location_instability,
    subdivision_weight,
)
from gigagen.core.relation import harmonic_affinity
from gigagen.core.world_state import WorldState
from gigagen.core.simulator import SimulatorState

if TYPE_CHECKING:
    from .bridge import SimulatorBridge


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
  Enter      Inspect / Edit selected entity
  r          Show relations for entity
  R          Global relations browser
  o          Show outcomes

[b]Editing[/b]
  Enter      Open editor (Char/Faction/Location)
  a          Add subdivision (in faction editor)
  d          Delete subdivision (in faction editor)

[b]Relations Browser (R)[/b]
  0/1/2/3    Filter: All / Char↔Char / Char→Fac / Fac→Loc
  w/k/n      Sort by: Weight / Kind / Name
  n          Create new relation (derived)

[b]Global[/b]
  Ctrl+S     Save worldpack to JSON
  v          Validate invariants
  h          Harmonic dashboard
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
            lines.append("[b]Harmonic[/b]")
            lines.append(f"  Mode: {ent.mode or '(none)'}  Family: {ent.scale_family or '(none)'}  Notes: {ent.note_count}")
            if ent.intervals:
                lines.append(f"  Intervals: {ent.intervals}")
            if ent.subdivisions:
                lines.append("")
                lines.append(f"[b]Subdivisions ({len(ent.subdivisions)})[/b]")
                for sub in ent.subdivisions:
                    name = sub.name or "(unnamed)"
                    note = sub.note or "-"
                    leader = sub.leader_id or "-"
                    lines.append(f"  {name:<28} root={note:<4} leader={leader}")
            lines.append("")
            lines.append("[b]State[/b]")
            lines.append(f"  Base: {ent.base_location_id or '(none)'}  Leader: {ent.leader_id or '(none)'}")
            lines.append(f"  Status: {ent.status}  Power: {ent.power:.2f}  Cohesion: {ent.cohesion:.2f}")

        elif isinstance(ent, Location):
            lines.append("")
            tonic = ent.tonic or "(none)"
            lines.append(f"Zone: {ent.zone_level}  Tonic: {tonic}  Biome: {', '.join(ent.biome_tags)}")
            lines.append(f"Status: {ent.status}  Tension: {ent.tension:.2f}  Access: {ent.access}")
            lines.append(f"Controller: {ent.controlling_faction_id or '(none)'}")
            if ent.parent_location_id:
                lines.append(f"Parent: {ent.parent_location_id}")
            if ent.secondary_faction_ids:
                lines.append(f"Secondary: {', '.join(ent.secondary_faction_ids)}")

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


class GlobalRelationsScreen(ModalScreen[None]):
    """Global relations browser with filtering and sorting."""

    BINDINGS = [
        ("escape", "dismiss", "Close"),
        ("1", "filter_cc", "Char\u2194Char"),
        ("2", "filter_cf", "Char\u2192Fac"),
        ("3", "filter_fl", "Fac\u2192Loc"),
        ("0", "filter_all", "All"),
        ("w", "sort_weight", "Sort:Weight"),
        ("k", "sort_kind", "Sort:Kind"),
        ("s", "sort_source", "Sort:Source"),
        ("n", "new_relation", "New Rel"),
    ]

    DEFAULT_CSS = """
    GlobalRelationsScreen {
        align: center middle;
    }
    #global-rel-dialog {
        width: 90%;
        height: 85%;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }
    #rel-filter-bar {
        height: 3;
        dock: top;
        padding: 0 1;
    }
    """

    def __init__(self, ws: WorldState, bridge: "SimulatorBridge | None" = None) -> None:
        super().__init__()
        self.ws = ws
        self._bridge = bridge
        self._current_filter: str | None = None

    def compose(self) -> ComposeResult:
        from .widgets import RelationsTable
        with Vertical(id="global-rel-dialog"):
            with Horizontal(id="rel-filter-bar"):
                yield Static(
                    "[b]RELATIONS[/b]  "
                    "[dim]0[/dim]=All  [dim]1[/dim]=Char\u2194Char  "
                    "[dim]2[/dim]=Char\u2192Fac  [dim]3[/dim]=Fac\u2192Loc  |  "
                    "[dim]w[/dim]=Sort:Weight  [dim]k[/dim]=Sort:Kind  [dim]n[/dim]=Sort:Name"
                )
            yield RelationsTable(id="global-rel-table")
            with Center():
                yield Button("Close", variant="primary", id="global-rel-close")

    def on_mount(self) -> None:
        from .widgets import RelationsTable
        table = self.query_one("#global-rel-table", RelationsTable)
        table.set_data(list(self.ws.relations), dict(self.ws.entities))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "global-rel-close":
            self.dismiss(None)

    def _get_rel_table(self):
        from .widgets import RelationsTable
        return self.query_one("#global-rel-table", RelationsTable)

    def action_filter_cc(self) -> None:
        self._current_filter = "cc" if self._current_filter != "cc" else None
        self._get_rel_table().set_filter(self._current_filter)

    def action_filter_cf(self) -> None:
        self._current_filter = "cf" if self._current_filter != "cf" else None
        self._get_rel_table().set_filter(self._current_filter)

    def action_filter_fl(self) -> None:
        self._current_filter = "fl" if self._current_filter != "fl" else None
        self._get_rel_table().set_filter(self._current_filter)

    def action_filter_all(self) -> None:
        self._current_filter = None
        self._get_rel_table().set_filter(None)

    def action_sort_weight(self) -> None:
        self._get_rel_table().set_sort("weight")

    def action_sort_kind(self) -> None:
        self._get_rel_table().set_sort("kind")

    def action_sort_source(self) -> None:
        self._get_rel_table().set_sort("source")

    def action_new_relation(self) -> None:
        if self._bridge is None:
            return

        def on_result(created: bool) -> None:
            if created:
                # Refresh the table with updated relations
                from .widgets import RelationsTable
                table = self.query_one("#global-rel-table", RelationsTable)
                table.set_data(list(self.ws.relations), dict(self.ws.entities))

        self.app.push_screen(NewRelationScreen(self._bridge), on_result)


class FactionEditorScreen(ModalScreen[bool]):
    """Full editor for a faction: status, power, cohesion, subdivisions, members."""

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("a", "add_subdivision", "Add Sub"),
        ("d", "delete_subdivision", "Del Sub"),
    ]

    DEFAULT_CSS = """
    FactionEditorScreen {
        align: center middle;
    }
    #fac-editor-dialog {
        width: 85%;
        height: 90%;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
        overflow-y: auto;
    }
    .fac-section-title {
        text-style: bold;
        margin: 1 0 0 0;
    }
    .fac-locked {
        color: $text-disabled;
    }
    #fac-error {
        color: red;
        margin: 1 0;
    }
    .fac-field-row {
        height: 3;
        margin: 0 1;
    }
    """

    def __init__(self, faction_id: str, bridge: "SimulatorBridge") -> None:
        super().__init__()
        self.faction_id = faction_id
        self.bridge = bridge
        self._error_widget: Static | None = None

    def compose(self) -> ComposeResult:
        ws = self.bridge.ws
        fac = ws.entities[self.faction_id]
        if not isinstance(fac, Faction):
            return

        with VerticalScroll(id="fac-editor-dialog"):
            # Header — locked identity
            yield Static(
                f"[b]=== {fac.name} ===[/b]\n"
                f"[dim]Mode: {fac.mode}  Family: {fac.scale_family}  "
                f"Notes: {fac.note_count}  Intervals: {fac.intervals}[/dim]",
                classes="fac-locked",
            )

            # Editable properties
            yield Static("[b]Properties[/b]", classes="fac-section-title")
            catalogs = self.bridge.catalogs
            fac_statuses = catalogs.get("faction_statuses") or sorted({
                e.status for e in ws.entities.values() if isinstance(e, Faction)
            })
            status_options = [(s, s) for s in fac_statuses]
            with Horizontal(classes="fac-field-row"):
                yield Label("Status: ")
                yield Select(
                    [(s[0], s[1]) for s in status_options],
                    value=fac.status,
                    id="fac-status",
                )
            with Horizontal(classes="fac-field-row"):
                yield Label("Power (0.0-1.0): ")
                yield Input(value=f"{fac.power:.2f}", id="fac-power", type="number")
            with Horizontal(classes="fac-field-row"):
                yield Label("Cohesion (0.0-1.0): ")
                yield Input(value=f"{fac.cohesion:.2f}", id="fac-cohesion", type="number")

            # Leader select
            members = [
                e for e in ws.entities.values()
                if isinstance(e, Character) and e.current_faction_id == self.faction_id
            ]
            leader_opts: list[tuple[str, str | None]] = [("(none)", None)]
            for m in sorted(members, key=lambda c: c.civil_name):
                leader_opts.append((f"{m.civil_name} ({m.archetype})", m.id))
            with Horizontal(classes="fac-field-row"):
                yield Label("Leader: ")
                yield Select(
                    leader_opts,
                    value=fac.leader_id,
                    id="fac-leader",
                )

            # Subdivisions table with political weight
            yield Static(
                f"[b]Subdivisions ({len(fac.subdivisions)})[/b]  "
                f"[dim]a=add  d=delete[/dim]",
                classes="fac-section-title",
            )
            sub_table = DataTable(id="fac-sub-table")
            sub_table.cursor_type = "row"
            sub_table.add_columns("Name", "Root Note", "Leader", "Type", "Members", "Weight")
            # Compute subdivision weights
            all_sub_roots = [s.note for s in fac.subdivisions if s.note]
            for sub in fac.subdivisions:
                sub_name = sub.name or "(unnamed)"
                sub_note = sub.note or "-"
                sub_leader = "-"
                if sub.leader_id and sub.leader_id in ws.entities:
                    sub_leader = ws.entities[sub.leader_id].name
                sub_type = sub.type or "-"
                member_count = sum(
                    1 for e in ws.entities.values()
                    if isinstance(e, Character)
                    and e.current_faction_id == self.faction_id
                    and e.current_subdivision_id == sub.name
                )
                # Political weight
                if sub.note:
                    others = [r for r in all_sub_roots if r != sub.note]
                    weight = subdivision_weight(sub.note, others)
                    weight_str = f"{weight:.2f}"
                else:
                    weight_str = "-"
                sub_table.add_row(
                    sub_name, sub_note, sub_leader, sub_type,
                    str(member_count), weight_str,
                    key=sub.name or f"_sub_{fac.subdivisions.index(sub)}",
                )
            yield sub_table

            # Members table with affinity — Enter to reassign subdivision
            yield Static(
                "[b]Members[/b]  [dim]Enter on member to reassign subdivision[/dim]",
                classes="fac-section-title",
            )
            mem_table = DataTable(id="fac-mem-table")
            mem_table.cursor_type = "row"
            mem_table.add_columns("Character", "Note", "Archetype", "Subdivision", "Affinity")
            for m in sorted(members, key=lambda c: c.civil_name):
                sub_id = m.current_subdivision_id or "-"
                sub_root = None
                if m.current_subdivision_id:
                    for s in fac.subdivisions:
                        if s.name == m.current_subdivision_id:
                            sub_root = s.note
                            break
                aff = character_faction_affinity(m.note, fac.intervals, sub_root)
                if aff >= 0.3:
                    aff_str = f"[green]{aff:+.2f}[/green]"
                elif aff <= -0.3:
                    aff_str = f"[red]{aff:+.2f}[/red]"
                else:
                    aff_str = f"[yellow]{aff:+.2f}[/yellow]"
                mem_table.add_row(
                    m.civil_name, m.note, m.archetype, sub_id, aff_str,
                    key=m.id,
                )
            yield mem_table

            # Error area
            yield Static("", id="fac-error")

            # Buttons
            with Center():
                with Horizontal():
                    yield Button("Save", variant="primary", id="fac-save")
                    yield Button("Cancel", id="fac-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "fac-cancel":
            self.dismiss(False)
        elif event.button.id == "fac-save":
            self._save()

    def action_cancel(self) -> None:
        self.dismiss(False)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle Enter on member table → reassign subdivision."""
        if event.data_table.id != "fac-mem-table":
            return
        char_id = str(event.row_key.value)
        ws = self.bridge.ws
        fac = ws.entities.get(self.faction_id)
        if not isinstance(fac, Faction):
            return
        char = ws.entities.get(char_id)
        if not isinstance(char, Character):
            return

        # Build subdivision options with affinity scores
        sub_opts: list[tuple[str, str | None]] = [("(none)", None)]
        for sub in fac.subdivisions:
            if sub.name is None:
                continue
            aff = character_faction_affinity(char.note, fac.intervals, sub.note)
            aff_label = f"{aff:+.2f}" if sub.note else "n/a"
            sub_opts.append((f"{sub.name} [{aff_label}]", sub.name))

        self.app.push_screen(
            SubdivisionPickerScreen(char.civil_name, sub_opts, char.current_subdivision_id),
            callback=lambda result: self._apply_subdivision_change(char_id, result),
        )

    def _apply_subdivision_change(self, char_id: str, new_sub: str | None | bool) -> None:
        if new_sub is False:
            return  # cancelled
        faction_id = self.faction_id

        def mutator(ws: WorldState) -> None:
            c = ws.entities.get(char_id)
            if isinstance(c, Character):
                c.current_subdivision_id = new_sub

        result = self.bridge.apply_edit(mutator)
        if result.valid:
            self.dismiss(True)
        else:
            self._show_error("\n".join(result.errors))

    def action_add_subdivision(self) -> None:
        self.app.push_screen(
            AddSubdivisionScreen(),
            callback=self._apply_add_subdivision,
        )

    def _apply_add_subdivision(self, result: tuple[str, str | None] | None) -> None:
        if result is None:
            return
        name, note = result
        faction_id = self.faction_id

        def mutator(ws: WorldState) -> None:
            from gigagen.core.entity import Subdivision
            fac = ws.entities.get(faction_id)
            if isinstance(fac, Faction):
                fac.subdivisions.append(Subdivision(name=name, note=note))

        res = self.bridge.apply_edit(mutator)
        if res.valid:
            self.dismiss(True)
        else:
            self._show_error("\n".join(res.errors))

    def action_delete_subdivision(self) -> None:
        sub_table = self.query_one("#fac-sub-table", DataTable)
        if sub_table.cursor_row is None:
            return
        keys = list(sub_table.rows.keys())
        if not (0 <= sub_table.cursor_row < len(keys)):
            return
        sub_name = str(keys[sub_table.cursor_row].value)
        faction_id = self.faction_id

        def mutator(ws: WorldState) -> None:
            fac = ws.entities.get(faction_id)
            if isinstance(fac, Faction):
                fac.subdivisions = [s for s in fac.subdivisions if s.name != sub_name]
                for e in ws.entities.values():
                    if isinstance(e, Character) and e.current_subdivision_id == sub_name:
                        e.current_subdivision_id = None

        result = self.bridge.apply_edit(mutator)
        if result.valid:
            self.dismiss(True)
        else:
            self._show_error("\n".join(result.errors))

    def _save(self) -> None:
        try:
            status = self.query_one("#fac-status", Select).value
            power_str = self.query_one("#fac-power", Input).value
            cohesion_str = self.query_one("#fac-cohesion", Input).value
            leader = self.query_one("#fac-leader", Select).value

            power = float(power_str)
            cohesion = float(cohesion_str)
            if not (0.0 <= power <= 1.0):
                self._show_error("Power must be between 0.0 and 1.0")
                return
            if not (0.0 <= cohesion <= 1.0):
                self._show_error("Cohesion must be between 0.0 and 1.0")
                return
        except (ValueError, TypeError) as e:
            self._show_error(f"Invalid input: {e}")
            return

        faction_id = self.faction_id

        def mutator(ws: WorldState) -> None:
            fac = ws.entities[faction_id]
            if isinstance(fac, Faction):
                fac.status = status
                fac.power = power
                fac.cohesion = cohesion
                fac.leader_id = leader

        result = self.bridge.apply_edit(mutator)
        if result.valid:
            self.dismiss(True)
        else:
            self._show_error("\n".join(result.errors))

    def _show_error(self, msg: str) -> None:
        error = self.query_one("#fac-error", Static)
        error.update(f"[red]{msg}[/red]")


class SubdivisionPickerScreen(ModalScreen[str | None | bool]):
    """Quick picker for reassigning a character's subdivision."""

    BINDINGS = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    SubdivisionPickerScreen {
        align: center middle;
    }
    #subpicker-dialog {
        width: 50;
        height: auto;
        max-height: 60%;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }
    """

    def __init__(
        self,
        char_name: str,
        options: list[tuple[str, str | None]],
        current: str | None,
    ) -> None:
        super().__init__()
        self.char_name = char_name
        self.options = options
        self.current = current

    def compose(self) -> ComposeResult:
        with Vertical(id="subpicker-dialog"):
            yield Label(f"Reassign [b]{self.char_name}[/b] to subdivision:")
            yield Select(
                self.options,
                value=self.current,
                id="subpicker-select",
            )
            with Horizontal():
                yield Button("OK", variant="primary", id="subpicker-ok")
                yield Button("Cancel", id="subpicker-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "subpicker-ok":
            val = self.query_one("#subpicker-select", Select).value
            self.dismiss(val)
        elif event.button.id == "subpicker-cancel":
            self.dismiss(False)

    def action_cancel(self) -> None:
        self.dismiss(False)


class AddSubdivisionScreen(ModalScreen[tuple[str, str | None] | None]):
    """Form to add a new subdivision to a faction."""

    BINDINGS = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    AddSubdivisionScreen {
        align: center middle;
    }
    #addsub-dialog {
        width: 50;
        height: auto;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }
    .addsub-row {
        height: 3;
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        # Chromatic notes — generic musical alphabet
        chromatic = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        with Vertical(id="addsub-dialog"):
            yield Label("[b]Add Subdivision[/b]")
            with Horizontal(classes="addsub-row"):
                yield Label("Name: ")
                yield Input(placeholder="e.g. New Cell", id="addsub-name")
            note_opts: list[tuple[str, str | None]] = [("(none)", None)]
            for n in chromatic:
                note_opts.append((n, n))
            with Horizontal(classes="addsub-row"):
                yield Label("Root Note: ")
                yield Select(note_opts, value=None, id="addsub-note")
            with Horizontal():
                yield Button("Add", variant="primary", id="addsub-ok")
                yield Button("Cancel", id="addsub-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "addsub-ok":
            name = self.query_one("#addsub-name", Input).value.strip()
            if not name:
                return
            note = self.query_one("#addsub-note", Select).value
            self.dismiss((name, note))
        elif event.button.id == "addsub-cancel":
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)


class LocationEditorScreen(ModalScreen[bool]):
    """Full editor for a location: status, tension, access, faction control."""

    BINDINGS = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    LocationEditorScreen {
        align: center middle;
    }
    #loc-editor-dialog {
        width: 85%;
        height: 90%;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
        overflow-y: auto;
    }
    .loc-section-title {
        text-style: bold;
        margin: 1 0 0 0;
    }
    .loc-locked {
        color: $text-disabled;
    }
    #loc-error {
        color: red;
        margin: 1 0;
    }
    .loc-field-row {
        height: 3;
        margin: 0 1;
    }
    #loc-instability-bar {
        margin: 1 0;
    }
    """

    def __init__(self, location_id: str, bridge: "SimulatorBridge") -> None:
        super().__init__()
        self.location_id = location_id
        self.bridge = bridge

    def compose(self) -> ComposeResult:
        ws = self.bridge.ws
        loc = ws.entities[self.location_id]
        if not isinstance(loc, Location):
            return

        # Gather all factions for selects
        all_facs = sorted(
            (e for e in ws.entities.values() if isinstance(e, Faction)),
            key=lambda f: f.name,
        )

        with VerticalScroll(id="loc-editor-dialog"):
            # Header — locked identity
            tonic = loc.tonic or "(none)"
            parent = loc.parent_location_id or "(none)"
            biomes = ", ".join(loc.biome_tags) if loc.biome_tags else "(none)"
            yield Static(
                f"[b]=== {loc.name} ===[/b]\n"
                f"[dim]Zone: {loc.zone_level}  Tonic: {tonic}  "
                f"Parent: {parent}  Biome: {biomes}[/dim]",
                classes="loc-locked",
            )

            # Editable properties
            yield Static("[b]Properties[/b]", classes="loc-section-title")

            catalogs = self.bridge.catalogs
            loc_statuses = catalogs.get("location_statuses") or sorted({
                e.status for e in ws.entities.values() if isinstance(e, Location)
            })
            status_options = [(s, s) for s in loc_statuses]
            with Horizontal(classes="loc-field-row"):
                yield Label("Status: ")
                yield Select(
                    status_options,
                    value=loc.status,
                    id="loc-status",
                )

            with Horizontal(classes="loc-field-row"):
                yield Label("Tension (0.0-1.0): ")
                yield Input(value=f"{loc.tension:.2f}", id="loc-tension", type="number")

            access_values = sorted({
                e.access for e in ws.entities.values() if isinstance(e, Location)
            })
            access_options = [(a, a) for a in access_values]
            with Horizontal(classes="loc-field-row"):
                yield Label("Access: ")
                yield Select(
                    access_options,
                    value=loc.access,
                    id="loc-access",
                )

            # Controlling faction
            ctrl_opts: list[tuple[str, str | None]] = [("(none)", None)]
            for f in all_facs:
                ctrl_opts.append((f.name, f.id))
            with Horizontal(classes="loc-field-row"):
                yield Label("Controller: ")
                yield Select(
                    ctrl_opts,
                    value=loc.controlling_faction_id,
                    id="loc-controller",
                )

            # Secondary factions — checkboxes via DataTable with toggle
            yield Static("[b]Secondary Factions[/b]", classes="loc-section-title")
            sec_table = DataTable(id="loc-sec-table")
            sec_table.cursor_type = "row"
            sec_table.add_columns("", "Faction", "Mode")
            current_secondary = set(loc.secondary_faction_ids)
            for f in all_facs:
                check = "\u2611" if f.id in current_secondary else "\u2610"
                sec_table.add_row(check, f.name, f.mode or "-", key=f.id)
            yield sec_table
            yield Static(
                "[dim]Press Enter on a row to toggle secondary faction[/dim]",
            )

            # Instability indicator
            yield Static("[b]Instability[/b]", classes="loc-section-title")
            instab = self._compute_instability(loc, ws)
            instab_bar = self._instability_bar(instab)
            yield Static(instab_bar, id="loc-instability-bar")

            # Residents table
            yield Static("[b]Residents[/b]", classes="loc-section-title")
            res_table = DataTable(id="loc-res-table")
            res_table.cursor_type = "row"
            res_table.add_columns("Character", "Note", "Faction", "Affinity")
            residents = sorted(
                (e for e in ws.entities.values()
                 if isinstance(e, Character) and e.current_location_id == self.location_id),
                key=lambda c: c.civil_name,
            )
            # Get controlling faction intervals for affinity calc
            ctrl_intervals = None
            if loc.controlling_faction_id:
                ctrl_fac = ws.entities.get(loc.controlling_faction_id)
                if isinstance(ctrl_fac, Faction):
                    ctrl_intervals = ctrl_fac.intervals

            for c in residents:
                fac_name = "-"
                if c.current_faction_id and c.current_faction_id in ws.entities:
                    fac_name = ws.entities[c.current_faction_id].name
                aff = character_location_affinity(c.note, loc.tonic, ctrl_intervals)
                if aff is None:
                    aff_str = "[dim]n/a[/dim]"
                elif aff >= 0.3:
                    aff_str = f"[green]{aff:+.2f}[/green]"
                elif aff <= -0.3:
                    aff_str = f"[red]{aff:+.2f}[/red]"
                else:
                    aff_str = f"[yellow]{aff:+.2f}[/yellow]"
                res_table.add_row(c.civil_name, c.note, fac_name, aff_str)
            if not residents:
                res_table.add_row("[dim](no residents)[/dim]", "", "", "")
            yield res_table

            # Error area
            yield Static("", id="loc-error")

            # Buttons
            with Center():
                with Horizontal():
                    yield Button("Save", variant="primary", id="loc-save")
                    yield Button("Cancel", id="loc-cancel")

    def _compute_instability(self, loc: Location, ws: WorldState) -> float:
        """Compute location instability from all factions present."""
        faction_ids = []
        if loc.controlling_faction_id:
            faction_ids.append(loc.controlling_faction_id)
        faction_ids.extend(loc.secondary_faction_ids)
        intervals_list = []
        for fid in faction_ids:
            fac = ws.entities.get(fid)
            if isinstance(fac, Faction) and fac.intervals:
                intervals_list.append(fac.intervals)
        return location_instability(loc.tonic, intervals_list)

    def _instability_bar(self, instab: float) -> str:
        width = 20
        filled = int(instab * width)
        bar = "\u2588" * filled + "\u2591" * (width - filled)
        if instab >= 0.6:
            color = "red"
        elif instab >= 0.3:
            color = "yellow"
        else:
            color = "green"
        return f"  [{color}][{bar}] {instab:.2f}[/{color}]"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "loc-cancel":
            self.dismiss(False)
        elif event.button.id == "loc-save":
            self._save()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Toggle secondary faction when a row in sec_table is selected."""
        if event.data_table.id != "loc-sec-table":
            return
        row_key = event.row_key
        fac_id = str(row_key.value)
        # Toggle in our tracking
        sec_table = self.query_one("#loc-sec-table", DataTable)
        # Read current check state from first column
        row_data = sec_table.get_row(row_key)
        current_check = row_data[0]
        if current_check == "\u2611":
            new_check = "\u2610"
        else:
            new_check = "\u2611"
        # Update the cell
        col_key = list(sec_table.columns.keys())[0]
        sec_table.update_cell(row_key, col_key, new_check)

    def action_cancel(self) -> None:
        self.dismiss(False)

    def _save(self) -> None:
        try:
            status = self.query_one("#loc-status", Select).value
            tension_str = self.query_one("#loc-tension", Input).value
            access = self.query_one("#loc-access", Select).value
            controller = self.query_one("#loc-controller", Select).value

            tension = float(tension_str)
            if not (0.0 <= tension <= 1.0):
                self._show_error("Tension must be between 0.0 and 1.0")
                return
        except (ValueError, TypeError) as e:
            self._show_error(f"Invalid input: {e}")
            return

        # Collect secondary factions from the toggle table
        sec_table = self.query_one("#loc-sec-table", DataTable)
        secondary_ids: list[str] = []
        for row_key in sec_table.rows:
            row_data = sec_table.get_row(row_key)
            if row_data[0] == "\u2611":
                secondary_ids.append(str(row_key.value))

        location_id = self.location_id

        def mutator(ws: WorldState) -> None:
            loc = ws.entities[location_id]
            if isinstance(loc, Location):
                loc.status = status
                loc.tension = tension
                loc.access = access
                loc.controlling_faction_id = controller
                loc.secondary_faction_ids = secondary_ids

        result = self.bridge.apply_edit(mutator)
        if result.valid:
            self.dismiss(True)
        else:
            self._show_error("\n".join(result.errors))

    def _show_error(self, msg: str) -> None:
        error = self.query_one("#loc-error", Static)
        error.update(f"[red]{msg}[/red]")


# =========================================================================
# Phase 4 screens
# =========================================================================


class CharacterEditorScreen(ModalScreen[bool]):
    """Editor for character state fields."""

    BINDINGS = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    CharacterEditorScreen {
        align: center middle;
    }
    #char-editor-dialog {
        width: 70;
        height: auto;
        max-height: 85%;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
        overflow-y: auto;
    }
    .ced-field-row {
        height: 3;
        margin: 0 1;
    }
    #ced-error {
        color: red;
        margin: 1 0;
    }
    """

    def __init__(self, char_id: str, bridge: "SimulatorBridge") -> None:
        super().__init__()
        self.char_id = char_id
        self.bridge = bridge

    def compose(self) -> ComposeResult:
        ws = self.bridge.ws
        char = ws.entities[self.char_id]
        if not isinstance(char, Character):
            return

        all_facs = sorted(
            (e for e in ws.entities.values() if isinstance(e, Faction)),
            key=lambda f: f.name,
        )
        all_locs = sorted(
            (e for e in ws.entities.values() if isinstance(e, Location)),
            key=lambda l: l.name,
        )

        with VerticalScroll(id="char-editor-dialog"):
            # Locked identity
            yield Static(
                f"[b]=== {char.civil_name} ({char.role_name}) ===[/b]\n"
                f"[dim]Archetype: {char.archetype}  Note: {char.note}  "
                f"Hero: {char.hero_type}  Lineage: {char.lineage or '(none)'}[/dim]",
            )

            # Status — from catalogs or deduced from existing entities
            catalogs = self.bridge.catalogs
            char_statuses = catalogs.get("character_statuses") or sorted({
                e.status for e in ws.entities.values() if isinstance(e, Character)
            })
            status_opts = [(s, s) for s in char_statuses]
            with Horizontal(classes="ced-field-row"):
                yield Label("Status: ")
                yield Select(status_opts, value=char.status, id="ced-status")

            # Emotion — from catalogs or deduced
            emo_states = catalogs.get("emotional_states") or sorted({
                e.emotional_load for e in ws.entities.values() if isinstance(e, Character)
            })
            emo_opts = [(s, s) for s in emo_states]
            with Horizontal(classes="ced-field-row"):
                yield Label("Emotion: ")
                yield Select(emo_opts, value=char.emotional_load, id="ced-emotion")

            # Location
            loc_opts: list[tuple[str, str]] = []
            for l in all_locs:
                loc_opts.append((l.name, l.id))
            with Horizontal(classes="ced-field-row"):
                yield Label("Location: ")
                yield Select(loc_opts, value=char.current_location_id, id="ced-location")

            # Faction
            fac_opts: list[tuple[str, str | None]] = [("(none)", None)]
            for f in all_facs:
                fac_opts.append((f.name, f.id))
            with Horizontal(classes="ced-field-row"):
                yield Label("Faction: ")
                yield Select(fac_opts, value=char.current_faction_id, id="ced-faction")

            # Subdivision
            sub_opts: list[tuple[str, str | None]] = [("(none)", None)]
            if char.current_faction_id:
                fac = ws.entities.get(char.current_faction_id)
                if isinstance(fac, Faction):
                    for s in fac.subdivisions:
                        if s.name:
                            aff = character_faction_affinity(char.note, fac.intervals, s.note)
                            label = f"{s.name} [{aff:+.2f}]" if s.note else s.name
                            sub_opts.append((label, s.name))
            with Horizontal(classes="ced-field-row"):
                yield Label("Subdivision: ")
                yield Select(sub_opts, value=char.current_subdivision_id, id="ced-subdivision")

            yield Static("", id="ced-error")
            with Center():
                with Horizontal():
                    yield Button("Save", variant="primary", id="ced-save")
                    yield Button("Cancel", id="ced-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ced-cancel":
            self.dismiss(False)
        elif event.button.id == "ced-save":
            self._save()

    def action_cancel(self) -> None:
        self.dismiss(False)

    def _save(self) -> None:
        status = self.query_one("#ced-status", Select).value
        emotion = self.query_one("#ced-emotion", Select).value
        location = self.query_one("#ced-location", Select).value
        faction = self.query_one("#ced-faction", Select).value
        subdivision = self.query_one("#ced-subdivision", Select).value

        char_id = self.char_id

        def mutator(ws: WorldState) -> None:
            c = ws.entities.get(char_id)
            if isinstance(c, Character):
                c.status = status
                c.emotional_load = emotion
                c.current_location_id = location
                c.current_faction_id = faction
                c.current_subdivision_id = subdivision

        result = self.bridge.apply_edit(mutator)
        if result.valid:
            self.dismiss(True)
        else:
            error = self.query_one("#ced-error", Static)
            error.update(f"[red]{chr(10).join(result.errors)}[/red]")


class NewRelationScreen(ModalScreen[bool]):
    """Form to create a new derived relation."""

    BINDINGS = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    NewRelationScreen {
        align: center middle;
    }
    #newrel-dialog {
        width: 65;
        height: auto;
        max-height: 80%;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }
    .newrel-row {
        height: 3;
        margin: 0 1;
    }
    #newrel-error {
        color: red;
        margin: 1 0;
    }
    """

    def __init__(self, bridge: "SimulatorBridge") -> None:
        super().__init__()
        self.bridge = bridge

    def compose(self) -> ComposeResult:
        from gigagen.core.relation import RELATION_KINDS
        ws = self.bridge.ws

        entity_opts = sorted(
            [(e.name, e.id) for e in ws.entities.values()],
            key=lambda x: x[0],
        )
        kind_opts = sorted([(k, k) for k in RELATION_KINDS])
        pol_opts = [("Positive (+1)", 1), ("Neutral (0)", 0), ("Negative (-1)", -1)]

        with Vertical(id="newrel-dialog"):
            yield Label("[b]Create New Relation[/b]  [dim](canon: derived)[/dim]")
            with Horizontal(classes="newrel-row"):
                yield Label("Source: ")
                yield Select(entity_opts, id="newrel-source")
            with Horizontal(classes="newrel-row"):
                yield Label("Target: ")
                yield Select(entity_opts, id="newrel-target")
            with Horizontal(classes="newrel-row"):
                yield Label("Kind: ")
                yield Select(kind_opts, id="newrel-kind")
            with Horizontal(classes="newrel-row"):
                yield Label("Weight (0.0-1.0): ")
                yield Input(value="0.5", id="newrel-weight", type="number")
            with Horizontal(classes="newrel-row"):
                yield Label("Polarity: ")
                yield Select(pol_opts, value=0, id="newrel-polarity")
            yield Static("", id="newrel-error")
            with Center():
                with Horizontal():
                    yield Button("Create", variant="primary", id="newrel-ok")
                    yield Button("Cancel", id="newrel-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "newrel-cancel":
            self.dismiss(False)
        elif event.button.id == "newrel-ok":
            self._create()

    def action_cancel(self) -> None:
        self.dismiss(False)

    def _create(self) -> None:
        from gigagen.core.relation import Relation
        try:
            source = self.query_one("#newrel-source", Select).value
            target = self.query_one("#newrel-target", Select).value
            kind = self.query_one("#newrel-kind", Select).value
            weight = float(self.query_one("#newrel-weight", Input).value)
            polarity = self.query_one("#newrel-polarity", Select).value

            if not source or not target:
                self._show_error("Select source and target")
                return
            if source == target:
                self._show_error("Source and target must differ")
                return
            if not (0.0 <= weight <= 1.0):
                self._show_error("Weight must be 0.0-1.0")
                return
        except (ValueError, TypeError) as e:
            self._show_error(f"Invalid input: {e}")
            return

        rel_id = f"rel.derived.{source}.{target}.{kind}"

        def mutator(ws: WorldState) -> None:
            # Check for duplicate
            for r in ws.relations:
                if r.source_id == source and r.target_id == target and r.kind == kind:
                    return  # skip duplicate
            ws.relations.append(Relation(
                id=rel_id,
                source_id=source,
                target_id=target,
                kind=kind,
                weight=weight,
                polarity=polarity,
                canon_level="derived",
            ))

        result = self.bridge.apply_edit(mutator)
        if result.valid:
            self.dismiss(True)
        else:
            self._show_error("\n".join(result.errors))

    def _show_error(self, msg: str) -> None:
        error = self.query_one("#newrel-error", Static)
        error.update(f"[red]{msg}[/red]")


class ValidationResultScreen(ModalScreen[None]):
    """Shows full invariant validation results."""

    BINDINGS = [("escape", "dismiss", "Close")]

    DEFAULT_CSS = """
    ValidationResultScreen {
        align: center middle;
    }
    #val-dialog {
        width: 70;
        height: auto;
        max-height: 80%;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
        overflow-y: auto;
    }
    """

    def __init__(self, bridge: "SimulatorBridge") -> None:
        super().__init__()
        self.bridge = bridge

    def compose(self) -> ComposeResult:
        from gigagen.core.invariants import validate_invariants
        result = validate_invariants(
            self.bridge.ws,
            self.bridge.worldpack_dir / "invariants.json",
        )
        if result.valid:
            content = "[green]\u2714 World state is valid. All invariants pass.[/green]"
        else:
            lines = [f"[red]\u2718 {len(result.errors)} error(s) found:[/red]\n"]
            for err in result.errors:
                lines.append(f"  [red]\u2022 {err}[/red]")
            content = "\n".join(lines)

        with Vertical(id="val-dialog"):
            yield Static("[b]Invariant Validation[/b]\n")
            yield Static(content)
            with Center():
                yield Button("Close", variant="primary", id="val-close")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "val-close":
            self.dismiss(None)


class HarmonicDashboardScreen(ModalScreen[None]):
    """System-wide harmonic metrics dashboard."""

    BINDINGS = [("escape", "dismiss", "Close")]

    DEFAULT_CSS = """
    HarmonicDashboardScreen {
        align: center middle;
    }
    #harmonic-dialog {
        width: 90%;
        height: 90%;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
        overflow-y: auto;
    }
    """

    def __init__(self, ws: WorldState) -> None:
        super().__init__()
        self.ws = ws

    def compose(self) -> ComposeResult:
        from gigagen.core.harmony import faction_compatibility

        ws = self.ws
        facs = sorted(
            (e for e in ws.entities.values() if isinstance(e, Faction)),
            key=lambda f: f.name,
        )
        chars = sorted(
            (e for e in ws.entities.values() if isinstance(e, Character)),
            key=lambda c: c.civil_name,
        )
        locs = sorted(
            (e for e in ws.entities.values() if isinstance(e, Location)),
            key=lambda l: l.name,
        )

        with VerticalScroll(id="harmonic-dialog"):
            yield Static("[b]HARMONIC DASHBOARD[/b]\n")

            # 1. Faction compatibility matrix
            yield Static("[b]Faction Compatibility Matrix[/b]")
            compat_table = DataTable(id="compat-matrix")
            compat_table.add_column("", key="label")
            for f in facs:
                short = f.name[:8]
                compat_table.add_column(short, key=f.id)
            for fa in facs:
                row_data: dict[str, str] = {"label": fa.name[:12]}
                for fb in facs:
                    if fa.id == fb.id:
                        row_data[fb.id] = "[dim]---[/dim]"
                    else:
                        score = faction_compatibility(fa.intervals, fb.intervals)
                        if score >= 0.7:
                            row_data[fb.id] = f"[green]{score:.2f}[/green]"
                        elif score >= 0.3:
                            row_data[fb.id] = f"[yellow]{score:.2f}[/yellow]"
                        else:
                            row_data[fb.id] = f"[red]{score:.2f}[/red]"
                compat_table.add_row(
                    *[row_data.get("label", "")] + [row_data.get(f.id, "") for f in facs]
                )
            yield compat_table

            # 2. Location instability ranking
            yield Static("\n[b]Location Instability Ranking[/b]")
            instab_data: list[tuple[str, float]] = []
            for loc in locs:
                fac_ids = []
                if loc.controlling_faction_id:
                    fac_ids.append(loc.controlling_faction_id)
                fac_ids.extend(loc.secondary_faction_ids)
                intervals_list = []
                for fid in fac_ids:
                    fac = ws.entities.get(fid)
                    if isinstance(fac, Faction) and fac.intervals:
                        intervals_list.append(fac.intervals)
                instab = location_instability(loc.tonic, intervals_list)
                instab_data.append((loc.name, instab))
            instab_data.sort(key=lambda x: x[1], reverse=True)
            instab_lines = []
            for name, score in instab_data:
                bar = "\u2588" * int(score * 15) + "\u2591" * (15 - int(score * 15))
                if score >= 0.6:
                    instab_lines.append(f"  [red]{name:<20} [{bar}] {score:.2f}[/red]")
                elif score >= 0.3:
                    instab_lines.append(f"  [yellow]{name:<20} [{bar}] {score:.2f}[/yellow]")
                else:
                    instab_lines.append(f"  [green]{name:<20} [{bar}] {score:.2f}[/green]")
            yield Static("\n".join(instab_lines))

            # 3. Character-faction affinity summary
            yield Static("\n[b]Character-Faction Affinity[/b]  [dim](negative = misplaced)[/dim]")
            aff_table = DataTable(id="aff-summary")
            aff_table.add_columns("Character", "Note", "Faction", "Subdivision", "Affinity")
            for c in chars:
                fac_name = "-"
                sub_root = None
                if c.current_faction_id:
                    fac_ent = ws.entities.get(c.current_faction_id)
                    if isinstance(fac_ent, Faction):
                        fac_name = fac_ent.name
                        if c.current_subdivision_id:
                            for s in fac_ent.subdivisions:
                                if s.name == c.current_subdivision_id:
                                    sub_root = s.note
                                    break
                        aff = character_faction_affinity(c.note, fac_ent.intervals, sub_root)
                        if aff >= 0.3:
                            aff_str = f"[green]{aff:+.2f}[/green]"
                        elif aff <= -0.3:
                            aff_str = f"[red]{aff:+.2f} !!![/red]"
                        else:
                            aff_str = f"[yellow]{aff:+.2f}[/yellow]"
                    else:
                        aff_str = "[dim]n/a[/dim]"
                else:
                    aff_str = "[dim]n/a[/dim]"
                aff_table.add_row(
                    c.civil_name, c.note, fac_name,
                    c.current_subdivision_id or "-", aff_str,
                )
            yield aff_table

            with Center():
                yield Button("Close", variant="primary", id="harmonic-close")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "harmonic-close":
            self.dismiss(None)
