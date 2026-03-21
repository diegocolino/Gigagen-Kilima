"""Milestone 5 tests — temporal simulation of the 62-hour NB1."""

from __future__ import annotations

import io
import pathlib
from typing import Any

import pytest

from gigagen.core.entity import Character, Location
from gigagen.core.world_state import WorldState
from gigagen.core.simulator import (
    SimulatorState,
    build_simulator,
    advance_to,
    load_timeline_maps,
    load_event_rules,
)
from gigagen.io.load_worldpack import load_worldpack, load_timeline_events
from gigagen.cli.console import run_console, _handle_command, ConsoleContext


WORLDS_DIR = pathlib.Path(__file__).resolve().parent.parent / "worlds" / "kilima"


@pytest.fixture
def ws() -> WorldState:
    return load_worldpack(WORLDS_DIR, seed=1, apply_variation=False)


@pytest.fixture
def events() -> list[dict[str, Any]]:
    return load_timeline_events(WORLDS_DIR)


@pytest.fixture
def char_map() -> dict[str, str]:
    cm, _ = load_timeline_maps(WORLDS_DIR)
    return cm


@pytest.fixture
def loc_map() -> dict[str, str]:
    _, lm = load_timeline_maps(WORLDS_DIR)
    return lm


@pytest.fixture
def erules() -> dict[str, dict[str, Any]]:
    return load_event_rules(WORLDS_DIR)


@pytest.fixture
def sim(
    ws: WorldState,
    events: list[dict[str, Any]],
    char_map: dict[str, str],
    loc_map: dict[str, str],
    erules: dict[str, dict[str, Any]],
) -> SimulatorState:
    return build_simulator(ws, events, char_map=char_map, loc_map=loc_map, event_rules=erules)


# ---------------------------------------------------------------------------
# Timeline loading
# ---------------------------------------------------------------------------

class TestTimelineLoading:
    def test_events_loaded(self, events: list[dict[str, Any]]) -> None:
        assert len(events) > 0

    def test_events_sorted_by_hour(self, events: list[dict[str, Any]]) -> None:
        hours = [e["hour"] for e in events]
        assert hours == sorted(hours)

    def test_has_key_events(self, events: list[dict[str, Any]]) -> None:
        ids = {e.get("id") for e in events}
        assert "E01" in ids, "Missing funeral event"
        assert "E07" in ids, "Missing declaration of war"
        assert "E15" in ids, "Missing kidnapping"
        assert "E09" in ids, "Missing Dev's decision"
        assert "E24" in ids, "Missing final shot"


# ---------------------------------------------------------------------------
# Basic simulation
# ---------------------------------------------------------------------------

