"""Map widget — panel-based hierarchical map of locations and characters."""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.color import Color
from textual.containers import Horizontal, Vertical
from textual.widgets import Static

from gigagen.core.entity import Character, MacroFaction, Location
from gigagen.core.world_state import WorldState


_COLOR_PALETTE = [
    "red", "blue", "cyan", "yellow", "green",
    "magenta", "white", "bright_black",
]

# Map color names to Textual Color objects for border styling
_COLOR_MAP = {
    "red": Color(220, 50, 50),
    "blue": Color(60, 120, 220),
    "cyan": Color(50, 200, 200),
    "yellow": Color(220, 200, 50),
    "green": Color(50, 200, 80),
    "magenta": Color(200, 50, 200),
    "white": Color(200, 200, 200),
    "bright_black": Color(100, 100, 100),
}

_STATUS_COLORS = {
    "stable": "green",
    "active": "green",
    "peaceful": "green",
    "tense": "yellow",
    "fragile": "yellow",
    "unstable": "red",
    "besieged": "red",
    "breached": "red",
    "hidden": "$text-muted",
}

# Zone display order and labels
_ZONE_ORDER = ["high", "mid", "low", "hidden", "external", "virtual"]
_ZONE_LABELS = {
    "high": "\u25b2 HIGH",
    "mid": "\u25a0 MID",
    "low": "\u25bc LOW",
    "hidden": "\u25c6 HIDDEN",
    "external": "\u25cb EXTERNAL",
    "virtual": "\u25c7 VIRTUAL",
}


def _faction_color(faction_id: str | None, faction_ids: list[str]) -> str:
    if not faction_id or faction_id not in faction_ids:
        return "white"
    idx = faction_ids.index(faction_id)
    return _COLOR_PALETTE[idx % len(_COLOR_PALETTE)]


def _build_zones(ws: WorldState) -> list[tuple[str, list[str]]]:
    """Build zone groups dynamically from location data."""
    zones: dict[str, list[str]] = {}
    for eid, ent in ws.entities.items():
        if isinstance(ent, Location):
            z = ent.zone_level
            if z not in zones:
                zones[z] = []
            zones[z].append(eid)
    for z in zones:
        zones[z].sort(key=lambda lid: ws.entities[lid].name)
    result = []
    for z in _ZONE_ORDER:
        if z in zones:
            label = _ZONE_LABELS.get(z, z.upper())
            result.append((label, zones[z]))
    for z in sorted(zones):
        if z not in _ZONE_ORDER:
            result.append((z.upper(), zones[z]))
    return result


