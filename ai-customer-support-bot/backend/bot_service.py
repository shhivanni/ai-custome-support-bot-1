from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from models import Session as ChatSession, Conversation, FAQ, EscalationLog
from llm_service import LLMService
from datetime import datetime, timedelta
import uuid

class BotService:
    def __init__(self, db: Session):
        self.db = db
        self.llm_service = LLMService()
        self.max_conversation_history = 20  # Keep last 20 messages in memory
    
    def start_session(self, customer_email: Optional[str] = None, customer_name: Optional[str] = None) -> str:
        """Start a new chat session"""
        session = ChatSession(
            customer_email=customer_email,
            customer_name=customer_name
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session.id
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get session by ID"""
        return self.db.query(ChatSession).filter(ChatSession.id == session_id).first()
    
    def process_message(self, session_id: str, user_message: str) -> Dict:
        """Process user message and generate bot response"""
        
        # Get or create session
        session = self.get_session(session_id)
        if not session:
            return {"error": "Session not found", "session_id": session_id}
        
        if not session.is_active:
            return {"error": "Session is no longer active", "session_id": session_id}
        
        # Get conversation history for context
        conversation_history = self._get_conversation_history(session_id)
        
        # Get active FAQs
        faqs = self._get_active_faqs()
        
        # Generate response using LLM
        try:
            bot_response, should_escalate, matched_faq_id = self.llm_service.generate_response(
                user_message=user_message,
                conversation_history=conversation_history,
                faqs=faqs
            )
            
            # Save conversation
            conversation = Conversation(
                session_id=session_id,
                user_message=user_message,
                bot_response=bot_response,
                escalated=should_escalate,
                faq_matched=matched_faq_id
            )
            self.db.add(conversation)
            
            # Handle escalation if needed
            if should_escalate:
                self._escalate_session(session_id, "LLM determined escalation needed")
                session.escalated = True
            
            # Update session timestamp
            session.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            return {
                "bot_response": bot_response,
                "session_id": session_id,
                "escalated": should_escalate,
                "matched_faq": matched_faq_id,
                "timestamp": conversation.timestamp.isoformat()
            }
            
        except Exception as e:
            self.db.rollback()
            print(f"Error processing message: {e}")
            return {
                "error": "Failed to process message",
                "session_id": session_id
            }
    
    def get_conversation_history(self, session_id: str) -> List[Dict]:
        """Get formatted conversation history for a session"""
        conversations = self.db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).order_by(Conversation.timestamp).all()
        
        return [
            {
                "user_message": conv.user_message,
                "bot_response": conv.bot_response,
                "timestamp": conv.timestamp.isoformat(),
                "escalated": conv.escalated,
                "faq_matched": conv.faq_matched
            }
            for conv in conversations
        ]
    
    def _get_conversation_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for LLM context"""
        conversations = self.db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).order_by(Conversation.timestamp.desc()).limit(self.max_conversation_history).all()
        
        # Reverse to get chronological order
        conversations = list(reversed(conversations))
        
        return [
            {
                "user_message": conv.user_message,
                "bot_response": conv.bot_response
            }
            for conv in conversations
        ]
    
    def _get_active_faqs(self) -> List[Dict]:
        """Get active FAQs for LLM knowledge"""
        faqs = self.db.query(FAQ).filter(
            FAQ.is_active == True
        ).order_by(FAQ.priority).all()
        
        return [
            {
                "id": faq.id,
                "question": faq.question,
                "answer": faq.answer,
                "category": faq.category
            }
            for faq in faqs
        ]
    
    def _escalate_session(self, session_id: str, reason: str):
        """Create escalation log for session"""
        escalation = EscalationLog(
            session_id=session_id,
            reason=reason
        )
        self.db.add(escalation)
    
    def escalate_manually(self, session_id: str, reason: str) -> bool:
        """Manually escalate a session"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.escalated = True
        self._escalate_session(session_id, f"Manual escalation: {reason}")
        
        try:
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Error escalating session: {e}")
            return False
    
    def end_session(self, session_id: str) -> bool:
        """End a chat session"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.is_active = False
        session.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Error ending session: {e}")
            return False
    
    def get_session_summary(self, session_id: str) -> Optional[str]:
        """Generate summary of session for reporting"""
        conversations = self._get_conversation_history(session_id)
        if not conversations:
            return None
        
        return self.llm_service.summarize_conversation(conversations)
    
    def cleanup_old_sessions(self, hours: int = 24):
        """Clean up old inactive sessions"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        old_sessions = self.db.query(ChatSession).filter(
            ChatSession.updated_at < cutoff_time,
            ChatSession.is_active == False
        )
        
        count = old_sessions.count()
        old_sessions.delete()
        self.db.commit()
        
        print(f"Cleaned up {count} old sessions")
        return count
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        return self.db.query(ChatSession).filter(
            ChatSession.is_active == True
        ).count()
    
    def get_escalated_sessions(self) -> List[Dict]:
        """Get all escalated sessions with details"""
        escalated_sessions = self.db.query(ChatSession).filter(
            ChatSession.escalated == True
        ).all()
        
        result = []
        for session in escalated_sessions:
            # Get latest escalation log
            escalation = self.db.query(EscalationLog).filter(
                EscalationLog.session_id == session.id
            ).order_by(EscalationLog.timestamp.desc()).first()
            
            result.append({
                "session_id": session.id,
                "customer_email": session.customer_email,
                "customer_name": session.customer_name,
                "created_at": session.created_at.isoformat(),
                "escalation_reason": escalation.reason if escalation else "Unknown",
                "escalation_time": escalation.timestamp.isoformat() if escalation else None,
                "resolved": escalation.resolved if escalation else False
            })
        
        return result