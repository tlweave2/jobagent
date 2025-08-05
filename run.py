#!/usr/bin/env python3
"""
AutoApply AI - Quick Launcher

Simple launcher script for AutoApply AI.
"""

import subprocess
import sys
import os

def main():
    """Launch AutoApply AI."""
    print("🤖 AutoApply AI Launcher")
    print("=" * 30)
    print("🌐 Starting web interface by default...")
    print()
    print("Options:")
    print("1. 🌐 Continue with Web Interface")
    print("2. 💻 Switch to Command Line Interface") 
    print("3. ❌ Exit")
    
    # Auto-select web interface after 3 seconds if no input
    import time
    import select
    import sys
    
    print("\nStarting web interface in 3 seconds (press any key to see options)...")
    
    # Check if input is available (Linux/Mac)
    if hasattr(select, 'select'):
        ready, _, _ = select.select([sys.stdin], [], [], 3)
        if ready:
            input()  # consume the input
        else:
            choice = "1"  # auto-select web interface
    else:
        # Windows fallback - just wait for input
        try:
            choice = input("Select an option (1-3) or wait 3 seconds for web interface: ").strip()
        except KeyboardInterrupt:
            choice = "1"
    
    if not choice:
        choice = "1"
    
    if choice == "1":
        print("🚀 Starting web interface...")
        try:
            subprocess.run([sys.executable, "scripts/start_web.py"], check=True)
        except KeyboardInterrupt:
            print("\n👋 Web interface stopped")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    elif choice == "2":
        print("🚀 Starting command line interface...")
        try:
            subprocess.run([sys.executable, "orchestrator.py"], check=True)
        except KeyboardInterrupt:
            print("\n👋 Command line interface stopped")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    elif choice == "3":
        print("👋 Goodbye!")
    
    else:
        print("🌐 Starting web interface (default)...")
        try:
            subprocess.run([sys.executable, "scripts/start_web.py"], check=True)
        except KeyboardInterrupt:
            print("\n👋 Web interface stopped")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
