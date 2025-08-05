#!/usr/bin/env python3
"""
AutoApply AI - Direct Web Interface Launcher

Directly starts the web interface without any prompts.
"""

import asyncio
import webbrowser
import sys
import os

async def main():
    """Start the web interface directly."""
    print("🤖 AutoApply AI - Starting Web Interface")
    print("=" * 50)
    
    try:
        # Add the current directory to the path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from web_interface.web_server import AutoApplyWebServer
        
        server = AutoApplyWebServer(host='localhost', port=8000)
        
        # Open browser after a short delay
        def open_browser():
            print("🌐 Opening web browser at http://localhost:8000")
            webbrowser.open('http://localhost:8000')
        
        # Schedule browser opening after 2 seconds
        asyncio.get_event_loop().call_later(2, open_browser)
        
        # Start the server
        await server.start_server()
        
    except ImportError as e:
        print(f"❌ Failed to import web server: {e}")
        print("💡 Try running: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting web interface: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 AutoApply AI stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
