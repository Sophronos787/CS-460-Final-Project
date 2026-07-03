"""
wbd.data
--------
Loads mission -> drop-table data from a JSON file into the
{mission: set(items)} shape find_missions() expects, and (optionally)
loads real per-rotation rotation-weight data into the
{(mission, item): weight} shape find_missions()'s rotation_weight
parameter expects.
"""

import json
from pathlib import Path
from typing import Dict, Set, Tuple

DEFAULT_DATA_PATH = Path(__file__).parent.parent / "data" / "drop_tables.json"
DEFAULT_WEIGHTS_PATH = Path(__file__).parent.parent / "data" / "rotation_weights.json"


def load_drop_tables(path: Path = DEFAULT_DATA_PATH) -> Dict[str, Set[str]]:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return {mission: set(items) for mission, items in raw.items()}


def load_rotation_weights(
    path: Path = DEFAULT_WEIGHTS_PATH,
) -> Dict[Tuple[str, str], float]:
    """
    Load real rotation-weight data: for each (mission, item) pair, the
    expected number of mission runs/rotations needed to obtain that item at
    least once, derived from the scraped drop table's listed drop chance
    (weight = 1 / probability). Keys are stored on disk as "mission|item"
    strings (JSON can't use tuples as keys) and are split back into
    (mission, item) tuples here.

    Returns an empty dict (rather than raising) if the file is missing, so
    callers can treat "no weights file" the same as "run unweighted".
    """
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    weights: Dict[Tuple[str, str], float] = {}
    for key, weight in raw.items():
        mission, item = key.split("|", 1)
        weights[(mission, item)] = weight
    return weights
