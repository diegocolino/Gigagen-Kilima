"""Chronica — Universo Impreso.

The seed enters here. Generates the complete past:
- Resolves lineage elements from their element_pool
- Macrofactions emerge from lineage groupings
- Characters 1gen (Founders, Leaders, Notaries)
- Macro-events resolved
- Locations L3-L6 with derived tonics
- Micro-events
- Characters 2gen

Uses namespaced RNGs for reproducibility.
"""

from __future__ import annotations

import hashlib
import random
from typing import TYPE_CHECKING

from ..core.entity import Lineage
from ..core.world_state import WorldState

if TYPE_CHECKING:
    pass


class ChronicaError(Exception):
    """Raised when Chronica fails."""


class SeedEngine:
    """Produces reproducible RNGs by namespace.

    Each namespace creates an independent RNG stream. Adding new namespaces
    doesn't affect existing ones, preserving backward compatibility.

    Usage:
        engine = SeedEngine(42)
        rng_elements = engine.rng("elements")
        rng_founders = engine.rng("founders")
    """

    def __init__(self, seed: int):
        self._seed = seed
        self._cache: dict[str, random.Random] = {}

    @property
    def seed(self) -> int:
        return self._seed

    def rng(self, namespace: str) -> random.Random:
        """Get or create an RNG for the given namespace."""
        if namespace not in self._cache:
            # Combine seed and namespace into a deterministic hash
            combined = f"{self._seed}:{namespace}"
            hash_bytes = hashlib.sha256(combined.encode()).digest()
            derived_seed = int.from_bytes(hash_bytes[:8], "big")
            self._cache[namespace] = random.Random(derived_seed)
        return self._cache[namespace]


def run(ws: WorldState, config: dict, *, seed: int | None = None) -> WorldState:
    """Execute Chronica layer.

    Args:
        ws: WorldState from Theogony.
        config: Worldpack configuration.
        seed: The seed for RNG namespaces. If None, uses ws.seed.

    Returns:
        WorldState with phase='chronica', complete past generated.

    Raises:
        ChronicaError: If required data is missing.
    """
    if ws.catalogs is None:
        raise ChronicaError("Chronica requires catalogs from Genesis")

    effective_seed = seed if seed is not None else ws.seed
    engine = SeedEngine(effective_seed)

    ws = ws.model_copy(deep=True)
    ws.seed = effective_seed

    # 1. Resolve lineage elements
    ws = _resolve_lineages(ws, engine)

    # 2. Resolve macrofactions (stub)
    ws = _resolve_macrofactions(ws, engine)

    # 3. Resolve characters 1gen (stub)
    ws = _resolve_characters_1gen(ws, engine)

    # 4. Resolve macro-events (stub)
    ws = _resolve_macro_events(ws, engine)

    # 5. Resolve locations L3-L6 (stub)
    ws = _resolve_locations_l3_l6(ws, engine)

    # 6. Resolve micro-events (stub)
    ws = _resolve_micro_events(ws, engine)

    # 7. Resolve characters 2gen (stub)
    ws = _resolve_characters_2gen(ws, engine)

    ws.phase = "chronica"
    return ws


def _resolve_lineages(ws: WorldState, engine: SeedEngine) -> WorldState:
    """Resolve each lineage's element from its element_pool.

    Uses the 'elements' namespace RNG.
    """
    rng = engine.rng("elements")

    for entity in ws.entities.values():
        if not isinstance(entity, Lineage):
            continue

        # Skip lineages without element_pool (e.g., Convergence)
        if not entity.element_pool:
            continue

        # Skip if already resolved (shouldn't happen, but defensive)
        if entity.element is not None:
            continue

        # Choose element from pool
        entity.element = rng.choice(entity.element_pool)

    return ws


def _resolve_macrofactions(ws: WorldState, engine: SeedEngine) -> WorldState:
    """Resolve macrofactions from lineage groupings.

    TODO: Group lineages by compatible elements.
    Macrofactions emerge with mode inherited from founding lineage.
    """
    # Stub — macrofactions already exist from Kilima data
    # In full implementation: generate macrofactions dynamically
    return ws


def _resolve_characters_1gen(ws: WorldState, engine: SeedEngine) -> WorldState:
    """Resolve Characters 1gen: Founders (S), Leaders (A), Notaries (B).

    TODO: Generate characters per lineage using the 'founders' namespace.
    """
    # Stub — characters already exist from Kilima data
    return ws


def _resolve_macro_events(ws: WorldState, engine: SeedEngine) -> WorldState:
    """Resolve macro-events (historical bifurcations).

    TODO: Gamble resolution of canonical macro-events using 'events' namespace.
    Examples: Capitol Foundation, First Revolution, First Wall Foundation.
    """
    # Stub — events not yet implemented
    return ws


def _resolve_locations_l3_l6(ws: WorldState, engine: SeedEngine) -> WorldState:
    """Resolve locations levels 3-6 (born from history).

    TODO: Assign tonics derived from founding lineage using 'locations' namespace.
    """
    # Stub — locations already exist from Kilima data
    return ws


def _resolve_micro_events(ws: WorldState, engine: SeedEngine) -> WorldState:
    """Resolve micro-events (fill time between macro-events).

    TODO: Generate micro-events using 'events' namespace.
    """
    # Stub — micro-events not yet implemented
    return ws


def _resolve_characters_2gen(ws: WorldState, engine: SeedEngine) -> WorldState:
    """Resolve Characters 2gen (NPCs, secondaries).

    TODO: Generate secondary characters using '2gen' namespace.
    """
    # Stub — 2gen not yet implemented
    return ws
