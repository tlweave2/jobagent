"""
Form Filling Agent - Intelligent Application Form Completion

This agent uses AI to analyze and complete job application forms.
It retrieves user data from the vector database and generates custom responses.
"""

import asyncio
import json
import os
from typing import Dict, Any, List
from playwright.async_api import Page
from langchain.llms import Ollama
from langchain.chat_models import ChatAnthropic
from langchain.schema import HumanMessage, SystemMessage

class FormFillingAgent:
    """Agent responsible for intelligently filling out job application forms."""
    
    def __init__(self, user_profile_db):
        self.user_profile_db = user_profile_db
        self.local_llm = None
        self.claude_llm = None
        
        print("📝 Form Filling Agent initialized")
    
    async def initialize(self):
        """Initialize AI models for form analysis and filling."""
        print("📝 Connecting to AI models...")
        
        # Initialize local LLM (Ollama)
        try:
            self.local_llm = Ollama(
                model="qwen2.5vl:7b",
                base_url="http://localhost:11434"
            )
            print("   ✅ Local LLM (Ollama) connected")
        except Exception as e:
            print(f"   ❌ Local LLM connection failed: {e}")
        
        # Initialize Claude for complex reasoning
        try:
            self.claude_llm = ChatAnthropic(
                model="claude-3-sonnet-20240229",
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
            )
            print("   ✅ Claude LLM connected")
        except Exception as e:
            print(f"   ⚠️  Claude LLM not available: {e}")
        
        print("✅ Form Filling Agent ready")
    
    async def complete_application(self, application_id: str, job: Dict[str, Any], page: Page) -> bool:
        """Complete a job application form."""
        print(f"📝 Starting application form completion for: {job['title']}")
        
        try:
            # Step 1: Find and click Easy Apply button
            easy_apply_success = await self.click_easy_apply_button(page)
            if not easy_apply_success:
                print("❌ Could not find or click Easy Apply button")
                return False
            
            # Step 2: Process application form steps
            max_steps = 10
            for step in range(max_steps):
                print(f"📋 Form step {step + 1}/{max_steps}")
                
                # Get current page state
                page_content = await self.analyze_page_content(page)
                
                # Check if application is complete
                if self.is_application_complete(page_content):
                    print("✅ Application completed successfully!")
                    return True
                
                # Check if we're at the review/submit stage
                if self.is_review_stage(page_content):
                    print("📋 Reached review stage, submitting application...")
                    submit_success = await self.submit_application(page)
                    if submit_success:
                        print("✅ Application submitted!")
                        return True
                    else:
                        print("❌ Failed to submit application")
                        return False
                
                # Fill out current form step
                form_success = await self.fill_current_form_step(page, page_content, job)
                if not form_success:
                    print("❌ Failed to fill current form step")
                    return False
                
                # Look for and click Next button
                next_success = await self.click_next_button(page)
                if not next_success:
                    print("❌ Could not find Next button")
                    break
                
                # Brief delay between steps
                await asyncio.sleep(2)
            
            print("⚠️  Application may not have completed fully")
            return False
            
        except Exception as e:
            print(f"❌ Form completion error: {e}")
            return False
    
    async def click_easy_apply_button(self, page: Page) -> bool:
        """Find and click the Easy Apply button."""
        easy_apply_selectors = [
            "button:has-text('Easy Apply')",
            ".jobs-s-apply button",
            ".jobs-apply-button",
            "[aria-label*='Easy Apply']",
            "button[aria-label*='Easy Apply']"
        ]
        
        for selector in easy_apply_selectors:
            try:
                element = await page.query_selector(selector)
                if element and await element.is_visible():
                    print(f"✅ Found Easy Apply button: {selector}")
                    await element.click()
                    await asyncio.sleep(3)
                    return True
            except:
                continue
        
        print("❌ Easy Apply button not found")
        return False
    
    async def analyze_page_content(self, page: Page) -> Dict[str, Any]:
        """Analyze current page content using AI."""
        try:
            # Get page text and interactive elements
            page_text = await page.inner_text("body")
            url = page.url
            title = await page.title()
            
            # Find all form elements
            form_elements = await self.extract_form_elements(page)
            
            return {
                'url': url,
                'title': title,
                'text': page_text,
                'form_elements': form_elements
            }
            
        except Exception as e:
            print(f"❌ Error analyzing page: {e}")
            return {'error': str(e)}
    
    async def extract_form_elements(self, page: Page) -> List[Dict[str, Any]]:
        """Extract all form elements from the page."""
        elements = []
        
        try:
            # Find input fields
            inputs = await page.query_selector_all("input, textarea, select")
            
            for input_elem in inputs:
                try:
                    element_info = await self.analyze_form_element(input_elem, page)
                    if element_info:
                        elements.append(element_info)
                except:
                    continue
            
            # Find file upload elements
            file_inputs = await page.query_selector_all("input[type='file']")
            for file_input in file_inputs:
                try:
                    element_info = await self.analyze_form_element(file_input, page)
                    if element_info:
                        element_info['is_file_upload'] = True
                        elements.append(element_info)
                except:
                    continue
            
        except Exception as e:
            print(f"❌ Error extracting form elements: {e}")
        
        return elements
    
    async def analyze_form_element(self, element, page: Page) -> Dict[str, Any]:
        """Analyze a single form element."""
        try:
            # Get element attributes
            tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
            input_type = await element.get_attribute("type") or "text"
            name = await element.get_attribute("name") or ""
            placeholder = await element.get_attribute("placeholder") or ""
            required = await element.get_attribute("required") is not None
            
            # Get label
            label = await self.get_element_label(element, page)
            
            # Get options for select elements
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
            print(f"Error analyzing element: {e}")
            return None
    
    async def get_element_label(self, element, page: Page) -> str:
        """Get the label for a form element."""
        try:
            # Try to find associated label by ID
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
            
            # Try to find label in parent
            parent = await element.query_selector("xpath=..")
            if parent:
                parent_text = await parent.inner_text()
                if len(parent_text) < 200:
                    return parent_text.strip()
            
            return "Unknown field"
            
        except:
            return "Unknown field"
    
    async def fill_current_form_step(self, page: Page, page_content: Dict[str, Any], job: Dict[str, Any]) -> bool:
        """Fill out the current form step using AI and vector DB."""
        form_elements = page_content.get('form_elements', [])
        
        if not form_elements:
            print("   ℹ️  No form elements found on this page")
            return True
        
        print(f"   📝 Found {len(form_elements)} form elements to fill")
        
        success_count = 0
        
        for element_info in form_elements:
            try:
                filled = await self.fill_single_element(element_info, job, page)
                if filled:
                    success_count += 1
            except Exception as e:
                print(f"   ❌ Error filling element: {e}")
                continue
        
        print(f"   ✅ Successfully filled {success_count}/{len(form_elements)} elements")
        return success_count > 0
    
    async def fill_single_element(self, element_info: Dict[str, Any], job: Dict[str, Any], page: Page) -> bool:
        """Fill a single form element."""
        element = element_info['element']
        label = element_info['label']
        element_type = element_info['type']
        tag = element_info['tag']
        
        print(f"      🔸 Filling: {label[:50]}...")
        
        try:
            # Handle file uploads
            if element_info.get('is_file_upload') or element_type == 'file':
                return await self.handle_file_upload(element, label)
            
            # Handle select dropdowns
            if tag == 'select':
                return await self.handle_select_element(element, element_info, job)
            
            # Handle text inputs
            if element_type in ['text', 'email', 'tel', 'url']:
                return await self.handle_text_input(element, label, job)
            
            # Handle textareas
            if tag == 'textarea':
                return await self.handle_textarea(element, label, job)
            
            # Handle checkboxes and radio buttons
            if element_type in ['checkbox', 'radio']:
                return await self.handle_checkbox_radio(element, label, job)
            
            print(f"      ⚠️  Unsupported element type: {element_type}")
            return False
            
        except Exception as e:
            print(f"      ❌ Error filling element: {e}")
            return False
    
    async def handle_file_upload(self, element, label: str) -> bool:
        """Handle file upload fields."""
        # Determine what type of file is needed
        if any(keyword in label.lower() for keyword in ['resume', 'cv']):
            file_path = await self.user_profile_db.get_resume_path()
            if file_path and os.path.exists(file_path):
                await element.set_input_files(file_path)
                print(f"      ✅ Uploaded resume: {file_path}")
                return True
        
        elif any(keyword in label.lower() for keyword in ['cover', 'letter']):
            file_path = await self.user_profile_db.get_cover_letter_path()
            if file_path and os.path.exists(file_path):
                await element.set_input_files(file_path)
                print(f"      ✅ Uploaded cover letter: {file_path}")
                return True
        
        print(f"      ⚠️  No suitable file found for: {label}")
        return False
    
    async def handle_select_element(self, element, element_info: Dict[str, Any], job: Dict[str, Any]) -> bool:
        """Handle select dropdown elements."""
        options = element_info.get('options', [])
        label = element_info['label']
        
        if not options:
            print(f"      ⚠️  No options found for select: {label}")
            return False
        
        # Use AI to choose the best option
        best_option = await self.choose_best_option(label, options, job)
        
        if best_option:
            try:
                await element.select_option(value=best_option['value'])
                print(f"      ✅ Selected: {best_option['text']}")
                return True
            except:
                # Try selecting by text if value fails
                try:
                    await element.select_option(label=best_option['text'])
                    print(f"      ✅ Selected: {best_option['text']}")
                    return True
                except:
                    print(f"      ❌ Failed to select option")
                    return False
        
        return False
    
    async def handle_text_input(self, element, label: str, job: Dict[str, Any]) -> str:
        """Handle text input fields."""
        # Get appropriate value from vector DB
        value = await self.get_field_value(label, job)
        
        if value:
            await element.fill(str(value))
            print(f"      ✅ Filled with: {str(value)[:30]}...")
            return True
        
        print(f"      ⚠️  No value found for: {label}")
        return False
    
    async def handle_textarea(self, element, label: str, job: Dict[str, Any]) -> bool:
        """Handle textarea elements (cover letters, etc.)."""
        # Check if this is a cover letter field
        if any(keyword in label.lower() for keyword in ['cover', 'letter', 'why', 'interest', 'motivation']):
            cover_letter = await self.generate_cover_letter(job)
            if cover_letter:
                await element.fill(cover_letter)
                print(f"      ✅ Generated custom cover letter")
                return True
        
        # Otherwise treat as regular text field
        return await self.handle_text_input(element, label, job)
    
    async def handle_checkbox_radio(self, element, label: str, job: Dict[str, Any]) -> bool:
        """Handle checkbox and radio button elements."""
        # Use AI to determine if this should be checked
        should_check = await self.should_check_option(label, job)
        
        if should_check:
            await element.check()
            print(f"      ✅ Checked: {label[:30]}...")
            return True
        
        return False
    
    async def get_field_value(self, label: str, job: Dict[str, Any]) -> str:
        """Get the appropriate value for a field from the vector database."""
        # Query vector database for relevant information
        return await self.user_profile_db.get_field_value(label, job)
    
    async def choose_best_option(self, label: str, options: List[Dict], job: Dict[str, Any]) -> Dict:
        """Use AI to choose the best option from a dropdown."""
        if not self.local_llm:
            return options[0] if options else None
        
        try:
            prompt = f"""
            Choose the best option for the field "{label}" from these choices:
            {json.dumps(options, indent=2)}
            
            Job context:
            Title: {job.get('title', 'Unknown')}
            Company: {job.get('company', 'Unknown')}
            
            Return only the option value (not the full JSON).
            """
            
            response = self.local_llm(prompt)
            
            # Find matching option
            for option in options:
                if option['value'] in response or option['text'] in response:
                    return option
            
            return options[0] if options else None
            
        except Exception as e:
            print(f"      ❌ AI option selection failed: {e}")
            return options[0] if options else None
    
    async def should_check_option(self, label: str, job: Dict[str, Any]) -> bool:
        """Determine if a checkbox/radio should be checked."""
        # Query vector database for user preferences
        return await self.user_profile_db.should_check_option(label, job)
    
    async def generate_cover_letter(self, job: Dict[str, Any]) -> str:
        """Generate a custom cover letter for the job."""
        if not self.claude_llm:
            return await self.user_profile_db.get_default_cover_letter()
        
        try:
            user_info = await self.user_profile_db.get_user_summary()
            
            prompt = f"""
            Write a personalized cover letter for this job application:
            
            Job Title: {job.get('title', 'Unknown')}
            Company: {job.get('company', 'Unknown')}
            
            User Profile: {user_info}
            
            Requirements:
            - 150-200 words
            - Professional tone
            - Highlight relevant experience
            - Show enthusiasm for the role
            - Don't repeat resume content verbatim
            
            Return only the cover letter text, no additional formatting.
            """
            
            messages = [
                SystemMessage(content="You are an expert at writing compelling cover letters."),
                HumanMessage(content=prompt)
            ]
            
            response = await self.claude_llm.agenerate([messages])
            cover_letter = response.generations[0][0].text.strip()
            
            return cover_letter
            
        except Exception as e:
            print(f"❌ Cover letter generation failed: {e}")
            return await self.user_profile_db.get_default_cover_letter()
    
    def is_application_complete(self, page_content: Dict[str, Any]) -> bool:
        """Check if the application has been completed."""
        text = page_content.get('text', '').lower()
        
        completion_indicators = [
            'application submitted',
            'thank you for applying',
            'application received',
            'application complete',
            'successfully submitted',
            'your application has been sent'
        ]
        
        return any(indicator in text for indicator in completion_indicators)
    
    def is_review_stage(self, page_content: Dict[str, Any]) -> bool:
        """Check if we're at the review/submit stage."""
        text = page_content.get('text', '').lower()
        
        review_indicators = [
            'review your application',
            'review application',
            'submit application',
            'confirm and submit',
            'final review'
        ]
        
        return any(indicator in text for indicator in review_indicators)
    
    async def submit_application(self, page: Page) -> bool:
        """Submit the application at the review stage."""
        submit_selectors = [
            "button:has-text('Submit application')",
            "button:has-text('Submit')",
            "input[type='submit']",
            "button[aria-label*='Submit']",
            ".jobs-apply-form__submit-button"
        ]
        
        for selector in submit_selectors:
            try:
                element = await page.query_selector(selector)
                if element and await element.is_visible():
                    await element.click()
                    await asyncio.sleep(5)  # Wait for submission
                    return True
            except:
                continue
        
        return False
    
    async def click_next_button(self, page: Page) -> bool:
        """Find and click the Next button."""
        next_selectors = [
            "button:has-text('Next')",
            "button:has-text('Continue')",
            "input[value='Next']",
            "button[aria-label*='Next']"
        ]
        
        for selector in next_selectors:
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
        """Shutdown the form filling agent."""
        print("📝 Form Filling Agent shut down")
