"""GigagenApp — main Textual application for the God Mode TUI."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.timer import Timer
from textual.widgets import DataTable, Static, Footer

from gigagen.io.export_world_state import export_world_state, save_worldpack

from .bridge import SimulatorBridge
from .widgets import (
    TimelineBar,
    CharacterTable,
    FactionPanel,
    LocationPanel,
    VariablesPanel,
    EventLogPanel,
)
from .screens import (
    HelpScreen,
    SeedPickerScreen,
    InspectorScreen,
    RelationsScreen,
    OutcomesScreen,
    GlobalRelationsScreen,
    FactionEditorScreen,
    LocationEditorScreen,
    CharacterEditorScreen,
    NewRelationScreen,
    ValidationResultScreen,
    HarmonicDashboardScreen,
    MapScreen,
    TimelineScreen,
    LifePackInspectorScreen,
)


class GigagenApp(App):
    """God Mode TUI for Gigagen/Kilima."""

    CSS_PATH = "styles.tcss"
    TITLE = "GIGAGEN"
    ENABLE_COMMAND_PALETTE = False

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("question_mark", "help", "Help", show=True, key_display="?"),
        Binding("right", "step_forward_1", "Step +1", show=True, key_display="\u2192", priority=True),
        Binding("shift+right", "step_forward_5", "+5h", show=False, priority=True),
        Binding("left", "step_backward_1", "Step -1", show=True, key_display="\u2190", priority=True),
        Binding("shift+left", "step_backward_5", "-5h", show=False, priority=True),
        Binding("home", "jump_start", "H00", show=True, priority=True),
        Binding("end", "jump_end", "H62", show=True, priority=True),
        Binding("space", "toggle_play", "Play/Pause", show=True, priority=True),
        Binding("p", "toggle_play", "Play", show=False),
        Binding("plus", "speed_up", "+Speed", show=True, key_display="+"),
        Binding("minus", "speed_down", "-Speed", show=True, key_display="-"),
        Binding("equals", "speed_up", "+Speed", show=False),
        Binding("c", "focus_characters", "Chars", show=True),
        Binding("f", "focus_factions", "Factions", show=True),
        Binding("l", "focus_locations", "Locs", show=True),
        Binding("e", "focus_events", "Events", show=True),
        Binding("enter", "inspect", "Inspect", show=False),
        Binding("r", "relations", "Relations", show=False),
        Binding("R", "global_relations", "All Rels", show=True, key_display="R"),
        Binding("o", "outcomes", "Outcomes", show=True),
        Binding("s", "change_seed", "Seed", show=True),
        Binding("x", "export", "Export", show=True),
        Binding("ctrl+s", "save_worldpack", "Save", show=True, key_display="^S"),
        Binding("v", "validate", "Validate", show=True),
        Binding("h", "harmonic", "Harmonic", show=True),
        Binding("m", "map", "Map", show=True),
        Binding("t", "timeline", "Timeline", show=True),
        Binding("L", "lifepack", "LifePack", show=True, key_display="L"),
    ]

    def __init__(self, bridge: SimulatorBridge) -> None:
        super().__init__()
        self.bridge = bridge
        self._play_timer: Timer | None = None
        self._play_speed: float = 1.0  # seconds per hour
        self._playing: bool = False

    def compose(self) -> ComposeResult:
        # Header
        seed_str = f"seed {self.bridge.seed:03d}"
        yield Static(
            f"  GIGAGEN \u00b7 {self.bridge.ws.world_id} \u00b7 {seed_str}",
            id="header-bar",
        )

        # Timeline bar
        yield TimelineBar(id="timeline")

        # Main content
        with Vertical(id="main-content"):
            # Top row: characters + event log
            with Horizontal(id="top-row"):
                with Vertical(id="char-panel"):
                    yield CharacterTable(id="characters")
                with Vertical(id="event-panel"):
                    yield EventLogPanel(id="eventlog")

            # Bottom row: factions + locations + variables
            with Horizontal(id="bottom-row"):
                with Vertical(id="faction-panel"):
                    yield FactionPanel(id="factions")
                with Vertical(id="location-panel"):
                    yield LocationPanel(id="locations")
                with Vertical(id="variables-panel"):
                    yield VariablesPanel(id="variables")

        # Footer
        yield Footer()

    def on_mount(self) -> None:
        # Initialize known variables from worldpack event rules
        variables = self.query_one("#variables", VariablesPanel)
        variables.set_known_vars(self.bridge.known_variable_names)
        self._refresh_all()

    def _refresh_all(self) -> None:
        """Refresh all panels with current state."""
        b = self.bridge

        # Header
        header = self.query_one("#header-bar", Static)
        dirty = " [yellow][MODIFIED][/yellow]" if b.dirty else ""
        header.update(
            f"  GIGAGEN \u00b7 {b.ws.world_id} \u00b7 seed {b.seed:03d}"
            f"     H{b.current_hour:02d}/H{b.max_hour:02d}"
            f"     Cohesion: {b.cohesion:+.1f}{dirty}"
        )

        # Timeline
        timeline = self.query_one("#timeline", TimelineBar)
        timeline.hour = b.current_hour
        timeline.max_hour = b.max_hour
        timeline.playing = self._playing
        timeline.speed = self._play_speed

        # Characters
        char_table = self.query_one("#characters", CharacterTable)
        char_table.update_data(b.ws, b.sim)

        # Event log
        event_log = self.query_one("#eventlog", EventLogPanel)
        event_log.update_data(b.event_log, b.current_hour)

        # Factions
        factions = self.query_one("#factions", FactionPanel)
        factions.update_data(b.ws)

        # Locations
        locations = self.query_one("#locations", LocationPanel)
        locations.update_data(b.ws)

        # Variables
        variables = self.query_one("#variables", VariablesPanel)
        variables.update_data(b.resolved_variables)

    # --- Time control actions ---

    def _get_active_map(self) -> "MapScreen | None":
        """Return the active MapScreen if one is on top, else None."""
        if len(self.screen_stack) > 1:
            top = self.screen_stack[-1]
            if isinstance(top, MapScreen):
                return top
        return None

    def _has_modal(self) -> bool:
        """Check if a non-map modal screen is currently active."""
        if len(self.screen_stack) <= 1:
            return False
        return not isinstance(self.screen_stack[-1], MapScreen)

    def action_step_forward_1(self) -> None:
        if self._has_modal():
            return
        map_screen = self._get_active_map()
        if map_screen:
            map_screen.step_and_refresh(1)
        else:
            self.bridge.step_forward(1)
            self._refresh_all()

    def action_step_forward_5(self) -> None:
        if self._has_modal():
            return
        map_screen = self._get_active_map()
        if map_screen:
            map_screen.step_and_refresh(5)
        else:
            self.bridge.step_forward(5)
            self._refresh_all()

    def action_step_backward_1(self) -> None:
        if self._has_modal():
            return
        map_screen = self._get_active_map()
        if map_screen:
            map_screen.step_and_refresh(-1)
        else:
            self.bridge.step_backward(1)
            self._refresh_all()

    def action_step_backward_5(self) -> None:
        if self._has_modal():
            return
        map_screen = self._get_active_map()
        if map_screen:
            map_screen.step_and_refresh(-5)
        else:
            self.bridge.step_backward(5)
            self._refresh_all()

    def action_jump_start(self) -> None:
        if self._has_modal():
            return
        self.bridge.jump_to(0)
        map_screen = self._get_active_map()
        if map_screen:
            map_screen.refresh_map()
        else:
            self._refresh_all()

    def action_jump_end(self) -> None:
        if self._has_modal():
            return
        self.bridge.jump_to(self.bridge.max_hour)
        map_screen = self._get_active_map()
        if map_screen:
            map_screen.refresh_map()
        else:
            self._refresh_all()

    def action_toggle_play(self) -> None:
        map_screen = self._get_active_map()
        if map_screen:
            map_screen.action_toggle_play()
            return
        if self._has_modal():
            return
        if self._playing:
            self._stop_play()
        else:
            self._start_play()

    def _start_play(self) -> None:
        if self.bridge.current_hour >= self.bridge.max_hour:
            return
        self._playing = True
        self._play_timer = self.set_interval(
            self._play_speed, self._auto_step, name="autoplay"
        )
        self._refresh_all()

    def _stop_play(self) -> None:
        self._playing = False
        if self._play_timer is not None:
            self._play_timer.stop()
            self._play_timer = None
        self._refresh_all()

    def _auto_step(self) -> None:
        if self.bridge.current_hour >= self.bridge.max_hour:
            self._stop_play()
            return
        self.bridge.step_forward(1)
        self._refresh_all()

    def action_speed_up(self) -> None:
        self._play_speed = max(0.1, self._play_speed - 0.1)
        self._play_speed = round(self._play_speed, 1)
        if self._playing:
            self._stop_play()
            self._start_play()
        else:
            self._refresh_all()

    def action_speed_down(self) -> None:
        self._play_speed = min(5.0, self._play_speed + 0.1)
        self._play_speed = round(self._play_speed, 1)
        if self._playing:
            self._stop_play()
            self._start_play()
        else:
            self._refresh_all()

    # --- Panel focus actions ---

    def action_focus_characters(self) -> None:
        self.query_one("#char-table", DataTable).focus()

    def action_focus_factions(self) -> None:
        try:
            self.query_one("#fac-table", DataTable).focus()
        except Exception:
            self.query_one("#factions").focus()

    def action_focus_locations(self) -> None:
        try:
            self.query_one("#loc-table", DataTable).focus()
        except Exception:
            self.query_one("#locations").focus()

    def action_focus_events(self) -> None:
        self.query_one("#eventlog").focus()

    # --- Row selection handler (Enter on DataTables) ---

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle Enter on any main DataTable — open the appropriate editor."""
        table_id = event.data_table.id
        entity_id = str(event.row_key.value) if event.row_key.value else None
        if not entity_id:
            return

        if table_id == "char-table":
            self._open_character_editor(entity_id)
        elif table_id == "fac-table":
            # Row keys are "fac.xxx::SubName" or "fac.xxx"
            faction_id = entity_id.split("::")[0]
            self._open_faction_editor(faction_id)
        elif table_id == "loc-table":
            self._open_location_editor(entity_id)

    # --- Inspection actions ---

    def _get_focused_entity_id(self) -> str | None:
        """Get the selected entity from whichever panel has focus."""
        # Check factions panel
        fac_panel = self.query_one("#factions", FactionPanel)
        fac_id = fac_panel.get_selected_id()
        try:
            if self.query_one("#fac-table", DataTable).has_focus:
                return fac_id
        except Exception:
            pass
        # Check locations panel
        loc_panel = self.query_one("#locations", LocationPanel)
        loc_id = loc_panel.get_selected_id()
        try:
            if self.query_one("#loc-table", DataTable).has_focus:
                return loc_id
        except Exception:
            pass
        # Default to character table
        char_table = self.query_one("#characters", CharacterTable)
        return char_table.get_selected_id()

    def action_inspect(self) -> None:
        # If faction table has focus, open faction editor
        try:
            fac_table = self.query_one("#fac-table", DataTable)
            if fac_table.has_focus:
                fac_panel = self.query_one("#factions", FactionPanel)
                fac_id = fac_panel.get_selected_id()
                if fac_id:
                    self._open_faction_editor(fac_id)
                return
        except Exception:
            pass

        # If location table has focus, open location editor
        try:
            loc_table = self.query_one("#loc-table", DataTable)
            if loc_table.has_focus:
                loc_panel = self.query_one("#locations", LocationPanel)
                loc_id = loc_panel.get_selected_id()
                if loc_id:
                    self._open_location_editor(loc_id)
                return
        except Exception:
            pass

        # If character table has focus, open character editor
        try:
            char_dt = self.query_one("#char-table", DataTable)
            if char_dt.has_focus:
                char_table = self.query_one("#characters", CharacterTable)
                char_id = char_table.get_selected_id()
                if char_id:
                    self._open_character_editor(char_id)
                return
        except Exception:
            pass

        # Otherwise inspect selected entity
        entity_id = self._get_focused_entity_id()
        if entity_id:
            self.push_screen(
                InspectorScreen(entity_id, self.bridge.ws, self.bridge.sim)
            )

    def _open_faction_editor(self, faction_id: str) -> None:
        def on_result(changed: bool) -> None:
            if changed:
                self._refresh_all()

        self.push_screen(
            FactionEditorScreen(faction_id, self.bridge),
            on_result,
        )

    def _open_location_editor(self, location_id: str) -> None:
        def on_result(changed: bool) -> None:
            if changed:
                self._refresh_all()

        self.push_screen(
            LocationEditorScreen(location_id, self.bridge),
            on_result,
        )

    def _open_character_editor(self, char_id: str) -> None:
        def on_result(changed: bool) -> None:
            if changed:
                self._refresh_all()

        self.push_screen(
            CharacterEditorScreen(char_id, self.bridge),
            on_result,
        )

    def action_relations(self) -> None:
        entity_id = self._get_focused_entity_id()
        if entity_id:
            self.push_screen(RelationsScreen(entity_id, self.bridge.ws))

    def action_global_relations(self) -> None:
        self.push_screen(GlobalRelationsScreen(self.bridge.ws, self.bridge))

    def action_outcomes(self) -> None:
        self.push_screen(
            OutcomesScreen(self.bridge.sim, self.bridge.current_hour)
        )

    # --- Global actions ---

    def action_change_seed(self) -> None:
        def on_seed(new_seed: int | None) -> None:
            if new_seed is not None and new_seed != self.bridge.seed:
                self._stop_play()
                self.bridge.change_seed(new_seed)
                self._refresh_all()

        self.push_screen(SeedPickerScreen(self.bridge.seed), on_seed)

    def action_export(self) -> None:
        path = f"outputs/{self.bridge.ws.world_id}_seed_{self.bridge.seed:03d}_H{self.bridge.current_hour:02d}.json"
        result = export_world_state(self.bridge.ws, path)
        self.notify(f"Exported to {result}", title="Export")

    def action_save_worldpack(self) -> None:
        save_worldpack(self.bridge.ws, self.bridge.worldpack_dir)
        self.bridge.dirty = False
        self._refresh_all()
        self.notify("Worldpack saved", title="Save")

    def action_validate(self) -> None:
        self.push_screen(ValidationResultScreen(self.bridge))

    def action_harmonic(self) -> None:
        self.push_screen(HarmonicDashboardScreen(self.bridge.ws))

    def action_map(self) -> None:
        def on_dismiss(_: None) -> None:
            self._refresh_all()
        self.push_screen(MapScreen(self.bridge), on_dismiss)

    def action_timeline(self) -> None:
        def on_dismiss(hour: int | None) -> None:
            if hour is not None:
                self.bridge.jump_to(hour)
            self._refresh_all()
        self.push_screen(TimelineScreen(self.bridge), on_dismiss)

    def action_lifepack(self) -> None:
        """Open the Life Pack inspector for the selected character."""
        try:
            char_table = self.query_one("#characters", CharacterTable)
            char_id = char_table.get_selected_id()
            if char_id:
                self.push_screen(
                    LifePackInspectorScreen(char_id, self.bridge.ws)
                )
        except Exception:
            pass

    def action_help(self) -> None:
        self.push_screen(HelpScreen())


def run_tui(
    worldpack_dir: str | Path,
    seed: int = 1,
) -> None:
    """Launch the Gigagen TUI."""
    bridge = SimulatorBridge.from_worldpack(worldpack_dir, seed=seed)
    app = GigagenApp(bridge)
    app.run()
