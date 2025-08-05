"""
AI-Powered Form Filling Agent - Actually Uses AI!

This version integrates the LLM interfaces and vector database to make
intelligent decisions about form filling using AI reasoning.
"""

import asyncio
import json
import re
from typing import Dict, Any, List, Optional
from playwright.async_api import Page

class AIFormFillingAgent:
    """Form filling agent that actually uses AI for decision making."""
    
    def __init__(self, user_profile_db, local_llm, cloud_llm):
        self.user_profile_db = user_profile_db
        self.local_llm = local_llm
        self.cloud_llm = cloud_llm
        
        print("🤖 AI-Powered Form Filling Agent initialized")
    
    async def apply_to_job(self, navigation_agent, job_details: Dict[str, Any]) -> Dict[str, Any]:
        """Apply to a job using AI-powered form analysis and completion."""
        page = navigation_agent.get_current_page()
        
        print(f"🤖 Starting AI-powered application for: {job_details['title']}")
        
        try:
            # Step 1: AI analyzes the page to understand what to do
            page_analysis = await self.ai_analyze_page(page, job_details)
            
            if not page_analysis.get('is_application_page'):
                return {
                    'success': False,
                    'error': 'Not detected as application page',
                    'analysis': page_analysis
                }
            
            # Step 2: Find and click Easy Apply using AI
            easy_apply_success = await self.ai_find_and_click_easy_apply(page)
            if not easy_apply_success:
                return {
                    'success': False,
                    'error': 'Could not find Easy Apply button with AI'
                }
            
            # Step 3: AI-powered form completion loop
            form_completion_result = await self.ai_complete_application_forms(page, job_details)
            
            return form_completion_result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'AI application failed: {str(e)}'
            }

    async def ai_analyze_page(self, page: Page, job_details: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to analyze the current page and determine what to do."""
        
        # Get page content
        page_content = await self.get_comprehensive_page_content(page)
        
        # Use local LLM for fast page analysis
        analysis_prompt = f"""
        Analyze this LinkedIn job page and determine the next actions:

        URL: {page_content['url']}
        Title: {page_content['title']}
        
        Page Text (key sections):
        {page_content['text'][:2000]}
        
        Interactive Elements Found:
        Buttons: {[btn['text'][:30] for btn in page_content['buttons'][:10]]}
        Input Fields: {[inp['label'][:30] for inp in page_content['inputs'][:10]]}
        
        Job Details:
        - Title: {job_details.get('title', 'Unknown')}
        - Company: {job_details.get('company', 'Unknown')}
        
        Return JSON analysis with:
        {{
            "is_application_page": true/false,
            "page_type": "job_listing|application_form|login|confirmation|error",
            "has_easy_apply": true/false,
            "next_action": "click_easy_apply|fill_form|submit|login_required|job_unavailable",
            "confidence": 0.0-1.0,
            "reasoning": "explanation of analysis"
        }}
        """
        
        try:
            if await self.local_llm.initialize():
                analysis = await self.local_llm.analyze_page({
                    'url': page_content['url'],
                    'title': page_content['title'],
                    'text': page_content['text'],
                    'interactive_elements': page_content['buttons'] + page_content['inputs']
                })
                
                if 'error' not in analysis:
                    print(f"🧠 AI Page Analysis: {analysis.get('reasoning', 'No reasoning provided')}")
                    return analysis
        except Exception as e:
            print(f"⚠️ Local LLM analysis failed: {e}")
        
        # Fallback analysis
        return self.fallback_page_analysis(page_content, job_details)

    async def ai_find_and_click_easy_apply(self, page: Page) -> bool:
        """Use AI to intelligently find and click the Easy Apply button."""
        
        # Get all clickable elements
        clickable_elements = await self.get_clickable_elements(page)
        
        # Use AI to identify the Easy Apply button
        button_analysis_prompt = f"""
        Identify the Easy Apply button from these clickable elements:
        
        {json.dumps(clickable_elements[:20], indent=2)}
        
        Return JSON with:
        {{
            "easy_apply_button_index": index_number,
            "confidence": 0.0-1.0,
            "reasoning": "why this is the Easy Apply button"
        }}
        
        Look for buttons with text containing: "Easy Apply", "Apply", "Apply Now", etc.
        The button should be for job applications, not other actions.
        """
        
        try:
            if await self.local_llm.initialize():
                # Use local LLM for quick button identification
                response = await self.local_llm._call_ollama(button_analysis_prompt)
                
                if response:
                    button_analysis = json.loads(response)
                    button_index = button_analysis.get('easy_apply_button_index')
                    
                    if button_index is not None and 0 <= button_index < len(clickable_elements):
                        element_info = clickable_elements[button_index]
                        
                        # Click the identified button
                        try:
                            element = element_info['element']
                            await element.click()
                            await asyncio.sleep(3)
                            
                            print(f"🤖 AI clicked: {element_info['text'][:50]}")
                            return True
                            
                        except Exception as e:
                            print(f"❌ Failed to click AI-identified button: {e}")
        
        except Exception as e:
            print(f"⚠️ AI button identification failed: {e}")
        
        # Fallback to traditional selectors
        return await self.fallback_click_easy_apply(page)

    async def ai_complete_application_forms(self, page: Page, job_details: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to complete the entire application form process."""
        
        max_steps = 10
        completed_steps = 0
        
        for step in range(max_steps):
            print(f"🤖 AI Form Step {step + 1}/{max_steps}")
            
            # AI analyzes current form step
            form_analysis = await self.ai_analyze_current_form(page, job_details)
            
            if form_analysis.get('is_complete'):
                print("✅ AI detected application completion!")
                return {
                    'success': True,
                    'steps_completed': completed_steps,
                    'completion_method': 'ai_detected'
                }
            
            if form_analysis.get('is_submit_stage'):
                print("🤖 AI detected submit stage, attempting submission...")
                submit_success = await self.ai_submit_application(page)
                return {
                    'success': submit_success,
                    'steps_completed': completed_steps,
                    'completion_method': 'ai_submit'
                }
            
            # AI fills current form step
            fill_result = await self.ai_fill_current_step(page, form_analysis, job_details)
            
            if fill_result.get('filled_fields', 0) > 0:
                completed_steps += 1
            
            # AI finds and clicks next button
            next_success = await self.ai_click_next_button(page)
            if not next_success:
                print("🤖 AI could not find next button")
                break
            
            await asyncio.sleep(2)
        
        return {
            'success': completed_steps > 0,
            'steps_completed': completed_steps,
            'completion_method': 'partial'
        }

    async def ai_analyze_current_form(self, page: Page, job_details: Dict[str, Any]) -> Dict[str, Any]:
        """AI analyzes the current form step to understand what needs to be filled."""
        
        form_elements = await self.extract_all_form_elements(page)
        page_text = await page.inner_text("body")
        
        form_analysis_prompt = f"""
        Analyze this job application form step:
        
        Page Text (key parts):
        {page_text[:1500]}
        
        Form Elements:
        {json.dumps([{
            'type': elem['type'],
            'label': elem['label'],
            'required': elem['required'],
            'options': elem['options'][:5] if elem['options'] else []
        } for elem in form_elements[:15]], indent=2)}
        
        Job Context:
        - Title: {job_details.get('title', 'Unknown')}
        - Company: {job_details.get('company', 'Unknown')}
        
        Return JSON analysis:
        {{
            "form_type": "personal_info|work_experience|questions|review|upload",
            "is_complete": true/false,
            "is_submit_stage": true/false,
            "required_fields": ["field1", "field2"],
            "complexity": "simple|moderate|complex",
            "special_instructions": "any special handling needed"
        }}
        """
        
        try:
            if await self.local_llm.initialize():
                response = await self.local_llm._call_ollama(form_analysis_prompt)
                if response:
                    return json.loads(response)
        except Exception as e:
            print(f"⚠️ AI form analysis failed: {e}")
        
        # Fallback analysis
        return {
            'form_type': 'unknown',
            'is_complete': 'application submitted' in page_text.lower(),
            'is_submit_stage': any(term in page_text.lower() for term in ['review', 'submit', 'confirm']),
            'required_fields': [],
            'complexity': 'moderate'
        }

    async def ai_fill_current_step(self, page: Page, form_analysis: Dict[str, Any], job_details: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to intelligently fill the current form step."""
        
        form_elements = await self.extract_all_form_elements(page)
        filled_count = 0
        
        for element_info in form_elements:
            try:
                # Use AI to determine what value to put in this field
                field_value = await self.ai_determine_field_value(element_info, job_details, form_analysis)
                
                if field_value:
                    success = await self.ai_fill_single_field(element_info, field_value)
                    if success:
                        filled_count += 1
                        print(f"  ✅ AI filled: {element_info['label'][:40]} = {str(field_value)[:30]}")
                
            except Exception as e:
                print(f"  ❌ Error filling field {element_info['label']}: {e}")
        
        return {
            'filled_fields': filled_count,
            'total_fields': len(form_elements)
        }

    async def ai_determine_field_value(self, element_info: Dict[str, Any], job_details: Dict[str, Any], form_context: Dict[str, Any]) -> Optional[str]:
        """Use AI and vector DB to determine the best value for a form field."""
        
        field_label = element_info['label']
        field_type = element_info['type']
        field_options = element_info.get('options', [])
        
        # First, try vector database search
        vector_results = await self.user_profile_db.search_profile_data(field_label, n_results=3)
        
        # Use AI to determine the best response
        value_prompt = f"""
        Determine the best value for this job application field:
        
        Field Information:
        - Label: {field_label}
        - Type: {field_type}
        - Required: {element_info.get('required', False)}
        - Options: {field_options[:10] if field_options else 'Free text'}
        
        Job Context:
        - Title: {job_details.get('title', 'Unknown')}
        - Company: {job_details.get('company', 'Unknown')}
        
        User Profile Data (from vector search):
        {json.dumps([result['text'] for result in vector_results], indent=2)}
        
        Form Context: {form_context.get('form_type', 'unknown')} form
        
        Return JSON with:
        {{
            "value": "the_value_to_enter",
            "reasoning": "why this value",
            "confidence": 0.0-1.0
        }}
        
        For dropdowns, return exactly one of the provided options.
        For text fields, provide appropriate text based on the user profile.
        For yes/no questions, return "yes" or "no".
        If no good value can be determined, return null.
        """
        
        try:
            # Use cloud LLM for complex reasoning
            if await self.cloud_llm.initialize():
                smart_answer = await self.cloud_llm.generate_smart_answer(
                    field_label, 
                    {
                        'job_title': job_details.get('title'),
                        'company': job_details.get('company'),
                        'field_type': field_type
                    }, 
                    vector_results
                )
                
                if smart_answer and smart_answer != "Unable to generate answer at this time.":
                    return smart_answer
            
            # Fallback to local LLM
            if await self.local_llm.initialize():
                response = await self.local_llm._call_ollama(value_prompt)
                if response:
                    result = json.loads(response)
                    return result.get('value')
                    
        except Exception as e:
            print(f"⚠️ AI value determination failed: {e}")
        
        # Final fallback - try to get from vector DB directly
        return await self.user_profile_db.answer_question(field_label)

    async def ai_fill_single_field(self, element_info: Dict[str, Any], value: str) -> bool:
        """Fill a single form field with AI-determined value."""
        
        element = element_info['element']
        field_type = element_info['type']
        
        try:
            if field_type == 'select':
                # Handle dropdown
                options = element_info.get('options', [])
                
                # Find best matching option
                best_option = None
                for option in options:
                    if value.lower() in option['text'].lower() or option['text'].lower() in value.lower():
                        best_option = option
                        break
                
                if best_option:
                    await element.select_option(value=best_option['value'])
                    return True
                    
            elif field_type in ['text', 'email', 'tel', 'url', 'number']:
                await element.fill(str(value))
                return True
                
            elif field_type == 'textarea':
                await element.fill(str(value))
                return True
                
            elif field_type == 'file':
                # Handle file uploads
                return await self.ai_handle_file_upload(element, element_info['label'])
                
            elif field_type in ['checkbox', 'radio']:
                # Handle checkboxes/radio buttons
                if value.lower() in ['yes', 'true', '1', 'check', 'select']:
                    await element.check()
                    return True
                    
        except Exception as e:
            print(f"❌ Error filling field: {e}")
            return False
        
        return False

    async def ai_handle_file_upload(self, element, field_label: str) -> bool:
        """AI determines and uploads the appropriate file."""
        
        # Use AI to determine what type of file is needed
        file_type_prompt = f"""
        What type of file should be uploaded for this field?
        
        Field Label: {field_label}
        
        Return JSON:
        {{
            "file_type": "resume|cover_letter|portfolio|other",
            "confidence": 0.0-1.0
        }}
        """
        
        try:
            if await self.local_llm.initialize():
                response = await self.local_llm._call_ollama(file_type_prompt)
                if response:
                    result = json.loads(response)
                    file_type = result.get('file_type')
                    
                    if file_type == 'resume':
                        file_path = await self.user_profile_db.get_contact_info().get('resume_path')
                        if file_path:
                            await element.set_input_files(file_path)
                            return True
                    elif file_type == 'cover_letter':
                        # Generate dynamic cover letter
                        cover_letter = await self.ai_generate_cover_letter()
                        if cover_letter:
                            # Save to temp file and upload
                            import tempfile
                            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                                f.write(cover_letter)
                                temp_path = f.name
                            
                            await element.set_input_files(temp_path)
                            return True
                            
        except Exception as e:
            print(f"⚠️ AI file upload determination failed: {e}")
        
        return False

    async def ai_generate_cover_letter(self) -> str:
        """Generate a custom cover letter using AI."""
        
        if await self.cloud_llm.initialize():
            # Get user profile summary
            contact_info = await self.user_profile_db.get_contact_info()
            
            return await self.cloud_llm.generate_cover_letter({
                'title': 'Software Engineer',  # Will be passed from job_details
                'company': 'Unknown Company'
            }, {
                'name': contact_info.get('name', 'Unknown'),
                'background': 'Software engineer with experience',
                'skills': 'Programming, problem solving',
                'experience': 'Multiple years of development'
            })
        
        return "I am excited to apply for this position and believe my skills and experience make me a strong candidate."

    async def ai_click_next_button(self, page: Page) -> bool:
        """Use AI to find and click the Next/Continue button."""
        
        clickable_elements = await self.get_clickable_elements(page)
        
        next_button_prompt = f"""
        Identify the Next/Continue button from these elements:
        
        {json.dumps([{
            'index': i,
            'text': elem['text'][:50],
            'type': elem['type']
        } for i, elem in enumerate(clickable_elements[:15])], indent=2)}
        
        Return JSON:
        {{
            "next_button_index": index_number,
            "confidence": 0.0-1.0
        }}
        
        Look for buttons with: "Next", "Continue", "Proceed", "Save and continue", etc.
        """
        
        try:
            if await self.local_llm.initialize():
                response = await self.local_llm._call_ollama(next_button_prompt)
                if response:
                    result = json.loads(response)
                    button_index = result.get('next_button_index')
                    
                    if button_index is not None and 0 <= button_index < len(clickable_elements):
                        element = clickable_elements[button_index]['element']
                        await element.click()
                        await asyncio.sleep(3)
                        return True
                        
        except Exception as e:
            print(f"⚠️ AI next button click failed: {e}")
        
        # Fallback
        return await self.fallback_click_next(page)

    async def ai_submit_application(self, page: Page) -> bool:
        """Use AI to find and click the final submit button."""
        
        clickable_elements = await self.get_clickable_elements(page)
        
        submit_prompt = f"""
        Identify the final application submission button:
        
        {json.dumps([{
            'index': i,
            'text': elem['text'][:50],
            'type': elem['type']  
        } for i, elem in enumerate(clickable_elements[:15])], indent=2)}
        
        Return JSON:
        {{
            "submit_button_index": index_number,
            "confidence": 0.0-1.0
        }}
        
        Look for: "Submit application", "Submit", "Send application", "Apply now", etc.
        """
        
        try:
            if await self.local_llm.initialize():
                response = await self.local_llm._call_ollama(submit_prompt)
                if response:
                    result = json.loads(response)
                    button_index = result.get('submit_button_index')
                    
                    if button_index is not None and 0 <= button_index < len(clickable_elements):
                        element = clickable_elements[button_index]['element']
                        await element.click()
                        await asyncio.sleep(5)
                        return True
                        
        except Exception as e:
            print(f"⚠️ AI submit failed: {e}")
            
        return False

    # Helper methods
    async def get_comprehensive_page_content(self, page: Page) -> Dict[str, Any]:
        """Get comprehensive page content for AI analysis."""
        try:
            url = page.url
            title = await page.title()
            text = await page.inner_text("body")
            
            # Get buttons
            buttons = []
            button_elements = await page.query_selector_all("button, input[type='submit'], input[type='button']")
            for btn in button_elements[:20]:
                try:
                    text_content = await btn.inner_text()
                    if text_content.strip():
                        buttons.append({
                            'text': text_content.strip(),
                            'element': btn
                        })
                except:
                    continue
            
            # Get inputs
            inputs = []
            input_elements = await page.query_selector_all("input, textarea, select")
            for inp in input_elements[:20]:
                try:
                    label = await self.get_element_label(inp, page)
                    input_type = await inp.get_attribute("type") or "text"
                    inputs.append({
                        'label': label,
                        'type': input_type,
                        'element': inp
                    })
                except:
                    continue
            
            return {
                'url': url,
                'title': title,
                'text': text,
                'buttons': buttons,
                'inputs': inputs
            }
            
        except Exception as e:
            print(f"❌ Error getting page content: {e}")
            return {'error': str(e)}

    async def get_clickable_elements(self, page: Page) -> List[Dict[str, Any]]:
        """Get all clickable elements for AI analysis."""
        elements = []
        
        selectors = ["button", "input[type='submit']", "input[type='button']", "a[role='button']"]
        
        for selector in selectors:
            try:
                found_elements = await page.query_selector_all(selector)
                for elem in found_elements:
                    try:
                        text = await elem.inner_text()
                        if text.strip():
                            elements.append({
                                'text': text.strip(),
                                'type': selector,
                                'element': elem
                            })
                    except:
                        continue
            except:
                continue
        
        return elements

    async def extract_all_form_elements(self, page: Page) -> List[Dict[str, Any]]:
        """Extract all form elements for AI processing."""
        elements = []
        
        try:
            form_elements = await page.query_selector_all("input, textarea, select")
            
            for elem in form_elements:
                try:
                    element_info = await self.analyze_form_element(elem, page)
                    if element_info:
                        elements.append(element_info)
                except:
                    continue
                    
        except Exception as e:
            print(f"❌ Error extracting form elements: {e}")
        
        return elements

    async def analyze_form_element(self, element, page: Page) -> Dict[str, Any]:
        """Analyze a single form element."""
        try:
            tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
            input_type = await element.get_attribute("type") or "text"
            name = await element.get_attribute("name") or ""
            placeholder = await element.get_attribute("placeholder") or ""
            required = await element.get_attribute("required") is not None
            
            label = await self.get_element_label(element, page)
            
            options = []
            if tag_name == "select":
                option_elements = await element.query_selector_all("option")
                for option in option_elements:
                    text = await option.inner_text()
                    value = await option.get_attribute("value")
                    if text.strip():
                        options.append({'text': text.strip(), 'value': value})
            
            return {
                'tag': tag_name,
                'type': input_type,
                'name': name,
                'label': label,
                'placeholder': placeholder,
                'required': required,
                'options': options,
                'element': element
            }
            
        except Exception as e:
            return None

    async def get_element_label(self, element, page: Page) -> str:
        """Get label for form element."""
        try:
            # Try ID-based label
            element_id = await element.get_attribute("id")
            if element_id:
                label = await page.query_selector(f"label[for='{element_id}']")
                if label:
                    return await label.inner_text()
            
            # Try placeholder
            placeholder = await element.get_attribute("placeholder")
            if placeholder:
                return placeholder
            
            # Try aria-label
            aria_label = await element.get_attribute("aria-label")
            if aria_label:
                return aria_label
            
            return "Unknown field"
            
        except:
            return "Unknown field"

    # Fallback methods (when AI fails)
    def fallback_page_analysis(self, page_content: Dict[str, Any], job_details: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback page analysis when AI fails."""
        text = page_content.get('text', '').lower()
        
        return {
            'is_application_page': 'linkedin.com/jobs' in page_content.get('url', ''),
            'page_type': 'job_listing',
            'has_easy_apply': any('easy apply' in btn['text'].lower() for btn in page_content.get('buttons', [])),
            'next_action': 'click_easy_apply',
            'confidence': 0.7,
            'reasoning': 'Fallback analysis based on URL and button text'
        }

    async def fallback_click_easy_apply(self, page: Page) -> bool:
        """Fallback Easy Apply clicking."""
        selectors = [
            "button:has-text('Easy Apply')",
            ".jobs-s-apply button",
            "button[aria-label*='Easy Apply']"
        ]
        
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element and await element.is_visible():
                    await element.click()
                    await asyncio.sleep(3)
                    return True
            except:
                continue
        
        return False

    async def fallback_click_next(self, page: Page) -> bool:
        """Fallback next button clicking."""
        selectors = [
            "button:has-text('Next')",
            "button:has-text('Continue')",
            "input[value='Next']"
        ]
        
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element and await element.is_visible():
                    await element.click()
                    await asyncio.sleep(3)
                    return True
            except:
                continue
        
        return False

    async def shutdown(self):
        """Shutdown the AI form filling agent."""
        print("🤖 AI Form Filling Agent shut down")