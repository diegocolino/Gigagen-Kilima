"""Seed-based variation logic for WorldState.

Varies seeded fields deterministically without touching fixed identity.
Resolves NB1 variables (VAR_DEV, VAR_BRAIS, VAR_ENDING) per seed.
"""

from __future__ import annotations

import json
import pathlib
import random
from typing import Any

from .entity import BaseEntity, Character, Faction, Location
from .relation import Relation
from .world_state import WorldState


# Default emotional options if worldpack doesn't specify catalogs
_DEFAULT_EMOTIONAL_OPTIONS = ["neutral"]


def _resolve_variables(
    rng: random.Random,
    variables: list[dict[str, Any]],
) -> dict[str, str]:
    """Resolve each variable using the seeded RNG.

    Returns a dict mapping variable id to the chosen option.
    """
    resolved: dict[str, str] = {}
    for var in variables:
        var_id = var["id"]
        options = var["options"]
        probs = var.get("probability", {})
        if probs:
            weights = [probs.get(opt, 1.0 / len(options)) for opt in options]
        else:
            weights = [1.0 / len(options)] * len(options)
        choice = rng.choices(options, weights=weights, k=1)[0]
        resolved[var_id] = choice
    return resolved


def _vary_character_emotions(
    rng: random.Random,
    entities: dict[str, BaseEntity],
    fixed_emotions: dict[str, str],
    emotional_options: list[str] | None = None,
) -> None:
    """Vary emotional_load for characters whose canon_level is not fixed,
    or whose emotional_load is a seeded field.

    Characters with grief at H00 (funeral) keep grief as base but may shift.
    """
    options = emotional_options or _DEFAULT_EMOTIONAL_OPTIONS
    for eid, ent in entities.items():
        if not isinstance(ent, Character):
            continue
        base_emotion = fixed_emotions.get(eid, ent.emotional_load)
        # 60% chance to keep base emotion, 40% chance to shift
        if rng.random() < 0.4:
            ent.emotional_load = rng.choice(options)
        else:
            ent.emotional_load = base_emotion


def _vary_location_tensions(
    rng: random.Random,
    entities: dict[str, BaseEntity],
) -> None:
    """Apply small random variation to location tension values."""
    for ent in entities.values():
        if not isinstance(ent, Location):
            continue
        base = ent.tension
        delta = rng.uniform(-0.15, 0.15)
        ent.tension = max(0.0, min(1.0, round(base + delta, 2)))


def _vary_faction_state(
    rng: random.Random,
    entities: dict[str, BaseEntity],
) -> None:
    """Apply small random variation to faction power and cohesion."""
    for ent in entities.values():
        if not isinstance(ent, Faction):
            continue
        power_delta = rng.uniform(-0.1, 0.1)
        cohesion_delta = rng.uniform(-0.1, 0.1)
        ent.power = max(0.0, min(1.0, round(ent.power + power_delta, 2)))
        ent.cohesion = max(0.0, min(1.0, round(ent.cohesion + cohesion_delta, 2)))


def apply_seed_variation(
    ws: WorldState,
    invariants_path: str | pathlib.Path | None = None,
    *,
    catalogs: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Apply seed-based variation to a WorldState in place.

    - Resolves variables deterministically
    - Varies seeded fields (emotions, tensions, faction power/cohesion)
    - Does NOT touch fixed identity fields (archetype, note, hero_type, etc.)

    Returns the resolved variables dict.
    """
    rng = random.Random(ws.seed)

    # -- Load and resolve variables --
    resolved_vars: dict[str, str] = {}
    if invariants_path is not None:
        inv_path = pathlib.Path(invariants_path)
        if inv_path.exists():
            inv_data = json.loads(inv_path.read_text(encoding="utf-8"))
            variables = inv_data.get("variables", [])
            resolved_vars = _resolve_variables(rng, variables)

    # -- Store resolved variables in tags --
    for var_id, choice in resolved_vars.items():
        ws.tags.append(f"{var_id}={choice}")

    # -- Snapshot base emotional loads before variation --
    fixed_emotions: dict[str, str] = {}
    for eid, ent in ws.entities.items():
        if isinstance(ent, Character):
            fixed_emotions[eid] = ent.emotional_load

    # -- Load emotional options from catalogs --
    emotional_options = None
    if catalogs:
        emotional_options = catalogs.get("emotional_states")

    # -- Apply seeded variations --
    _vary_character_emotions(rng, ws.entities, fixed_emotions, emotional_options)
    _vary_location_tensions(rng, ws.entities)
    _vary_faction_state(rng, ws.entities)

    return resolved_vars