class TestSimulation:
    def test_initial_hour(self, sim: SimulatorState) -> None:
        assert sim.current_hour == 0

    def test_advance_basic(
        self, ws: WorldState, sim: SimulatorState, events: list[dict[str, Any]]
    ) -> None:
        entries = advance_to(ws, sim, 1, events, ws.seed)
        assert sim.current_hour == 1
        assert len(entries) >= 0  # may or may not have events at H01

    def test_advance_to_16(
        self, ws: WorldState, sim: SimulatorState, events: list[dict[str, Any]]
    ) -> None:
        """Advance to H16 — Kive declares war, VAR_BRAIS resolved."""
        advance_to(ws, sim, 16, events, ws.seed)
        assert sim.current_hour == 16
        assert len(sim.event_log) > 0
        # Brais variable should be resolved at H16
        assert "VAR_BRAIS" in sim.resolved_variables

    def test_advance_to_20_brais_dies(
        self, ws: WorldState, sim: SimulatorState, events: list[dict[str, Any]]
    ) -> None:
        """At H20, Brais dies and Nora+Pau are kidnapped."""
        advance_to(ws, sim, 20, events, ws.seed)
        brais = ws.entities.get("char.innocent")
        assert isinstance(brais, Character)
        assert brais.status == "dead"
        assert sim.outcomes["char.innocent"].life_state == "dead"

        nora = ws.entities.get("char.caregiver")
        assert isinstance(nora, Character)
        assert nora.status == "captive"

    def test_advance_to_35_dev_decision(
        self, ws: WorldState, sim: SimulatorState, events: list[dict[str, Any]]
    ) -> None:
        """At H35, Dev's decision is resolved."""
        advance_to(ws, sim, 35, events, ws.seed)
        assert "VAR_DEV" in sim.resolved_variables
        assert sim.resolved_variables["VAR_DEV"] in ("participates", "refuses")

    def test_advance_to_37_rescued(
        self, ws: WorldState, sim: SimulatorState, events: list[dict[str, Any]]
    ) -> None:
        """At H37, Nora+Pau are rescued by Yeri."""
        advance_to(ws, sim, 37, events, ws.seed)
        nora = ws.entities.get("char.caregiver")
        assert isinstance(nora, Character)
        assert nora.status == "active"
        assert nora.current_location_id == "loc.cave"

    def test_advance_to_56_cave_breached(
        self, ws: WorldState, sim: SimulatorState, events: list[dict[str, Any]]
    ) -> None:
        """At H56, The Cave is breached."""
        advance_to(ws, sim, 56, events, ws.seed)
        cave = ws.entities.get("loc.cave")
        assert isinstance(cave, Location)
        assert cave.status == "breached"

    def test_advance_to_62_ending(
        self, ws: WorldState, sim: SimulatorState, events: list[dict[str, Any]]
    ) -> None:
        """Full timeline: ending resolved, someone dies."""
        advance_to(ws, sim, 62, events, ws.seed)
        assert sim.current_hour == 62
        assert "VAR_ENDING" in sim.resolved_variables

        ending = sim.resolved_variables["VAR_ENDING"]
        if ending == "kive_dies":
            kive = ws.entities.get("char.rebel")
            assert isinstance(kive, Character)
            assert kive.status == "dead"
        else:
            pau = ws.entities.get("char.jester")
            assert isinstance(pau, Character)
            assert pau.status == "dead"

    def test_cannot_advance_past_max(
        self, ws: WorldState, sim: SimulatorState, events: list[dict[str, Any]]
    ) -> None:
        advance_to(ws, sim, 100, events, ws.seed)
        assert sim.current_hour == 62


# ---------------------------------------------------------------------------
# Cohesion tracking
# ---------------------------------------------------------------------------

class TestCohesion:
    def test_cohesion_changes(
        self, ws: WorldState, sim: SimulatorState, events: list[dict[str, Any]]
    ) -> None:
        """Cohesion should change as events occur."""
        advance_to(ws, sim, 62, events, ws.seed)
        # Some events have cohesion deltas, so total should not be 0
        assert sim.cohesion != 0.0


# ---------------------------------------------------------------------------
# Event log
# ---------------------------------------------------------------------------

class TestEventLog:
    def test_log_populated(
        self, ws: WorldState, sim: SimulatorState, events: list[dict[str, Any]]
    ) -> None:
        advance_to(ws, sim, 62, events, ws.seed)
        assert len(sim.event_log) > 20

    def test_log_has_variable_markers(
        self, ws: WorldState, sim: SimulatorState, events: list[dict[str, Any]]
    ) -> None:
        advance_to(ws, sim, 62, events, ws.seed)
        var_entries = [e for e in sim.event_log if e.variable_resolved]
        assert len(var_entries) == 3, f"Expected 3 variable resolutions, got {len(var_entries)}"


# ---------------------------------------------------------------------------
# Outcomes
# ---------------------------------------------------------------------------

class TestOutcomes:
    def test_outcomes_for_all_12(
        self, ws: WorldState, sim: SimulatorState, events: list[dict[str, Any]]
    ) -> None:
        assert len(sim.outcomes) == 12

    def test_outcomes_after_full_run(
        self, ws: WorldState, sim: SimulatorState, events: list[dict[str, Any]]
    ) -> None:
        advance_to(ws, sim, 62, events, ws.seed)
        # Brais should be automaton
        assert sim.outcomes["char.innocent"].life_state == "automaton"
        # Len should still be digitalized
        assert sim.outcomes["char.orphan"].life_state == "digitalized"


# ---------------------------------------------------------------------------
# Console commands (advance, hour, outcomes, log)
# ---------------------------------------------------------------------------

