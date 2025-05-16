(function() {
  // Check if widget is already loaded
  if (window.CustomChatbotWidget) return;
  window.CustomChatbotWidget = true;

  // Parse bot_id from script src query param
  function getBotId() {
    const scripts = document.getElementsByTagName('script');
    for (let s of scripts) {
      if (s.src && s.src.includes('chatbot-widget.js')) {
        const params = new URLSearchParams(s.src.split('?')[1]);
        return params.get('bot_id');
      }
    }
    return null;
  }

  const botId = getBotId();
  if (!botId) {
    console.error('Chatbot widget: bot_id is required in script src.');
    return;
  }

  // Create styles
  const style = document.createElement('style');
  style.textContent = `
    #custom-chatbot-container {
      position: fixed;
      bottom: 20px;
      right: 20px;
      font-family: Arial, sans-serif;
      z-index: 99999;
    }
    #custom-chatbot-toggle {
      width: 60px;
      height: 60px;
      border-radius: 50%;
      background-color: #007bff;
      color: white;
      border: none;
      cursor: pointer;
      font-size: 30px;
      box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    #custom-chatbot-window {
      width: 320px;
      max-height: 400px;
      background: white;
      box-shadow: 0 4px 20px rgba(0,0,0,0.2);
      border-radius: 8px;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      margin-bottom: 10px;
      font-size: 14px;
    }
    #custom-chatbot-header {
      background-color: #007bff;
      color: white;
      padding: 10px;
      font-weight: bold;
    }
    #custom-chatbot-messages {
      flex-grow: 1;
      overflow-y: auto;
      padding: 10px;
    }
    .custom-chatbot-message {
      margin-bottom: 10px;
      clear: both;
      display: flex;
    }
    .custom-chatbot-message.user {
      justify-content: flex-end;
    }
    .custom-chatbot-message.bot {
      justify-content: flex-start;
    }
    .custom-chatbot-message .bubble {
      max-width: 75%;
      padding: 8px 12px;
      border-radius: 15px;
      line-height: 1.3;
    }
    .custom-chatbot-message.user .bubble {
      background-color: #007bff;
      color: white;
      border-bottom-right-radius: 0;
    }
    .custom-chatbot-message.bot .bubble {
      background-color: #e9ecef;
      color: #333;
      border-bottom-left-radius: 0;
    }
    #custom-chatbot-input-container {
      border-top: 1px solid #ddd;
      padding: 8px;
      display: flex;
    }
    #custom-chatbot-input {
      flex-grow: 1;
      border: 1px solid #ccc;
      border-radius: 20px;
      padding: 6px 12px;
      font-size: 14px;
      outline: none;
    }
    #custom-chatbot-send {
      background-color: #007bff;
      border: none;
      color: white;
      padding: 6px 16px;
      margin-left: 8px;
      border-radius: 20px;
      cursor: pointer;
      font-weight: bold;
    }
    #custom-chatbot-send:disabled {
      background-color: #aaa;
      cursor: not-allowed;
    }
  `;
  document.head.appendChild(style);

  // Create container
  const container = document.createElement('div');
  container.id = 'custom-chatbot-container';

  // Create chat toggle button
  const toggleBtn = document.createElement('button');
  toggleBtn.id = 'custom-chatbot-toggle';
  toggleBtn.title = 'Open chat';
  toggleBtn.innerHTML = '&#128172;'; // chat bubble emoji
  container.appendChild(toggleBtn);

  // Create chat window (hidden by default)
  const chatWindow = document.createElement('div');
  chatWindow.id = 'custom-chatbot-window';
  chatWindow.style.display = 'none';

  chatWindow.innerHTML = `
    <div id="custom-chatbot-header">Chatbot</div>
    <div id="custom-chatbot-messages"></div>
    <div id="custom-chatbot-input-container">
      <input id="custom-chatbot-input" type="text" placeholder="Type a message..." />
      <button id="custom-chatbot-send" disabled>Send</button>
    </div>
  `;
  container.appendChild(chatWindow);

  document.body.appendChild(container);

  const messagesDiv = chatWindow.querySelector('#custom-chatbot-messages');
  const input = chatWindow.querySelector('#custom-chatbot-input');
  const sendBtn = chatWindow.querySelector('#custom-chatbot-send');

  // Toggle chat window
  toggleBtn.addEventListener('click', () => {
    if (chatWindow.style.display === 'none') {
      chatWindow.style.display = 'flex';
      toggleBtn.title = 'Close chat';
      input.focus();
    } else {
      chatWindow.style.display = 'none';
      toggleBtn.title = 'Open chat';
    }
  });

  // Enable/disable send button based on input
  input.addEventListener('input', () => {
    sendBtn.disabled = input.value.trim() === '';
  });

  // Helper: add message to chat
  function addMessage(text, sender = 'bot') {
    const msg = document.createElement('div');
    msg.classList.add('custom-chatbot-message', sender);
    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.textContent = text;
    msg.appendChild(bubble);
    messagesDiv.appendChild(msg);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  }

  // Send message to backend API
  async function sendMessage(text) {
    addMessage(text, 'user');
    input.value = '';
    sendBtn.disabled = true;

    addMessage('...', 'bot');

    try {
      const response = await fetch(`https://your-backend-domain.com/api/ask`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ url: `bot://${botId}`, query: text })
      });
      if (!response.ok) throw new Error('Network response was not ok');
      const data = await response.json();

      // Remove '...' message
      const lastMsg = messagesDiv.querySelector('.custom-chatbot-message.bot:last-child');
      if (lastMsg && lastMsg.textContent === '...') {
        messagesDiv.removeChild(lastMsg);
      }

      addMessage(data.response || 'Sorry, no answer found.', 'bot');
    } catch (err) {
      console.error(err);
      // Remove '...' message
      const lastMsg = messagesDiv.querySelector('.custom-chatbot-message.bot:last-child');
      if (lastMsg && lastMsg.textContent === '...') {
        messagesDiv.removeChild(lastMsg);
      }
      addMessage('Error: Failed to get response', 'bot');
    }
  }

  // Send message on button click or Enter key
  sendBtn.addEventListener('click', () => {
    if (input.value.trim()) {
      sendMessage(input.value.trim());
    }
  });

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (input.value.trim()) {
        sendMessage(input.value.trim());
      }
    }
  });
})();
