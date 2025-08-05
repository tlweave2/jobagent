"""
Test script to verify the job agent system is working with a simple test page.
"""
import sys
import os
from pathlib import Path

# Add project to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from browser.playwright_driver import BrowserDriver
from models.local_llm import LocalLLM

def test_system():
    """Test the basic functionality of the job agent system."""
    print("Testing job agent system...")
    
    # Test browser
    print("1. Testing browser driver...")
    browser = BrowserDriver(headless=False)
    
    try:
        # Load a simple test page
        browser.load_page("https://httpbin.org/forms/post")
        print("   ✓ Browser loaded test page successfully")
        
        # Get snapshot
        snapshot = browser.get_page_snapshot()
        print(f"   ✓ Page snapshot captured: {len(snapshot['buttons'])} buttons, {len(snapshot['inputs'])} inputs")
        
        # Test LLM connection
        print("2. Testing local LLM connection...")
        llm = LocalLLM()
        
        # Create simple test profile
        test_profile = {
            "full_name": "Test User",
            "email": "test@example.com",
            "phone": "555-1234"
        }
        
        # Analyze the test form
        result = llm.analyze(snapshot, test_profile)
        print(f"   ✓ LLM analysis completed: {len(result.get('actions', []))} actions suggested")
        
        print("\n✓ All systems working correctly!")
        print("\nSnapshot summary:")
        print(f"  - Page text length: {len(snapshot.get('text', ''))}")
        print(f"  - Buttons found: {[btn['text'][:30] for btn in snapshot.get('buttons', [])]}")
        print(f"  - Input fields: {len(snapshot.get('inputs', []))}")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
    finally:
        browser.close()

if __name__ == "__main__":
    test_system()
