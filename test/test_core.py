import random
import sys
import time
import tracemalloc
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from wbd.core import find_missions, uncovered_items
from wbd.data import load_drop_tables, load_rotation_weights


# --------------------------------------------------------------------------
# Test 1: hand-traceable small case
# --------------------------------------------------------------------------
def test_small_hand_traceable_case():
    drop_tables = {
        "Hydron (Defense)": {"Serration", "Fieldron Sample", "Neural Sensors"},
        "Sechura (Survival)": {"Neural Sensors", "Orokin Cell"},
        "Draco (Capture)": {"Serration", "Split Chamber"},
        "Adaro (Sabotage)": {"Orokin Cell", "Fieldron Sample"},
    }
    needed = {"Serration", "Neural Sensors", "Orokin Cell", "Split Chamber"}

    expected = [
        ("Hydron (Defense)", {"Serration", "Neural Sensors"}),
        ("Sechura (Survival)", {"Orokin Cell"}),
        ("Draco (Capture)", {"Split Chamber"}),
    ]

    actual = find_missions(needed, drop_tables)

    assert actual == expected
    assert uncovered_items(needed, actual) == set()


# --------------------------------------------------------------------------
# Test 2: rotation weighting changes which mission is preferred
# --------------------------------------------------------------------------
def test_rotation_weighting_prefers_faster_mission():
    drop_tables = {
        "Fast Mission": {"Rare Item"},
        "Slow Mission": {"Rare Item"},
    }
    needed = {"Rare Item"}
    rotation_weight = {
        ("Fast Mission", "Rare Item"): 1,   # drops every run
        ("Slow Mission", "Rare Item"): 5,   # only in a late, rare rotation
    }

    expected = [("Fast Mission", {"Rare Item"})]
    actual = find_missions(needed, drop_tables, rotation_weight=rotation_weight)

    assert actual == expected


# --------------------------------------------------------------------------
# Test 3: item with no known source is reported, not silently dropped
# --------------------------------------------------------------------------
def test_unreachable_item_is_reported():
    drop_tables = {
        "Hydron (Defense)": {"Serration"},
    }
    needed = {"Serration", "Nonexistent Mod"}

    actual = find_missions(needed, drop_tables)
    missing = uncovered_items(needed, actual)

    assert actual == [("Hydron (Defense)", {"Serration"})]
    assert missing == {"Nonexistent Mod"}


# --------------------------------------------------------------------------
# Test 4: full needed-item set is always covered on the bundled dataset
# (sanity check that the shipped data.json is internally consistent)
# --------------------------------------------------------------------------
def test_bundled_dataset_covers_its_own_items():
    drop_tables = load_drop_tables()
    all_items = set().union(*drop_tables.values())

    result = find_missions(all_items, drop_tables)
    missing = uncovered_items(all_items, result)

    assert missing == set()


# --------------------------------------------------------------------------
# Test 5: empty input returns empty output without error
# --------------------------------------------------------------------------
def test_empty_needed_items():
    drop_tables = {"Hydron (Defense)": {"Serration"}}
    assert find_missions(set(), drop_tables) == []


# --------------------------------------------------------------------------
# Test 6: the real needed_items.txt list (Serration, Neural Sensors,
# Orokin Cell, Split Chamber, Control Module) is fully covered on the real
# scraped dataset, and real rotation weighting still finds a valid cover.
# Also checks that Saturn/Cephalon Capture (Conclave) -- the single mission
# whose Rotation B drops Control Module, Neural Sensors, AND Orokin Cell
# together -- gets picked, since it covers 3 needed items in one mission.
# --------------------------------------------------------------------------
def test_needed_items_file_is_covered_with_real_weights():
    needed = {"Serration", "Neural Sensors", "Orokin Cell", "Split Chamber", "Control Module"}
    drop_tables = load_drop_tables()
    rotation_weight = load_rotation_weights()

    result = find_missions(needed, drop_tables, rotation_weight=rotation_weight)
    missing = uncovered_items(needed, result)

    assert missing == set()
    missions_used = {mission for mission, _ in result}
    assert "Cephalon Capture (Saturn, Conclave)" in missions_used


# --------------------------------------------------------------------------
# Runtime / memory measurement on a larger synthetic dataset
# (not an assertion-based test -- prints figures for the report)
# --------------------------------------------------------------------------
def test_runtime_and_memory_on_synthetic_dataset(capsys):
    random.seed(42)
    items = [f"item_{i}" for i in range(30)]
    missions = {
        f"mission_{m}": set(random.sample(items, k=random.randint(2, 6)))
        for m in range(50)
    }
    needed_large = set(random.sample(items, k=20))

    tracemalloc.start()
    start = time.perf_counter()
    result = find_missions(needed_large, missions)
    elapsed = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    with capsys.disabled():
        print(
            f"\n[perf] missions_selected={len(result)} "
            f"runtime_ms={elapsed * 1000:.3f} peak_kb={peak / 1024:.2f}"
        )

    assert uncovered_items(needed_large, result) == set()
