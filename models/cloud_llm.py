"""
Cloud LLM interface.

This module defines a wrapper around an external language model service
such as OpenAI's GPT or Anthropic's Claude. It is used as a fallback
when the local model cannot recover from a stuck state. The focus here
is on recovery prompts rather than normal form navigation.
"""
from __future__ import annotations

import json
import os
from typing import Dict, Any
import anthropic


class CloudLLM:
    """Wrapper for a remote language model used for recovery and complex tasks."""

    def __init__(self, model_name: str = "claude-3-sonnet-20240229") -> None:
        self.model_name = model_name
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = anthropic.Anthropic(api_key=api_key)

    def analyze(self, snapshot: Dict[str, Any], profile: Dict[str, Any] = None, mode: str = "recovery") -> Dict[str, Any]:
        """Ask the cloud model for guidance in a specific mode.

        Args:
            snapshot: Dictionary containing the current page state.
            profile: User profile information (optional).
            mode: A string indicating the type of prompt to use. For
                recovery you might build a prompt asking how to dismiss
                modals. Other modes could include summarisation or
                advanced question answering.

        Returns:
            A dictionary with a list of actions to recover from the
            stalled state. In a full implementation this should parse
            the JSON output from the cloud model.
        """
        try:
            if mode == "recovery":
                prompt = self._build_recovery_prompt(snapshot)
            else:
                prompt = self._build_form_prompt(snapshot, profile or {})
            
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse the response
            response_text = response.content[0].text
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                # Try to extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    return {"actions": [], "is_final_step": False}
                    
        except Exception as e:
            print(f"Error calling cloud LLM: {e}")
            return {"actions": [], "is_final_step": False}
    
    def _build_recovery_prompt(self, snapshot: Dict[str, Any]) -> str:
        """Build a prompt for recovery scenarios."""
        buttons = snapshot.get("buttons", [])
        page_text = snapshot.get("text", "")[:1000]  # Limit text length
        
        return f"""You are helping to recover from a stuck state in a LinkedIn job application form.

Current page text (first 1000 chars): {page_text}

Available buttons: {json.dumps([{"id": btn["id"], "text": btn["text"]} for btn in buttons], indent=2)}

The application seems to be stuck. Please analyze the situation and suggest recovery actions.
Look for:
- Modal dialogs that need to be dismissed
- Error messages that need addressing  
- Navigation buttons to continue the process
- Any obvious next steps

Return a JSON response with:
{{"actions": [list of actions], "is_final_step": false}}

Actions should be in format:
{{"action": "click", "id": "btn_X"}}"""

    def _build_form_prompt(self, snapshot: Dict[str, Any], profile: Dict[str, Any]) -> str:
        """Build a prompt for form filling."""
        buttons = snapshot.get("buttons", [])
        inputs = snapshot.get("inputs", [])
        
        return f"""You are helping to fill out a LinkedIn job application form.

User Profile:
- Name: {profile.get('full_name', '')}
- Email: {profile.get('email', '')}
- Phone: {profile.get('phone', '')}
- Location: {profile.get('location', '')}

Available buttons: {json.dumps([{"id": btn["id"], "text": btn["text"]} for btn in buttons], indent=2)}

Available inputs: {json.dumps([{"id": inp["id"], "label": inp["label"], "type": inp["type"]} for inp in inputs], indent=2)}

Please fill out the form appropriately and return a JSON response with:
{{"actions": [list of actions], "is_final_step": boolean}}

Actions should be in format:
- {{"action": "fill", "id": "input_X", "value": "text"}}
- {{"action": "click", "id": "btn_X"}}
- {{"action": "upload", "id": "input_X", "file": "/path/to/file"}}"""