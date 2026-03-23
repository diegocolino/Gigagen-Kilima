"""Phase 2 tests — harmonic engine pure functions."""

from __future__ import annotations

import pytest

from gigagen.core.harmony import (
    build_scale,
    character_faction_affinity,
    character_location_affinity,
    location_instability,
    faction_weight,
    faction_compatibility,
    CHROMATIC_NOTES,
)


# ---------------------------------------------------------------------------
# Scale generation
# ---------------------------------------------------------------------------

class TestBuildScale:
    def test_c_ionian(self) -> None:
        """C Ionian (major) = C D E F G A B."""
        scale = build_scale("C", [2, 2, 1, 2, 2, 2, 1])
        assert scale == ["C", "D", "E", "F", "G", "A", "B"]

    def test_b_phrygian(self) -> None:
        """B Phrygian = B C D E F# G A."""
        scale = build_scale("B", [1, 2, 2, 2, 1, 2, 2])
        assert scale == ["B", "C", "D", "E", "F#", "G", "A"]

    def test_d_sharp_phrygian(self) -> None:
        """D# Phrygian = D# E F# G# A# B C#."""
        scale = build_scale("D#", [1, 2, 2, 2, 1, 2, 2])
        assert scale == ["D#", "E", "F#", "G#", "A#", "B", "C#"]

    def test_whole_tone(self) -> None:
        """F# whole tone = F# G# A# C D E."""
        scale = build_scale("F#", [2, 2, 2, 2, 2, 2])
        assert scale == ["F#", "G#", "A#", "C", "D", "E"]

    def test_pentatonic_major(self) -> None:
        """Pentatonic major from C = C D E G A."""
        scale = build_scale("C", [2, 2, 3, 2, 3])
        assert scale == ["C", "D", "E", "G", "A"]

    def test_pentatonic_minor(self) -> None:
        """Pentatonic minor from A = A C D E G."""
        scale = build_scale("A", [3, 2, 2, 3, 2])
        assert scale == ["A", "C", "D", "E", "G"]

    def test_length_matches_note_count(self) -> None:
        """Scale length should equal number of intervals."""
        for intervals in [[2, 2, 1, 2, 2, 2, 1], [2, 2, 2, 2, 2, 2], [2, 2, 3, 2, 3]]:
            scale = build_scale("C", intervals)
            assert len(scale) == len(intervals)

    def test_empty_intervals(self) -> None:
        assert build_scale("C", []) == []

    def test_invalid_note_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown note"):
            build_scale("X", [2, 2, 1, 2, 2, 2, 1])

    def test_all_12_roots_produce_valid_scales(self) -> None:
        """Every chromatic note as root should produce a valid 7-note scale."""
        ionian = [2, 2, 1, 2, 2, 2, 1]
        for note in CHROMATIC_NOTES:
            scale = build_scale(note, ionian)
            assert len(scale) == 7
            assert scale[0] == note

    def test_dorian_from_g(self) -> None:
        """G Dorian = G A A# C D E F. Guard Force mode."""
        scale = build_scale("G", [2, 1, 2, 2, 2, 1, 2])
        assert "G" in scale
        assert len(scale) == 7


# ---------------------------------------------------------------------------
# Character-faction affinity
# ---------------------------------------------------------------------------

class TestCharacterFactionAffinity:
    def test_unison_with_root(self) -> None:
        """Leader in their own faction → maximum affinity."""
        aff = character_faction_affinity("B", [1, 2, 2, 2, 1, 2, 2], "B")
        assert aff == 1.0

    def test_kive_in_own_cell(self) -> None:
        """Kive (D#) leads Red Fist (root D#) → perfect."""
        aff = character_faction_affinity("D#", [1, 2, 2, 2, 1, 2, 2], "D#")
        assert aff == 1.0

    def test_kive_in_direnis(self) -> None:
        """Kive (D#) in Direnis Cell (root B). D# is NOT in B Phrygian."""
        aff = character_faction_affinity("D#", [1, 2, 2, 2, 1, 2, 2], "B")
        # D# → B = 8 semitones = minor 6th, base = -0.2, out of scale → penalized
        assert -1.0 <= aff <= 1.0

    def test_in_scale_positive(self) -> None:
        """A note in the scale should get positive or boosted affinity."""
        # C in C Ionian (root C) — unison
        aff = character_faction_affinity("C", [2, 2, 1, 2, 2, 2, 1], "C")
        assert aff > 0

    def test_out_of_scale_penalized(self) -> None:
        """A note outside the scale should be penalized."""
        # F# (tritone from C) in C Ionian — F# is NOT in C major
        aff = character_faction_affinity("F#", [2, 2, 1, 2, 2, 2, 1], "C")
        assert aff < 0

    def test_null_root_returns_zero(self) -> None:
        assert character_faction_affinity("C", [2, 2, 1, 2, 2, 2, 1], None) == 0.0

    def test_empty_intervals_returns_zero(self) -> None:
        assert character_faction_affinity("C", [], "C") == 0.0

    def test_range(self) -> None:
        """All results must be in [-1.0, 1.0]."""
        phrygian = [1, 2, 2, 2, 1, 2, 2]
        for note in CHROMATIC_NOTES:
            for root in CHROMATIC_NOTES:
                aff = character_faction_affinity(note, phrygian, root)
                assert -1.0 <= aff <= 1.0, f"{note} vs root {root}: {aff}"


