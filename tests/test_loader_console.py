"""Milestone 3 tests — loader, exporter, and console."""

from __future__ import annotations

import io
import json
import pathlib

import pytest

from gigagen.core.entity import Character, Faction, Location
from gigagen.core.world_state import WorldState
from gigagen.io.load_worldpack import load_worldpack
from gigagen.io.export_world_state import export_world_state
from gigagen.cli.console import run_console, _handle_command


WORLDS_DIR = pathlib.Path(__file__).resolve().parent.parent / "worlds" / "kilima"
OUTPUTS_DIR = pathlib.Path(__file__).resolve().parent.parent / "outputs"


# ---------------------------------------------------------------------------
# Loader tests
# ---------------------------------------------------------------------------

class TestLoadWorldpack:
    @pytest.fixture(scope="class")
    def ws(self) -> WorldState:
        return load_worldpack(WORLDS_DIR, seed=1)

    def test_world_id(self, ws: WorldState) -> None:
        assert ws.world_id == "world.kilima"

    def test_seed(self, ws: WorldState) -> None:
        assert ws.seed == 1

    def test_phase(self, ws: WorldState) -> None:
        assert ws.phase == "block_1_start"

    def test_loads_12_characters(self, ws: WorldState) -> None:
        chars = [e for e in ws.entities.values() if isinstance(e, Character)]
        assert len(chars) == 12

    def test_loads_4_factions(self, ws: WorldState) -> None:
        facs = [e for e in ws.entities.values() if isinstance(e, Faction)]
        assert len(facs) == 4

    def test_loads_15_locations(self, ws: WorldState) -> None:
        locs = [e for e in ws.entities.values() if isinstance(e, Location)]
        assert len(locs) == 15

    def test_loads_27_relations(self, ws: WorldState) -> None:
        assert len(ws.relations) == 27

    def test_active_factions(self, ws: WorldState) -> None:
        assert len(ws.active_faction_ids) == 4

    def test_active_locations(self, ws: WorldState) -> None:
        assert len(ws.active_location_ids) == 15

    def test_no_kilima_data_in_gigagen_source(self) -> None:
        """Verify no Kilima data is hardcoded in Gigagen core/io source."""
        src_dir = pathlib.Path(__file__).resolve().parent.parent / "src" / "gigagen"
        kilima_names = {"Kive", "Len", "Freya", "Brais", "Resistencia", "kilima"}
        for py_file in src_dir.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            for name in kilima_names:
                assert name not in content, (
                    f"Kilima data '{name}' found in {py_file.relative_to(src_dir)}"
                )


class TestLoaderReproducibility:
    def test_same_seed_same_output(self) -> None:
        ws1 = load_worldpack(WORLDS_DIR, seed=42)
        ws2 = load_worldpack(WORLDS_DIR, seed=42)
        assert ws1.model_dump_json() == ws2.model_dump_json()

    def test_different_seeds_differ(self) -> None:
        ws1 = load_worldpack(WORLDS_DIR, seed=1)
        ws2 = load_worldpack(WORLDS_DIR, seed=2)
        assert ws1.model_dump_json() != ws2.model_dump_json()


# ---------------------------------------------------------------------------
# Exporter tests
# ---------------------------------------------------------------------------

class TestExporter:
    def test_export_creates_file(self, tmp_path: pathlib.Path) -> None:
        ws = load_worldpack(WORLDS_DIR, seed=1)
        out_path = tmp_path / "test_export.json"
        result = export_world_state(ws, out_path)
        assert result.exists()

    def test_export_valid_json(self, tmp_path: pathlib.Path) -> None:
        ws = load_worldpack(WORLDS_DIR, seed=1)
        out_path = tmp_path / "test_export.json"
        export_world_state(ws, out_path)
        data = json.loads(out_path.read_text(encoding="utf-8"))
        assert data["world_id"] == "world.kilima"
        assert data["seed"] == 1

    def test_export_reproducible(self, tmp_path: pathlib.Path) -> None:
        ws1 = load_worldpack(WORLDS_DIR, seed=7)
        ws2 = load_worldpack(WORLDS_DIR, seed=7)
        p1 = tmp_path / "a.json"
        p2 = tmp_path / "b.json"
        export_world_state(ws1, p1)
        export_world_state(ws2, p2)
        assert p1.read_text(encoding="utf-8") == p2.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Console tests
# ---------------------------------------------------------------------------

class TestConsole:
    @pytest.fixture
    def ws(self) -> WorldState:
        return load_worldpack(WORLDS_DIR, seed=1)

    def _run_cmd(self, ws: WorldState, command: str) -> str:
        out = io.StringIO()
        _handle_command(ws, command, out, "outputs")
        return out.getvalue()

    def test_show_world(self, ws: WorldState) -> None:
        output = self._run_cmd(ws, "show world")
        assert "world.kilima" in output
        assert "Seed:" in output

    def test_list_characters(self, ws: WorldState) -> None:
        output = self._run_cmd(ws, "list characters")
        assert "REB" in output
        assert "ORP" in output
        assert "DEI" in output

    def test_list_factions(self, ws: WorldState) -> None:
        output = self._run_cmd(ws, "list factions")
        assert "The Resistance" in output
        assert "The AI" in output

    def test_list_locations(self, ws: WorldState) -> None:
        output = self._run_cmd(ws, "list locations")
        assert "The Cave" in output
        assert "The Limbo" in output

    def test_inspect_character(self, ws: WorldState) -> None:
        output = self._run_cmd(ws, "inspect char.rebel")
        assert "Kive" in output
        assert "REB" in output
        assert "D#" in output
        assert "Relations" in output

    def test_inspect_faction(self, ws: WorldState) -> None:
        output = self._run_cmd(ws, "inspect fac.resistencia")
        assert "The Resistance" in output
        assert "underground" in output

    def test_inspect_location(self, ws: WorldState) -> None:
        output = self._run_cmd(ws, "inspect loc.cave")
        assert "The Cave" in output
        assert "hidden" in output

    def test_inspect_relations(self, ws: WorldState) -> None:
        output = self._run_cmd(ws, "inspect rel.char.rebel")
        assert "sibling" in output
        assert "close_friend" in output

    def test_inspect_nonexistent(self, ws: WorldState) -> None:
        output = self._run_cmd(ws, "inspect char.nobody")
        assert "not found" in output

    def test_export_command(self, ws: WorldState, tmp_path: pathlib.Path) -> None:
        out_path = tmp_path / "console_export.json"
        output = self._run_cmd(ws, f"export {out_path}")
        assert "Exported" in output
        assert out_path.exists()

    def test_help_command(self, ws: WorldState) -> None:
        output = self._run_cmd(ws, "help")
        assert "show world" in output
        assert "inspect" in output

    def test_unknown_command(self, ws: WorldState) -> None:
        output = self._run_cmd(ws, "foobar")
        assert "Unknown command" in output

    def test_quit_returns_false(self, ws: WorldState) -> None:
        out = io.StringIO()
        result = _handle_command(ws, "quit", out, "outputs")
        assert result is False

    def test_full_session(self, ws: WorldState) -> None:
        """Simulate a full console session via input stream."""
        commands = "show world\nlist characters\nlist factions\nquit\n"
        inp = io.StringIO(commands)
        out = io.StringIO()
        run_console(ws, input_stream=inp, output_stream=out)
        output = out.getvalue()
        assert "world.kilima" in output
        assert "REB" in output
        assert "The Resistance" in output
