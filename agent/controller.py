"""
Controller for applying to a single job using LinkedIn Easy Apply.

This module defines the main loop that coordinates the browser, local LLM
and optional cloud LLM. It loads the job URL, triggers Easy Apply,
iterates through form steps and handles recovery when necessary. The
implementation is left as an exercise; the functions below define the
expected interface.
"""
from __future__ import annotations

import time
import yaml
import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# These imports refer to other modules in this repository. They currently
# do not implement any logic but serve as placeholders for your own
# implementations.
from browser.playwright_driver import BrowserDriver
from models.local_llm import LocalLLM
from models.cloud_llm import CloudLLM


def load_profile(profile_path: str) -> Dict[str, Any]:
    """Load user profile from YAML file."""
    try:
        with open(profile_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading profile from {profile_path}: {e}")
        return {}


def apply_to_job(job_url: str, profile_path: str = "data/user_profile.yaml", use_cloud: bool = True) -> None:
    """Entry point for applying to a single job.

    Args:
        job_url: URL of the job posting to apply to.
        profile_path: Path to YAML file containing user profile.
        use_cloud: Whether to allow the fallback cloud model when the UI
            appears to be stuck. If False only the local model is used.

    The typical flow implemented by this function should be:

    1. Instantiate a ``BrowserDriver`` and load the job URL.
    2. Locate and click the Easy Apply button.
    3. Enter a loop that:
        a. Takes a snapshot of the current form step (buttons and inputs).
        b. Invokes ``LocalLLM.analyze`` with the snapshot and user profile.
        c. Executes the returned actions via ``BrowserDriver``.
        d. Breaks if ``is_final_step`` is True.
        e. Monitors for UI stalls and optionally invokes the cloud model via
           ``CloudLLM.analyze`` to recover.
    4. Logs the result (success or failure).

    The actual logic for loading the profile, building prompts, and
    interacting with the DOM is up to you. This scaffold exists so you
    can begin filling in the details.
    """
    print(f"Starting job application for: {job_url}")
    
    # Load user profile
    profile = load_profile(profile_path)
    if not profile:
        print("Error: Could not load user profile")
        return
    
    # Initialize components
    headless = os.getenv("HEADLESS_MODE", "false").lower() == "true"
    browser = BrowserDriver(headless=headless)
    
    try:
        # Initialize LLMs
        ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5vl:7b")
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        local_llm = LocalLLM(model_name=ollama_model, host=ollama_host)
        
        cloud_llm = None
        if use_cloud:
            try:
                cloud_llm = CloudLLM()
                print("Cloud LLM (Anthropic) initialized")
            except Exception as e:
                print(f"Could not initialize cloud LLM: {e}")
        
        # Step 1: Load the job URL
        print("Loading job page...")
        browser.load_page(job_url)
        
        # Step 2: Look for and click Easy Apply button
        print("Looking for Easy Apply button...")
        easy_apply_selector = browser.find_easy_apply_button()
        if not easy_apply_selector:
            print("Easy Apply button not found. This might not be an Easy Apply job.")
            return
        
        # Click Easy Apply
        print("Clicking Easy Apply button...")
        try:
            browser.page.click(easy_apply_selector)
            time.sleep(3)  # Wait for form to load
        except Exception as e:
            print(f"Error clicking Easy Apply button: {e}")
            return
        
        # Step 3: Main application loop
        max_steps = 10  # Prevent infinite loops
        step_count = 0
        stall_count = 0
        last_snapshot_hash = None
        
        print("Starting application form process...")
        
        while step_count < max_steps:
            step_count += 1
            print(f"\n--- Step {step_count} ---")
            
            # Take snapshot of current page
            try:
                snapshot = browser.get_page_snapshot()
            except Exception as e:
                print(f"Error getting page snapshot: {e}")
                break
            
            # Check if page hasn't changed (stalled)
            current_hash = hash(str(snapshot.get("text", "")))
            if current_hash == last_snapshot_hash:
                stall_count += 1
                print(f"Page appears unchanged (stall count: {stall_count})")
                
                if stall_count >= 3:
                    print("Page appears to be stalled, attempting recovery...")
                    if cloud_llm:
                        print("Using cloud LLM for recovery...")
                        result = cloud_llm.analyze(snapshot, profile, mode="recovery")
                    else:
                        print("No cloud LLM available for recovery")
                        break
                else:
                    # Wait and try again
                    time.sleep(2)
                    continue
            else:
                stall_count = 0
                last_snapshot_hash = current_hash
            
            # Analyze current state with local LLM
            print("Analyzing page with local LLM...")
            result = local_llm.analyze(snapshot, profile)
            
            actions = result.get("actions", [])
            is_final = result.get("is_final_step", False)
            
            print(f"LLM suggested {len(actions)} actions, final step: {is_final}")
            
            # Execute actions
            if actions:
                print("Executing actions...")
                execution_result = browser.execute_actions(actions)
                print(f"Execution result: {execution_result.get('status', 'unknown')}")
                
                # Wait between actions
                time.sleep(2)
            else:
                print("No actions suggested")
                
                # If no actions and we've tried multiple times, we might be done
                if step_count > 3:
                    # Check if we're on a success page
                    page_text = snapshot.get("text", "").lower()
                    if any(keyword in page_text for keyword in [
                        "application submitted", "thank you", "success", 
                        "we have received", "application complete"
                    ]):
                        print("Application appears to be successful!")
                        is_final = True
                    else:
                        print("No actions available and no success indicators found")
                        break
            
            # Check if this is the final step
            if is_final:
                print("Application process completed!")
                break
                
            # Add delay between form steps
            time.sleep(int(os.getenv("MIN_DELAY_BETWEEN_APPS", "2")))
        
        if step_count >= max_steps:
            print("Reached maximum number of steps - process may not have completed")
        
        print("Job application process finished")
        
    except Exception as e:
        print(f"Error during job application: {e}")
        raise
    finally:
        # Clean up browser
        print("Closing browser...")
        browser.close()