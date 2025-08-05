"""
Command‑line entry point for batch job applications.

This script reads the search presets from ``data/linkedin_search.yaml``
and iterates through each preset. For each one it builds a search
URL, loads the search results, extracts job cards, filters them for
Easy Apply jobs and applies to each job using the logic defined in
``agent/controller.py``. The batch workflow is skeletal; details are
left to you to implement.
"""
from __future__ import annotations

import argparse
import sys
import yaml
from pathlib import Path

# Ensure the project root is on the Python path when executing directly
sys.path.append(str(Path(__file__).resolve().parents[1]))

from jobagent.agent.search_controller import run_search_and_apply


def main() -> None:
    parser = argparse.ArgumentParser(description="Search for jobs and apply in batch")
    parser.add_argument("--search-config", default="data/linkedin_search.yaml", help="Path to LinkedIn search config")
    parser.add_argument("--profile", default="data/user_profile.yaml", help="Path to user profile YAML")
    args = parser.parse_args()

    # Load search presets from YAML
    with open(args.search_config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    presets = config.get("searches", [])

    if not presets:
        print("No search presets found in the configuration file.")
        return

    for preset in presets:
        print(f"Running search preset: {preset}")
        try:
            run_search_and_apply(preset, profile_path=args.profile)
        except NotImplementedError:
            print("Batch search and apply logic is not yet implemented. Please fill in the details.")


if __name__ == "__main__":
    main()