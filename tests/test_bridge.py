"""Tests for SimulatorBridge — snapshot fidelity, rewind, seed switching."""

from __future__ import annotations

import copy
import pytest
from pathlib import Path

from gigagen.cli.tui.bridge import SimulatorBridge, Snapshot
from gigagen.core.entity import Character
from gigagen.core.world_state import WorldState
from gigagen.io.load_worldpack import load_worldpack, load_timeline_events
from gigagen.core.simulator import (
    build_simulator,
    load_timeline_maps,
    load_event_rules,
)

WORLDPACK = Path("worlds/kilima")


@pytest.fixture
def bridge() -> SimulatorBridge:
    return SimulatorBridge.from_worldpack(WORLDPACK, seed=1)


# ---------- Construction ----------

class TestBridgeConstruction:
    def test_creates_from_worldpack(self, bridge: SimulatorBridge) -> None:
        assert bridge.ws is not None
        assert bridge.sim is not None
        assert bridge.current_hour == 0
        assert bridge.max_hour == 62
        assert len(bridge.timeline_events) > 0

    def test_initial_snapshot_saved(self, bridge: SimulatorBridge) -> None:
        assert 0 in bridge.snapshots
        assert bridge.snapshots[0].hour == 0

    def test_seed_stored(self, bridge: SimulatorBridge) -> None:
        assert bridge.seed == 1


# ---------- Step Forward ----------

class TestStepForward:
    def test_step_forward_one(self, bridge: SimulatorBridge) -> None:
        bridge.step_forward(1)
        assert bridge.current_hour == 1

    def test_step_forward_multiple(self, bridge: SimulatorBridge) -> None:
        bridge.step_forward(5)
        assert bridge.current_hour == 5

    def test_step_forward_creates_snapshots(self, bridge: SimulatorBridge) -> None:
        bridge.step_forward(3)
        # Should have snapshots at H0, H1, H2, H3
        assert set(bridge.snapshots.keys()) == {0, 1, 2, 3}

    def test_step_forward_clamps_to_max(self, bridge: SimulatorBridge) -> None:
        bridge.step_forward(100)
        assert bridge.current_hour == 62

    def test_step_forward_at_max_is_noop(self, bridge: SimulatorBridge) -> None:
        bridge.step_forward(100)
        entries = bridge.step_forward(1)
        assert entries == []
        assert bridge.current_hour == 62


# ---------- Step Backward ----------

class TestStepBackward:
    def test_step_backward(self, bridge: SimulatorBridge) -> None:
        bridge.step_forward(5)
        bridge.step_backward(2)
        assert bridge.current_hour == 3

    def test_step_backward_to_zero(self, bridge: SimulatorBridge) -> None:
        bridge.step_forward(3)
        bridge.step_backward(10)
        assert bridge.current_hour == 0

    def test_step_backward_at_zero(self, bridge: SimulatorBridge) -> None:
        result = bridge.step_backward(1)
        assert result is True
        assert bridge.current_hour == 0


# ---------- Jump To ----------

class TestJumpTo:
    def test_jump_forward(self, bridge: SimulatorBridge) -> None:
        bridge.jump_to(10)
        assert bridge.current_hour == 10

    def test_jump_backward(self, bridge: SimulatorBridge) -> None:
        bridge.step_forward(10)
        bridge.jump_to(3)
        assert bridge.current_hour == 3

    def test_jump_to_same(self, bridge: SimulatorBridge) -> None:
        bridge.step_forward(5)
        result = bridge.jump_to(5)
        assert result is True
        assert bridge.current_hour == 5

    def test_jump_clamps_min(self, bridge: SimulatorBridge) -> None:
        bridge.jump_to(-5)
        assert bridge.current_hour == 0

    def test_jump_clamps_max(self, bridge: SimulatorBridge) -> None:
        bridge.jump_to(999)
        assert bridge.current_hour == 62


# ---------- Snapshot Fidelity ----------

