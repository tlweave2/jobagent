#!/usr/bin/env python3
"""
AutoApply AI - Development Setup Script

Sets up the development environment for AutoApply AI.
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔧 {description}...")
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        return False

def main():
    """Set up the development environment."""
    print("🚀 AutoApply AI Development Setup")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    print(f"✅ Python {sys.version} detected")
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        return False
    
    # Install Playwright browsers
    if not run_command("playwright install chromium", "Installing Playwright browser"):
        return False
    
    # Create .env file if it doesn't exist
    if not Path(".env").exists():
        if Path(".env.example").exists():
            run_command("cp .env.example .env", "Creating .env file")
            print("⚠️  Please edit .env file with your API keys and configuration")
        else:
            print("⚠️  No .env.example found. Please create .env file manually")
    
    # Create necessary directories
    dirs_to_create = ["logs", "database", "resumes", "coverletters"]
    for dir_name in dirs_to_create:
        Path(dir_name).mkdir(exist_ok=True)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your API keys")
    print("2. Edit data/user_profile.yaml with your information")
    print("3. Add your resume to resumes/ directory")
    print("4. Run: python run.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
