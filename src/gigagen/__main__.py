"""Entry point: python -m gigagen [worldpack_dir] [--seed N]"""

import argparse
import sys

from gigagen.io.load_worldpack import load_worldpack
from gigagen.cli.console import run_console


def main() -> None:
    parser = argparse.ArgumentParser(description="Gigagen — universe compiler")
    parser.add_argument(
        "worldpack",
        nargs="?",
        default="worlds/kilima",
        help="Path to worldpack directory (default: worlds/kilima)",
    )
    parser.add_argument("--seed", type=int, default=1, help="Seed (default: 1)")
    args = parser.parse_args()

    ws = load_worldpack(args.worldpack, seed=args.seed)
    run_console(ws)


if __name__ == "__main__":
    main()