class TestSnapshotFidelity:
    def test_rewind_restores_world_state(self, bridge: SimulatorBridge) -> None:
        """After advancing and rewinding, world state matches the snapshot."""
        bridge.step_forward(5)
        # Save state at H5 for comparison
        h5_entities_count = len(bridge.ws.entities)

        bridge.step_forward(20)
        # State has progressed
        assert bridge.current_hour == 25

        # Rewind to H5
        bridge.jump_to(5)
        assert bridge.current_hour == 5
        assert len(bridge.ws.entities) == h5_entities_count

    def test_rewind_restores_simulator_state(self, bridge: SimulatorBridge) -> None:
        """After rewinding, simulator state (cohesion, log, etc.) matches."""
        bridge.step_forward(10)
        h10_cohesion = bridge.cohesion
        h10_log_len = len(bridge.event_log)

        bridge.step_forward(20)
        bridge.jump_to(10)

        assert bridge.cohesion == h10_cohesion
        assert len(bridge.event_log) == h10_log_len

    def test_rewind_to_zero_restores_initial(self, bridge: SimulatorBridge) -> None:
        """Rewinding to H00 gives the pristine initial state."""
        # Capture initial character statuses
        initial_statuses = {}
        for eid, ent in bridge.ws.entities.items():
            if isinstance(ent, Character):
                initial_statuses[eid] = ent.status

        bridge.step_forward(62)
        bridge.jump_to(0)

        for eid, status in initial_statuses.items():
            ent = bridge.ws.entities[eid]
            if isinstance(ent, Character):
                assert ent.status == status, f"{eid} status mismatch after rewind"

    def test_forward_after_rewind_is_deterministic(self, bridge: SimulatorBridge) -> None:
        """Advancing from the same snapshot produces identical results."""
        bridge.step_forward(30)
        h30_ws_json = bridge.ws.model_dump_json()

        # Rewind to 0 and advance again
        bridge.jump_to(0)
        bridge.step_forward(30)
        assert bridge.ws.model_dump_json() == h30_ws_json


# ---------- Seed Switching ----------

class TestSeedSwitching:
    def test_change_seed_resets_hour(self, bridge: SimulatorBridge) -> None:
        bridge.step_forward(20)
        bridge.change_seed(42)
        assert bridge.current_hour == 0
        assert bridge.seed == 42

    def test_change_seed_clears_snapshots(self, bridge: SimulatorBridge) -> None:
        bridge.step_forward(10)
        assert len(bridge.snapshots) > 1
        bridge.change_seed(99)
        # Should have only the new H00 snapshot
        assert set(bridge.snapshots.keys()) == {0}

    def test_different_seeds_different_state(self, bridge: SimulatorBridge) -> None:
        """Different seeds should produce different world states at H62."""
        bridge.step_forward(62)
        seed1_json = bridge.ws.model_dump_json()

        bridge.change_seed(999)
        bridge.step_forward(62)
        seed999_json = bridge.ws.model_dump_json()

        # Seeds apply variation, so states should differ
        assert seed1_json != seed999_json

    def test_same_seed_same_result(self, bridge: SimulatorBridge) -> None:
        """Re-running with the same seed must produce identical state."""
        bridge.step_forward(62)
        run1_json = bridge.ws.model_dump_json()

        bridge.change_seed(1)  # Same seed
        bridge.step_forward(62)
        run2_json = bridge.ws.model_dump_json()

        assert run1_json == run2_json


# ---------- Reset ----------

class TestReset:
    def test_reset_returns_to_h00(self, bridge: SimulatorBridge) -> None:
        bridge.step_forward(30)
        bridge.reset()
        assert bridge.current_hour == 0

    def test_reset_preserves_seed(self, bridge: SimulatorBridge) -> None:
        bridge.step_forward(10)
        bridge.reset()
        assert bridge.seed == 1


# ---------- Helper Methods ----------

class TestHelpers:
    def test_events_at_hour(self, bridge: SimulatorBridge) -> None:
        events = bridge.events_at_hour(0)
        # There may or may not be events at H0, but method should work
        assert isinstance(events, list)

    def test_events_up_to_hour(self, bridge: SimulatorBridge) -> None:
        bridge.step_forward(10)
        logged = bridge.events_up_to_hour(10)
        for e in logged:
            assert e.hour <= 10
