"""
Cloud LLM interface.

This module defines a wrapper around an external language model service
such as OpenAI's GPT or Anthropic's Claude. It is used as a fallback
when the local model cannot recover from a stuck state. The focus here
is on recovery prompts rather than normal form navigation.
"""
from __future__ import annotations

from typing import Dict, Any


class CloudLLM:
    """Wrapper for a remote language model used for recovery and complex tasks."""

    def __init__(self, model_name: str = "claude") -> None:
        self.model_name = model_name
        # TODO: set up API key and client for the cloud model

    def analyze(self, snapshot: Dict[str, Any], mode: str = "recovery") -> Dict[str, Any]:
        """Ask the cloud model for guidance in a specific mode.

        Args:
            snapshot: Dictionary containing the current page state.
            mode: A string indicating the type of prompt to use. For
                recovery you might build a prompt asking how to dismiss
                modals. Other modes could include summarisation or
                advanced question answering.

        Returns:
            A dictionary with a list of actions to recover from the
            stalled state. In a full implementation this should parse
            the JSON output from the cloud model.
        """
        # TODO: call out to the cloud model and parse the result
        return {"actions": []}