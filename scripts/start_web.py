#!/usr/bin/env python3
"""
AutoApply AI - Web Interface Launcher

This script starts the web server and opens the browser interface.
"""

import asyncio
import webbrowser
import os
import sys
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import aiohttp
        import aiohttp_cors
        print("✅ Web server dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("🔧 Installing required packages...")
        os.system("pip install aiohttp aiohttp-cors websockets")
        return True

async def start_web_server():
    """Start the web server."""
    try:
        from web_interface.web_server import AutoApplyWebServer
        
        print("🤖 AutoApply AI - Web Interface")
        print("=" * 50)
        
        server = AutoApplyWebServer(host='localhost', port=8000)
        
        # Open browser after a short delay
        def open_browser():
            print("🌐 Opening web browser...")
            webbrowser.open('http://localhost:8000')
        
        # Schedule browser opening after 2 seconds
        asyncio.get_event_loop().call_later(2, open_browser)
        
        # Start the server
        await server.start_server()
        
    except ImportError as e:
        print(f"❌ Failed to import web server: {e}")
        print("🔄 Falling back to command line interface...")
        
        # Fall back to the original orchestrator
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from orchestrator import main
        await main()
    except Exception as e:
        print(f"❌ Error starting web server: {e}")
        print("🔄 Falling back to command line interface...")
        
        # Fall back to the original orchestrator
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from orchestrator import main
        await main()

def main():
    """Main entry point."""
    print("🚀 Starting AutoApply AI...")
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Cannot start due to missing dependencies")
        return
    
    try:
        # Start the web server
        asyncio.run(start_web_server())
    except KeyboardInterrupt:
        print("\n👋 AutoApply AI stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
