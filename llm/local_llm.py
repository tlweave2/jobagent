"""
Local LLM Interface - Fast Local AI for Quick Decisions

Handles page analysis, form understanding, and quick decision making
using local models (Ollama).
"""

import asyncio
import json
import requests
import base64
from typing import Dict, Any, Optional, List

class LocalLLM:
    """Interface to local LLM (Ollama) for fast AI operations."""
    
    def __init__(self):
        self.model_name = "qwen2.5vl:7b"  # Vision-capable model
        self.host = "http://localhost:11434"
        self.initialized = False
        
        print("🧠 Local LLM interface initialized")
    
    async def initialize(self):
        """Initialize connection to local LLM."""
        try:
            # Test connection
            response = requests.get(f"{self.host}/api/version", timeout=5)
            if response.status_code == 200:
                print(f"✅ Connected to Ollama at {self.host}")
                self.initialized = True
                return True
            else:
                print(f"❌ Ollama not responding at {self.host}")
                return False
        except Exception as e:
            print(f"❌ Failed to connect to Ollama: {e}")
            return False
    
    async def analyze_page(self, page_content: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a web page and determine what actions to take."""
        if not self.initialized:
            return {'error': 'LLM not initialized'}
        
        try:
            # Build prompt for page analysis
            prompt = self._build_page_analysis_prompt(page_content)
            
            # Call local LLM
            response = await self._call_ollama(prompt)
            
            if response:
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    return {'error': 'Invalid JSON response', 'raw_response': response}
            else:
                return {'error': 'No response from LLM'}
        
        except Exception as e:
            return {'error': f'Page analysis failed: {e}'}
    
    async def understand_form_field(self, field_info: Dict[str, Any], context: str = "") -> Dict[str, Any]:
        """Understand what a form field is asking for."""
        try:
            prompt = f"""
Analyze this form field and determine what information it's requesting:

Field Information:
- Type: {field_info.get('type', 'unknown')}
- Label: {field_info.get('label', 'unknown')}
- Placeholder: {field_info.get('placeholder', '')}
- Context: {context}

Determine:
1. What type of information this field wants
2. What category it belongs to (personal, contact, work_auth, experience, etc.)
3. How important/required it seems

Return JSON with: {{"field_type": "...", "category": "...", "importance": "high/medium/low", "description": "..."}}
"""
            
            response = await self._call_ollama(prompt)
            if response:
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    return {'error': 'Invalid JSON response'}
            
            return {'error': 'No response from LLM'}
        
        except Exception as e:
            return {'error': f'Field analysis failed: {e}'}
    
    async def decide_next_action(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Decide what action to take next based on current page state."""
        try:
            prompt = f"""
Based on the current page state, decide the next action:

Current State:
- URL: {current_state.get('url', 'unknown')}
- Page Title: {current_state.get('title', 'unknown')}
- Available Actions: {current_state.get('available_actions', [])}
- Current Step: {current_state.get('current_step', 'unknown')}

Possible actions:
- click_button: Click a specific button
- fill_form: Fill out form fields
- navigate: Navigate to a different page
- wait: Wait for page to load
- complete: Application is complete

Return JSON with: {{"action": "...", "target": "...", "reason": "...", "confidence": 0.0-1.0}}
"""
            
            response = await self._call_ollama(prompt)
            if response:
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    return {'action': 'wait', 'reason': 'LLM response parsing failed'}
            
            return {'action': 'wait', 'reason': 'No LLM response'}
        
        except Exception as e:
            return {'action': 'wait', 'reason': f'Decision failed: {e}'}
    
    def _build_page_analysis_prompt(self, page_content: Dict[str, Any]) -> str:
        """Build prompt for page analysis."""
        url = page_content.get('url', 'unknown')
        title = page_content.get('title', 'unknown')
        text = page_content.get('text', '')[:2000]  # Limit text length
        interactive_elements = page_content.get('interactive_elements', [])
        
        # Simplify interactive elements for prompt
        buttons = [elem for elem in interactive_elements if elem.get('type') == 'button']
        inputs = [elem for elem in interactive_elements if elem.get('type') == 'input']
        
        prompt = f"""
Analyze this job application page and determine the next steps:

Page Information:
- URL: {url}
- Title: {title}
- Site: {page_content.get('site', 'unknown')}

Page Text (first 2000 chars):
{text}

Interactive Elements:
Buttons: {[btn.get('text', 'unknown')[:50] for btn in buttons[:10]]}
Input Fields: {[inp.get('label', 'unknown')[:50] for inp in inputs[:10]]}

Determine:
1. What type of page this is (job_listing, application_form, login, success, etc.)
2. What actions are available
3. What the next step should be
4. If this looks like an Easy Apply job

Return JSON with:
{{
  "page_type": "...",
  "available_actions": ["...", "..."],
  "next_step": "...",
  "is_easy_apply": true/false,
  "confidence": 0.0-1.0,
  "reasoning": "..."
}}
"""
        return prompt
    
    async def _call_ollama(self, prompt: str, image_data: bytes = None) -> Optional[str]:
        """Make async call to Ollama API."""
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            }
            
            # Add image if provided
            if image_data:
                encoded_image = base64.b64encode(image_data).decode('utf-8')
                payload["images"] = [encoded_image]
            
            # Make request in thread pool since requests is sync
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(f"{self.host}/api/generate", json=payload, timeout=30)
            )
            
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                print(f"❌ Ollama API error: {response.status_code}")
                return None
        
        except Exception as e:
            print(f"❌ Ollama call failed: {e}")
            return None
