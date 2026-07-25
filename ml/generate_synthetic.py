"""Entry point: generate the full synthetic bank dataset and write CSVs.

Orchestrates entities -> baseline behaviour -> scenario injection, then writes
CSV snapshots to ml/data/. Run: `python -m ml.generate_synthetic` (from repo root)
or `python generate_synthetic.py` (from ml/). No feature engineering here.
"""
from __future__ import annotations

import os
import sys

# allow running both as module and as script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.synthetic import config as C
from ml.synthetic.entities import generate_entities
from ml.synthetic.behaviour import generate_baseline
from ml.synthetic.scenarios import inject


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def build() -> dict:
    entities = generate_entities()
    base = generate_baseline(entities)
    events = inject(entities, base)
    return {**entities, **events}


def main() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    tables = build()
    for name, df in tables.items():
        path = os.path.join(DATA_DIR, f"{name}.csv")
        df.to_csv(path, index=False)
        print(f"wrote {name:14s} {len(df):8d} rows -> {path}")

    # quick label summary for sanity
    tx = tables["transactions"]
    lg = tables["logins"]
    print("\n--- label summary ---")
    print("transactions by scenario:\n", tx["scenario"].value_counts().to_string())
    print("txn malicious rate:", round(tx["label"].mean(), 4))
    print("logins by scenario:\n", lg["scenario"].value_counts().to_string())


if __name__ == "__main__":
    main()
