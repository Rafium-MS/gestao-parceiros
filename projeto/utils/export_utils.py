"""Helper functions for exporting data."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Mapping, Sequence


def export_to_csv(records: Sequence[Mapping[str, object]], output_path: Path | str) -> Path:
    """Write a sequence of records to a CSV file and return the path."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if not records:
        path.write_text("", encoding="utf-8")
        return path

    fieldnames = list(records[0].keys())
    with path.open("w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(record)
    return path
