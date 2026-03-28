"""Existence — Universo Jugable.

The player enters the universe. Creates a character, interacts with IN12,
accesses factions, occupies locations.

Deterministic given Contempo. The universe exists — the player enters it.

This is a stub for future implementation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.world_state import WorldState


def run(ws: "WorldState", config: dict) -> "WorldState":
    """Execute Existence layer.

    Args:
        ws: WorldState from Contempo.
        config: Player/session configuration.

    Returns:
        WorldState with phase='existence', ready for player interaction.
    """
    # Stub — returns ws unchanged for now
    return ws
