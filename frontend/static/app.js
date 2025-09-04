class VexereChatbot {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.websocket = null;
        this.isConnected = false;
        
        this.initializeElements();
        this.setupEventListeners();
        this.initializeWebSocket();
        this.updateTime();
        
        console.log('🚀 Vexere Chatbot initialized with session:', this.sessionId);
    }

    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    initializeElements() {
        this.elements = {
            chatMessages: document.getElementById('chatMessages'),
            messageInput: document.getElementById('messageInput'),
            sendBtn: document.getElementById('sendBtn'),
            typingIndicator: document.getElementById('typingIndicator'),
            clearChat: document.getElementById('clearChat'),
            connectionStatus: document.getElementById('connectionStatus')
        };
    }

    setupEventListeners() {
        // Send message on button click
        this.elements.sendBtn.addEventListener('click', () => this.sendMessage());
        
        // Send message on Enter key (but allow Shift+Enter for new line)
        this.elements.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Auto-resize textarea and enable/disable send button
        this.elements.messageInput.addEventListener('input', () => {
            this.autoResizeTextarea();
            this.toggleSendButton();
        });

        // Clear chat
        this.elements.clearChat.addEventListener('click', () => this.clearChat());
    }

    autoResizeTextarea() {
        const textarea = this.elements.messageInput;
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 100) + 'px';
    }

    toggleSendButton() {
        const hasText = this.elements.messageInput.value.trim().length > 0;
        this.elements.sendBtn.disabled = !hasText;
    }

    initializeWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/${this.sessionId}`;
        
        console.log('🔗 Connecting WebSocket to:', wsUrl);
        
        try {
            this.websocket = new WebSocket(wsUrl);

            this.websocket.onopen = () => {
                console.log('✅ WebSocket connected');
                this.isConnected = true;
                this.updateConnectionStatus('🟢 Kết nối WebSocket');
            };

            this.websocket.onmessage = (event) => {
                console.log('📨 WebSocket message received:', event.data);
                try {
                    const data = JSON.parse(event.data);
                    this.handleBotResponse(data);
                } catch (error) {
                    console.error('❌ Error parsing WebSocket message:', error);
                }
            };

            this.websocket.onclose = () => {
                console.log('❌ WebSocket disconnected, using HTTP fallback');
                this.isConnected = false;
                this.updateConnectionStatus('🔄 Kết nối HTTP');
            };

            this.websocket.onerror = (error) => {
                console.error('❌ WebSocket error:', error);
                this.isConnected = false;
                this.updateConnectionStatus('⚠️ Lỗi kết nối');
            };
        } catch (error) {
            console.error('❌ WebSocket not supported:', error);
            this.isConnected = false;
            this.updateConnectionStatus('🔄 Chế độ HTTP');
        }
    }

    updateConnectionStatus(status) {
        if (this.elements.connectionStatus) {
            this.elements.connectionStatus.textContent = status;
        }
    }

    async sendMessage() {
        const message = this.elements.messageInput.value.trim();
        if (!message) return;

        console.log('📤 Sending message:', message);

        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Clear input and disable send button
        this.elements.messageInput.value = '';
        this.autoResizeTextarea();
        this.toggleSendButton();

        // Show typing indicator
        this.showTypingIndicator();

        // Send via WebSocket if connected, otherwise use HTTP
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            console.log('📡 Sending via WebSocket');
            this.sendViaWebSocket(message);
        } else {
            console.log('📡 Sending via HTTP');
            await this.sendViaHTTP(message);
        }
    }

    sendViaWebSocket(message) {
        const messageData = {
            message: message,
            session_id: this.sessionId,
            timestamp: Date.now()
        };

        try {
            this.websocket.send(JSON.stringify(messageData));
            console.log('✅ Message sent via WebSocket');
        } catch (error) {
            console.error('❌ WebSocket send failed:', error);
            // Fallback to HTTP
            this.sendViaHTTP(message);
        }
    }

    async sendViaHTTP(message) {
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId
                })
            });

            if (response.ok) {
                const data = await response.json();
                console.log('✅ HTTP response received:', data);
                this.handleBotResponse(data);
            } else {
                console.error('❌ HTTP request failed:', response.status);
                this.handleError('Lỗi kết nối server (HTTP ' + response.status + ')');
            }
        } catch (error) {
            console.error('❌ HTTP request error:', error);
            this.handleError('Không thể kết nối với server. Vui lòng thử lại.');
        }
    }

    handleBotResponse(data) {
        console.log('🤖 Handling bot response:', data);
        
        this.hideTypingIndicator();
        
        // Extract message from response (support both formats)
        const botMessage = data.response || data.message || 'Xin lỗi, tôi không thể trả lời lúc này.';
        
        // Add bot message to chat
        this.addMessage(botMessage, 'bot');
        
        // Handle error status
        if (data.status === 'error') {
            console.warn('⚠️ Bot response contains error');
        }
    }

    handleError(errorMessage) {
        this.hideTypingIndicator();
        this.addMessage(errorMessage, 'bot', 'error');
    }

    addMessage(text, sender, type = 'normal') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        if (type === 'error') {
            messageDiv.style.opacity = '0.8';
        }

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';

        const content = document.createElement('div');
        content.className = 'message-content';

        const messageText = document.createElement('div');
        messageText.className = 'message-text';
        
        // Format message text (convert \n to <br>, etc.)
        const formattedText = this.formatMessage(text);
        messageText.innerHTML = formattedText;

        const messageTime = document.createElement('div');
        messageTime.className = 'message-time';
        
        const timeSpan = document.createElement('span');
        timeSpan.className = 'time';
        timeSpan.textContent = this.getCurrentTime();
        
        messageTime.appendChild(timeSpan);

        content.appendChild(messageText);
        content.appendChild(messageTime);

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);

        this.elements.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        console.log(`✅ Message added: ${sender} - ${text.substring(0, 50)}...`);
    }

    formatMessage(text) {
        // Convert newlines to <br>
        text = text.replace(/\n/g, '<br>');
        
        // Convert bullet points
        text = text.replace(/• /g, '<li>');
        
        // Simple URL detection and linking
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        text = text.replace(urlRegex, '<a href="$1" target="_blank">$1</a>');
        
        return text;
    }

    getCurrentTime() {
        return new Date().toLocaleTimeString('vi-VN', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }

    showTypingIndicator() {
        this.elements.typingIndicator.style.display = 'flex';
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        this.elements.typingIndicator.style.display = 'none';
    }

    scrollToBottom() {
        this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
    }

    clearChat() {
        if (confirm('Bạn có chắc muốn xóa toàn bộ cuộc trò chuyện?')) {
            // Keep only the welcome message (first message)
            const messages = this.elements.chatMessages.querySelectorAll('.message');
            for (let i = 1; i < messages.length; i++) {
                messages[i].remove();
            }
            console.log('🧹 Chat cleared');
        }
    }

    updateTime() {
        // Update empty time elements
        const timeElements = document.querySelectorAll('.time:empty');
        const currentTime = this.getCurrentTime();
        
        timeElements.forEach(element => {
            element.textContent = currentTime;
        });
    }
}

// Initialize the chatbot when the page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 DOM loaded, initializing Vexere Chatbot...');
    window.vexereChatbot = new VexereChatbot();
});

// Handle page visibility change to reconnect WebSocket if needed
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible' && window.vexereChatbot) {
        if (!window.vexereChatbot.isConnected) {
            console.log('🔄 Page visible, attempting to reconnect WebSocket...');
            window.vexereChatbot.initializeWebSocket();
        }
    }
});

// Handle online/offline events
window.addEventListener('online', () => {
    console.log('🌐 Back online');
    if (window.vexereChatbot && !window.vexereChatbot.isConnected) {
        window.vexereChatbot.initializeWebSocket();
    }
});

window.addEventListener('offline', () => {
    console.log('📴 Gone offline');
    if (window.vexereChatbot) {
        window.vexereChatbot.updateConnectionStatus('📴 Offline');
    }
});
