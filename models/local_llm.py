"""
Local LLM interface.

This module defines a thin wrapper around a local language model such as
LLaMA or Mistral, accessible via the Ollama API or another provider.
It constructs prompts and returns structured JSON-like output to guide
the browser actions.
"""
from __future__ import annotations

import json
import requests
from typing import Dict, Any
import os


class LocalLLM:
    """Wrapper for a locally running language model."""

    def __init__(self, model_name: str = "qwen2.5vl:7b", host: str = "http://localhost:11434") -> None:
        self.model_name = model_name
        self.host = host
        
    def _call_ollama(self, prompt: str) -> str:
        """Make a request to Ollama API."""
        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return ""

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
        # Extract relevant information from snapshot
        buttons = snapshot.get("buttons", [])
        inputs = snapshot.get("inputs", [])
        page_text = snapshot.get("text", "")
        
        # Check if this looks like a final step
        is_final = any(keyword in page_text.lower() for keyword in [
            "application submitted", "thank you", "success", "review application",
            "submit application", "confirm", "finish"
        ])
        
        # Look for Easy Apply button first
        easy_apply_button = None
        for btn in buttons:
            if "easy apply" in btn.get("text", "").lower():
                easy_apply_button = btn
                break
        
        # If we found Easy Apply button, click it
        if easy_apply_button and not any(inp for inp in inputs if inp.get("type") != "hidden"):
            return {
                "actions": [{"action": "click", "id": easy_apply_button["id"]}],
                "is_final_step": False
            }
        
        # Build prompt for form filling
        prompt = self._build_form_prompt(snapshot, profile)
        
        # Get response from local LLM
        llm_response = self._call_ollama(prompt)
        
        # Parse the response
        try:
            parsed_response = json.loads(llm_response)
            return {
                "actions": parsed_response.get("actions", []),
                "is_final_step": parsed_response.get("is_final_step", is_final)
            }
        except json.JSONDecodeError:
            print(f"Failed to parse LLM response: {llm_response}")
            # Fallback: try to fill basic fields
            return self._fallback_form_fill(inputs, profile, is_final)
    
    def _build_form_prompt(self, snapshot: Dict[str, Any], profile: Dict[str, Any]) -> str:
        """Build a prompt for the LLM to analyze the form."""
        buttons = snapshot.get("buttons", [])
        inputs = snapshot.get("inputs", [])
        
        prompt = f"""You are an AI assistant helping to fill out a LinkedIn job application form. 

User Profile:
- Name: {profile.get('full_name', '')}
- Email: {profile.get('email', '')}
- Phone: {profile.get('phone', '')}
- Location: {profile.get('location', '')}
- Resume path: {profile.get('resume_path', '')}
- Cover letter path: {profile.get('cover_letter_path', '')}

Default answers: {json.dumps(profile.get('default_answers', []))}

Current page has these buttons:
{json.dumps([{"id": btn["id"], "text": btn["text"]} for btn in buttons], indent=2)}

Current page has these input fields:
{json.dumps([{"id": inp["id"], "label": inp["label"], "type": inp["type"]} for inp in inputs], indent=2)}

Please analyze this form and return a JSON response with:
1. "actions": A list of actions to perform (click, fill, upload)
2. "is_final_step": Boolean indicating if this appears to be the final step

For each action, use this format:
- {{"action": "click", "id": "btn_X"}} for clicking buttons
- {{"action": "fill", "id": "input_X", "value": "text to enter"}} for filling inputs
- {{"action": "upload", "id": "input_X", "file": "/path/to/file"}} for file uploads

Match input labels to appropriate profile fields. For file inputs asking for resume/CV, use the resume_path. For cover letter, use cover_letter_path.

Return only valid JSON:"""
        
        return prompt
    
    def _fallback_form_fill(self, inputs: list, profile: Dict[str, Any], is_final: bool) -> Dict[str, Any]:
        """Fallback form filling when LLM fails."""
        actions = []
        
        for inp in inputs:
            label = inp.get("label", "").lower()
            input_type = inp.get("type", "")
            
            if input_type == "file":
                if "resume" in label or "cv" in label:
                    actions.append({
                        "action": "upload",
                        "id": inp["id"],
                        "file": profile.get("resume_path", "")
                    })
                elif "cover" in label:
                    actions.append({
                        "action": "upload",
                        "id": inp["id"],
                        "file": profile.get("cover_letter_path", "")
                    })
            elif input_type in ["text", "email", "tel"]:
                if "name" in label and "first" in label:
                    full_name = profile.get("full_name", "")
                    first_name = full_name.split()[0] if full_name else ""
                    actions.append({"action": "fill", "id": inp["id"], "value": first_name})
                elif "name" in label and "last" in label:
                    full_name = profile.get("full_name", "")
                    last_name = full_name.split()[-1] if full_name and len(full_name.split()) > 1 else ""
                    actions.append({"action": "fill", "id": inp["id"], "value": last_name})
                elif "email" in label:
                    actions.append({"action": "fill", "id": inp["id"], "value": profile.get("email", "")})
                elif "phone" in label:
                    actions.append({"action": "fill", "id": inp["id"], "value": profile.get("phone", "")})
                elif "location" in label or "city" in label:
                    actions.append({"action": "fill", "id": inp["id"], "value": profile.get("location", "")})
        
        return {
            "actions": actions,
            "is_final_step": is_final
        }