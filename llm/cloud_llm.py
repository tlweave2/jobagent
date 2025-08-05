"""
Cloud LLM Interface - Advanced AI for Complex Reasoning

Handles complex reasoning, cover letter generation, and recovery scenarios
using cloud models (Claude, GPT-4).
"""

import asyncio
import json
import os
from typing import Dict, Any, Optional, List
from anthropic import AsyncAnthropic

class CloudLLM:
    """Interface to cloud LLM (Claude) for complex AI operations."""
    
    def __init__(self):
        self.anthropic_client = None
        self.model_name = "claude-3-5-sonnet-20241022"
        self.initialized = False
        
        print("☁️ Cloud LLM interface initialized")
    
    async def initialize(self):
        """Initialize connection to cloud LLM."""
        try:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                print("⚠️  No ANTHROPIC_API_KEY found, cloud LLM unavailable")
                return False
            
            self.anthropic_client = AsyncAnthropic(api_key=api_key)
            print("✅ Connected to Claude AI")
            self.initialized = True
            return True
        
        except Exception as e:
            print(f"❌ Failed to connect to Claude: {e}")
            return False
    
    async def generate_cover_letter(self, job_details: Dict[str, Any], user_profile: Dict[str, Any]) -> str:
        """Generate a custom cover letter for a specific job."""
        if not self.initialized:
            return "Cover letter generation not available (Cloud LLM not initialized)"
        
        try:
            prompt = f"""
Generate a professional, compelling cover letter for this job application:

Job Details:
- Title: {job_details.get('title', 'Unknown')}
- Company: {job_details.get('company', 'Unknown')}
- Description: {job_details.get('description', 'No description available')[:1000]}

User Profile:
- Name: {user_profile.get('name', 'Unknown')}
- Background: {user_profile.get('background', 'No background provided')}
- Skills: {user_profile.get('skills', 'No skills listed')}
- Experience: {user_profile.get('experience', 'No experience details')}

Requirements:
1. Professional tone, 3-4 paragraphs
2. Highlight relevant skills and experience
3. Show enthusiasm for the company/role
4. Include specific examples where possible
5. End with a strong call to action

Generate only the cover letter text, no extra formatting or metadata.
"""
            
            response = await self.anthropic_client.messages.create(
                model=self.model_name,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text.strip()
        
        except Exception as e:
            print(f"❌ Cover letter generation failed: {e}")
            return f"Unable to generate cover letter: {e}"
    
    async def analyze_stuck_state(self, page_content: Dict[str, Any], history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze when the system appears stuck and suggest recovery actions."""
        if not self.initialized:
            return {'action': 'manual_intervention', 'reason': 'Cloud LLM not available'}
        
        try:
            prompt = f"""
The job application system appears to be stuck. Analyze the situation and suggest recovery actions:

Current Page:
- URL: {page_content.get('url', 'unknown')}
- Title: {page_content.get('title', 'unknown')}
- Text Content: {page_content.get('text', '')[:1500]}

Recent Actions (last 5):
{json.dumps(history[-5:], indent=2)}

Common stuck scenarios:
1. Captcha/verification required
2. Login expired
3. Form validation errors
4. Page loading issues
5. Unexpected modal/popup
6. Application already submitted
7. Job no longer available

Analyze the situation and determine:
1. What might be causing the stuck state
2. What recovery action to take
3. Whether manual intervention is needed

Return JSON with:
{{
  "diagnosis": "...",
  "action": "retry/refresh/navigate/manual_intervention/abandon",
  "target": "...",
  "reason": "...",
  "confidence": 0.0-1.0
}}
"""
            
            response = await self.anthropic_client.messages.create(
                model=self.model_name,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text.strip()
            return json.loads(response_text)
        
        except Exception as e:
            print(f"❌ Stuck state analysis failed: {e}")
            return {
                'action': 'manual_intervention',
                'reason': f'Analysis failed: {e}',
                'confidence': 0.0
            }
    
    async def optimize_application_strategy(self, job_details: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize application strategy for a specific job."""
        if not self.initialized:
            return {'strategy': 'standard', 'priority': 'medium'}
        
        try:
            prompt = f"""
Analyze this job opportunity and optimize the application strategy:

Job Details:
- Title: {job_details.get('title', 'Unknown')}
- Company: {job_details.get('company', 'Unknown')}
- Location: {job_details.get('location', 'Unknown')}
- Description: {job_details.get('description', 'No description')[:1000]}
- Site: {job_details.get('site', 'unknown')}

User Profile Match:
- Target roles: {user_profile.get('target_roles', [])}
- Skills: {user_profile.get('skills', [])}
- Experience level: {user_profile.get('experience_level', 'unknown')}
- Preferences: {user_profile.get('preferences', {})}

Determine:
1. How well this job matches the user's profile (0.0-1.0)
2. Application priority (high/medium/low)
3. Recommended strategy (standard/enhanced/skip)
4. Key points to emphasize

Return JSON with:
{{
  "match_score": 0.0-1.0,
  "priority": "high/medium/low",
  "strategy": "standard/enhanced/skip",
  "key_points": ["...", "..."],
  "reasoning": "..."
}}
"""
            
            response = await self.anthropic_client.messages.create(
                model=self.model_name,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text.strip()
            return json.loads(response_text)
        
        except Exception as e:
            print(f"❌ Strategy optimization failed: {e}")
            return {
                'match_score': 0.5,
                'priority': 'medium',
                'strategy': 'standard',
                'reasoning': f'Optimization failed: {e}'
            }
    
    async def generate_smart_answer(self, question: str, context: Dict[str, Any], user_data: List[Dict[str, Any]]) -> str:
        """Generate intelligent answers to application questions."""
        if not self.initialized:
            return "Unable to generate answer (Cloud LLM not available)"
        
        try:
            prompt = f"""
Generate a smart, honest answer to this job application question:

Question: {question}

Context:
- Job: {context.get('job_title', 'Unknown')} at {context.get('company', 'Unknown')}
- Field type: {context.get('field_type', 'unknown')}

User Data (relevant information):
{json.dumps(user_data, indent=2)}

Requirements:
1. Be honest and accurate
2. Highlight relevant experience/skills
3. Keep appropriate length for the context
4. Use professional language
5. Don't exaggerate or lie

Generate only the answer text, no extra formatting.
"""
            
            response = await self.anthropic_client.messages.create(
                model=self.model_name,
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text.strip()
        
        except Exception as e:
            print(f"❌ Smart answer generation failed: {e}")
            return "Unable to generate answer at this time."
