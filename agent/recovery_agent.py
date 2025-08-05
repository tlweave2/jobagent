"""
Recovery agent for handling stalled user interfaces.

This module defines a simple interface for invoking a cloud‑hosted
language model when the page appears to be stuck. The idea is that
you detect when the DOM stops changing (using logic in
``browser/dom_utils.py``), then call the cloud model to analyse the
current DOM and visible text and suggest recovery actions.

An instance of ``CloudLLM`` from ``models/cloud_llm.py`` is used to
generate those recovery actions. You could also implement heuristics
to recognise common modal dialogs without needing to invoke the model.
"""
from __future__ import annotations

from typing import Dict, Any

from jobagent.models.cloud_llm import CloudLLM


class RecoveryAgent:
    """Encapsulates fallback behaviour when a page stalls."""

    def __init__(self, cloud_model: CloudLLM) -> None:
        self.cloud_model = cloud_model

    def recover(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Given a snapshot of the current page, ask the cloud model for recovery actions.

        Returns the same structured output as the local model: a dictionary
        containing a list of actions. How you build the prompt for the
        cloud model is up to you and should reflect the fact that you are
        trying to recover from an unexpected state or modal dialog.
        """
        # TODO: implement cloud recovery call
        return {"actions": []}