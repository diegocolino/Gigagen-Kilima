"""Custom widgets for the Gigagen TUI."""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static, DataTable, Label
from textual.reactive import reactive

from gigagen.core.entity import Character, Faction, Location
from gigagen.core.relation import Relation
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
        table.add_columns("Name", "Arch", "Status", "Emotion", "Location", "Division", "Faction")
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
            division = c.current_subdivision_id or "-"
            fac_name = "-"
            if c.current_faction_id and c.current_faction_id in ws.entities:
                fac_name = ws.entities[c.current_faction_id].name
            name = c.civil_name
            self._table.add_row(
                name, c.archetype, c.status, c.emotional_load,
                c.current_location_id, division, fac_name,
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
    """Displays faction status as an interactive DataTable."""

    DEFAULT_CSS = """
    FactionPanel {
        height: 100%;
        overflow-y: auto;
    }
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._table: DataTable | None = None

    def compose(self) -> ComposeResult:
        table = DataTable(id="fac-table")
        table.cursor_type = "row"
        table.add_columns("Division", "Parent", "Status", "Leader", "Type", "Note")
        self._table = table
        yield table

    def update_data(self, ws: WorldState) -> None:
        if self._table is None:
            return
        self._table.clear()
        facs = sorted(
            (e for e in ws.entities.values() if isinstance(e, Faction)),
            key=lambda f: f.name,
        )
        for f in facs:
            if f.subdivisions:
                for sub in f.subdivisions:
                    sub_name = sub.name or "(unnamed)"
                    sub_leader = "-"
                    if sub.leader_id and sub.leader_id in ws.entities:
                        sub_leader = ws.entities[sub.leader_id].name
                    self._table.add_row(
                        sub_name, f.name, f.status,
                        sub_leader, sub.type or "-", sub.note or "-",
                        key=f"{f.id}::{sub.name or '_unnamed'}",
                    )
            else:
                # Factions without subdivisions show as a single row
                leader_name = "-"
                if f.leader_id and f.leader_id in ws.entities:
                    leader_name = ws.entities[f.leader_id].name
                self._table.add_row(
                    f.name, "-", f.status,
                    leader_name, "-", "-",
                    key=f.id,
                )

    def get_selected_id(self) -> str | None:
        """Returns the faction ID (strips subdivision suffix if present)."""
        if self._table is None or self._table.cursor_row is None:
            return None
        try:
            keys = list(self._table.rows.keys())
            if 0 <= self._table.cursor_row < len(keys):
                raw = str(keys[self._table.cursor_row].value)
                # Keys are "fac.xxx::SubName" or "fac.xxx"
                return raw.split("::")[0]
        except Exception:
            pass
        return None


class LocationPanel(Static):
    """Displays location status as an interactive DataTable."""

    DEFAULT_CSS = """
    LocationPanel {
        height: 100%;
        overflow-y: auto;
    }
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._table: DataTable | None = None

    def compose(self) -> ComposeResult:
        table = DataTable(id="loc-table")
        table.cursor_type = "row"
        table.add_columns("Location", "Parent", "Zone", "Status", "Tension", "Access", "Controller")
        self._table = table
        yield table

    def update_data(self, ws: WorldState) -> None:
        if self._table is None:
            return
        self._table.clear()
        locs = sorted(
            (e for e in ws.entities.values() if isinstance(e, Location)),
            key=lambda loc: loc.name,
        )
        for loc in locs:
            parent_name = "-"
            if loc.parent_location_id and loc.parent_location_id in ws.entities:
                parent_name = ws.entities[loc.parent_location_id].name
            ctrl_name = "-"
            if loc.controlling_faction_id and loc.controlling_faction_id in ws.entities:
                ctrl_name = ws.entities[loc.controlling_faction_id].name
            tension_bar = "\u2588" * int(loc.tension * 5) + "\u2591" * (5 - int(loc.tension * 5))
            self._table.add_row(
                loc.name, parent_name, loc.zone_level, loc.status,
                f"{tension_bar} {loc.tension:.1f}", loc.access,
                ctrl_name,
                key=loc.id,
            )

    def get_selected_id(self) -> str | None:
        if self._table is None or self._table.cursor_row is None:
            return None
        try:
            keys = list(self._table.rows.keys())
            if 0 <= self._table.cursor_row < len(keys):
                return str(keys[self._table.cursor_row].value)
        except Exception:
            pass
        return None


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


class RelationsTable(Static):
    """Global relations table with filtering."""

    DEFAULT_CSS = """
    RelationsTable {
        height: 100%;
        overflow-y: auto;
    }
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._table: DataTable | None = None
        self._relations: list[Relation] = []
        self._entities: dict[str, Any] = {}
        self._filter: str | None = None  # None=all, "cc"=char-char, "cf"=char-fac, "fl"=fac-loc
        self._sort_key: str = "source"

    def compose(self) -> ComposeResult:
        table = DataTable(id="rel-table")
        table.cursor_type = "row"
        table.add_columns("Source", "Target", "Kind", "Weight", "Pol", "Canon", "Tags")
        self._table = table
        yield table

    def set_data(self, relations: list[Relation], entities: dict[str, Any]) -> None:
        self._relations = relations
        self._entities = entities
        self._rebuild()

    def set_filter(self, filter_key: str | None) -> None:
        self._filter = filter_key
        self._rebuild()

    def set_sort(self, sort_key: str) -> None:
        self._sort_key = sort_key
        self._rebuild()

    def _classify(self, rel: Relation) -> str:
        s, t = rel.source_id, rel.target_id
        if s.startswith("char.") and t.startswith("char."):
            return "cc"
        if s.startswith("char.") and t.startswith("fac."):
            return "cf"
        if s.startswith("fac.") and t.startswith("loc."):
            return "fl"
        return "other"

    def _resolve_name(self, entity_id: str) -> str:
        ent = self._entities.get(entity_id)
        return ent.name if ent else entity_id

    def _rebuild(self) -> None:
        if self._table is None:
            return
        self._table.clear()

        rels = self._relations
        if self._filter:
            rels = [r for r in rels if self._classify(r) == self._filter]

        if self._sort_key == "weight":
            rels = sorted(rels, key=lambda r: r.weight, reverse=True)
        elif self._sort_key == "kind":
            rels = sorted(rels, key=lambda r: r.kind)
        else:
            rels = sorted(rels, key=lambda r: self._resolve_name(r.source_id))

        for r in rels:
            pol_sym = {1: "[green]+[/green]", 0: "~", -1: "[red]-[/red]"}.get(r.polarity, "?")
            tags = ", ".join(r.tags[:2]) if r.tags else "-"
            self._table.add_row(
                self._resolve_name(r.source_id),
                self._resolve_name(r.target_id),
                r.kind,
                f"{r.weight:.1f}",
                pol_sym,
                r.canon_level,
                tags,
                key=r.id,
            )
