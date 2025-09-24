let sessionId = localStorage.getItem('sessionId') || crypto.randomUUID();
localStorage.setItem('sessionId', sessionId);

async function sendMessage() {
    const input = document.getElementById("user-input");
    const message = input.value.trim();
    if (!message) return;

    appendMessage("You", message, "user");
    input.value = "";

    // Add a loading indicator
    const loadingMessage = appendMessage("Bot", "...", "bot loading-message");

    const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: message, session_id: sessionId })
    });

    // Remove the loading indicator
    document.getElementById("chat-box").removeChild(loadingMessage);

    const data = await response.json();

    appendMessage("Bot", data.response, "bot");
}

function appendMessage(sender, text, cls) {
    const chatBox = document.getElementById("chat-box");
    const msg = document.createElement("div");
    msg.className = "message " + cls;

    const content = document.createElement("div");
    content.innerHTML = `<b>${sender}:</b> ${text}`;
    msg.appendChild(content);

    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;

    return msg; // Return the created element
}

// Add event listener for Enter key
document.getElementById("user-input").addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});