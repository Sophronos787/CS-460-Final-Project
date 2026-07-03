"""
wbd.core
--------
Greedy set-cover algorithm for routing a player's needed-item list to the
smallest set of Warframe missions that collectively drop every item.
"""

from typing import Dict, Iterable, List, Optional, Set, Tuple

Mission = str
Item = str


def find_missions(
    needed_items: Iterable[Item],
    drop_tables: Dict[Mission, Set[Item]],
    rotation_weight: Optional[Dict[Tuple[Mission, Item], float]] = None,
) -> List[Tuple[Mission, Set[Item]]]:
    """
    Greedily select missions that cover all needed_items.

    Parameters
    ----------
    needed_items : iterable of item names the player wants.
    drop_tables : mapping of mission name -> set of item names it can drop.
    rotation_weight : optional mapping of (mission, item) -> expected number
        of rotations/runs needed to realistically obtain that item from that
        mission. Lower is better (faster to farm). Items/pairs not present
        default to a weight of 1. When omitted, every drop is treated as
        equally fast (weight 1), i.e. plain unweighted set cover.

    Returns
    -------
    List of (mission_name, items_covered_by_that_mission), in selection
    order. Items with no source in drop_tables are silently left uncovered
    and the loop exits early -- callers can diff needed_items against the
    union of covered sets to detect this.
    """
    remaining: Set[Item] = set(needed_items)
    chosen: List[Tuple[Mission, Set[Item]]] = []

    while remaining:
        best_mission: Optional[Mission] = None
        best_score: float = -1.0
        best_covered: Set[Item] = set()

        for mission, drops in drop_tables.items():
            covered = drops & remaining
            if not covered:
                continue

            if rotation_weight:
                avg_rot = sum(
                    rotation_weight.get((mission, item), 1) for item in covered
                ) / len(covered)
            else:
                avg_rot = 1

            score = len(covered) / avg_rot

            if score > best_score:
                best_score = score
                best_mission = mission
                best_covered = covered

        if best_mission is None:
            # No remaining mission covers any of the leftover items.
            break

        chosen.append((best_mission, best_covered))
        remaining -= best_covered

    return chosen


def uncovered_items(
    needed_items: Iterable[Item], result: List[Tuple[Mission, Set[Item]]]
) -> Set[Item]:
    """Return any needed items that no mission in drop_tables could supply."""
    covered: Set[Item] = set()
    for _, items in result:
        covered |= items
    return set(needed_items) - covered
