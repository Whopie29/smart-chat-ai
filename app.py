from flask import Flask, render_template_string, request, session, jsonify
from markupsafe import Markup
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
import markdown
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key")  # Secure key from env

# Groq LLM
llm = ChatGroq(
    temperature=0.5,
    groq_api_key=os.getenv("GROQ_API_KEY", ""),
    model_name="llama3-70b-8192"
)

# ----------------------
# Your HTML_TEMPLATE here
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Chat AI - AI Assistant</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- Social Meta Tags -->
    <meta property="og:title" content="Smart Chat AI - AI Assistant">
    <meta property="og:description" content="Your intelligent AI assistant, available 24/7 for anything you need">
    <meta property="og:url" content="https://www.onspace.ai">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="OnSpace.AI">
    <meta property="og:image" content="https://via.placeholder.com/1200x630.png?text=Smart Chat AI">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Smart Chat AI - AI Assistant">
    <meta name="twitter:description" content="Your intelligent AI assistant, available 24/7 for anything you need">
    <meta name="twitter:image" content="https://via.placeholder.com/1200x630.png?text=Smart Chat AI">
    <meta name="twitter:url" content="https://www.onspace.ai">
    
    <style>
        * {
            font-family: 'Inter', sans-serif;
        }
        
        :root {
            --bg-primary: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%);
            --bg-glass: rgba(255, 255, 255, 0.05);
            --border-glass: rgba(255, 255, 255, 0.1);
            --text-primary: #ffffff;
            --text-secondary: #9ca3af;
            --text-muted: #6b7280;
            --chat-user: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            --chat-ai: rgba(75, 85, 99, 0.3);
            --input-bg: rgba(31, 41, 55, 0.8);
            --chip-bg: rgba(75, 85, 99, 0.4);
            --chip-hover: rgba(75, 85, 99, 0.6);
            --scrollbar-track: rgba(75, 85, 99, 0.2);
            --scrollbar-thumb: rgba(156, 163, 175, 0.3);
            --scrollbar-hover: rgba(156, 163, 175, 0.5);
        }
        
        [data-theme="light"] {
            --bg-primary: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            --bg-glass: rgba(255, 255, 255, 0.8);
            --border-glass: rgba(0, 0, 0, 0.1);
            --text-primary: #1f2937;
            --text-secondary: #4b5563;
            --text-muted: #9ca3af;
            --chat-user: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            --chat-ai: rgba(255, 255, 255, 0.9);
            --input-bg: rgba(255, 255, 255, 0.9);
            --chip-bg: rgba(255, 255, 255, 0.7);
            --chip-hover: rgba(255, 255, 255, 0.9);
            --scrollbar-track: rgba(0, 0, 0, 0.05);
            --scrollbar-thumb: rgba(0, 0, 0, 0.2);
            --scrollbar-hover: rgba(0, 0, 0, 0.3);
        }
        
        body {
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            transition: all 0.3s ease;
        }
        
        .glass-effect {
            background: var(--bg-glass);
            backdrop-filter: blur(20px);
            border: 1px solid var(--border-glass);
        }
        
        .chat-bubble-user {
            background: var(--chat-user);
            color: white;
        }
        
        .chat-bubble-ai {
            background: var(--chat-ai);
            border: 1px solid var(--border-glass);
        }
        
        .floating-input {
            background: var(--input-bg);
            backdrop-filter: blur(20px);
            border: 1px solid var(--border-glass);
        }
        
        .suggestion-chip {
            background: var(--chip-bg);
            border: 1px solid var(--border-glass);
            transition: all 0.3s ease;
        }
        
        .suggestion-chip:hover {
            background: var(--chip-hover);
            transform: translateY(-1px);
        }
        
        .typing-indicator {
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }
        
        .typing-dot {
            width: 6px;
            height: 6px;
            background: var(--text-secondary);
            border-radius: 50%;
            animation: typing 1.4s infinite;
        }
        
        .typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .typing-dot:nth-child(3) { animation-delay: 0.4s; }
        
        @keyframes typing {
            0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
            30% { transform: translateY(-10px); opacity: 1; }
        }
        
        .fade-in {
            animation: fadeIn 0.5s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .scroll-smooth {
            scroll-behavior: smooth;
        }
        
        /* Custom scrollbar */
        .chat-container::-webkit-scrollbar {
            width: 6px;
        }
        
        .chat-container::-webkit-scrollbar-track {
            background: var(--scrollbar-track);
            border-radius: 3px;
        }
        
        .chat-container::-webkit-scrollbar-thumb {
            background: var(--scrollbar-thumb);
            border-radius: 3px;
        }
        
        .chat-container::-webkit-scrollbar-thumb:hover {
            background: var(--scrollbar-hover);
        }
        
        /* Theme Toggle */
        .theme-toggle {
            width: 60px;
            height: 32px;
            background: var(--chip-bg);
            border-radius: 16px;
            position: relative;
            cursor: pointer;
            border: 1px solid var(--border-glass);
            transition: all 0.3s ease;
        }
        
        .theme-toggle-slider {
            width: 26px;
            height: 26px;
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            border-radius: 50%;
            position: absolute;
            top: 2px;
            left: 2px;
            transition: transform 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 12px;
        }
        
        [data-theme="light"] .theme-toggle-slider {
            transform: translateX(28px);
        }
        
        /* Markdown styling */
        .ai-message pre {
            background: var(--scrollbar-track);
            border: 1px solid var(--border-glass);
            border-radius: 8px;
            padding: 12px;
            margin: 8px 0;
            overflow-x: auto;
        }
        
        .ai-message code {
            background: var(--scrollbar-track);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
        }
        
        .ai-message pre code {
            background: transparent;
            padding: 0;
        }
        
        .ai-message h1, .ai-message h2, .ai-message h3 {
            color: var(--text-primary);
            margin: 16px 0 8px 0;
        }
        
        .ai-message ul, .ai-message ol {
            margin: 8px 0;
            padding-left: 20px;
        }
        
        .ai-message li {
            margin: 4px 0;
        }
        
        .ai-message blockquote {
            border-left: 4px solid #3b82f6;
            padding-left: 16px;
            margin: 16px 0;
            font-style: italic;
            opacity: 0.9;
        }

        /* Light mode text colors */
        [data-theme="light"] .text-white { color: var(--text-primary) !important; }
        [data-theme="light"] .text-gray-300 { color: var(--text-secondary) !important; }
        [data-theme="light"] .text-gray-400 { color: var(--text-muted) !important; }
        [data-theme="light"] .text-gray-500 { color: var(--text-muted) !important; }
        
        /* Light mode shadows */
        [data-theme="light"] .glass-effect {
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        
        [data-theme="light"] .chat-bubble-ai {
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
    </style>
</head>
<body class="text-white">
    <!-- Header -->
    <header class="fixed top-0 left-0 right-0 z-50 glass-effect">
        <div class="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <div class="w-8 h-8 rounded-lg bg-white bg-opacity-10 flex items-center justify-center">
                    <img src="https://cdn-ai.onspace.ai/onspace/project/image/dJhJe8NZY5jRCbtAbBVTbf/bot.png" alt="Smart Chat AI Logo" class="w-6 h-6 object-contain">
                </div>
                <span class="font-semibold text-lg">Smart Chat AI</span>
            </div>
            <div class="flex items-center space-x-4">
                <div class="theme-toggle" id="themeToggle">
                    <div class="theme-toggle-slider" id="themeSlider">
                        <i class="fas fa-moon" id="themeIcon"></i>
                    </div>
                </div>
                <button id="clearBtn" class="flex items-center space-x-2 px-3 py-2 rounded-lg bg-gray-700 hover:bg-gray-600 transition-all duration-300" title="Clear Chat">
                    <i class="fas fa-trash text-sm"></i>
                </button>
                <button id="upgradeBtn" class="flex items-center space-x-2 px-4 py-2 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 transition-all duration-300">
                    <i class="fas fa-star text-sm"></i>
                    <span class="text-sm font-medium">Upgrade</span>
                </button>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="pt-20 pb-32 min-h-screen flex flex-col">
        <!-- Welcome Section -->
        <div id="welcomeSection" class="flex-1 flex items-center justify-center px-6 {% if chat_history %}hidden{% endif %}">
            <div class="text-center max-w-2xl mx-auto">
                <!-- Avatar -->
                <div class="w-24 h-24 mx-auto mb-8 rounded-2xl glass-effect flex items-center justify-center">
                    <img src="https://cdn-ai.onspace.ai/onspace/project/image/dJhJe8NZY5jRCbtAbBVTbf/bot.png" alt="Smart Chat AI Logo" class="w-12 h-12 object-contain">
                </div>
                
                <!-- Welcome Text -->
                <h1 class="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
                    Good to See You!
                </h1>
                <h2 class="text-2xl md:text-3xl font-semibold mb-6 text-gray-300">
                    How Can I be an Assistance?
                </h2>
                <p class="text-gray-400 mb-12">I'm available 24/7 for you, ask me anything</p>
                
                <!-- Feature Pills -->
                <div class="flex flex-wrap gap-3 justify-center mb-12">
                    <div class="flex items-center space-x-2 px-4 py-2 rounded-full glass-effect">
                        <i class="fas fa-lock text-green-400 text-sm"></i>
                        <span class="text-sm text-gray-300">Unlock more features with the Pro plan</span>
                    </div>
                    <div class="flex items-center space-x-2 px-4 py-2 rounded-full glass-effect">
                        <div class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                        <span class="text-sm text-gray-300">Active extensions</span>
                    </div>
                </div>
                
                <!-- Suggestion Chips -->
                <div class="flex flex-wrap gap-3 justify-center">
                    <button class="suggestion-chip px-4 py-2 rounded-lg text-sm text-gray-300 hover:text-white" data-suggestion="Any advice for me?">
                        <i class="fas fa-lightbulb mr-2"></i>
                        Any advice for me?
                    </button>
                    <button class="suggestion-chip px-4 py-2 rounded-lg text-sm text-gray-300 hover:text-white" data-suggestion="Some youtube video idea">
                        <i class="fas fa-video mr-2"></i>
                        Some youtube video idea
                    </button>
                    <button class="suggestion-chip px-4 py-2 rounded-lg text-sm text-gray-300 hover:text-white" data-suggestion="Life lessons from books">
                        <i class="fas fa-book mr-2"></i>
                        Life lessons from books
                    </button>
                </div>
            </div>
        </div>

        <!-- Chat Container -->
        <div id="chatContainer" class="flex-1 {% if not chat_history %}hidden{% endif %}">
            <div class="max-w-4xl mx-auto px-6 h-full flex flex-col">
                <div class="chat-container flex-1 overflow-y-auto space-y-6 py-6 scroll-smooth max-h-[calc(100vh-200px)]" id="chatHistory">
                    <!-- Load existing chat history -->
                    {% for message in chat_history %}
                    <div class="fade-in {% if message.role == 'user' %}ml-12{% else %}mr-12{% endif %}">
                        <div class="{% if message.role == 'user' %}chat-bubble-user ml-auto{% else %}chat-bubble-ai{% endif %} max-w-2xl rounded-2xl p-4">
                            <div class="flex items-start space-x-3">
                                {% if message.role == 'ai' %}
                                <div class="w-8 h-8 rounded-lg bg-white bg-opacity-10 flex items-center justify-center flex-shrink-0 mt-1">
                                    <img src="https://cdn-ai.onspace.ai/onspace/project/image/dJhJe8NZY5jRCbtAbBVTbf/bot.png" alt="Smart Chat AI" class="w-5 h-5 object-contain">
                                </div>
                                {% endif %}
                                <div class="flex-1">
                                    <div class="text-white text-base leading-relaxed {% if message.role == 'ai' %}ai-message{% endif %}">
                                        {% if message.role == 'ai' %}
                                            {{ message.content | markdown | safe }}
                                        {% else %}
                                            {{ message.content }}
                                        {% endif %}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </main>

    <!-- Input Section -->
    <div class="fixed bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-gray-900 to-transparent">
        <div class="max-w-4xl mx-auto">
            <div class="floating-input rounded-2xl p-4">
                <div class="flex items-center space-x-4">
                    <button id="attachBtn" class="text-gray-400 hover:text-white transition-colors">
                        <i class="fas fa-plus text-lg"></i>
                    </button>
                    <input 
                        type="text" 
                        id="messageInput" 
                        placeholder="Ask anything..."
                        class="flex-1 bg-transparent text-white placeholder-gray-400 outline-none text-base"
                        maxlength="1000"
                    >
                    <button id="sendBtn" class="text-blue-400 hover:text-blue-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
                        <i class="fas fa-paper-plane text-lg"></i>
                    </button>
                </div>
            </div>
            
            <!-- Footer -->
            <div class="text-center mt-4">
                <p class="text-xs text-gray-500">
                    Unlock new era with Smart Chat AI <a href="#" class="text-blue-400 hover:text-blue-300 underline">share us</a>
                </p>
            </div>
        </div>
    </div>

    <!-- Loading Overlay -->
    <div id="loadingOverlay" class="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm flex items-center justify-center z-50 hidden">
        <div class="glass-effect rounded-2xl p-8 text-center">
            <div class="typing-indicator mb-4">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
            <p class="text-gray-300">AI is thinking...</p>
        </div>
    </div>

    <script>
        // Theme Management
        const themeToggle = document.getElementById('themeToggle');
        const themeIcon = document.getElementById('themeIcon');
        
        // Initialize theme from localStorage or default to dark
        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);
        updateThemeIcon(savedTheme);
        
        themeToggle.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
        });
        
        function updateThemeIcon(theme) {
            themeIcon.className = theme === 'dark' ? 'fas fa-moon' : 'fas fa-sun';
        }

        // DOM Elements
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        const chatHistory = document.getElementById('chatHistory');
        const welcomeSection = document.getElementById('welcomeSection');
        const chatContainer = document.getElementById('chatContainer');
        const suggestionChips = document.querySelectorAll('.suggestion-chip');
        const loadingOverlay = document.getElementById('loadingOverlay');
        const attachBtn = document.getElementById('attachBtn');
        const upgradeBtn = document.getElementById('upgradeBtn');
        const clearBtn = document.getElementById('clearBtn');

        // Chat state
        let isLoading = false;
        let chatStarted = {{ 'true' if chat_history else 'false' }};

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            messageInput.focus();
            if (chatStarted) {
                scrollToBottom();
            }
        });

        // Event Listeners
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        messageInput.addEventListener('input', function() {
            const hasContent = this.value.trim().length > 0;
            sendBtn.classList.toggle('text-blue-400', hasContent);
            sendBtn.classList.toggle('text-gray-500', !hasContent);
        });

        sendBtn.addEventListener('click', sendMessage);

        suggestionChips.forEach(chip => {
            chip.addEventListener('click', function() {
                const suggestion = this.dataset.suggestion;
                messageInput.value = suggestion;
                sendMessage();
            });
        });

        clearBtn.addEventListener('click', clearChat);

        attachBtn.addEventListener('click', function() {
            showToast('File attachment feature coming soon!', 'info');
        });

        upgradeBtn.addEventListener('click', function() {
            showToast('Upgrade feature coming soon!', 'info');
        });

        // Functions
        async function sendMessage() {
            const message = messageInput.value.trim();
            if (!message || isLoading) return;

            if (!chatStarted) {
                startChat();
            }

            // Add user message
            addMessage(message, 'user');
            messageInput.value = '';
            
            // Show loading
            showLoading();

            try {
                const response = await fetch('/chat_api', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message })
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                
                if (data.error) {
                    throw new Error(data.error);
                }

                // Add AI response with markdown support
                addMessage(data.ai_response, 'ai');
                
            } catch (error) {
                console.error('Error:', error);
                addMessage('Sorry, I encountered an error. Please try again.', 'ai', true);
                showToast('Failed to send message. Please try again.', 'error');
            } finally {
                hideLoading();
            }
        }

        function startChat() {
            chatStarted = true;
            welcomeSection.classList.add('hidden');
            chatContainer.classList.remove('hidden');
        }

        function addMessage(content, role, isError = false) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `fade-in ${role === 'user' ? 'ml-12' : 'mr-12'}`;
            
            const bubbleClass = role === 'user' ? 'chat-bubble-user ml-auto' : 'chat-bubble-ai';
            const textColor = isError ? 'text-red-300' : 'text-white';
            
            let messageContent = content;
            if (role === 'ai' && !isError) {
                // For AI messages, we'll handle markdown on the server side
                messageContent = escapeHtml(content);
            } else {
                messageContent = escapeHtml(content);
            }
            
            messageDiv.innerHTML = `
                <div class="${bubbleClass} max-w-2xl rounded-2xl p-4">
                    <div class="flex items-start space-x-3">
                        ${role === 'ai' ? `
                                <div class="w-8 h-8 rounded-lg bg-white bg-opacity-10 flex items-center justify-center flex-shrink-0 mt-1">
                                    <img src="https://cdn-ai.onspace.ai/onspace/project/image/dJhJe8NZY5jRCbtAbBVTbf/bot.png" alt="Smart Chat AI" class="w-5 h-5 object-contain">
                                </div>
                        ` : ''}
                        <div class="flex-1">
                            <div class="${textColor} text-base leading-relaxed" style="white-space: pre-wrap;">${messageContent}</div>
                        </div>
                    </div>
                </div>
            `;
            
            chatHistory.appendChild(messageDiv);
            scrollToBottom();
        }

        function showLoading() {
            isLoading = true;
            loadingOverlay.classList.remove('hidden');
            sendBtn.disabled = true;
        }

        function hideLoading() {
            isLoading = false;
            loadingOverlay.classList.add('hidden');
            sendBtn.disabled = false;
            messageInput.focus();
        }

        function scrollToBottom() {
            setTimeout(() => {
                chatHistory.scrollTop = chatHistory.scrollHeight;
            }, 100);
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function showToast(message, type = 'info') {
            const toast = document.createElement('div');
            const bgColor = type === 'error' ? 'bg-red-500' : type === 'success' ? 'bg-green-500' : 'bg-blue-500';
            
            toast.className = `fixed top-24 right-6 ${bgColor} text-white px-6 py-3 rounded-lg shadow-lg z-50 transform translate-x-full transition-transform duration-300`;
            toast.textContent = message;
            
            document.body.appendChild(toast);
            
            setTimeout(() => {
                toast.classList.remove('translate-x-full');
            }, 100);
            
            setTimeout(() => {
                toast.classList.add('translate-x-full');
                setTimeout(() => {
                    if (document.body.contains(toast)) {
                        document.body.removeChild(toast);
                    }
                }, 300);
            }, 3000);
        }

        async function clearChat() {
            if (!confirm('Are you sure you want to clear the chat history?')) {
                return;
            }
            
            try {
                const response = await fetch('/clear');
                if (response.ok) {
                    // Reload the page to show welcome section
                    window.location.reload();
                } else {
                    throw new Error('Failed to clear chat');
                }
            } catch (error) {
                console.error('Error clearing chat:', error);
                showToast('Failed to clear chat history', 'error');
            }
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                messageInput.focus();
            }
            
            if (e.key === 'Escape') {
                messageInput.value = '';
                messageInput.focus();
            }
        });
    </script>
