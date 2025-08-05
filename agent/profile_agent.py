"""
Profile agent for answering screening questions.

This module loads the user profile from ``data/user_profile.yaml`` and
exposes helper functions to answer common screening questions during job
applications. For example, if a form asks "Are you authorised to work in
the US?" the profile agent can return "Yes" based on the stored
information. If a question is not found in the default answers it may
fallback to a default value or ask the user.
"""
from __future__ import annotations

import yaml
from typing import Dict, Optional


class UserProfile:
    """Representation of the applicant's personal data and preferences."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data

    @classmethod
    def load_from_yaml(cls, path: str) -> "UserProfile":
        """Load a user profile from a YAML file and return a ``UserProfile`` instance."""
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls(data)

    def answer_question(self, question: str) -> Optional[str]:
        """Return an answer to a given screening question if available.

        Screening questions are stored under the key ``default_answers`` in
        the YAML file as a list of question/answer pairs. Matching can be
        implemented however you like (exact match, fuzzy match, etc.). If
        no answer is found, return ``None``.
        """
        default_answers = self.data.get("default_answers", [])
        for entry in default_answers:
            if entry.get("question", "").lower() == question.strip().lower():
                return entry.get("answer")
        return None