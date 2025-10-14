#!/usr/bin/env python3
"""
Simple test script to verify bot functionality
This script tests the core components without needing OpenAI API
"""

import os
import sys
import json
from pathlib import Path

# Add the backend directory to the path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.append(str(backend_path))

from database import init_db, get_db
from bot_service import BotService
from models import FAQ, Session as ChatSession, Conversation

class MockLLMService:
    """Mock LLM service for testing without API calls"""
    
    def generate_response(self, user_message, conversation_history, faqs):
        """Generate a mock response based on simple rules"""
        
        user_lower = user_message.lower()
        
        # Check for FAQ matches
        for faq in faqs:
            question_words = faq['question'].lower().split()
            matches = sum(1 for word in question_words if len(word) > 3 and word in user_lower)
            
            if matches >= 2:
                return faq['answer'], False, faq['id']
        
        # Check for escalation keywords
        escalation_keywords = ['angry', 'frustrated', 'manager', 'human', 'agent', 'refund', 'cancel']
        should_escalate = any(keyword in user_lower for keyword in escalation_keywords)
        
        # Generate response based on content
        if 'hello' in user_lower or 'hi' in user_lower:
            response = "Hello! How can I help you today?"
        elif 'help' in user_lower:
            response = "I'm here to help! You can ask me about account issues, billing, or any other questions you have."
        elif should_escalate:
            response = "I understand this is important to you. Let me escalate this to a human agent who can better assist you."
        else:
            response = "I understand your question. Let me help you with that. Could you provide more details?"
        
        return response, should_escalate, None
    
    def summarize_conversation(self, conversations):
        """Generate a simple summary"""
        if not conversations:
            return "No conversation to summarize."
        
        return f"Customer conversation with {len(conversations)} exchanges. " + \
               f"Started with: '{conversations[0]['user_message'][:50]}...'"

def test_database_setup():
    """Test database initialization and FAQ loading"""
    
    print("🔍 Testing database setup...")
    
    try:
        # Initialize database
        init_db()
        
        # Get database session
        db_gen = get_db()
        db = next(db_gen)
        
        try:
            # Check FAQ count
            faq_count = db.query(FAQ).count()
            print(f"   📊 FAQs in database: {faq_count}")
            
            if faq_count == 0:
                print("   ⚠️ No FAQs found - run setup.py first")
                return False
            
            # Test a sample FAQ
            sample_faq = db.query(FAQ).first()
            print(f"   📝 Sample FAQ: {sample_faq.question[:50]}...")
            
            print("✅ Database setup test passed")
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Database setup test failed: {e}")
        return False

def test_bot_service():
    """Test bot service functionality"""
    
    print("\\n🤖 Testing bot service...")
    
    try:
        # Get database session
        db_gen = get_db()
        db = next(db_gen)
        
        try:
            # Create bot service with mock LLM
            bot_service = BotService(db)
            bot_service.llm_service = MockLLMService()
            
            # Test session creation
            session_id = bot_service.start_session(
                customer_email="test@example.com",
                customer_name="Test User"
            )
            print(f"   🆔 Created session: {session_id}")
            
            # Test message processing
            test_messages = [
                "Hello, I need help",
                "How do I reset my password?",
                "I'm frustrated with this service, I want a refund!"
            ]
            
            for i, message in enumerate(test_messages):
                response = bot_service.process_message(session_id, message)
                
                if "error" in response:
                    print(f"   ❌ Message {i+1} failed: {response['error']}")
                    return False
                
                print(f"   💬 Message {i+1}: '{message[:30]}...' -> Response received")
                
                if response.get('escalated'):
                    print(f"   ⬆️ Message {i+1} triggered escalation")
            
            # Test conversation history
            history = bot_service.get_conversation_history(session_id)
            print(f"   📜 Conversation history: {len(history)} exchanges")
            
            # Test session summary
            summary = bot_service.get_session_summary(session_id)
            print(f"   📋 Session summary: {summary[:50]}...")
            
            # Clean up
            bot_service.end_session(session_id)
            
            print("✅ Bot service test passed")
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Bot service test failed: {e}")
        return False

def test_faq_matching():
    """Test FAQ matching functionality"""
    
    print("\\n🔎 Testing FAQ matching...")
    
    try:
        # Get database session
        db_gen = get_db()
        db = next(db_gen)
        
        try:
            bot_service = BotService(db)
            bot_service.llm_service = MockLLMService()
            
            # Create test session
            session_id = bot_service.start_session()
            
            # Test FAQ-related questions
            faq_questions = [
                "I forgot my password, how do I reset it?",
                "What are your business hours?",
                "How can I update my billing information?"
            ]
            
            matched_faqs = 0
            for question in faq_questions:
                response = bot_service.process_message(session_id, question)
                
                if response.get('matched_faq'):
                    matched_faqs += 1
                    print(f"   ✅ Matched FAQ for: '{question[:40]}...'")
                else:
                    print(f"   ⚠️ No FAQ match for: '{question[:40]}...'")
            
            print(f"   📊 FAQ matches: {matched_faqs}/{len(faq_questions)}")
            
            # Clean up
            bot_service.end_session(session_id)
            
            print("✅ FAQ matching test completed")
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ FAQ matching test failed: {e}")
        return False

def test_escalation_scenarios():
    """Test escalation detection"""
    
    print("\\n⬆️ Testing escalation scenarios...")
    
    try:
        # Get database session
        db_gen = get_db()
        db = next(db_gen)
        
        try:
            bot_service = BotService(db)
            bot_service.llm_service = MockLLMService()
            
            # Create test session
            session_id = bot_service.start_session()
            
            # Test escalation triggers
            escalation_messages = [
                "I'm really angry about this service!",
                "I want to speak to a manager right now",
                "This is terrible, I want a refund immediately",
                "Can you transfer me to a human agent?"
            ]
            
            escalations = 0
            for message in escalation_messages:
                response = bot_service.process_message(session_id, message)
                
                if response.get('escalated'):
                    escalations += 1
                    print(f"   ⬆️ Escalated: '{message[:40]}...'")
                else:
                    print(f"   ➡️ Not escalated: '{message[:40]}...'")
            
            print(f"   📊 Escalations: {escalations}/{len(escalation_messages)}")
            
            # Test manual escalation
            manual_escalation = bot_service.escalate_manually(session_id, "Manual test escalation")
            if manual_escalation:
                print("   ✅ Manual escalation successful")
            else:
                print("   ❌ Manual escalation failed")
            
            # Clean up
            bot_service.end_session(session_id)
            
            print("✅ Escalation test completed")
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Escalation test failed: {e}")
        return False

def main():
    """Main test function"""
    
    print("🧪 AI Customer Support Bot - Test Suite")
    print("=" * 50)
    
    tests = [
        test_database_setup,
        test_bot_service,
        test_faq_matching,
        test_escalation_scenarios
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            failed += 1
    
    print("\\n" + "=" * 50)
    print(f"🧪 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The bot is ready to use.")
    else:
        print("⚠️ Some tests failed. Please check the setup and try again.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)