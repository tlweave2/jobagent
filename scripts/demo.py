"""
Demo script to show how the AI job application system works.
This uses a test form instead of LinkedIn to demonstrate the functionality.
"""
import sys
import os
from pathlib import Path

# Add project to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from browser.playwright_driver import BrowserDriver
from models.local_llm import LocalLLM
import yaml

def demo_application():
    """Demonstrate the job application system with a test form."""
    print("🤖 AI Job Application System Demo")
    print("="*50)
    
    # Load profile
    try:
        with open("data/user_profile.yaml", 'r') as f:
            profile = yaml.safe_load(f)
        print(f"✓ Loaded profile for: {profile['full_name']}")
    except Exception as e:
        print(f"✗ Error loading profile: {e}")
        return
    
    # Initialize browser (visible for demo)
    print("✓ Starting browser...")
    browser = BrowserDriver(headless=False)
    
    try:
        # Load test form
        print("✓ Loading test form page...")
        browser.load_page("https://httpbin.org/forms/post")
        
        print("\n📸 Taking page snapshot...")
        snapshot = browser.get_page_snapshot()
        
        print(f"   Found {len(snapshot['buttons'])} buttons")
        print(f"   Found {len(snapshot['inputs'])} input fields")
        
        # Show what was detected
        print("\n🔍 Detected form elements:")
        for btn in snapshot['buttons']:
            print(f"   Button: '{btn['text'][:50]}...' (ID: {btn['id']})")
        
        for inp in snapshot['inputs']:
            print(f"   Input: '{inp['label'][:30]}...' Type: {inp['type']} (ID: {inp['id']})")
        
        # Initialize LLM
        print("\n🧠 Initializing AI...")
        try:
            llm = LocalLLM()
            print("✓ Local LLM (Ollama) connected")
            
            # Get AI analysis
            print("\n🤔 AI analyzing form...")
            result = llm.analyze(snapshot, profile)
            
            actions = result.get('actions', [])
            print(f"✓ AI suggested {len(actions)} actions:")
            
            for i, action in enumerate(actions, 1):
                print(f"   {i}. {action['action'].upper()}: {action.get('value', action.get('file', 'N/A'))}")
            
            # Ask user if they want to execute
            if actions:
                response = input(f"\n🚀 Execute these {len(actions)} actions? (y/n): ")
                if response.lower() == 'y':
                    print("\n⚡ Executing actions...")
                    result = browser.execute_actions(actions)
                    
                    for i, action_result in enumerate(result.get('results', []), 1):
                        status = action_result.get('status', 'unknown')
                        print(f"   Action {i}: {status}")
                    
                    print("\n✅ Demo completed! Check the browser to see the results.")
                else:
                    print("Demo cancelled by user.")
            else:
                print("No actions suggested by AI.")
                
        except Exception as e:
            print(f"✗ Error with LLM: {e}")
            print("💡 Make sure Ollama is running: ollama serve")
        
        input("\nPress Enter to close browser...")
        
    except Exception as e:
        print(f"✗ Error during demo: {e}")
    finally:
        browser.close()
        print("🏁 Demo finished!")

if __name__ == "__main__":
    demo_application()
