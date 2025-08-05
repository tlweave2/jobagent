"""
Navigation Agent - Website Navigation and Session Management

This agent handles navigation across multiple job sites, maintains sessions,
and provides a consistent interface for other agents to interact with web pages.
"""

import asyncio
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright, Page, BrowserContext

class NavigationAgent:
    """Agent responsible for web navigation and session management."""
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.current_site = None
        
        print("🧭 Navigation Agent initialized")
    
    async def initialize(self):
        """Initialize browser and navigation capabilities."""
        print("🧭 Starting browser for navigation...")
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--no-first-run"
            ]
        )
        
        # Create persistent context for login sessions
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-US"
        )
        
        self.page = await self.context.new_page()
        
        print("✅ Navigation Agent ready")
    
    async def navigate_to_job(self, job_url: str) -> bool:
        """Navigate to a specific job posting."""
        print(f"🧭 Navigating to: {job_url}")
        
        try:
            # Determine which site we're dealing with
            if "linkedin.com" in job_url:
                self.current_site = "linkedin"
                return await self.navigate_to_linkedin_job(job_url)
            else:
                self.current_site = "external"
                return await self.navigate_to_external_job(job_url)
                
        except Exception as e:
            print(f"❌ Navigation error: {e}")
            return False
    
    async def navigate_to_linkedin_job(self, job_url: str) -> bool:
        """Navigate to a LinkedIn job posting."""
        try:
            # Go to job page
            await self.page.goto(job_url, timeout=30000)
            await self.page.wait_for_load_state("networkidle")
            
            # Check if we need to login
            if "login" in self.page.url:
                print("🔐 LinkedIn login required...")
                success = await self.handle_linkedin_login()
                if not success:
                    return False
                
                # Retry navigation after login
                await self.page.goto(job_url, timeout=30000)
                await self.page.wait_for_load_state("networkidle")
            
            # Verify we're on the job page
            if "jobs/view" in self.page.url:
                print("✅ Successfully navigated to LinkedIn job")
                return True
            else:
                print(f"⚠️  Unexpected page: {self.page.url}")
                return False
                
        except Exception as e:
            print(f"❌ LinkedIn navigation error: {e}")
            return False
    
    async def navigate_to_external_job(self, job_url: str) -> bool:
        """Navigate to an external job site."""
        try:
            await self.page.goto(job_url, timeout=30000)
            await self.page.wait_for_load_state("networkidle")
            
            print("✅ Successfully navigated to external job site")
            return True
            
        except Exception as e:
            print(f"❌ External site navigation error: {e}")
            return False
    
    async def handle_linkedin_login(self) -> bool:
        """Handle LinkedIn login process."""
        print("🔐 Handling LinkedIn login...")
        
        try:
            # Check if already on login page
            if "login" not in self.page.url:
                await self.page.goto("https://www.linkedin.com/login", timeout=30000)
            
            # For now, wait for manual login
            print("⚠️  Please log in manually in the browser")
            print("⏳ Waiting for login to complete...")
            
            # Wait for URL to change away from login page
            await self.page.wait_for_url(lambda url: "login" not in url, timeout=120000)
            
            # Verify login by checking for LinkedIn feed or profile
            current_url = self.page.url
            if any(indicator in current_url for indicator in ["feed", "/in/", "linkedin.com/jobs"]):
                print("✅ LinkedIn login successful")
                return True
            else:
                print("⚠️  Login status unclear, continuing...")
                return True
                
        except Exception as e:
            print(f"❌ LinkedIn login error: {e}")
            return False
    
    def get_current_page(self) -> Page:
        """Get the current page object for other agents to use."""
        return self.page
    
    async def take_screenshot(self, filename: str = None) -> str:
        """Take a screenshot of the current page."""
        if not filename:
            import time
            filename = f"screenshot_{int(time.time())}.png"
        
        try:
            await self.page.screenshot(path=filename, full_page=True)
            print(f"📸 Screenshot saved: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Screenshot error: {e}")
            return ""
    
    async def get_page_content(self) -> Dict[str, Any]:
        """Get comprehensive page content for analysis."""
        try:
            # Get basic page info
            url = self.page.url
            title = await self.page.title()
            
            # Get text content
            text_content = await self.page.inner_text("body")
            
            # Get all interactive elements
            interactive_elements = []
            
            # Find buttons
            buttons = await self.page.query_selector_all("button")
            for button in buttons:
                try:
                    text = await button.inner_text()
                    if text.strip():
                        interactive_elements.append({
                            'type': 'button',
                            'text': text.strip(),
                            'element': button
                        })
                except:
                    continue
            
            # Find input fields
            inputs = await self.page.query_selector_all("input, textarea, select")
            for input_elem in inputs:
                try:
                    input_type = await input_elem.get_attribute("type") or "text"
                    label = await self.get_input_label(input_elem)
                    interactive_elements.append({
                        'type': 'input',
                        'input_type': input_type,
                        'label': label,
                        'element': input_elem
                    })
                except:
                    continue
            
            return {
                'url': url,
                'title': title,
                'text': text_content,
                'interactive_elements': interactive_elements,
                'site': self.current_site
            }
            
        except Exception as e:
            print(f"❌ Error getting page content: {e}")
            return {'error': str(e)}
    
    async def get_input_label(self, input_element) -> str:
        """Get the label for an input element."""
        try:
            # Try to find associated label
            input_id = await input_element.get_attribute("id")
            if input_id:
                label = await self.page.query_selector(f"label[for='{input_id}']")
                if label:
                    return await label.inner_text()
            
            # Try to find nearby label
            placeholder = await input_element.get_attribute("placeholder")
            if placeholder:
                return placeholder
            
            # Try to find label in parent elements
            parent = await input_element.query_selector("xpath=..")
            if parent:
                parent_text = await parent.inner_text()
                if len(parent_text) < 100:  # Reasonable label length
                    return parent_text.strip()
            
            return "Unknown field"
            
        except:
            return "Unknown field"
    
    async def refresh_page(self):
        """Refresh the current page."""
        try:
            await self.page.reload(timeout=30000)
            await self.page.wait_for_load_state("networkidle")
            print("🔄 Page refreshed")
        except Exception as e:
            print(f"❌ Page refresh error: {e}")
    
    async def shutdown(self):
        """Shutdown the navigation agent."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        print("🧭 Navigation Agent shut down")
