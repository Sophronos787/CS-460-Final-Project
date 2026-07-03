# CS-460-Final-Project
Algorithms – Final Project 
Where I had to design something original and algorithm-focused:  
Design and create a brand-new algorithm (strongly preferred)

# WBD — Warframe Mission Coverage Optimizer

Given a list of items you need (mods, resources, blueprints), WBD returns the
smallest set of missions that together drop everything on your list, using a
greedy set-cover algorithm.

## Requirements

- Python 3.9+
- pytest (`pip install pytest`)

## Run it

```bash
python main.py "Serration" "Neural Sensors" "Orokin Cell" "Split Chamber"
```

Or from a file, one item per line:

```bash
python main.py --items-file needed_items.txt
```

By default the CLI applies real rotation weighting (see "Data note" below).
Pass `--no-weights` to fall back to plain unweighted set cover:

```bash
python main.py --items-file needed_items.txt --no-weights
```

## Run the tests

```bash
make test
```

which runs:

```bash
pytest tests/ -v -s
```

## Project layout

```
wbd/
  core.py             # find_missions() — the greedy set-cover algorithm
  data.py             # loads data/drop_tables.json and data/rotation_weights.json
data/
  drop_tables.json      # real mission -> item drop-table dataset (see below)
  rotation_weights.json # real per-(mission, item) rotation weights (see below)
tests/
  test_core.py    # 7 tests: correctness, rotation weighting, edge cases, perf, real-data coverage
main.py           # CLI entry point
```

## Data note

`data/drop_tables.json` and `data/rotation_weights.json` are a curated
subset (17 missions, 56 distinct items) pulled directly from the official
Warframe PC drop-table page
(`warframe-web-assets.nyc3.cdn.digitaloceanspaces.com/uploads/cms/...html`,
"Last Update: 25 June, 2026"). It's
still a subset rather than a full scrape, the source page lists drops for
hundreds of missions across every planet, and pulling all of it would bloat
the JSON far past what's useful for a demo, but every item and every
percentage in the file is real, copied as-listed from the site.

One nice real find from the data: Saturn's Conclave missions (e.g.
`Cephalon Capture (Saturn, Conclave)`) drop Control Module, Neural Sensors,
*and* Orokin Cell together in Rotation B — but each at only a 0.25%
("Legendary") chance. Unweighted set cover happily picks that single
mission to knock out three needed items at once; weighted set cover
correctly avoids it for Orokin Cell (a 400-run expected wait) in favor of
`Adrastea (Jupiter, Caches)`'s far faster 15.10% drop, only falling back to
the Conclave mission for Control Module and Neural Sensors, which have no
faster source in this dataset. Try `python main.py --items-file
needed_items.txt` vs. `--no-weights` to see the difference. The algorithm
itself is still fully data-agnostic — swapping in a larger dataset requires
no code changes, only a bigger JSON file.

## Algorithm summary

`find_missions(needed_items, drop_tables, rotation_weight=None)` repeatedly
picks the mission that covers the most still-needed items (optionally
weighted by how many rotations/runs it realistically takes to get an item
from that mission), removes those items, and repeats until everything is
covered or no remaining mission helps. See `wbd/core.py` for the full,
commented implementation.
