// Initialize FastRTC client
const rtcClient = new FastRTCClient({
    offer_url: "/webrtc/offer", // Adjust if your server uses a different endpoint
    additional_inputs_url: "/input_hook",
    additional_outputs_url: "/outputs",
    debug: false,
});

// Helper functions for message display
function displayUserMessage(message) {
    const chatBox = document.getElementById('chat-box');
    const userMsg = document.createElement('div');
    userMsg.className = 'message user';
    userMsg.textContent = message;
    chatBox.appendChild(userMsg);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function displayBotMessage(message) {
    const chatBox = document.getElementById('chat-box');
    const botMsg = document.createElement('div');
    botMsg.className = 'message bot';
    botMsg.textContent = message;
    chatBox.appendChild(botMsg);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Connect button logic
document.getElementById("connect-button").addEventListener("click", () => {
    rtcClient.start();
    document.getElementById("connect-button").style.display = "none";
    document.getElementById("disconnect-button").style.display = "inline-block";
});

// Disconnect button logic
document.getElementById("disconnect-button").addEventListener("click", () => {
    rtcClient.stop();
    document.getElementById("connect-button").style.display = "inline-block";
    document.getElementById("disconnect-button").style.display = "none";
});

document.getElementById('send-button').addEventListener('click', sendMessage);
document.getElementById('message-input').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') sendMessage();
});

function sendMessage() {
    const input = document.getElementById('message-input');
    const message = input.value.trim();
    if (!message) return;

    // Display user message
    displayUserMessage(message);
    input.value = '';

    // Send to server
    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
    })
    .then(response => response.json())
    .then(botReply => {
        // Display bot reply
        displayBotMessage(botReply.response);

        // Send webrtc_id to /input_hook if available
        if (rtcClient && rtcClient.getWebRTCId) {
            const webrtcId = rtcClient.getWebRTCId();
            fetch('/input_hook', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ webrtc_id: webrtcId })
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Register onAdditionalOutputs callback
rtcClient.onAdditionalOutputs((output) => {
    const data = JSON.parse(output.data);
    if (data.role === "user") {
        displayUserMessage(data.content);
    } else if (data.role === "assistant") {
        displayBotMessage(data.content);
    }
});
