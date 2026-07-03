"""
WBD command-line interface.

Usage:
    python main.py "Serration" "Neural Sensors" "Orokin Cell"
    python main.py --items-file needed_items.txt
"""

import argparse
import sys

from wbd.core import find_missions, uncovered_items
from wbd.data import load_drop_tables, load_rotation_weights


def parse_args():
    parser = argparse.ArgumentParser(description="Find the smallest mission set covering your needed items.")
    parser.add_argument("items", nargs="*", help="Item names you need, e.g. Serration \"Neural Sensors\"")
    parser.add_argument(
        "--items-file",
        help="Path to a text file with one needed item per line (alternative to positional args).",
    )
    parser.add_argument(
        "--no-weights",
        action="store_true",
        help="Ignore data/rotation_weights.json and run plain unweighted set cover.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    needed = list(args.items)
    if args.items_file:
        with open(args.items_file, "r", encoding="utf-8") as f:
            needed += [line.strip() for line in f if line.strip()]

    if not needed:
        print("No items given. Pass item names as arguments or via --items-file.", file=sys.stderr)
        sys.exit(1)

    drop_tables = load_drop_tables()
    rotation_weight = None if args.no_weights else load_rotation_weights()
    result = find_missions(needed, drop_tables, rotation_weight=rotation_weight)
    missing = uncovered_items(needed, result)

    print(f"Needed items: {len(needed)}")
    print(f"Missions selected: {len(result)}\n")
    for mission, covered in result:
        print(f"  - {mission}: covers {sorted(covered)}")

    if missing:
        print(f"\nNo known source in this dataset for: {sorted(missing)}")


if __name__ == "__main__":
    main()
