"""Custom widgets for the Gigagen TUI."""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static, DataTable, Label
from textual.reactive import reactive

from gigagen.core.entity import Character, Faction, Location
from gigagen.core.world_state import WorldState
from gigagen.core.simulator import SimulatorState


class TimelineBar(Static):
    """Visual progress bar showing current hour in the 62-hour timeline."""

    hour: reactive[int] = reactive(0)
    max_hour: reactive[int] = reactive(62)
    playing: reactive[bool] = reactive(False)
    speed: reactive[float] = reactive(1.0)

    def render(self) -> str:
        width = max(self.size.width - 20, 10)
        progress = self.hour / self.max_hour if self.max_hour > 0 else 0
        filled = int(width * progress)
        bar = "\u2588" * filled + "\u2591" * (width - filled)
        status = "\u25b6" if self.playing else "\u23f8"
        speed_str = f"{self.speed:.1f}s"
        return f" {status} [{bar}] H{self.hour:02d}/H{self.max_hour:02d}  {speed_str}"


class CharacterTable(Static):
    """Displays all characters in a table format."""

    DEFAULT_CSS = """
    CharacterTable {
        height: 100%;
        overflow-y: auto;
    }
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._table: DataTable | None = None

    def compose(self) -> ComposeResult:
        table = DataTable(id="char-table")
        table.cursor_type = "row"
        table.add_columns("Name", "Arch", "Status", "Emotion", "Location", "Faction")
        self._table = table
        yield table

    def update_data(self, ws: WorldState, sim: SimulatorState) -> None:
        if self._table is None:
            return
        self._table.clear()
        chars = sorted(
            (e for e in ws.entities.values() if isinstance(e, Character)),
            key=lambda c: c.civil_name,
        )
        for c in chars:
            fac = c.current_faction_id or "-"
            style = ""
            if c.status == "dead":
                style = "dim"
            elif c.status == "digitalized":
                style = "italic"
            name = c.civil_name
            self._table.add_row(
                name, c.archetype, c.status, c.emotional_load,
                c.current_location_id, fac,
                key=c.id,
            )

    def get_selected_id(self) -> str | None:
        if self._table is None or self._table.cursor_row is None:
            return None
        try:
            row_key = self._table.get_row_at(self._table.cursor_row)
            # Row keys are set to entity id
            keys = list(self._table.rows.keys())
            if 0 <= self._table.cursor_row < len(keys):
                return str(keys[self._table.cursor_row].value)
        except Exception:
            pass
        return None


class FactionPanel(Static):
    """Displays faction status."""

    can_focus = True

    DEFAULT_CSS = """
    FactionPanel {
        height: 100%;
        overflow-y: auto;
    }
    """

    def update_data(self, ws: WorldState) -> None:
        facs = sorted(
            (e for e in ws.entities.values() if isinstance(e, Faction)),
            key=lambda f: f.name,
        )
        lines = ["[b]FACTIONS[/b]\n"]
        for f in facs:
            leader = f.leader_id or "-"
            pwr_bar = "\u2588" * int(f.power * 10) + "\u2591" * (10 - int(f.power * 10))
            coh_bar = "\u2588" * int(f.cohesion * 10) + "\u2591" * (10 - int(f.cohesion * 10))
            lines.append(f"[bold]{f.name}[/bold] ({f.status})")
            lines.append(f"  Power:    [{pwr_bar}] {f.power:.2f}")
            lines.append(f"  Cohesion: [{coh_bar}] {f.cohesion:.2f}")
            lines.append(f"  Leader:   {leader}")
            lines.append("")
        self.update("\n".join(lines))


class LocationPanel(Static):
    """Displays location status."""

    can_focus = True

    DEFAULT_CSS = """
    LocationPanel {
        height: 100%;
        overflow-y: auto;
    }
    """

    def update_data(self, ws: WorldState) -> None:
        locs = sorted(
            (e for e in ws.entities.values() if isinstance(e, Location)),
            key=lambda loc: loc.name,
        )
        lines = ["[b]LOCATIONS[/b]\n"]
        for loc in locs:
            ctrl = loc.controlling_faction_id or "-"
            tension_bar = "\u2588" * int(loc.tension * 10) + "\u2591" * (10 - int(loc.tension * 10))
            lines.append(f"[bold]{loc.name}[/bold] ({loc.zone_level})")
            lines.append(f"  Status:  {loc.status}  Access: {loc.access}")
            lines.append(f"  Tension: [{tension_bar}] {loc.tension:.2f}")
            lines.append(f"  Control: {ctrl}")
            lines.append("")
        self.update("\n".join(lines))


class VariablesPanel(Static):
    """Displays variable resolution status."""

    can_focus = True

    DEFAULT_CSS = """
    VariablesPanel {
        height: 100%;
        overflow-y: auto;
    }
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._known_vars: list[str] = []

    def set_known_vars(self, var_names: list[str]) -> None:
        """Set the list of variable names to track (loaded from worldpack)."""
        self._known_vars = sorted(var_names)

    def update_data(self, resolved: dict[str, str]) -> None:
        lines = ["[b]VARIABLES[/b]\n"]
        # Show known variables first, then any extra resolved ones
        shown = set()
        for var in self._known_vars:
            shown.add(var)
            if var in resolved:
                val = resolved[var]
                lines.append(f"  [green]\u2611[/green] {var}: [bold]{val}[/bold]")
            else:
                lines.append(f"  [dim]\u2610[/dim] {var}: [dim]unresolved[/dim]")
        for var in sorted(resolved):
            if var not in shown:
                lines.append(f"  [green]\u2611[/green] {var}: [bold]{resolved[var]}[/bold]")
        self.update("\n".join(lines))


class EventLogPanel(Static):
    """Scrollable event log."""

    can_focus = True

    DEFAULT_CSS = """
    EventLogPanel {
        height: 100%;
        overflow-y: auto;
    }
    """

    def update_data(self, event_log: list, current_hour: int) -> None:
        lines = [f"[b]EVENT LOG[/b] (H{current_hour:02d})\n"]
        # Show events in reverse chronological order
        for entry in reversed(event_log):
            marker = " [yellow]***[/yellow]" if entry.variable_resolved else ""
            lines.append(
                f"  H{entry.hour:02d} [{entry.event_id}] {entry.name}{marker}"
            )
            if entry.variable_resolved:
                lines.append(f"       [green]>> {entry.variable_resolved}[/green]")
        if not event_log:
            lines.append("  [dim](no events yet)[/dim]")
        self.update("\n".join(lines))
