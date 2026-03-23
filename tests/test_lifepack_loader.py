"""LP-2 tests: loading Life Packs from worldpack."""

from __future__ import annotations

import pathlib

import pytest

from gigagen.core.lifepack import LifePack
from gigagen.io.load_worldpack import load_worldpack

WORLDPACK = pathlib.Path("worlds/kilima")


class TestLifepackLoading:
    def test_worldpack_loads_with_lifepacks(self) -> None:
        ws = load_worldpack(WORLDPACK, seed=1)
        assert len(ws.lifepacks) >= 1

    def test_kive_lifepack_loaded(self) -> None:
        ws = load_worldpack(WORLDPACK, seed=1)
        lp = ws.get_lifepack("kilima_in12_rebel")
        assert lp is not None
        assert isinstance(lp, LifePack)
        assert lp.meta.entity_id == "kilima_in12_rebel"
        assert lp.meta.tonic == "D#"

    def test_kive_octave_7_has_cris(self) -> None:
        """LP-2 success criterion."""
        ws = load_worldpack(WORLDPACK, seed=1)
        lp = ws.get_lifepack("kilima_in12_rebel")
        assert lp is not None
        slot = lp.octave_7_personajes.slots["7_quinta_justa"]
        assert slot.entity_name == "Cris"

    def test_missing_lifepack_returns_none(self) -> None:
        ws = load_worldpack(WORLDPACK, seed=1)
        assert ws.get_lifepack("nonexistent_character") is None

    def test_lifepack_not_required(self) -> None:
        """Characters without lifepacks still load fine."""
        ws = load_worldpack(WORLDPACK, seed=1)
        # Len has no lifepack file
        assert ws.get_lifepack("kilima_in12_orphan") is None
        # But Len exists as a character
        assert "kilima_in12_orphan" in ws.entities

    def test_lifepack_meta_matches_character(self) -> None:
        ws = load_worldpack(WORLDPACK, seed=1)
        lp = ws.get_lifepack("kilima_in12_rebel")
        assert lp is not None
        char = ws.entities["kilima_in12_rebel"]
        assert lp.meta.entity_name == char.name

    def test_lifepack_serialization_roundtrip(self) -> None:
        ws = load_worldpack(WORLDPACK, seed=1)
        lp = ws.get_lifepack("kilima_in12_rebel")
        assert lp is not None
        # Serialize and reload
        data = lp.model_dump(mode="json")
        restored = LifePack.model_validate(data)
        assert restored.meta.tonic == lp.meta.tonic
        assert len(restored.octave_7_personajes.slots) == len(
            lp.octave_7_personajes.slots
        )
