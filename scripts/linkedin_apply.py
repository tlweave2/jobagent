"""
LinkedIn job application script with login handling.
"""
import sys
import os
import time
from pathlib import Path

# Add project to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from browser.playwright_driver import BrowserDriver
from models.local_llm import LocalLLM
from models.cloud_llm import CloudLLM
import yaml
from dotenv import load_dotenv

load_dotenv()

def load_profile(profile_path: str):
    """Load user profile from YAML file."""
    try:
        with open(profile_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading profile: {e}")
        return {}

def linkedin_login(browser: BrowserDriver):
    """Handle LinkedIn login process."""
    print("Logging into LinkedIn...")
    
    # Go to LinkedIn login
    browser.load_page("https://www.linkedin.com/login")
    time.sleep(2)
    
    # Enter credentials
    email = os.getenv("LINKEDIN_EMAIL")
    password = os.getenv("LINKEDIN_PASSWORD")
    
    if not email or not password:
        print("LinkedIn credentials not found in .env file")
        return False
    
    try:
        # Find and fill email
        email_input = browser.page.query_selector("input[name='session_key']")
        if email_input:
            email_input.fill(email)
            time.sleep(1)
        
        # Find and fill password
        password_input = browser.page.query_selector("input[name='session_password']")
        if password_input:
            password_input.fill(password)
            time.sleep(1)
        
        # Click login button
        login_button = browser.page.query_selector("button[type='submit']")
        if login_button:
            login_button.click()
            time.sleep(5)  # Wait for login to complete
            
            # Check if we're logged in by looking for the feed or profile
            current_url = browser.page.url
            if "feed" in current_url or "in/" in current_url:
                print("✓ Successfully logged into LinkedIn")
                return True
            else:
                print("Login may have failed or requires additional verification")
                return False
    
    except Exception as e:
        print(f"Error during login: {e}")
        return False
    
    return False

def apply_with_login(job_url: str, profile_path: str = "data/user_profile.yaml"):
    """Apply to job with LinkedIn login."""
    print(f"Starting LinkedIn job application with login for: {job_url}")
    
    # Load profile
    profile = load_profile(profile_path)
    if not profile:
        print("Could not load profile")
        return
    
    # Initialize browser (non-headless for debugging)
    browser = BrowserDriver(headless=False)
    
    try:
        # Login to LinkedIn first
        if not linkedin_login(browser):
            print("Failed to login to LinkedIn")
            return
        
        # Navigate to job
        print(f"Navigating to job: {job_url}")
        browser.load_page(job_url)
        time.sleep(3)
        
        # Look for Easy Apply button
        print("Looking for Easy Apply button...")
        easy_apply_selectors = [
            "button:has-text('Easy Apply')",
            ".jobs-s-apply button",
            ".jobs-apply-button",
            "[aria-label*='Easy Apply']",
            "button:has-text('Apply')"
        ]
        
        easy_apply_found = False
        for selector in easy_apply_selectors:
            try:
                element = browser.page.query_selector(selector)
                if element and element.is_visible():
                    print(f"Found Easy Apply button with selector: {selector}")
                    element.click()
                    time.sleep(3)
                    easy_apply_found = True
                    break
            except:
                continue
        
        if not easy_apply_found:
            print("Easy Apply button not found. Checking page content...")
            page_text = browser.page.inner_text("body")
            print(f"Page contains 'Easy Apply': {'Easy Apply' in page_text}")
            print(f"Page contains 'Apply': {'Apply' in page_text}")
            
            # Save screenshot for debugging
            screenshot_path = "debug_screenshot.png"
            browser.page.screenshot(path=screenshot_path)
            print(f"Screenshot saved to {screenshot_path}")
            return
        
        # Initialize LLMs
        local_llm = LocalLLM()
        cloud_llm = None
        try:
            cloud_llm = CloudLLM()
        except:
            print("Cloud LLM not available")
        
        # Application loop
        max_steps = 5
        for step in range(max_steps):
            print(f"\n--- Application Step {step + 1} ---")
            
            # Get page snapshot
            snapshot = browser.get_page_snapshot()
            
            # Check for completion indicators
            page_text = snapshot.get("text", "").lower()
            if any(keyword in page_text for keyword in [
                "application submitted", "thank you", "success",
                "we have received", "application complete"
            ]):
                print("✓ Application appears to be completed!")
                break
            
            # Analyze with LLM
            result = local_llm.analyze(snapshot, profile)
            actions = result.get("actions", [])
            
            print(f"LLM suggested {len(actions)} actions")
            
            if actions:
                # Execute actions
                browser.execute_actions(actions)
                time.sleep(2)
            else:
                print("No actions suggested")
                if step > 2:  # Give it a few tries
                    break
        
        print("Application process completed")
        
        # Keep browser open for a moment to see results
        input("Press Enter to close browser...")
        
    except Exception as e:
        print(f"Error during application: {e}")
        # Save screenshot for debugging
        try:
            browser.page.screenshot(path="error_screenshot.png")
            print("Error screenshot saved to error_screenshot.png")
        except:
            pass
    finally:
        browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python linkedin_apply.py <job_url>")
        print("Example: python linkedin_apply.py 'https://www.linkedin.com/jobs/view/4277963662/'")
        sys.exit(1)
    
    job_url = sys.argv[1]
    apply_with_login(job_url)
