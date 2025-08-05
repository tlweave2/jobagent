"""
Local LLM interface.

This module defines a thin wrapper around a local language model such as
LLaMA or Mistral, accessible via the Ollama API or another provider.
It constructs prompts and returns structured JSON-like output to guide
the browser actions.
"""
from __future__ import annotations

from typing import Dict, Any


class LocalLLM:
    """Wrapper for a locally running language model."""

    def __init__(self, model_name: str = "llama3") -> None:
        self.model_name = model_name
        # TODO: set up connection to the local model (e.g. via Ollama)

    def analyze(self, snapshot: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a plan for the current step of the form.

        Args:
            snapshot: Dictionary containing the current page state returned by
                ``BrowserDriver.get_page_snapshot``.
            profile: Dictionary containing the user's profile information.

        Returns:
            A dictionary with at least two keys:
            ``actions`` – a list of actions for the browser to execute.
            ``is_final_step`` – a boolean indicating whether this is the
            final step of the application form.
        """
        # In a real implementation you would build a prompt that includes
        # the page snapshot and relevant parts of the user profile. Then
        # send it to the local model and parse its response.
        #
        # For now we return an empty plan. Replace this with your own logic.
        return {"actions": [], "is_final_step": False}