class TestSimulatorConsole:
    def _make_ctx(
        self, ws: WorldState, events: list[dict[str, Any]],
        char_map: dict[str, str], loc_map: dict[str, str],
        erules: dict[str, dict[str, Any]],
    ) -> ConsoleContext:
        sim = build_simulator(ws, events, char_map=char_map, loc_map=loc_map, event_rules=erules)
        return ConsoleContext(ws=ws, sim=sim, timeline_events=events)

    def test_advance_command(
        self, ws: WorldState, events: list[dict[str, Any]],
        char_map: dict[str, str], loc_map: dict[str, str],
        erules: dict[str, dict[str, Any]],
    ) -> None:
        ctx = self._make_ctx(ws, events, char_map, loc_map, erules)
        out = io.StringIO()
        _handle_command(ctx, "advance 20", out)
        output = out.getvalue()
        assert "H20" in output
        assert ctx.sim.current_hour == 20

    def test_hour_command(
        self, ws: WorldState, events: list[dict[str, Any]],
        char_map: dict[str, str], loc_map: dict[str, str],
        erules: dict[str, dict[str, Any]],
    ) -> None:
        ctx = self._make_ctx(ws, events, char_map, loc_map, erules)
        out = io.StringIO()
        _handle_command(ctx, "hour", out)
        output = out.getvalue()
        assert "H00" in output

    def test_outcomes_command(
        self, ws: WorldState, events: list[dict[str, Any]],
        char_map: dict[str, str], loc_map: dict[str, str],
        erules: dict[str, dict[str, Any]],
    ) -> None:
        ctx = self._make_ctx(ws, events, char_map, loc_map, erules)
        advance_to(ctx.ws, ctx.sim, 62, events, ws.seed)
        out = io.StringIO()
        _handle_command(ctx, "outcomes", out)
        output = out.getvalue()
        assert "dead" in output or "automaton" in output

    def test_log_command(
        self, ws: WorldState, events: list[dict[str, Any]],
        char_map: dict[str, str], loc_map: dict[str, str],
        erules: dict[str, dict[str, Any]],
    ) -> None:
        ctx = self._make_ctx(ws, events, char_map, loc_map, erules)
        advance_to(ctx.ws, ctx.sim, 20, events, ws.seed)
        out = io.StringIO()
        _handle_command(ctx, "log", out)
        output = out.getvalue()
        assert "Event log" in output

    def test_full_simulation_session(
        self, ws: WorldState, events: list[dict[str, Any]],
        char_map: dict[str, str], loc_map: dict[str, str],
        erules: dict[str, dict[str, Any]],
    ) -> None:
        """Full session: advance through timeline, check outcomes."""
        commands = "advance 62\noutcomes\nhour\nlog 5\nquit\n"
        inp = io.StringIO(commands)
        out = io.StringIO()
        run_console(
            ws, timeline_events=events,
            char_map=char_map, loc_map=loc_map, event_rules=erules,
            input_stream=inp, output_stream=out,
        )
        output = out.getvalue()
        assert "H62" in output
        assert "dead" in output or "automaton" in output


# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------

class TestSimulatorReproducibility:
    def test_same_seed_same_simulation(
        self, events: list[dict[str, Any]],
        char_map: dict[str, str], loc_map: dict[str, str],
        erules: dict[str, dict[str, Any]],
    ) -> None:
        """Same seed produces identical simulation results."""
        ws1 = load_worldpack(WORLDS_DIR, seed=42, apply_variation=False)
        sim1 = build_simulator(ws1, events, char_map=char_map, loc_map=loc_map, event_rules=erules)
        advance_to(ws1, sim1, 62, events, ws1.seed)

        ws2 = load_worldpack(WORLDS_DIR, seed=42, apply_variation=False)
        sim2 = build_simulator(ws2, events, char_map=char_map, loc_map=loc_map, event_rules=erules)
        advance_to(ws2, sim2, 62, events, ws2.seed)

        assert sim1.resolved_variables == sim2.resolved_variables
        assert sim1.cohesion == sim2.cohesion
        assert len(sim1.event_log) == len(sim2.event_log)
