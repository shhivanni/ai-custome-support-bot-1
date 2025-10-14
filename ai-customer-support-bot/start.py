#!/usr/bin/env python3
"""
Quick start script for AI Customer Support Bot
This script provides an easy way to get the bot running
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'fastapi', 'uvicorn', 'sqlalchemy', 'pydantic', 
        'google.generativeai', 'python-dotenv', 'httpx', 'jinja2'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            # Handle special cases for package names
            if package == 'python-dotenv':
                __import__('dotenv')
            elif package == 'google.generativeai':
                __import__('google.generativeai')
            else:
                __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\\nTo install missing packages, run:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ .env file not found")
        print("Please create .env file with your configuration")
        print("You can copy from .env.example and update the values")
        return False
    
    # Read .env file and check for OpenAI API key
    try:
        with open(env_file, 'r') as f:
            content = f.read()
        
        if 'GEMINI_API_KEY=your_gemini_api_key_here' in content:
            print("⚠️ Please update GEMINI_API_KEY in .env file")
            return False
        
        if 'GEMINI_API_KEY=' not in content:
            print("⚠️ GEMINI_API_KEY not found in .env file")
            return False
        
        print("✅ .env file configured")
        return True
        
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False

def check_database():
    """Check if database is set up"""
    data_dir = Path("data")
    db_file = data_dir / "customer_support.db"
    
    if not data_dir.exists():
        print("⚠️ Data directory not found, will be created during setup")
        return False
    
    if not db_file.exists():
        print("⚠️ Database not found, needs initialization")
        return False
    
    print("✅ Database file exists")
    return True

def run_setup():
    """Run the setup script"""
    print("\\n🔧 Running setup script...")
    
    try:
        # Change to the correct directory
        backend_path = Path("backend")
        if backend_path.exists():
            result = subprocess.run([
                sys.executable, "backend/setup.py"
            ], capture_output=True, text=True)
        else:
            result = subprocess.run([
                sys.executable, "setup.py"
            ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Setup completed successfully")
            print(result.stdout)
            return True
        else:
            print("❌ Setup failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running setup: {e}")
        return False

def start_server():
    """Start the FastAPI server"""
    print("\\n🚀 Starting the AI Customer Support Bot server...")
    
    try:
        # Try different paths to find main.py
        main_paths = [
            Path("backend/main.py"),
            Path("main.py")
        ]
        
        main_file = None
        for path in main_paths:
            if path.exists():
                main_file = path
                break
        
        if not main_file:
            print("❌ main.py not found")
            return False
        
        print("🌐 Server will be available at: http://localhost:8000")
        print("📚 API documentation at: http://localhost:8000/docs")
        print("\\nPress Ctrl+C to stop the server\\n")
        
        # Run the server
        if str(main_file).startswith("backend"):
            subprocess.run([sys.executable, "backend/main.py"])
        else:
            subprocess.run([sys.executable, "main.py"])
        
        return True
        
    except KeyboardInterrupt:
        print("\\n\\n👋 Server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

def main():
    """Main function"""
    print("🤖 AI Customer Support Bot - Quick Start")
    print("=" * 50)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print("\\n📋 System Check:")
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check dependencies
    if not check_dependencies():
        print("\\n💡 To install dependencies, run:")
        print("pip install -r requirements.txt")
        return False
    
    # Check .env file
    env_ok = check_env_file()
    
    # Check database
    db_ok = check_database()
    
    # Run setup if needed
    if not db_ok:
        print("\\n🔧 Database setup required...")
        if not run_setup():
            return False
    
    if not env_ok:
        print("\\n⚠️ Please configure your .env file before starting:")
        print("1. Copy .env.example to .env")
        print("2. Add your Gemini API key")
        print("3. Run this script again")
        return False
    
    # Start server
    print("\\n✅ All checks passed!")
    return start_server()

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\\n\\n👋 Goodbye!")
        sys.exit(0)