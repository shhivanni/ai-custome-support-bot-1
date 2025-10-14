#  AI Customer Support Bot

A comprehensive AI-powered customer support chatbot with FAQ matching, contextual memory, and intelligent escalation capabilities. Built with FastAPI, SQLAlchemy, and Google Gemini AI integration.

##  Features

- **Intelligent Conversations**: AI-powered responses using Google Gemini AI
- **FAQ Matching**: Automatic matching of user queries with predefined FAQs
- **Contextual Memory**: Maintains conversation history for context-aware responses
- **Smart Escalation**: Automatic and manual escalation to human agents
- **Session Management**: Persistent chat sessions with user tracking
- **Real-time Chat Interface**: Clean, responsive web interface
- **Admin Dashboard**: Monitor sessions and escalated cases
- **Conversation Summaries**: AI-generated summaries for reporting



##  Quick Start

### Prerequisites

- Python 3.8+
- Google Gemini API Key
- Git (optional)

### Installation

1. **Clone or download the project**
   ```bash
   # If using git
   git clone <repository-url>
   cd ai-customer-support-bot
   
   # Or download and extract the zip file
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env and add your Gemini API key
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. **Initialize the database**
   ```bash
   python backend/setup.py
   ```

5. **Run the server**
   ```bash
   python backend/main.py
   ```

6. **Open in browser**
   Navigate to `http://localhost:8000`

##  Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key (required) | - |
| `DATABASE_URL` | Database connection string | `sqlite:///./data/customer_support.db` |
| `API_HOST` | Server host | `localhost` |
| `API_PORT` | Server port | `8000` |
| `MODEL_NAME` | Gemini model to use | `gemini-1.5-flash` |
| `MAX_TOKENS` | Maximum response tokens | `1000` |
| `TEMPERATURE` | Response creativity (0-2) | `0.7` |

### Database Models

The system uses the following main models:

- **Session**: Chat sessions with customer information
- **Conversation**: Individual message exchanges
- **FAQ**: Frequently asked questions and answers
- **EscalationLog**: Escalation events and reasons

##  API Endpoints

### Chat Operations

- `POST /api/sessions/start` - Start a new chat session
- `POST /api/chat` - Send message and get bot response
- `GET /api/sessions/{id}/history` - Get conversation history
- `POST /api/sessions/{id}/escalate` - Escalate session to human
- `POST /api/sessions/{id}/end` - End chat session
- `GET /api/sessions/{id}/summary` - Get AI summary

### FAQ Management

- `GET /api/faqs` - List all FAQs
- `POST /api/faqs` - Create new FAQ
- `GET /api/faqs/categories` - Get FAQ categories

### Admin Operations

- `GET /api/admin/stats` - Get system statistics
- `GET /api/admin/escalated` - Get escalated sessions

### Example Usage

#### Start a Chat Session
```json
POST /api/sessions/start
{
    "customer_name": "John Doe",
    "customer_email": "john@example.com"
}

Response:
{
    "session_id": "abc123...",
    "message": "Session started successfully"
}
```

#### Send a Message
```json
POST /api/chat
{
    "session_id": "abc123...",
    "message": "How do I reset my password?"
}

Response:
{
    "bot_response": "To reset your password: 1) Go to...",
    "session_id": "abc123...",
    "escalated": false,
    "matched_faq": "faq_id_123",
    "timestamp": "2024-01-15T10:30:00"
}
```

##  LLM Integration & Prompts

### System Prompt Structure

The bot uses a comprehensive system prompt that includes:

1. **Role Definition**: Customer support assistant identity
2. **Guidelines**: Behavior and response rules
3. **FAQ Knowledge**: Dynamically injected FAQ content
4. **Escalation Rules**: Conditions for human handoff
5. **Response Format**: Structured output requirements

### Core System Prompt

```
You are a helpful customer support assistant. Your goal is to provide accurate, friendly, and efficient support to customers.

Guidelines:
1. Always be polite and professional
2. Try to resolve customer issues using the provided FAQ knowledge
3. If you cannot answer a question confidently, suggest escalation to a human agent
4. Keep responses concise but complete
5. Ask clarifying questions when needed
6. Show empathy for customer concerns

{FAQ_KNOWLEDGE}

If you encounter any of these situations, indicate that the conversation should be escalated:
- Customer is angry or frustrated beyond what you can handle
- Technical issues that require specialized knowledge
- Billing disputes or refund requests
- Account security concerns
- Complex troubleshooting that hasn't been resolved after 3 attempts
- Customer specifically requests to speak with a human

Always end your response with [ESCALATE] if escalation is needed, otherwise end with [CONTINUE].
```

### Escalation Detection

The system uses multiple methods to detect when escalation is needed:

