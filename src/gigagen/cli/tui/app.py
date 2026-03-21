"""GigagenApp — main Textual application for the God Mode TUI."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.timer import Timer
from textual.widgets import DataTable, Static, Footer

from gigagen.io.export_world_state import export_world_state

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
        Binding("enter", "inspect", "Inspect", show=True),
        Binding("r", "relations", "Relations", show=False),
        Binding("o", "outcomes", "Outcomes", show=True),
        Binding("s", "change_seed", "Seed", show=True),
        Binding("x", "export", "Export", show=True),
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
        header.update(
            f"  GIGAGEN \u00b7 {b.ws.world_id} \u00b7 seed {b.seed:03d}"
            f"     H{b.current_hour:02d}/H{b.max_hour:02d}"
            f"     Cohesion: {b.cohesion:+.1f}"
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

    def action_step_forward_1(self) -> None:
        self.bridge.step_forward(1)
        self._refresh_all()

    def action_step_forward_5(self) -> None:
        self.bridge.step_forward(5)
        self._refresh_all()

    def action_step_backward_1(self) -> None:
        self.bridge.step_backward(1)
        self._refresh_all()

    def action_step_backward_5(self) -> None:
        self.bridge.step_backward(5)
        self._refresh_all()

    def action_jump_start(self) -> None:
        self.bridge.jump_to(0)
        self._refresh_all()

    def action_jump_end(self) -> None:
        self.bridge.jump_to(self.bridge.max_hour)
        self._refresh_all()

    def action_toggle_play(self) -> None:
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
        self.query_one("#factions").focus()

    def action_focus_locations(self) -> None:
        self.query_one("#locations").focus()

    def action_focus_events(self) -> None:
        self.query_one("#eventlog").focus()

    # --- Inspection actions ---

    def action_inspect(self) -> None:
        char_table = self.query_one("#characters", CharacterTable)
        entity_id = char_table.get_selected_id()
        if entity_id:
            self.push_screen(
                InspectorScreen(entity_id, self.bridge.ws, self.bridge.sim)
            )

    def action_relations(self) -> None:
        char_table = self.query_one("#characters", CharacterTable)
        entity_id = char_table.get_selected_id()
        if entity_id:
            self.push_screen(RelationsScreen(entity_id, self.bridge.ws))

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
