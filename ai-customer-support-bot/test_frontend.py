#!/usr/bin/env python3
"""
Quick test to verify frontend is being served correctly
"""

import requests
import time
import subprocess
import sys
from pathlib import Path

def test_frontend_serving():
    """Test if the frontend is being served at localhost:8000"""
    try:
        print("🧪 Testing frontend serving...")
        
        # Test the main page
        response = requests.get("http://localhost:8000", timeout=5)
        if response.status_code == 200:
            if "AI Customer Support" in response.text and "script src" in response.text:
                print("✅ Frontend HTML is being served correctly")
                
                # Test static files
                css_response = requests.get("http://localhost:8000/static/style.css", timeout=5)
                if css_response.status_code == 200:
                    print("✅ CSS file is accessible")
                else:
                    print("⚠️ CSS file not accessible")
                
                js_response = requests.get("http://localhost:8000/static/script.js", timeout=5)
                if js_response.status_code == 200:
                    print("✅ JavaScript file is accessible")
                else:
                    print("⚠️ JavaScript file not accessible")
                
                return True
            else:
                print("❌ Frontend content not found in response")
                return False
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server at localhost:8000")
        print("   Make sure the server is running with: python start.py")
        return False
    except Exception as e:
        print(f"❌ Error testing frontend: {e}")
        return False

def main():
    print("🚀 AI Customer Support Bot - Frontend Test")
    print("=" * 50)
    
    if test_frontend_serving():
        print("\n🎉 Frontend is working correctly!")
        print("\n📋 How to use:")
        print("1. Start the server: python start.py")
        print("2. Open your browser and go to: http://localhost:8000")
        print("3. You should see the chat interface")
        return True
    else:
        print("\n❌ Frontend test failed")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure the server is running: python start.py")
        print("2. Check that frontend files exist in the frontend/ directory")
        print("3. Verify the server logs for any errors")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)