"""Entry point: python -m gigagen [worldpack_dir] [--seed N] [--tui|--classic]"""

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
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--tui", action="store_true", default=True,
        help="Launch God Mode TUI (default)",
    )
    mode.add_argument(
        "--classic", action="store_true",
        help="Launch classic text console",
    )
    args = parser.parse_args()

    worldpack = args.worldpack

    if args.classic:
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
    else:
        from gigagen.cli.tui import run_tui
        run_tui(worldpack_dir=worldpack, seed=args.seed)


if __name__ == "__main__":
    main()
