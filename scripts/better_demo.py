"""
Better demo script with a real form that has input fields to demonstrate form filling.
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
import time

def demo_with_real_form():
    """Demonstrate the job application system with a real form with inputs."""
    print("🤖 AI Job Application System - Form Filling Demo")
    print("="*60)
    
    # Load profile
    try:
        with open("data/user_profile.yaml", 'r') as f:
            profile = yaml.safe_load(f)
        print(f"✓ Loaded profile for: {profile['full_name']}")
        print(f"  Email: {profile['email']}")
        print(f"  Phone: {profile['phone']}")
    except Exception as e:
        print(f"✗ Error loading profile: {e}")
        return
    
    # Initialize browser (visible for demo)
    print("✓ Starting browser...")
    browser = BrowserDriver(headless=False)
    
    try:
        # Create a simple HTML form for testing
        form_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Job Application Form - Demo</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
                .form-group { margin-bottom: 15px; }
                label { display: block; margin-bottom: 5px; font-weight: bold; }
                input, textarea, select { width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
                button { background-color: #0066cc; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
                button:hover { background-color: #0052a3; }
            </style>
        </head>
        <body>
            <h1>🎯 Job Application Form</h1>
            <form action="#" method="post">
                <div class="form-group">
                    <label for="firstName">First Name:</label>
                    <input type="text" id="firstName" name="firstName" required>
                </div>
                
                <div class="form-group">
                    <label for="lastName">Last Name:</label>
                    <input type="text" id="lastName" name="lastName" required>
                </div>
                
                <div class="form-group">
                    <label for="email">Email Address:</label>
                    <input type="email" id="email" name="email" required>
                </div>
                
                <div class="form-group">
                    <label for="phone">Phone Number:</label>
                    <input type="tel" id="phone" name="phone" required>
                </div>
                
                <div class="form-group">
                    <label for="location">Location:</label>
                    <input type="text" id="location" name="location" placeholder="City, State">
                </div>
                
                <div class="form-group">
                    <label for="experience">Years of Experience:</label>
                    <select id="experience" name="experience">
                        <option value="">Select...</option>
                        <option value="0-1">0-1 years</option>
                        <option value="2-3">2-3 years</option>
                        <option value="4-5">4-5 years</option>
                        <option value="6+">6+ years</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="resume">Upload Resume:</label>
                    <input type="file" id="resume" name="resume" accept=".pdf,.doc,.docx">
                </div>
                
                <div class="form-group">
                    <label for="coverLetter">Cover Letter:</label>
                    <textarea id="coverLetter" name="coverLetter" rows="4" placeholder="Tell us why you're interested in this position..."></textarea>
                </div>
                
                <div class="form-group">
                    <button type="submit">Submit Application</button>
                    <button type="button" style="margin-left: 10px; background-color: #666;">Save Draft</button>
                </div>
            </form>
        </body>
        </html>
        """
        
        # Save the HTML to a temporary file
        temp_file = "/tmp/demo_form.html"
        with open(temp_file, 'w') as f:
            f.write(form_html)
        
        # Load the test form
        print("✓ Loading demo job application form...")
        browser.load_page(f"file://{temp_file}")
        time.sleep(2)
        
        print("\n📸 Taking page snapshot...")
        snapshot = browser.get_page_snapshot()
        
        print(f"   Found {len(snapshot['buttons'])} buttons")
        print(f"   Found {len(snapshot['inputs'])} input fields")
        
        # Show what was detected
        print("\n🔍 Detected form elements:")
        for btn in snapshot['buttons']:
            print(f"   Button: '{btn['text'][:50]}' (ID: {btn['id']})")
        
        for inp in snapshot['inputs']:
            label = inp['label'][:40] + "..." if len(inp['label']) > 40 else inp['label']
            print(f"   Input: '{label}' Type: {inp['type']} (ID: {inp['id']})")
        
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
                if action['action'] == 'fill':
                    print(f"   {i}. FILL: '{action.get('value', 'N/A')}'")
                elif action['action'] == 'upload':
                    print(f"   {i}. UPLOAD: {action.get('file', 'N/A')}")
                else:
                    print(f"   {i}. {action['action'].upper()}: {action.get('value', action.get('file', 'N/A'))}")
            
            # Ask user if they want to execute
            if actions:
                print(f"\n🎯 This will demonstrate how the AI fills out job application forms!")
                response = input(f"🚀 Execute these {len(actions)} form-filling actions? (y/n): ")
                if response.lower() == 'y':
                    print("\n⚡ Executing AI-generated actions...")
                    result = browser.execute_actions(actions)
                    
                    success_count = 0
                    for i, action_result in enumerate(result.get('results', []), 1):
                        status = action_result.get('status', 'unknown')
                        if status == 'success':
                            success_count += 1
                        print(f"   Action {i}: {status}")
                    
                    print(f"\n✅ Demo completed! {success_count}/{len(actions)} actions successful.")
                    print("🎉 Check the browser to see how AI filled out the form!")
                    print("\n💡 This same process works for LinkedIn Easy Apply forms!")
                else:
                    print("Demo cancelled by user.")
            else:
                print("❌ No actions suggested by AI - this might indicate an issue.")
                
        except Exception as e:
            print(f"✗ Error with LLM: {e}")
            print("💡 Make sure Ollama is running: ollama serve")
        
        input("\nPress Enter to close browser and finish demo...")
        
    except Exception as e:
        print(f"✗ Error during demo: {e}")
    finally:
        browser.close()
        print("🏁 Demo finished!")
        # Clean up temp file
        try:
            os.remove("/tmp/demo_form.html")
        except:
            pass

if __name__ == "__main__":
    demo_with_real_form()