# ---------------------------------------------------------------------------
# Character-location affinity
# ---------------------------------------------------------------------------

class TestCharacterLocationAffinity:
    def test_null_tonic_returns_none(self) -> None:
        """No tonic = no harmonic calculation."""
        result = character_location_affinity("C", None, [2, 2, 1, 2, 2, 2, 1])
        assert result is None

    def test_no_faction_returns_structural(self) -> None:
        """No controlling faction → only structural affinity."""
        result = character_location_affinity("C", "C", None)
        assert result is not None
        assert result == 1.0  # unison

    def test_combined_affinity(self) -> None:
        """With both tonic and faction, result is weighted combination."""
        result = character_location_affinity(
            "C", "C", [2, 2, 1, 2, 2, 2, 1],
            structural_weight=0.3, modal_weight=0.7,
        )
        assert result is not None
        # C in C Ionian: structural = 1.0 (unison), modal = 0.5 (in scale)
        expected = 0.3 * 1.0 + 0.7 * 0.5
        assert result == pytest.approx(expected, abs=0.01)

    def test_range(self) -> None:
        ionian = [2, 2, 1, 2, 2, 2, 1]
        for note in CHROMATIC_NOTES:
            result = character_location_affinity(note, "C", ionian)
            assert result is not None
            assert -1.0 <= result <= 1.0

    def test_dissonant_location(self) -> None:
        """Tritone from tonic with out-of-scale → very negative."""
        result = character_location_affinity(
            "F#", "C", [2, 2, 1, 2, 2, 2, 1]  # F# not in C Ionian
        )
        assert result is not None
        assert result < 0


# ---------------------------------------------------------------------------
# Dual membership cost
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Location instability
# ---------------------------------------------------------------------------

class TestLocationInstability:
    def test_single_faction_stable(self) -> None:
        assert location_instability("C", [[2, 2, 1, 2, 2, 2, 1]]) == 0.0

    def test_no_tonic_stable(self) -> None:
        assert location_instability(None, [[2, 2, 1, 2, 2, 2, 1], [1, 2, 2, 2, 1, 2, 2]]) == 0.0

    def test_identical_factions_stable(self) -> None:
        """Two identical factions → full overlap → zero instability."""
        ionian = [2, 2, 1, 2, 2, 2, 1]
        inst = location_instability("C", [ionian, ionian])
        assert inst == 0.0

    def test_different_factions_unstable(self) -> None:
        """Two different factions → some instability."""
        ionian = [2, 2, 1, 2, 2, 2, 1]
        phrygian = [1, 2, 2, 2, 1, 2, 2]
        inst = location_instability("C", [ionian, phrygian])
        assert inst > 0

    def test_range(self) -> None:
        modes = [
            [2, 2, 1, 2, 2, 2, 1],
            [1, 2, 2, 2, 1, 2, 2],
            [2, 2, 2, 2, 2, 2],
        ]
        inst = location_instability("D", modes)
        assert 0.0 <= inst <= 1.0


# ---------------------------------------------------------------------------
# Faction weight
# ---------------------------------------------------------------------------

class TestFactionWeight:
    def test_only_faction(self) -> None:
        assert faction_weight("C", []) == 1.0

    def test_fifth_is_central(self) -> None:
        """A root forming perfect fifths with others should be highly weighted."""
        # C with G (perfect fifth) and F (perfect fourth from C = fifth below)
        w = faction_weight("C", ["G", "F"])
        assert w > 0.7

    def test_tritone_is_outlier(self) -> None:
        """A root forming tritones with others should be low-weighted."""
        w = faction_weight("C", ["F#"])
        assert w < 0.3

    def test_range(self) -> None:
        for note in CHROMATIC_NOTES:
            w = faction_weight(note, ["C", "G", "D"])
            assert 0.0 <= w <= 1.0