</body>
</html>
'''
# ----------------------

@app.template_filter("markdown")
def markdown_filter(text):
    return Markup(markdown.markdown(text, extensions=["fenced_code", "codehilite"]))

@app.route("/")
def index():
    if "chat_history" not in session:
        session["chat_history"] = []
    return render_template_string(HTML_TEMPLATE, chat_history=session["chat_history"])

@app.route("/chat_api", methods=["POST"])
def chat_api():
    if "chat_history" not in session:
        session["chat_history"] = []

    data = request.get_json()
    user_input = data.get("message", "").strip()
    is_edit = data.get("is_edit", False)

    if user_input:
        chat_history = session["chat_history"]

        if is_edit:
            for i in range(len(chat_history) - 1, -1, -1):
                if chat_history[i]["role"] == "user":
                    chat_history[i]["content"] = user_input
                    chat_history = chat_history[:i+1]
                    break
        else:
            chat_history.append({"role": "user", "content": user_input})

        session["chat_history"] = chat_history

        messages = []
        for msg in chat_history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))

        try:
            response = llm.invoke(messages)
            chat_history.append({"role": "ai", "content": response.content})
            session["chat_history"] = chat_history

            return jsonify({"ai_response": response.content})

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Empty message"}), 400

@app.route("/clear")
def clear():
    session.pop("chat_history", None)
    return jsonify({"status": "cleared"})
