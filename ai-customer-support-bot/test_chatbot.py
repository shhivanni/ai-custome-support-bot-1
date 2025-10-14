#!/usr/bin/env python3
"""
Simple test script to validate AI Customer Support Bot functionality
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    from llm_service import LLMService
    from database import init_db, SessionLocal
    from bot_service import BotService
    from dotenv import load_dotenv
    
    load_dotenv()

    def test_llm_service():
        """Test the LLM service directly"""
        print("🧪 Testing LLM Service...")
        try:
            llm = LLMService()
            response, should_escalate, faq_id = llm.generate_response(
                "Hello, I need help with my account password", [], []
            )
            print(f"✅ LLM Response: {response[:100]}...")
            print(f"   Escalate: {should_escalate}")
            return True
        except Exception as e:
            print(f"❌ LLM Service failed: {e}")
            return False

    def test_bot_service():
        """Test the bot service with database"""
        print("\n🤖 Testing Bot Service...")
        try:
            # Initialize database
            init_db()
            db = SessionLocal()
            
            try:
                # Create bot service
                bot = BotService(db)
                
                # Start a session
                session_id = bot.start_session("test@example.com", "Test User")
                print(f"✅ Session started: {session_id}")
                
                # Send a test message
                result = bot.process_message(session_id, "Hi, I need help with billing")
                
                if "bot_response" in result:
                    print(f"✅ Bot Response: {result['bot_response'][:100]}...")
                    print(f"   Escalated: {result.get('escalated', False)}")
                    return True
                else:
                    print(f"❌ Bot Service failed: {result}")
                    return False
                    
            finally:
                db.close()
                
        except Exception as e:
            print(f"❌ Bot Service failed: {e}")
            return False

    def main():
        """Main test function"""
        print("🚀 AI Customer Support Bot - Functionality Test")
        print("=" * 50)
        
        # Check environment variables
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ GEMINI_API_KEY not found in environment")
            return False
        elif api_key == "your_gemini_api_key_here":
            print("❌ Please update GEMINI_API_KEY in .env file")
            return False
        else:
            print("✅ API key configured")
        
        # Test LLM service
        if not test_llm_service():
            return False
        
        # Test bot service
        if not test_bot_service():
            return False
        
        print("\n🎉 All tests passed! Your chatbot is working correctly.")
        print("\n📋 Next steps:")
        print("1. Run 'python start.py' to start the web server")
        print("2. Open http://localhost:8000 in your browser")
        print("3. Or use the API at http://localhost:8000/docs")
        
        return True

    if __name__ == "__main__":
        try:
            success = main()
            sys.exit(0 if success else 1)
        except KeyboardInterrupt:
            print("\n\n👋 Test interrupted by user")
            sys.exit(0)

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're in the correct directory and all dependencies are installed")
    sys.exit(1)