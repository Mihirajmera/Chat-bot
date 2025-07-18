document.addEventListener('DOMContentLoaded', function() {
    const chatWindow = document.getElementById('chat-window');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const speechToggle = document.getElementById('speech-toggle');
    const speechIcon = document.getElementById('speech-icon');
    const speechText = document.getElementById('speech-text');
    const voiceInputBtn = document.getElementById('voice-input-btn');
    const voiceIcon = document.getElementById('voice-icon');
    const voiceText = document.getElementById('voice-text');
    const voiceStatus = document.getElementById('voice-status');
    const newChatBtn = document.getElementById('new-chat-btn');
    const chatHistory = document.getElementById('chat-history');
    
    let thinkingMsg = null;
    let speechEnabled = false;
    let speechSynthesis = window.speechSynthesis;
    let currentUtterance = null;
    let recognition = null;
    let currentChatId = null;
    let chatSessions = {};

    // Initialize chat history from localStorage
    function initChatHistory() {
        const savedHistory = localStorage.getItem('magexChatHistory');
        if (savedHistory) {
            chatSessions = JSON.parse(savedHistory);
            renderChatHistory();
        }
        createNewChat();
    }

    // Create a new chat session
    function createNewChat() {
        currentChatId = Date.now().toString();
        chatSessions[currentChatId] = {
            id: currentChatId,
            title: 'New Chat',
            messages: [],
            timestamp: new Date().toISOString()
        };
        chatWindow.innerHTML = '';
        renderChatHistory();
        saveChatHistory();
    }

    // Save chat history to localStorage
    function saveChatHistory() {
        localStorage.setItem('magexChatHistory', JSON.stringify(chatSessions));
    }

    // Render chat history in side panel
    function renderChatHistory() {
        chatHistory.innerHTML = '';
        Object.values(chatSessions).forEach(session => {
            const historyItem = document.createElement('div');
            historyItem.className = 'chat-history-item';
            if (session.id === currentChatId) {
                historyItem.classList.add('active');
            }
            
            const title = session.title || 'New Chat';
            const timestamp = new Date(session.timestamp).toLocaleDateString();
            
            historyItem.innerHTML = `
                <h4>${title}</h4>
                <p>${timestamp}</p>
            `;
            
            historyItem.addEventListener('click', () => loadChat(session.id));
            chatHistory.appendChild(historyItem);
        });
    }

    // Load a specific chat session
    function loadChat(chatId) {
        currentChatId = chatId;
        const session = chatSessions[chatId];
        if (session) {
            chatWindow.innerHTML = '';
            session.messages.forEach(msg => {
                appendMessage(msg.text, msg.sender, false);
            });
            renderChatHistory();
        }
    }

    // Update chat title based on first message
    function updateChatTitle(message) {
        if (chatSessions[currentChatId] && chatSessions[currentChatId].messages.length === 1) {
            chatSessions[currentChatId].title = message.substring(0, 30) + (message.length > 30 ? '...' : '');
            renderChatHistory();
            saveChatHistory();
        }
    }

    // Initialize speech recognition
    function initSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';
            
            recognition.onstart = function() {
                voiceStatus.style.display = 'block';
                voiceIcon.textContent = '🔴';
                voiceText.textContent = 'Listening...';
                voiceInputBtn.classList.add('listening');
            };
            
            recognition.onresult = function(event) {
                const transcript = event.results[0][0].transcript;
                userInput.value = transcript;
                voiceStatus.style.display = 'none';
                voiceIcon.textContent = '🎤';
                voiceText.textContent = 'Voice Input';
                voiceInputBtn.classList.remove('listening');
                
                // Auto-submit the form
                chatForm.dispatchEvent(new Event('submit'));
            };
            
            recognition.onerror = function(event) {
                console.log('Speech recognition error:', event.error);
                voiceStatus.style.display = 'none';
                voiceIcon.textContent = '🎤';
                voiceText.textContent = 'Voice Input';
                voiceInputBtn.classList.remove('listening');
            };
            
            recognition.onend = function() {
                voiceStatus.style.display = 'none';
                voiceIcon.textContent = '🎤';
                voiceText.textContent = 'Voice Input';
                voiceInputBtn.classList.remove('listening');
            };
        } else {
            voiceInputBtn.style.display = 'none';
            console.log('Speech recognition not supported');
        }
    }

    // Initialize speech synthesis
    function initSpeech() {
        if ('speechSynthesis' in window) {
            // Wait for voices to load
            speechSynthesis.onvoiceschanged = function() {
                const voices = speechSynthesis.getVoices();
                // Try to find a good English voice
                let selectedVoice = voices.find(voice => 
                    voice.lang.includes('en') && voice.name.includes('Siri')
                ) || voices.find(voice => 
                    voice.lang.includes('en') && voice.name.includes('Google')
                ) || voices.find(voice => 
                    voice.lang.includes('en')
                ) || voices[0];
                
                if (selectedVoice) {
                    console.log('Selected voice:', selectedVoice.name);
                }
            };
            speechSynthesis.getVoices();
        }
    }

    // Speak text function
    function speakText(text) {
        if (!speechEnabled || !speechSynthesis) return;
        
        // Stop any current speech
        if (currentUtterance) {
            speechSynthesis.cancel();
        }
        
        const utterance = new SpeechSynthesisUtterance(text);
        const voices = speechSynthesis.getVoices();
        
        // Try to find a good English voice
        let selectedVoice = voices.find(voice => 
            voice.lang.includes('en') && voice.name.includes('Siri')
        ) || voices.find(voice => 
            voice.lang.includes('en') && voice.name.includes('Google')
        ) || voices.find(voice => 
            voice.lang.includes('en')
        ) || voices[0];
        
        if (selectedVoice) {
            utterance.voice = selectedVoice;
        }
        
        utterance.rate = 0.9; // Slightly slower for clarity
        utterance.pitch = 1.0;
        utterance.volume = 0.8;
        
        currentUtterance = utterance;
        speechSynthesis.speak(utterance);
        
        utterance.onend = function() {
            currentUtterance = null;
        };
    }

    // Toggle speech function
    function toggleSpeech() {
        speechEnabled = !speechEnabled;
        
        if (speechEnabled) {
            speechIcon.textContent = '🔊';
            speechText.textContent = 'Speech On';
            speechToggle.classList.add('active');
            // Speak a welcome message
            speakText('Hello! I am Magex, your AI assistant. How can I help you today?');
        } else {
            speechIcon.textContent = '🔇';
            speechText.textContent = 'Speech Off';
            speechToggle.classList.remove('active');
            // Stop any current speech
            if (currentUtterance) {
                speechSynthesis.cancel();
                currentUtterance = null;
            }
        }
    }

    // Start voice input
    function startVoiceInput() {
        if (recognition) {
            recognition.start();
        }
    }

    function appendMessage(text, sender, saveToHistory = true) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message ' + sender;
        msgDiv.textContent = text;
        chatWindow.appendChild(msgDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
        
        // Save message to chat history
        if (saveToHistory && chatSessions[currentChatId]) {
            chatSessions[currentChatId].messages.push({
                text: text,
                sender: sender,
                timestamp: new Date().toISOString()
            });
            saveChatHistory();
        }
        
        return msgDiv;
    }

    // Initialize everything
    initSpeech();
    initSpeechRecognition();
    initChatHistory();

    // Event listeners
    speechToggle.addEventListener('click', toggleSpeech);
    voiceInputBtn.addEventListener('click', startVoiceInput);
    newChatBtn.addEventListener('click', createNewChat);

    // Chat form event listener
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const message = userInput.value.trim();
        if (!message) return; // Prevent empty messages
        
        appendMessage(message, 'user');
        updateChatTitle(message);
        userInput.value = '';
        userInput.disabled = true;
        thinkingMsg = appendMessage('Magex is thinking...', 'bot thinking');
        
        fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        })
        .then(res => res.json())
        .then(data => {
            if (thinkingMsg) thinkingMsg.remove();
            const botMessage = appendMessage(data.response, 'bot');
            // Speak the bot's response
            speakText(data.response);
        })
        .catch(() => {
            if (thinkingMsg) thinkingMsg.remove();
            const errorMessage = 'I apologize, but I encountered an issue. Please try again.';
            appendMessage(errorMessage, 'bot');
            speakText(errorMessage);
        })
        .finally(() => {
            userInput.disabled = false;
            userInput.focus();
        });
    });
}); 