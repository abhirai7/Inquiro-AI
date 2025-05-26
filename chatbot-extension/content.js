(function () {
  if (document.getElementById("chatbot-modal")) return;

  // Create Toggle Button
  const toggleBtn = document.createElement("button");
  toggleBtn.id = "chatbot-toggle";
  toggleBtn.innerHTML = "💬";
  document.body.appendChild(toggleBtn);

  // Create Chatbot Modal
  const modal = document.createElement("div");
  modal.id = "chatbot-modal";
  modal.innerHTML = `
    <div id="chatbot-header">🤖 Chat Assistant</div>
    <div id="chatbot-body"></div>
    <div id="chatbot-input-container">
      <input type="text" id="chatbot-input" placeholder="Type your question..." />
      <button id="chatbot-send">Send</button>
    </div>
  `;
  document.body.appendChild(modal);

  const input = document.getElementById("chatbot-input");
  const sendBtn = document.getElementById("chatbot-send");
  const body = document.getElementById("chatbot-body");

  toggleBtn.onclick = () => {
    modal.style.display = modal.style.display === "none" ? "flex" : "none";
  };

  modal.style.display = "none";

  function scrollToBottom() {
    body.scrollTop = body.scrollHeight;
  }

  async function sendQuery() {
    const query = input.value.trim();
    if (!query) return;

    body.innerHTML += `<div class="user-msg">${query}</div>`;
    scrollToBottom();
    input.value = "";
    input.disabled = true;
    sendBtn.disabled = true;

    // Typing indicator
    const typing = document.createElement("div");
    typing.className = "bot-msg";
    typing.innerText = "Typing...";
    body.appendChild(typing);
    scrollToBottom();

    try {
      const response = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          url: window.location.href,
          query: query,
        }),
      });

      const data = await response.json();
      typing.remove();
      body.innerHTML += `<div class="bot-msg">${data.response || "No response available."}</div>`;
    } catch (err) {
      typing.remove();
      body.innerHTML += `<div class="bot-msg">⚠️ Error: ${err.message}</div>`;
    } finally {
      scrollToBottom();
      input.disabled = false;
      sendBtn.disabled = false;
      input.focus();
    }
  }

  sendBtn.onclick = sendQuery;
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendQuery();
  });
})();