class LocationBox(Static):
    """A single location panel showing its name and resident characters."""

    DEFAULT_CSS = """
    LocationBox {
        border: solid $primary;
        padding: 0 1;
        margin: 0 1;
        min-width: 16;
        width: 1fr;
        height: auto;
        min-height: 3;
    }
    """

    def __init__(self, location_id: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.location_id = location_id

    def set_data(
        self,
        loc: Location,
        chars: list[Character],
        faction_ids: list[str],
        ws: WorldState,
        moved_ids: set[str] | None = None,
    ) -> None:
        moved = moved_ids or set()

        # Border color by controlling faction
        if loc.controlling_macro_faction_id:
            color_name = _faction_color(loc.controlling_macro_faction_id, faction_ids)
            border_color = _COLOR_MAP.get(color_name, Color(128, 128, 128))
            self.styles.border = ("solid", border_color)
        else:
            self.styles.border = ("solid", Color(80, 80, 80))

        # Location name with count
        status_color = _STATUS_COLORS.get(loc.status, "white")
        count_str = f" ({len(chars)})" if chars else ""
        lines = [f"[{status_color}][b]{loc.name}{count_str}[/b][/{status_color}]"]

        if chars:
            for c in sorted(chars, key=lambda x: x.civil_name):
                color = _faction_color(c.current_macro_faction_id, faction_ids)
                if c.id in moved:
                    # Moved indicator
                    lines.append(f"  [{color}][b]\u2192 {c.civil_name}[/b][/{color}]")
                else:
                    lines.append(f"  [{color}]\u25cf {c.civil_name}[/{color}]")
        else:
            lines.append("  [dim](empty)[/dim]")

        self.update("\n".join(lines))


class ZoneRow(Static):
    """A horizontal zone containing multiple LocationBox panels."""

    DEFAULT_CSS = """
    ZoneRow {
        height: auto;
        min-height: 4;
        padding: 0;
        margin: 0;
    }
    .zone-label {
        height: 1;
        padding: 0 1;
        text-style: bold;
        background: $primary-darken-1;
    }
    .zone-locations {
        height: auto;
        min-height: 3;
        padding: 0;
    }
    """

    def __init__(self, zone_label: str, location_ids: list[str], **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.zone_label = zone_label
        self.location_ids = location_ids

    def compose(self) -> ComposeResult:
        yield Static(f" [b]{self.zone_label}[/b]", classes="zone-label")
        with Horizontal(classes="zone-locations"):
            for loc_id in self.location_ids:
                yield LocationBox(loc_id, id=f"locbox-{loc_id.replace('.', '-').replace(':', '-')}")

    def update_data(
        self,
        ws: WorldState,
        chars_at: dict[str, list[Character]],
        faction_ids: list[str],
        moved_ids: set[str] | None = None,
    ) -> None:
        for loc_id in self.location_ids:
            loc = ws.entities.get(loc_id)
            if not isinstance(loc, Location):
                continue
            widget_id = f"locbox-{loc_id.replace('.', '-').replace(':', '-')}"
            try:
                box = self.query_one(f"#{widget_id}", LocationBox)
                box.set_data(loc, chars_at.get(loc_id, []), faction_ids, ws, moved_ids)
            except Exception:
                pass


class MapPanel(Static):
    """Full map panel with zone rows, built dynamically from worldpack data."""

    DEFAULT_CSS = """
    MapPanel {
        height: 100%;
        width: 100%;
        overflow-y: auto;
    }
    #map-header {
        height: 1;
        background: $primary;
        text-style: bold;
        padding: 0 1;
        dock: top;
    }
    #map-event-log {
        height: 1;
        padding: 0 1;
        background: $primary-darken-2;
    }
    #map-footer {
        height: 1;
        dock: bottom;
        padding: 0 1;
    }
    #map-legend {
        height: auto;
        padding: 0 1;
        margin: 1 0 0 0;
    }
    """

    def __init__(self, ws: WorldState, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._zones = _build_zones(ws)

    def compose(self) -> ComposeResult:
        yield Static("MAP", id="map-header")
        yield Static("[dim](no events yet)[/dim]", id="map-event-log")
        for i, (label, loc_ids) in enumerate(self._zones):
            yield ZoneRow(label, loc_ids, id=f"zone-{i}")
        yield Static("", id="map-legend")
        yield Static(
            "[dim]\u2190/\u2192 step  Shift+\u2190/\u2192 \u00b15h  Space play/pause  Esc close[/dim]",
            id="map-footer",
        )

    def refresh_map(
        self,
        ws: WorldState,
        current_hour: int,
        *,
        last_event: str | None = None,
        moved_ids: set[str] | None = None,
        playing: bool = False,
    ) -> None:
        """Refresh all zones with current data."""
        play_icon = "\u25b6" if playing else "\u23f8"
        self.query_one("#map-header", Static).update(
            f"  {play_icon} MAP \u00b7 H{current_hour:02d}"
        )

        # Event log
        if last_event:
            self.query_one("#map-event-log", Static).update(f"  [yellow]{last_event}[/yellow]")
        else:
            self.query_one("#map-event-log", Static).update("[dim]  (no events)[/dim]")

        faction_ids = sorted(
            eid for eid, e in ws.entities.items() if isinstance(e, MacroFaction)
        )
        chars_at: dict[str, list[Character]] = {}
        for eid, ent in ws.entities.items():
            if isinstance(ent, Character):
                loc = ent.current_location_id
                if loc not in chars_at:
                    chars_at[loc] = []
                chars_at[loc].append(ent)

        for i, (_label, _loc_ids) in enumerate(self._zones):
            try:
                zone = self.query_one(f"#zone-{i}", ZoneRow)
                zone.update_data(ws, chars_at, faction_ids, moved_ids)
            except Exception:
                pass

        legend_parts = []
        for fid in faction_ids:
            fname = ws.entities[fid].name if fid in ws.entities else fid
            color = _faction_color(fid, faction_ids)
            legend_parts.append(f"[{color}]\u25cf[/{color}] {fname}")
        self.query_one("#map-legend", Static).update("  ".join(legend_parts))
