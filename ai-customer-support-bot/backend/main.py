from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
import os
from pathlib import Path
from dotenv import load_dotenv

# Import our modules
from database import get_db, init_db
from bot_service import BotService
from models import FAQ

load_dotenv()

app = FastAPI(
    title="AI Customer Support Bot",
    description="An intelligent customer support bot with FAQ matching and escalation capabilities",
    version="1.0.0"
)

# CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resolve absolute path to the frontend directory (independent of CWD)
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = (BASE_DIR.parent / "frontend").resolve()

# Serve static files (frontend)
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

# Request/Response models
class StartSessionRequest(BaseModel):
    customer_email: Optional[str] = None
    customer_name: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    session_id: str

class EscalateRequest(BaseModel):
    session_id: str
    reason: str

class FAQCreate(BaseModel):
    question: str
    answer: str
    category: str
    keywords: Optional[str] = None
    priority: Optional[int] = 1

class FAQResponse(BaseModel):
    id: str
    question: str
    answer: str
    category: str
    priority: int
    is_active: bool

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    print("AI Customer Support Bot started successfully!")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AI Customer Support Bot"}

# Session management endpoints
@app.post("/api/sessions/start")
async def start_session(
    request: StartSessionRequest,
    db: Session = Depends(get_db)
):
    """Start a new chat session"""
    try:
        bot_service = BotService(db)
        session_id = bot_service.start_session(
            customer_email=request.customer_email,
            customer_name=request.customer_name
        )
        return {
            "session_id": session_id,
            "message": "Session started successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start session: {str(e)}"
        )

@app.post("/api/chat")
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Send a message and get bot response"""
    try:
        bot_service = BotService(db)
        response = bot_service.process_message(
            session_id=request.session_id,
            user_message=request.message
        )
        
        if "error" in response:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=response["error"]
            )
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )

@app.get("/api/sessions/{session_id}/history")
async def get_conversation_history(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get conversation history for a session"""
    try:
        bot_service = BotService(db)
        history = bot_service.get_conversation_history(session_id)
        return {"history": history}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation history: {str(e)}"
        )

@app.post("/api/sessions/{session_id}/escalate")
async def escalate_session(
    session_id: str,
    request: EscalateRequest,
    db: Session = Depends(get_db)
):
    """Manually escalate a session"""
    try:
        bot_service = BotService(db)
        success = bot_service.escalate_manually(session_id, request.reason)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        return {"message": "Session escalated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to escalate session: {str(e)}"
        )

@app.post("/api/sessions/{session_id}/end")
async def end_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """End a chat session"""
    try:
        bot_service = BotService(db)
        success = bot_service.end_session(session_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        return {"message": "Session ended successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to end session: {str(e)}"
        )

@app.get("/api/sessions/{session_id}/summary")
async def get_session_summary(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get AI-generated summary of a session"""
    try:
        bot_service = BotService(db)
        summary = bot_service.get_session_summary(session_id)
        
        if summary is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or no conversation history"
            )
        
        return {"summary": summary}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate session summary: {str(e)}"
        )

# FAQ management endpoints
@app.get("/api/faqs", response_model=List[FAQResponse])
async def get_faqs(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all active FAQs, optionally filtered by category"""
    try:
        query = db.query(FAQ).filter(FAQ.is_active == True)
        
        if category:
            query = query.filter(FAQ.category == category)
        
        faqs = query.order_by(FAQ.priority).all()
        
        return [
            FAQResponse(
                id=faq.id,
                question=faq.question,
                answer=faq.answer,
                category=faq.category,
                priority=faq.priority,
                is_active=faq.is_active
            )
            for faq in faqs
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get FAQs: {str(e)}"
        )

@app.post("/api/faqs", response_model=FAQResponse)
async def create_faq(
    faq_data: FAQCreate,
    db: Session = Depends(get_db)
):
    """Create a new FAQ"""
    try:
        faq = FAQ(
            question=faq_data.question,
            answer=faq_data.answer,
            category=faq_data.category,
            keywords=faq_data.keywords,
            priority=faq_data.priority
        )
        
        db.add(faq)
        db.commit()
        db.refresh(faq)
        
        return FAQResponse(
            id=faq.id,
            question=faq.question,
            answer=faq.answer,
            category=faq.category,
            priority=faq.priority,
            is_active=faq.is_active
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create FAQ: {str(e)}"
        )

@app.get("/api/faqs/categories")
async def get_faq_categories(db: Session = Depends(get_db)):
    """Get all FAQ categories"""
    try:
        categories = db.query(FAQ.category).filter(
            FAQ.is_active == True
        ).distinct().all()
        
        return {"categories": [cat[0] for cat in categories]}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get FAQ categories: {str(e)}"
        )

# Admin endpoints
@app.get("/api/admin/stats")
async def get_admin_stats(db: Session = Depends(get_db)):
    """Get admin statistics"""
    try:
        bot_service = BotService(db)
        
        active_sessions = bot_service.get_active_sessions_count()
        escalated_sessions = len(bot_service.get_escalated_sessions())
        
        return {
            "active_sessions": active_sessions,
            "escalated_sessions": escalated_sessions
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get admin stats: {str(e)}"
        )

@app.get("/api/admin/escalated")
async def get_escalated_sessions(db: Session = Depends(get_db)):
    """Get all escalated sessions"""
    try:
        bot_service = BotService(db)
        escalated = bot_service.get_escalated_sessions()
        return {"escalated_sessions": escalated}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get escalated sessions: {str(e)}"
        )

# Serve frontend
@app.get("/")
async def serve_frontend():
    """Serve the frontend chat interface"""
    index_file = (FRONTEND_DIR / "index.html")
    if index_file.exists():
        return FileResponse(str(index_file))
    else:
        return HTMLResponse("""
        <html>
            <head><title>AI Customer Support Bot</title></head>
            <body>
                <h1>AI Customer Support Bot API</h1>
                <p>The API is running successfully!</p>
                <p>Frontend interface is not yet available.</p>
                <a href="/docs">View API Documentation</a>
            </body>
        </html>
        """)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", "8000"))
    host = os.getenv("API_HOST", "localhost")
    debug = os.getenv("API_DEBUG", "True").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug
    )