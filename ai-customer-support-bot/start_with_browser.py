#!/usr/bin/env python3
"""
Start the AI Customer Support Bot and automatically open browser
"""

import os
import sys
import time
import subprocess
import webbrowser
import threading
from pathlib import Path

def check_server_ready():
    """Check if server is ready to accept connections"""
    import requests
    for attempt in range(30):  # Wait up to 30 seconds
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    return False

def open_browser_when_ready():
    """Open browser once server is ready"""
    print("🌐 Waiting for server to start...")
    if check_server_ready():
        print("🎉 Server is ready! Opening browser in fullscreen...")
        try:
            # Try to open Chrome in fullscreen mode (app mode)
            chrome_paths = [
                "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
            ]
            
            chrome_found = False
            for chrome_path in chrome_paths:
                if os.path.exists(chrome_path):
                    subprocess.Popen([
                        chrome_path,
                        "--app=http://localhost:8000",
                        "--start-fullscreen",
                        "--no-toolbar",
                        "--no-location-bar",
                        "--disable-web-security",
                        "--disable-features=VizDisplayCompositor"
                    ])
                    chrome_found = True
                    break
            
            if not chrome_found:
                # Fallback to Edge in app mode
                edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
                if os.path.exists(edge_path):
                    subprocess.Popen([
                        edge_path,
                        "--app=http://localhost:8000",
                        "--start-fullscreen"
                    ])
                else:
                    # Fallback to default browser
                    webbrowser.open("http://localhost:8000")
                    print("💡 For best experience, press F11 to go fullscreen")
                    
        except Exception as e:
            # Fallback to default browser
            webbrowser.open("http://localhost:8000")
            print("💡 For best experience, press F11 to go fullscreen")
    else:
        print("⚠️ Server took too long to start. You can manually open: http://localhost:8000")

def main():
    print("🚀 AI Customer Support Bot - Auto Startup")
    print("=" * 50)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print("\n📋 Starting server and browser...")
    
    try:
        # Start browser opening in background
        browser_thread = threading.Thread(target=open_browser_when_ready)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Start the main server
        print("🖥️ Starting FastAPI server...")
        subprocess.run([sys.executable, "start.py"])
        
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()