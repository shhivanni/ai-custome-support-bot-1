#!/usr/bin/env python3
"""
Demo script to test the AI Customer Support Bot
This script demonstrates the core functionality including:
- Starting a chat session
- Sending messages and getting responses
- Testing FAQ matching
- Testing escalation scenarios
- Getting conversation summary
"""

import requests
import json
import time
from typing import Dict, Any

class BotTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id = None
        self.session = requests.Session()
    
    def start_session(self, name: str = "Demo User", email: str = "demo@example.com") -> bool:
        """Start a new chat session"""
        print(f"🚀 Starting new session for {name}...")
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/sessions/start",
                json={
                    "customer_name": name,
                    "customer_email": email
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.session_id = data["session_id"]
                print(f"✅ Session started: {self.session_id[:8]}...")
                return True
            else:
                print(f"❌ Failed to start session: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting session: {e}")
            return False
    
    def send_message(self, message: str) -> Dict[str, Any]:
        """Send a message and get bot response"""
        if not self.session_id:
            raise ValueError("No active session. Call start_session() first.")
        
        print(f"\n👤 User: {message}")
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/chat",
                json={
                    "session_id": self.session_id,
                    "message": message
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                bot_response = data.get("bot_response", "")
                escalated = data.get("escalated", False)
                matched_faq = data.get("matched_faq")
                
                print(f"🤖 Bot: {bot_response}")
                
                if escalated:
                    print("🚨 Session has been escalated to human agent!")
                
                if matched_faq:
                    print(f"📚 Matched FAQ: {matched_faq}")
                
                return data
            else:
                print(f"❌ Failed to send message: {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return {"error": str(e)}
    
    def get_conversation_history(self) -> list:
        """Get the conversation history"""
        if not self.session_id:
            raise ValueError("No active session")
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/sessions/{self.session_id}/history"
            )
            
            if response.status_code == 200:
                return response.json().get("history", [])
            else:
                print(f"❌ Failed to get history: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting history: {e}")
            return []
    
    def get_session_summary(self) -> str:
        """Get AI-generated session summary"""
        if not self.session_id:
            raise ValueError("No active session")
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/sessions/{self.session_id}/summary"
            )
            
            if response.status_code == 200:
                return response.json().get("summary", "")
            else:
                print(f"❌ Failed to get summary: {response.text}")
                return ""
                
        except Exception as e:
            print(f"❌ Error getting summary: {e}")
            return ""
    
    def end_session(self) -> bool:
        """End the chat session"""
        if not self.session_id:
            return True
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/sessions/{self.session_id}/end"
            )
            
            if response.status_code == 200:
                print("✅ Session ended successfully")
                return True
            else:
                print(f"❌ Failed to end session: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error ending session: {e}")
            return False

def run_faq_test(tester: BotTester):
    """Test FAQ matching functionality"""
    print("\n" + "="*50)
    print("📚 Testing FAQ Matching")
    print("="*50)
    
    faq_questions = [
        "How do I reset my password?",
        "What are your business hours?",
        "How can I update my billing information?",
        "How do I delete my account?",
        "What is your refund policy?"
    ]
    
    for question in faq_questions:
        response = tester.send_message(question)
        time.sleep(1)  # Be nice to the API

def run_escalation_test(tester: BotTester):
    """Test escalation scenarios"""
    print("\n" + "="*50)
    print("🚨 Testing Escalation Scenarios")
    print("="*50)
    
    escalation_messages = [
        "I want to speak to a manager",
        "This service is terrible, I demand a refund!",
        "I need to speak with a human agent",
        "Your bot is useless, get me a real person"
    ]
    
    for message in escalation_messages:
        response = tester.send_message(message)
        if response.get("escalated"):
            print("✅ Escalation detected correctly!")
            break
        time.sleep(1)

def run_conversation_test(tester: BotTester):
    """Test conversational flow"""
    print("\n" + "="*50)
    print("💬 Testing Conversation Flow")
    print("="*50)
    
    conversation = [
        "Hi, I'm having trouble logging into my account",
        "I tried resetting my password but didn't receive the email",
        "Yes, I checked my spam folder",
        "My email is demo@example.com",
        "Thank you for your help!"
    ]
    
    for message in conversation:
        response = tester.send_message(message)
        time.sleep(1)

def main():
    """Main demo function"""
    print("🤖 AI Customer Support Bot - Demo Test")
    print("=" * 60)
    
    # Initialize tester
    tester = BotTester()
    
    # Check if server is running
    try:
        response = requests.get(f"{tester.base_url}/health")
        if response.status_code != 200:
            print("❌ Bot server is not running!")
            print("Please start the server with: python backend/main.py")
            return
        print("✅ Bot server is running")
    except Exception as e:
        print(f"❌ Cannot connect to bot server: {e}")
        print("Please start the server with: python backend/main.py")
        return
    
    # Start session
    if not tester.start_session("Demo User", "demo@example.com"):
        return
    
    # Run different test scenarios
    try:
        # Basic conversation test
        run_conversation_test(tester)
        
        # FAQ matching test
        run_faq_test(tester)
        
        # Escalation test
        run_escalation_test(tester)
        
        # Get conversation history
        print("\n" + "="*50)
        print("📋 Conversation History")
        print("="*50)
        
        history = tester.get_conversation_history()
        print(f"Total exchanges: {len(history)}")
        
        # Get session summary
        print("\n" + "="*50)
        print("📊 Session Summary")
        print("="*50)
        
        summary = tester.get_session_summary()
        if summary:
            print(f"AI Summary:\n{summary}")
        else:
            print("Could not generate summary")
        
    finally:
        # Always end the session
        tester.end_session()
    
    print("\n" + "="*60)
    print("🎉 Demo completed! Check the conversation flow above.")
    print("="*60)

if __name__ == "__main__":
    main()