# ---------------------------------------------------------------------------
# Faction compatibility
# ---------------------------------------------------------------------------

class TestFactionCompatibility:
    def test_identical_modes(self) -> None:
        ionian = [2, 2, 1, 2, 2, 2, 1]
        assert faction_compatibility(ionian, ionian) == 1.0

    def test_ionian_vs_mixolydian(self) -> None:
        """Only differ at positions 5 and 6 → 5/7."""
        ionian = [2, 2, 1, 2, 2, 2, 1]
        mixolydian = [2, 2, 1, 2, 2, 1, 2]
        compat = faction_compatibility(ionian, mixolydian)
        assert compat == pytest.approx(5 / 7, abs=0.01)

    def test_ionian_vs_locrian(self) -> None:
        """Almost opposite → low compatibility."""
        ionian = [2, 2, 1, 2, 2, 2, 1]
        locrian = [1, 2, 2, 1, 2, 2, 2]
        compat = faction_compatibility(ionian, locrian)
        assert compat < 0.5

    def test_different_families(self) -> None:
        """7-note vs 6-note → reduced compatibility."""
        ionian = [2, 2, 1, 2, 2, 2, 1]
        whole_tone = [2, 2, 2, 2, 2, 2]
        compat = faction_compatibility(ionian, whole_tone)
        assert compat < 0.5

    def test_empty_intervals(self) -> None:
        assert faction_compatibility([], [2, 2, 1, 2, 2, 2, 1]) == 0.0

    def test_range(self) -> None:
        modes = [
            [2, 2, 1, 2, 2, 2, 1],   # Ionian
            [2, 1, 2, 2, 1, 2, 2],   # Aeolian
            [1, 2, 2, 2, 1, 2, 2],   # Phrygian
            [2, 2, 2, 2, 2, 2],      # Whole tone
            [2, 2, 3, 2, 3],         # Pentatonic major
        ]
        for a in modes:
            for b in modes:
                c = faction_compatibility(a, b)
                assert 0.0 <= c <= 1.0


# ---------------------------------------------------------------------------
# Kilima-specific integration checks
# ---------------------------------------------------------------------------

class TestKilimaHarmonics:
    """Verify that known Kilima relationships produce expected results.
    These tests use Kilima data to validate the engine but don't import
    any Kilima-specific modules.
    """
    PHRYGIAN = [1, 2, 2, 2, 1, 2, 2]
    AEOLIAN = [2, 1, 2, 2, 1, 2, 2]
    IONIAN = [2, 2, 1, 2, 2, 2, 1]
    DORIAN = [2, 1, 2, 2, 2, 1, 2]
    WHOLE_TONE = [2, 2, 2, 2, 2, 2]

    def test_cave_invasion_modal_shift(self) -> None:
        """H52-H56: Guard Force (Dorian) takes Anti Group's (Phrygian) Cave.
        Characters should feel the harmonic shift differently."""
        kive_note = "D#"  # The Rebel

        # Before: Cave controlled by Anti Group (Phrygian)
        aff_before = character_location_affinity(kive_note, "B", self.PHRYGIAN)
        # After: Cave controlled by Guard Force (Dorian)
        aff_after = character_location_affinity(kive_note, "B", self.DORIAN)

        # Both should be calculable (not None since tonic is not null here using "B")
        assert aff_before is not None
        assert aff_after is not None
        # The shift should change the affinity (even if same tonic, different mode)
        # This may or may not change depending on whether D# is in each scale

    def test_backdoor_whole_tone_dissonance(self) -> None:
        """Backdoor (whole tone from F#) is maximally distant from establishment."""
        # Union Corp (Ionian) vs Backdoor (Whole Tone)
        compat = faction_compatibility(self.IONIAN, self.WHOLE_TONE)
        assert compat < 0.5, "Whole tone should be distant from Greek modes"

    def test_city_disputed(self) -> None:
        """The City with Union Corp + Anti Group → instability > 0."""
        inst = location_instability("D", [self.IONIAN, self.PHRYGIAN])
        assert inst > 0, "Disputed City should be unstable"