1. **LLM Response Analysis**: Parsing `[ESCALATE]` tags in responses
2. **Keyword Detection**: Monitoring for escalation keywords
3. **Sentiment Analysis**: Detecting frustration or anger
4. **Manual Override**: User-initiated escalation requests

### Conversation Summarization

```
Summarize this customer support conversation. Include:
1. Main customer issue or question
2. Key points discussed
3. Resolution status
4. Any unresolved concerns

Keep the summary concise but comprehensive.
```

##  Escalation Scenarios

### Automatic Escalation Triggers

1. **Emotional Indicators**
   - Anger, frustration expressions
   - Demanding tone
   - Multiple complaints

2. **Request Types**
   - Billing disputes
   - Refund requests
   - Account security issues
   - Complex technical problems

3. **Keywords**
   - "manager", "supervisor"
   - "human", "agent"
   - "terrible", "awful", "horrible"
   - "refund", "cancel", "billing"

### Manual Escalation

Users can manually request escalation at any time through:
- Web interface escalation button
- API endpoint for manual escalation
- Chat commands (e.g., "I want to speak to a human")

##  Session Management

### Session Lifecycle

1. **Start**: Create session with optional customer details
2. **Chat**: Exchange messages with contextual memory
3. **Escalate**: Transfer to human agent if needed
4. **End**: Close session and generate summary

### Contextual Memory

- Maintains last 20 message exchanges
- Preserves conversation flow and context
- Enables follow-up questions and references
- Automatic cleanup of old sessions

##  Testing

### Automated Tests

Run the test suite:
```bash
python tests/test_bot.py
```

The test suite covers:
- Database setup and FAQ loading
- Bot service functionality
- FAQ matching accuracy
- Escalation detection
- Session management

### Manual Testing

1. **Start a session** through the web interface
2. **Test FAQ matching** with questions like:
   - "How do I reset my password?"
   - "What are your business hours?"
   - "How can I update billing info?"

3. **Test escalation** with phrases like:
   - "I want to speak to a manager"
   - "This service is terrible"
   - "I demand a refund"

4. **Test conversation flow** with follow-up questions

##  Demo & Testing

### Quick Demo

To see the bot in action, use the included demo script:

```bash
# Start the server first
python backend/main.py

# In another terminal, run the demo
python demo_test.py
```

The demo script will:
- Start a new chat session
- Test FAQ matching with common questions
- Test escalation scenarios
- Generate an AI conversation summary
- Display conversation history

### Manual Testing

1. **Open the web interface** at `http://localhost:8000`
2. **Start a new session** with your name and email
3. **Try these test messages:**
   - "How do I reset my password?" (FAQ matching)
   - "What are your business hours?" (FAQ matching)
   - "I want to speak to a manager" (escalation test)
   - "This service is terrible!" (escalation test)
   - "I'm having trouble with my account" (general support)

### API Testing

Use tools like Postman or curl to test the API endpoints:

```bash
# Health check
curl http://localhost:8000/health

# Start session
curl -X POST http://localhost:8000/api/sessions/start \
  -H "Content-Type: application/json" \
  -d '{"customer_name": "Test User", "customer_email": "test@example.com"}'

# Send message (replace SESSION_ID)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "SESSION_ID", "message": "Hello, I need help"}'
```

## 🎨 Frontend Interface

### Chat Interface Features

- **Session Management**: Start new sessions with customer details
- **Real-time Chat**: Send messages and receive instant AI responses
- **Escalation Controls**: Manual escalation button for human assistance
- **Conversation History**: View complete chat history
- **FAQ Display**: Browse available frequently asked questions
- **Session Summary**: AI-generated conversation summaries
- **Responsive Design**: Works on desktop and mobile devices

### Interface Components

- **Session Setup Form**: Capture customer name and email
- **Chat Messages Area**: Display conversation flow
- **Message Input**: Type and send messages
- **Action Buttons**: Escalate, end session, view history
- **Status Indicators**: Show session state and escalation status
- **Loading States**: Visual feedback during API calls

##  Technical Achievements

### Core Features Implemented ✅

- **✅ LLM Integration**: Google Gemini AI for intelligent responses
- **✅ FAQ Matching**: Automatic matching with keyword-based algorithms
- **✅ Contextual Memory**: Maintains conversation history and context
- **✅ Smart Escalation**: Multiple detection methods for human handoff
- **✅ Session Management**: Persistent chat sessions with tracking
- **✅ REST API**: Comprehensive endpoints for all functionality
- **✅ Database Integration**: SQLite with session and conversation storage
- **✅ Frontend Interface**: Complete web-based chat interface
- **✅ Conversation Summaries**: AI-powered conversation summarization
- **✅ Demo System**: Automated testing and demonstration scripts

### Technical Stack

