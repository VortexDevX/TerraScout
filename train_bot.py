from __future__ import annotations

import argparse
import json
from pathlib import Path

from backend.scripts.train_policy import build_policy, load_rows


def default_source() -> Path:
    db_path = Path("backend/data/terrascout.sqlite3")
    if db_path.exists():
        return db_path
    files = sorted(Path("backend/training_json").glob("*.jsonl"), key=lambda path: path.stat().st_mtime)
    if files:
        return files[-1]
    raise SystemExit("No replay DB or JSONL found. Run bot first, then train.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Train TerraScout from real bot outcomes.")
    parser.add_argument("source", nargs="?", type=Path, help="Optional SQLite replay DB or JSONL export.")
    parser.add_argument("--out", type=Path, default=Path("backend/models/policy.json"))
    args = parser.parse_args()

    source = args.source or default_source()
    rows = load_rows(source)
    if not rows:
        raise SystemExit(f"No usable rows found in {source}")

    policy = build_policy(rows)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(policy, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Trained policy from {source}")
    print(f"Rows: {policy['source_examples']}, real outcomes: {policy['real_outcomes']}")
    print(f"Explore radius: {policy['explore_radius']}")
    print(f"Success rates: {policy['command_success_rates']}")
    print(f"Wrote {args.out}")
    print("Restart backend + bot to use policy.")


if __name__ == "__main__":
    main()
