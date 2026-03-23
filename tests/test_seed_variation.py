"""Milestone 4 tests — seed variation and invariant validation."""

from __future__ import annotations

import pathlib

import pytest

from gigagen.core.entity import Character, MacroFaction, Location
from gigagen.core.world_state import WorldState
from gigagen.core.seed import apply_seed_variation
from gigagen.core.invariants import validate_invariants
from gigagen.io.load_worldpack import load_worldpack


WORLDS_DIR = pathlib.Path(__file__).resolve().parent.parent / "worlds" / "kilima"
INVARIANTS_PATH = WORLDS_DIR / "invariants.json"


# ---------------------------------------------------------------------------
# Seed variation tests
# ---------------------------------------------------------------------------

class TestSeedVariation:
    def test_same_seed_same_result(self) -> None:
        ws1 = load_worldpack(WORLDS_DIR, seed=42)
        ws2 = load_worldpack(WORLDS_DIR, seed=42)
        assert ws1.model_dump_json() == ws2.model_dump_json()

    def test_different_seeds_differ(self) -> None:
        ws1 = load_worldpack(WORLDS_DIR, seed=1)
        ws2 = load_worldpack(WORLDS_DIR, seed=2)
        assert ws1.model_dump_json() != ws2.model_dump_json()

    def test_variation_changes_seeded_fields(self) -> None:
        """At least some seeded fields should differ between seeds."""
        ws1 = load_worldpack(WORLDS_DIR, seed=100)
        ws2 = load_worldpack(WORLDS_DIR, seed=200)

        # Collect all character emotions
        emotions_1 = sorted(
            (eid, e.emotional_load)
            for eid, e in ws1.entities.items()
            if isinstance(e, Character)
        )
        emotions_2 = sorted(
            (eid, e.emotional_load)
            for eid, e in ws2.entities.items()
            if isinstance(e, Character)
        )
        # Collect all location tensions
        tensions_1 = sorted(
            (eid, e.tension)
            for eid, e in ws1.entities.items()
            if isinstance(e, Location)
        )
        tensions_2 = sorted(
            (eid, e.tension)
            for eid, e in ws2.entities.items()
            if isinstance(e, Location)
        )

        # At least one field should differ across 100 different seeds
        differ = emotions_1 != emotions_2 or tensions_1 != tensions_2
        assert differ, "Seeds 100 and 200 produced identical seeded fields"

    def test_fixed_identity_preserved(self) -> None:
        """Fixed identity fields must not change between seeds."""
        ws_base = load_worldpack(WORLDS_DIR, seed=1, apply_variation=False)
        for seed in [1, 42, 999, 7777]:
            ws = load_worldpack(WORLDS_DIR, seed=seed)
            for eid, ent in ws.entities.items():
                base_ent = ws_base.entities[eid]
                assert ent.id == base_ent.id
                assert ent.entity_type == base_ent.entity_type
                assert ent.name == base_ent.name
                if isinstance(ent, Character):
                    assert isinstance(base_ent, Character)
                    assert ent.archetype == base_ent.archetype
                    assert ent.note == base_ent.note
                    assert ent.hero_type == base_ent.hero_type
                    assert ent.civil_name == base_ent.civil_name
                    assert ent.role_name == base_ent.role_name
                    assert ent.lineage == base_ent.lineage


# ---------------------------------------------------------------------------
# NB1 variable resolution tests
# ---------------------------------------------------------------------------

class TestVariableResolution:
    def test_variables_resolved(self) -> None:
        ws = load_worldpack(WORLDS_DIR, seed=1)
        var_tags = [t for t in ws.tags if t.startswith("VAR_")]
        assert len(var_tags) == 3, f"Expected 3 variable tags, got {var_tags}"

    def test_var_dev_resolved(self) -> None:
        ws = load_worldpack(WORLDS_DIR, seed=1)
        dev_tags = [t for t in ws.tags if t.startswith("VAR_DEV=")]
        assert len(dev_tags) == 1
        value = dev_tags[0].split("=")[1]
        assert value in ("participates", "refuses")

    def test_var_brais_resolved(self) -> None:
        ws = load_worldpack(WORLDS_DIR, seed=1)
        brais_tags = [t for t in ws.tags if t.startswith("VAR_BRAIS=")]
        assert len(brais_tags) == 1
        value = brais_tags[0].split("=")[1]
        assert value in ("lies", "betrays")

    def test_var_ending_resolved(self) -> None:
        ws = load_worldpack(WORLDS_DIR, seed=1)
        ending_tags = [t for t in ws.tags if t.startswith("VAR_ENDING=")]
        assert len(ending_tags) == 1
        value = ending_tags[0].split("=")[1]
        assert value in ("kive_dies", "pau_dies")

    def test_same_seed_same_variables(self) -> None:
        ws1 = load_worldpack(WORLDS_DIR, seed=42)
        ws2 = load_worldpack(WORLDS_DIR, seed=42)
        vars1 = sorted(t for t in ws1.tags if t.startswith("VAR_"))
        vars2 = sorted(t for t in ws2.tags if t.startswith("VAR_"))
        assert vars1 == vars2

    def test_variables_vary_across_seeds(self) -> None:
        """Over many seeds, both options should appear for at least one variable."""
        dev_values = set()
        for seed in range(1, 50):
            ws = load_worldpack(WORLDS_DIR, seed=seed)
            for t in ws.tags:
                if t.startswith("VAR_DEV="):
                    dev_values.add(t.split("=")[1])
        assert len(dev_values) == 2, (
            f"Expected both 'participates' and 'refuses', got {dev_values}"
        )


