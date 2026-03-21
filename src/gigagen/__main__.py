"""Entry point: python -m gigagen [worldpack_dir] [--seed N]"""

import argparse
import sys

from gigagen.io.load_worldpack import load_worldpack, load_timeline_events
from gigagen.core.simulator import load_timeline_maps, load_event_rules
from gigagen.cli.console import run_console


def main() -> None:
    parser = argparse.ArgumentParser(description="Gigagen -- universe compiler")
    parser.add_argument(
        "worldpack",
        nargs="?",
        default="worlds/kilima",
        help="Path to worldpack directory (default: worlds/kilima)",
    )
    parser.add_argument("--seed", type=int, default=1, help="Seed (default: 1)")
    args = parser.parse_args()

    worldpack = args.worldpack
    ws = load_worldpack(worldpack, seed=args.seed)
    events = load_timeline_events(worldpack)
    char_map, loc_map = load_timeline_maps(worldpack)
    event_rules = load_event_rules(worldpack)
    run_console(
        ws,
        timeline_events=events,
        char_map=char_map,
        loc_map=loc_map,
        event_rules=event_rules,
    )


if __name__ == "__main__":
    main()
