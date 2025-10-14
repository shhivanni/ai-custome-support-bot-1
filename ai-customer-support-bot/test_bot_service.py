#!/usr/bin/env python3
import sys
sys.path.append('./backend')
from bot_service import BotService
from database import get_db

# Test with actual database
db = next(get_db())
bot = BotService(db)

try:
    session_id = bot.start_session('Test User', 'test@example.com')
    print(f'Session started: {session_id}')
    
    result = bot.process_message(session_id, 'How do I reset my password?')
    print(f'Bot response: {result.get("bot_response", "No response")}')
    print(f'Escalated: {result.get("escalated", False)}')
    
    # Test FAQ matching
    result2 = bot.process_message(session_id, 'What are your business hours?')
    print(f'\nSecond question response: {result2.get("bot_response", "No response")}')
    
    # Test escalation
    result3 = bot.process_message(session_id, 'I want to speak to a manager!')
    print(f'\nEscalation test response: {result3.get("bot_response", "No response")}')
    print(f'Escalated: {result3.get("escalated", False)}')
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()