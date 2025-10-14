class ChatBot {
    constructor() {
        // Use localhost:8000 when opening HTML file directly, or current origin when served by backend
        this.apiBase = window.location.protocol === 'file:' 
            ? 'http://localhost:8000' 
            : window.location.origin;
        this.sessionId = null;
        this.isEscalated = false;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadFAQs();
        this.updateTimestamp();
        this.startSession(); // Auto-start session
        this.requestFullscreen(); // Request fullscreen on load
    }

    bindEvents() {
        // Message form
        document.getElementById('messageForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });

        // Escalation
        document.getElementById('escalateBtn').addEventListener('click', () => {
            this.showEscalationModal();
        });

        // End session / New chat
        document.getElementById('endSessionBtn').addEventListener('click', () => {
            this.newChat();
        });

        // Modal events
        document.getElementById('confirmEscalation').addEventListener('click', () => {
            this.confirmEscalation();
        });

        document.getElementById('cancelEscalation').addEventListener('click', () => {
            this.hideEscalationModal();
        });

        // Close modal on background click
        document.getElementById('escalationModal').addEventListener('click', (e) => {
            if (e.target === e.currentTarget) {
                this.hideEscalationModal();
            }
        });

        // FAQ toggle
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('faq-question')) {
                this.toggleFAQ(e.target.parentElement);
            }
        });
    }

    async startSession() {
        try {
            this.showLoading(true);
            
            const response = await fetch(`${this.apiBase}/api/sessions/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    customer_name: "Anonymous User",
                    customer_email: null
                })
            });

            if (!response.ok) {
                throw new Error('Failed to start session');
            }

            const data = await response.json();
            this.sessionId = data.session_id;
            
            // Session started successfully, ready to chat
            
            // Focus on message input
            document.getElementById('messageInput').focus();
            
        } catch (error) {
            console.error('Error starting session:', error);
            this.addMessage('Failed to start session. Please refresh the page to try again.', 'bot');
        } finally {
            this.showLoading(false);
        }
    }

    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        
        if (!message) return;

        try {
            // Add user message to chat
            this.addMessage(message, 'user');
            messageInput.value = '';
            
            this.showLoading(true);
            
            const response = await fetch(`${this.apiBase}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to send message');
            }

            const data = await response.json();
            
            // Add bot response to chat
            this.addMessage(data.bot_response, 'bot');
            
            // Check if escalated
            if (data.escalated && !this.isEscalated) {
                this.handleEscalation();
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessage('Sorry, I encountered an error processing your message. Please try again.', 'bot');
            this.showAlert('Failed to send message. Please try again.', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    addMessage(content, sender) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const now = new Date();
        const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        messageDiv.innerHTML = `
            <div class="message-content">
                ${sender === 'bot' ? '<strong>Support Bot:</strong> ' : ''}${this.escapeHtml(content)}
            </div>
            <div class="message-time">${timeStr}</div>
        `;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    showEscalationModal() {
        document.getElementById('escalationModal').style.display = 'flex';
    }

    hideEscalationModal() {
        document.getElementById('escalationModal').style.display = 'none';
        document.getElementById('escalationReason').value = '';
    }

    async confirmEscalation() {
        const reason = document.getElementById('escalationReason').value.trim();
        
        if (!reason) {
            this.showAlert('Please provide a reason for escalation.', 'error');
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/api/sessions/${this.sessionId}/escalate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    reason: reason
                })
            });

            if (!response.ok) {
                throw new Error('Failed to escalate session');
            }

            this.handleEscalation();
            this.hideEscalationModal();
            this.showAlert('Session escalated to human agent successfully!', 'success');
            
        } catch (error) {
            console.error('Error escalating session:', error);
            this.showAlert('Failed to escalate session. Please try again.', 'error');
        }
    }

    handleEscalation() {
        this.isEscalated = true;
        
        const chatInterface = document.getElementById('chatInterface');
        chatInterface.classList.add('escalated');
        
        // Add escalation notice
        const escalationNotice = document.createElement('div');
        escalationNotice.className = 'escalated-notice';
        escalationNotice.textContent = '⚠️ This session has been escalated to a human agent';
        
        const chatHeader = document.querySelector('.chat-header');
        chatInterface.insertBefore(escalationNotice, chatHeader.nextSibling);
        
        // Disable escalate button
        document.getElementById('escalateBtn').disabled = true;
        document.getElementById('escalateBtn').textContent = 'Escalated';
    }

    newChat() {
        if (confirm('Start a new chat session? This will clear the current conversation.')) {
            window.location.reload();
        }
    }

    async endSession() {
        try {
            if (this.sessionId) {
                await fetch(`${this.apiBase}/api/sessions/${this.sessionId}/end`, {
                    method: 'POST'
                });
            }
        } catch (error) {
            console.error('Error ending session:', error);
        }
    }

    async loadFAQs() {
        try {
            const response = await fetch(`${this.apiBase}/api/faqs`);
            
            if (!response.ok) {
                console.warn('Failed to load FAQs');
                return;
            }

            const faqs = await response.json();
            this.renderFAQs(faqs);
            
        } catch (error) {
            console.error('Error loading FAQs:', error);
        }
    }

    renderFAQs(faqs) {
        const faqList = document.getElementById('faqList');
        
        if (faqs.length === 0) {
            faqList.innerHTML = '<p>No FAQs available at the moment.</p>';
            return;
        }

        faqList.innerHTML = faqs.map(faq => `
            <div class="faq-item">
                <div class="faq-question">${this.escapeHtml(faq.question)}</div>
                <div class="faq-answer">${this.escapeHtml(faq.answer)}</div>
            </div>
        `).join('');
    }

    toggleFAQ(faqItem) {
        faqItem.classList.toggle('active');
    }

    showLoading(show) {
        const loadingIndicator = document.getElementById('loadingIndicator');
        const sendBtn = document.getElementById('sendBtn');
        const messageInput = document.getElementById('messageInput');
        
        if (show) {
            loadingIndicator.style.display = 'block';
            sendBtn.disabled = true;
            messageInput.disabled = true;
        } else {
            loadingIndicator.style.display = 'none';
            sendBtn.disabled = false;
            messageInput.disabled = false;
        }
    }

    showAlert(message, type) {
        // Remove existing alerts
        const existingAlerts = document.querySelectorAll('.alert');
        existingAlerts.forEach(alert => alert.remove());
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.textContent = message;
        
        const container = document.querySelector('.container');
        container.appendChild(alert);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    updateTimestamp() {
        // Update the initial bot message timestamp
        const timeElement = document.querySelector('.bot-message .message-time');
        if (timeElement && !timeElement.textContent) {
            const now = new Date();
            timeElement.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        }
    }

    requestFullscreen() {
        // Request fullscreen for better immersive experience
        if (document.documentElement.requestFullscreen) {
            document.documentElement.requestFullscreen().catch(err => {
                console.log('Fullscreen request failed:', err);
            });
        }
    }

    exitFullscreen() {
        // Exit fullscreen if currently in fullscreen
        if (document.exitFullscreen && document.fullscreenElement) {
            document.exitFullscreen();
        }
    }

    toggleFullscreen() {
        // Toggle fullscreen mode
        if (document.fullscreenElement) {
            this.exitFullscreen();
        } else {
            this.requestFullscreen();
        }
    }
}

// Note: ChatBot initialization moved to end of file to store global instance

// Handle Enter key in message input
document.addEventListener('keypress', (e) => {
    if (e.target.id === 'messageInput' && e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        document.getElementById('messageForm').dispatchEvent(new Event('submit'));
    }
});

// Handle Enter key in escalation textarea
document.addEventListener('keypress', (e) => {
    if (e.target.id === 'escalationReason' && e.key === 'Enter' && e.ctrlKey) {
        e.preventDefault();
        document.getElementById('confirmEscalation').click();
    }
});

// Handle F11 key for fullscreen toggle
document.addEventListener('keydown', (e) => {
    if (e.key === 'F11') {
        e.preventDefault();
        // Get the chatbot instance (we'll store it globally)
        if (window.chatBotInstance) {
            window.chatBotInstance.toggleFullscreen();
        }
    }
});

// Store chatbot instance globally for fullscreen access
document.addEventListener('DOMContentLoaded', () => {
    window.chatBotInstance = new ChatBot();
});
