import google.generativeai as genai
import os
import json
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_name = os.getenv("MODEL_NAME", "gemini-1.5-flash")
        self.model = genai.GenerativeModel(self.model_name)
        self.max_tokens = int(os.getenv("MAX_TOKENS", "1000"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
    
    def generate_response(self, user_message: str, conversation_history: List[Dict], faqs: List[Dict]) -> Tuple[str, bool, Optional[str]]:
        """
        Generate bot response using LLM
        Returns: (response_text, should_escalate, matched_faq_id)
        """
        
        # Create system prompt
        system_prompt = self._build_system_prompt(faqs)
        
        try:
            # Build conversation context for Gemini
            full_prompt = system_prompt + "\n\nConversation History:\n"
            
            # Add conversation history
            for conv in conversation_history[-10:]:  # Last 10 messages for context
                full_prompt += f"User: {conv['user_message']}\nBot: {conv['bot_response']}\n"
            
            # Add current user message
            full_prompt += f"\nUser: {user_message}\nBot:"
            
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            bot_response = response.text
            
            # Check if escalation is needed
            should_escalate = self._should_escalate(user_message, bot_response)
            
            # Try to match FAQ
            matched_faq_id = self._match_faq(user_message, faqs)
            
            return bot_response, should_escalate, matched_faq_id
            
        except Exception as e:
            print(f"LLM Error: {e}")
            return "I apologize, but I'm having technical difficulties. Please try again later or speak with a human agent.", True, None
    
    def _build_system_prompt(self, faqs: List[Dict]) -> str:
        """Build system prompt with FAQ knowledge"""
        
        faq_knowledge = ""
        if faqs:
            faq_knowledge = "\\n\\nFrequently Asked Questions:\\n"
            for faq in faqs:
                faq_knowledge += f"Q: {faq['question']}\\nA: {faq['answer']}\\n\\n"
        
        system_prompt = f"""You are a helpful customer support assistant. Your goal is to provide accurate, friendly, and efficient support to customers.

Guidelines:
1. Always be polite and professional
2. Try to resolve customer issues using the provided FAQ knowledge
3. If you cannot answer a question confidently, suggest escalation to a human agent
4. Keep responses concise but complete
5. Ask clarifying questions when needed
6. Show empathy for customer concerns

{faq_knowledge}

If you encounter any of these situations, indicate that the conversation should be escalated:
- Customer is angry or frustrated beyond what you can handle
- Technical issues that require specialized knowledge
- Billing disputes or refund requests
- Account security concerns
- Complex troubleshooting that hasn't been resolved after 3 attempts
- Customer specifically requests to speak with a human

Always end your response with [ESCALATE] if escalation is needed, otherwise end with [CONTINUE].
"""
        return system_prompt
    
    def _should_escalate(self, user_message: str, bot_response: str) -> bool:
        """Determine if the conversation should be escalated"""
        
        escalation_indicators = [
            "[ESCALATE]",
            "speak with a human",
            "transfer to agent",
            "human representative",
        ]
        
        # Check bot response for escalation indicators
        response_lower = bot_response.lower()
        for indicator in escalation_indicators:
            if indicator.lower() in response_lower:
                return True
        
        # Check user message for escalation keywords
        user_lower = user_message.lower()
        escalation_keywords = [
            "angry", "frustrated", "terrible", "awful", "horrible",
            "manager", "supervisor", "human", "agent", "representative",
            "refund", "cancel", "billing", "charge", "payment",
            "security", "hacked", "breach", "unauthorized"
        ]
        
        for keyword in escalation_keywords:
            if keyword in user_lower:
                return True
        
        return False
    
    def _match_faq(self, user_message: str, faqs: List[Dict]) -> Optional[str]:
        """Try to match user message with FAQ using simple keyword matching"""
        
        user_lower = user_message.lower()
        
        for faq in faqs:
            # Check question similarity
            question_words = faq['question'].lower().split()
            
            # Simple keyword matching
            matches = 0
            for word in question_words:
                if len(word) > 3 and word in user_lower:
                    matches += 1
            
            # If enough keywords match, consider it a match
            if matches >= 2 or matches / len(question_words) > 0.3:
                return faq['id']
        
        return None
    
    def summarize_conversation(self, conversations: List[Dict]) -> str:
        """Summarize a conversation for reporting or escalation"""
        
        if not conversations:
            return "No conversation history available."
        
        conversation_text = "\\n".join([
            f"User: {conv['user_message']}\\nBot: {conv['bot_response']}"
            for conv in conversations
        ])
        
        system_prompt = """Summarize this customer support conversation. Include:
1. Main customer issue or question
2. Key points discussed
3. Resolution status
4. Any unresolved concerns

Keep the summary concise but comprehensive."""
        
        try:
            full_prompt = system_prompt + "\n\nConversation to summarize:\n" + conversation_text
            
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=300,
                temperature=0.5,
            )
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            return response.text
            
        except Exception as e:
            print(f"Summarization Error: {e}")
            return f"Summary generation failed. Conversation had {len(conversations)} exchanges."