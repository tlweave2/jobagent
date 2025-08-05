"""
Memory manager for job applications.

This optional module provides a way to track which jobs have been
applied to, store form field mappings and other metadata. In a full
implementation you might use SQLite for structured data and a vector
store for retrieval of similar forms. For this scaffold we define
placeholder methods that read and write JSON lines files.
"""
from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from typing import Dict, Any, Iterable


class JobHistory:
    """A simple append‑only log of job application events."""

    def __init__(self, path: str = "data/applied_jobs.jsonl") -> None:
        self.path = Path(path)
        # Ensure the file exists
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)

    def log(self, record: Dict[str, Any]) -> None:
        """Append a JSON record to the history file with a timestamp."""
        record = record.copy()
        record["timestamp"] = datetime.utcnow().isoformat() + "Z"
        with open(self.path, "a", encoding="utf-8") as f:
            json.dump(record, f)
            f.write("\n")

    def load_all(self) -> Iterable[Dict[str, Any]]:
        """Yield all records from the history file."""
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    yield json.loads(line)