# ---------------------------------------------------------------------------
# Invariant validation tests
# ---------------------------------------------------------------------------

class TestInvariantValidation:
    def test_base_worldstate_valid(self) -> None:
        ws = load_worldpack(WORLDS_DIR, seed=1, apply_variation=False)
        result = validate_invariants(ws, INVARIANTS_PATH)
        assert result.valid, f"Invariant errors: {result.errors}"

    def test_varied_worldstate_valid(self) -> None:
        """Seed variation must not break invariants."""
        for seed in [1, 42, 100, 999]:
            ws = load_worldpack(WORLDS_DIR, seed=seed)
            result = validate_invariants(ws, INVARIANTS_PATH)
            assert result.valid, (
                f"Seed {seed} broke invariants: {result.errors}"
            )

    def test_detect_missing_character(self) -> None:
        ws = load_worldpack(WORLDS_DIR, seed=1, apply_variation=False)
        del ws.entities["kilima_in12_rebel"]
        result = validate_invariants(ws, INVARIANTS_PATH)
        assert not result.valid
        assert any("kilima_in12_rebel" in e for e in result.errors)

    def test_detect_wrong_archetype(self) -> None:
        ws = load_worldpack(WORLDS_DIR, seed=1, apply_variation=False)
        rebel = ws.entities["kilima_in12_rebel"]
        assert isinstance(rebel, Character)
        # Bypass pydantic validation to simulate corruption
        rebel.__dict__["archetype"] = "HER"
        result = validate_invariants(ws, INVARIANTS_PATH)
        assert not result.valid
        assert any("archetype" in e for e in result.errors)

    def test_detect_missing_relation(self) -> None:
        ws = load_worldpack(WORLDS_DIR, seed=1, apply_variation=False)
        # Remove the sibling relation
        ws.relations = [r for r in ws.relations if r.kind != "sibling"]
        result = validate_invariants(ws, INVARIANTS_PATH)
        assert not result.valid
        assert any("sibling" in e for e in result.errors)


# ---------------------------------------------------------------------------
# Visible comparison — seed 1 vs seed 2
# ---------------------------------------------------------------------------

class TestSeedComparison:
    def test_comparison_output(self) -> None:
        """Generate a comparison between seed 1 and seed 2."""
        ws1 = load_worldpack(WORLDS_DIR, seed=1)
        ws2 = load_worldpack(WORLDS_DIR, seed=2)

        diffs: list[str] = []

        # Compare variables
        vars1 = {t.split("=")[0]: t.split("=")[1] for t in ws1.tags if "=" in t}
        vars2 = {t.split("=")[0]: t.split("=")[1] for t in ws2.tags if "=" in t}
        for var_id in sorted(set(vars1) | set(vars2)):
            v1 = vars1.get(var_id, "?")
            v2 = vars2.get(var_id, "?")
            if v1 != v2:
                diffs.append(f"  {var_id}: seed1={v1}, seed2={v2}")

        # Compare character emotions
        for eid in sorted(ws1.entities):
            e1 = ws1.entities[eid]
            e2 = ws2.entities[eid]
            if isinstance(e1, Character) and isinstance(e2, Character):
                if e1.emotional_load != e2.emotional_load:
                    diffs.append(
                        f"  {eid} emotion: seed1={e1.emotional_load}, "
                        f"seed2={e2.emotional_load}"
                    )
            if isinstance(e1, Location) and isinstance(e2, Location):
                if e1.tension != e2.tension:
                    diffs.append(
                        f"  {eid} tension: seed1={e1.tension}, "
                        f"seed2={e2.tension}"
                    )

        # There should be differences
        assert len(diffs) > 0, "No differences found between seed 1 and seed 2"

        # Both must still be valid
        r1 = validate_invariants(ws1, INVARIANTS_PATH)
        r2 = validate_invariants(ws2, INVARIANTS_PATH)
        assert r1.valid, f"Seed 1 invalid: {r1.errors}"
        assert r2.valid, f"Seed 2 invalid: {r2.errors}"
