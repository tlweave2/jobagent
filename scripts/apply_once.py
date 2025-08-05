"""
Command‑line entry point for applying to a single job.

This script accepts a job URL and optional profile path, then calls
``agent.controller.apply_to_job`` to perform the Easy Apply workflow.
You should run this script from the project root so that relative
imports resolve correctly (e.g. ``python scripts/apply_once.py --url <URL>``).
"""
from __future__ import annotations

import argparse
import sys
import os

# Ensure the project root is on the Python path when executing directly
from pathlib import Path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

# Add the project root to PYTHONPATH as well
os.environ['PYTHONPATH'] = str(project_root) + ':' + os.environ.get('PYTHONPATH', '')

from agent.controller import apply_to_job


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply to a single LinkedIn job using Easy Apply")
    parser.add_argument("--url", required=True, help="Job URL to apply for")
    parser.add_argument("--profile", default="data/user_profile.yaml", help="Path to user profile YAML")
    parser.add_argument("--no-cloud", action="store_true", help="Disable fallback to cloud LLM")
    args = parser.parse_args()

    try:
        apply_to_job(args.url, profile_path=args.profile, use_cloud=not args.no_cloud)
    except NotImplementedError:
        print("The apply_to_job function is not yet implemented. Please fill in the logic.")


if __name__ == "__main__":
    main()