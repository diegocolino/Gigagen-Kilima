"""SimulatorBridge — wraps simulator with snapshot/rewind capability."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from gigagen.core.invariants import ValidationResult, validate_invariants
from gigagen.core.simulator import (
    SimulatorState,
    EventLogEntry,
    build_simulator,
    advance_to,
)
from gigagen.core.world_state import WorldState
from gigagen.io.load_worldpack import load_worldpack, load_timeline_events
from gigagen.core.simulator import load_timeline_maps, load_event_rules


@dataclass
class Snapshot:
    """A frozen copy of world + simulator state at a given hour."""
    hour: int
    ws: WorldState
    sim: SimulatorState


@dataclass
class SimulatorBridge:
    """High-level wrapper around the simulator with rewind support.

    Stores per-hour snapshots so stepping backward is O(1) via deepcopy restore.
    """
    worldpack_dir: Path
    ws: WorldState
    sim: SimulatorState
    timeline_events: list[dict[str, Any]]
    char_map: dict[str, str] = field(default_factory=dict)
    loc_map: dict[str, str] = field(default_factory=dict)
    event_rules: dict[str, dict[str, Any]] = field(default_factory=dict)
    snapshots: dict[int, Snapshot] = field(default_factory=dict)
    seed: int = 1
    dirty: bool = False

    @classmethod
    def from_worldpack(
        cls,
        worldpack_dir: str | Path,
        seed: int = 1,
    ) -> "SimulatorBridge":
        """Load a worldpack and build a fully initialized bridge."""
        import json
        wp = Path(worldpack_dir)
        ws = load_worldpack(wp, seed=seed)
        events = load_timeline_events(wp)
        char_map, loc_map = load_timeline_maps(wp)
        event_rules = load_event_rules(wp)
        # Load max_hour from worldpack defaults
        meta = json.loads((wp / "world.json").read_text(encoding="utf-8"))
        max_hour = meta.get("defaults", {}).get("duration_hours")
        sim = build_simulator(
            ws, events,
            char_map=char_map,
            loc_map=loc_map,
            event_rules=event_rules,
            max_hour=max_hour,
        )
        bridge = cls(
            worldpack_dir=wp,
            ws=ws,
            sim=sim,
            timeline_events=events,
            char_map=char_map,
            loc_map=loc_map,
            event_rules=event_rules,
            seed=seed,
        )
        # Save initial snapshot at H00
        bridge._save_snapshot()
        return bridge

    @property
    def catalogs(self) -> dict[str, Any]:
        """Load catalogs from world.json (cached)."""
        if not hasattr(self, "_catalogs_cache"):
            import json
            meta = json.loads((self.worldpack_dir / "world.json").read_text(encoding="utf-8"))
            self._catalogs_cache: dict[str, Any] = meta.get("catalogs", {})
        return self._catalogs_cache

    @property
    def known_variable_names(self) -> list[str]:
        """Extract variable names from event rules (resolve_variable configs)."""
        var_names: list[str] = []
        for rule in self.event_rules.values():
            var_cfg = rule.get("resolve_variable")
            if var_cfg and "var_id" in var_cfg:
                var_names.append(var_cfg["var_id"])
        return sorted(set(var_names))

    @property
    def current_hour(self) -> int:
        return self.sim.current_hour

    @property
    def max_hour(self) -> int:
        return self.sim.max_hour

    @property
    def cohesion(self) -> float:
        return self.sim.cohesion

    @property
    def event_log(self) -> list[EventLogEntry]:
        return self.sim.event_log

    @property
    def resolved_variables(self) -> dict[str, str]:
        return self.sim.resolved_variables

    @property
    def outcomes(self) -> dict[str, Any]:
        return self.sim.outcomes

    def _save_snapshot(self) -> None:
        """Save current state as a snapshot."""
        self.snapshots[self.sim.current_hour] = Snapshot(
            hour=self.sim.current_hour,
            ws=self.ws.model_copy(deep=True),
            sim=copy.deepcopy(self.sim),
        )

    def _restore_snapshot(self, hour: int) -> None:
        """Restore state from a snapshot."""
        snap = self.snapshots[hour]
        self.ws = snap.ws.model_copy(deep=True)
        self.sim = copy.deepcopy(snap.sim)

    def step_forward(self, n: int = 1) -> list[EventLogEntry]:
        """Advance n hours forward. Returns new event log entries."""
        if self.sim.current_hour >= self.sim.max_hour:
            return []
        target = min(self.sim.current_hour + n, self.sim.max_hour)
        # Advance one hour at a time to capture per-hour snapshots
        all_entries: list[EventLogEntry] = []
        current = self.sim.current_hour
        while current < target:
            next_hour = current + 1
            entries = advance_to(
                self.ws, self.sim, next_hour,
                self.timeline_events, self.seed,
            )
            all_entries.extend(entries)
            self._save_snapshot()
            current = next_hour
        return all_entries

    def step_backward(self, n: int = 1) -> bool:
        """Step backward n hours. Returns True if successful."""
        target = max(self.sim.current_hour - n, 0)
        return self.jump_to(target)

    def jump_to(self, hour: int) -> bool:
        """Jump to a specific hour. Returns True if successful."""
        hour = max(0, min(hour, self.sim.max_hour))
        if hour == self.sim.current_hour:
            return True

        if hour < self.sim.current_hour:
            # Rewind: find nearest snapshot at or before target
            best = -1
            for h in self.snapshots:
                if h <= hour and h > best:
                    best = h
            if best < 0:
                return False
            self._restore_snapshot(best)
            if best == hour:
                return True
            # Advance from snapshot to target
            self.step_forward(hour - best)
            return True
        else:
            # Forward: just advance
            self.step_forward(hour - self.sim.current_hour)
            return True

    def change_seed(self, new_seed: int) -> None:
        """Switch to a new seed. Reloads worldpack and resets to H00."""
        import json
        self.seed = new_seed
        self.snapshots.clear()
        ws = load_worldpack(self.worldpack_dir, seed=new_seed)
        events = load_timeline_events(self.worldpack_dir)
        meta = json.loads((self.worldpack_dir / "world.json").read_text(encoding="utf-8"))
        max_hour = meta.get("defaults", {}).get("duration_hours")
        sim = build_simulator(
            ws, events,
            char_map=self.char_map,
            loc_map=self.loc_map,
            event_rules=self.event_rules,
            max_hour=max_hour,
        )
        self.ws = ws
        self.sim = sim
        self.timeline_events = events
        self._save_snapshot()

    def reset(self) -> None:
        """Reset to H00 with the current seed."""
        self.change_seed(self.seed)

    def events_at_hour(self, hour: int) -> list[dict[str, Any]]:
        """Get timeline events scheduled at a specific hour."""
        return [e for e in self.timeline_events if e.get("hour") == hour]

    def events_up_to_hour(self, hour: int) -> list[EventLogEntry]:
        """Get all logged events up to the given hour."""
        return [e for e in self.sim.event_log if e.hour <= hour]

    def apply_edit(self, mutator: Callable[[WorldState], None]) -> ValidationResult:
        """Apply an edit to the world state with invariant validation.

        1. Deep-copy current ws
        2. Apply mutator to the copy
        3. Validate the copy against invariants
        4. If valid: apply mutator to real ws, save snapshot, set dirty
        5. Return ValidationResult
        """
        test_ws = self.ws.model_copy(deep=True)
        mutator(test_ws)
        invariants_path = self.worldpack_dir / "invariants.json"
        result = validate_invariants(test_ws, invariants_path)
        if result.valid:
            mutator(self.ws)
            self._save_snapshot()
            self.dirty = True
        return result