- **Backend**: FastAPI (Python)
- **AI/LLM**: Google Gemini 1.5 Flash
- **Database**: SQLAlchemy with SQLite
- **Frontend**: HTML/CSS/JavaScript
- **API**: RESTful endpoints with JSON
- **Configuration**: Environment-based settings

### Architecture Highlights

- **Modular Design**: Separated concerns (bot service, LLM service, database)
- **Scalable Structure**: Easy to extend with new features
- **Error Handling**: Comprehensive error handling and fallbacks
- **Security**: Environment-based secrets management
- **Documentation**: Detailed prompts and API documentation

##  Project Deliverables

### ✅ Completed Deliverables

1. **GitHub Repository Structure**
   - Well-organized codebase with clear directory structure
   - Comprehensive README with setup instructions
   - Sample data and configuration files

2. **LLM Integration Documentation**
   - `docs/PROMPTS.md` - Detailed prompt engineering guide
   - System prompt templates and examples
   - Google Gemini-specific optimizations
   - Escalation detection strategies

3. **Functional Implementation**
   - Complete backend API with all required endpoints
   - Frontend chat interface for testing and demonstration
   - Database schema with session tracking
   - FAQ management and matching system

4. **Testing and Demo**
   - `demo_test.py` - Automated testing script
   - Manual testing instructions
   - API endpoint examples
   - Comprehensive test scenarios

### Key Features Demonstrated

- **Conversational AI**: Natural language understanding and response
- **Context Awareness**: Maintains conversation state across messages
- **FAQ Intelligence**: Matches queries with relevant knowledge base
- **Escalation Logic**: Detects when human intervention is needed
- **Session Persistence**: Tracks conversations and generates summaries

### Chat Interface Features

- **Session Setup**: Optional customer information collection
- **Real-time Messaging**: Instant response display
- **Escalation Controls**: Manual escalation button and modal
- **FAQ Display**: Collapsible FAQ section
- **Status Indicators**: Session status (Active, Escalated, Ended)
- **Responsive Design**: Works on desktop and mobile

### User Experience

- Clean, modern design with gradient backgrounds
- Intuitive message bubbles (user vs bot)
- Loading indicators during processing
- Alert notifications for important events
- Keyboard shortcuts (Enter to send, Ctrl+Enter in modals)

##  Admin Features

### Statistics Dashboard

Access via `/api/admin/stats`:
- Active sessions count
- Total escalated sessions
- System health metrics

### Escalated Sessions Monitor

View all escalated sessions with:
- Customer information
- Escalation reason and timestamp
- Session summaries
- Resolution status

##  Security & Privacy

### Data Protection

- All sensitive data properly escaped
- Session-based access control
- No API keys exposed in frontend
- CORS protection enabled

### Privacy Compliance

- Optional customer information collection
- Data retention policies configurable
- Conversation data encrypted in database
- GDPR-ready data export capabilities

##  Deployment

### Local Development

```bash
# Development server with auto-reload
uvicorn backend.main:app --reload --host localhost --port 8000
```

### Production Deployment

1. **Environment Setup**
   ```bash
   # Set production environment variables
   export API_DEBUG=False
   export DATABASE_URL=postgresql://user:pass@host:5432/db
   ```

2. **Run with Gunicorn**
   ```bash
   pip install gunicorn
   gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

3. **Nginx Configuration**
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## 🔧 Customization

### Adding New FAQs

1. **Via API**
   ```json
   POST /api/faqs
   {
       "question": "New question?",
       "answer": "Detailed answer...",
       "category": "Category",
       "priority": 1
   }
   ```

2. **Via Database**
   - Add entries to `sample_faqs.json`
   - Run `python backend/setup.py` to reload

### Customizing Prompts

Edit the system prompt in `backend/llm_service.py`:
- Modify guidelines and behavior
- Update escalation conditions
- Add domain-specific knowledge

### Styling Changes

Modify `frontend/style.css` to customize:
- Color schemes and branding
- Layout and spacing
- Responsive breakpoints
- Animation effects

##  Troubleshooting

### Common Issues

1. **OpenAI API Errors**
   - Verify API key is correct
   - Check rate limits and billing
   - Test with curl: `curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models`

2. **Database Issues**
   - Ensure data directory exists
   - Run setup script: `python backend/setup.py`
   - Check file permissions

3. **Frontend Not Loading**
   - Verify backend server is running
   - Check CORS settings in main.py
   - Inspect browser console for errors



##  Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run test suite
5. Submit pull request

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings to functions
- Include type hints where appropriate

##  Support

For support and questions:
- Check the troubleshooting section
- Run the test suite for diagnostics
- Review API documentation at `/docs` when server is running

##  Demo

A complete working demo includes:
1. Interactive chat interface
2. FAQ matching demonstration
3. Escalation scenario examples
4. Admin dashboard preview

The system is designed to be production-ready with proper error handling, logging, and scalability considerations.
