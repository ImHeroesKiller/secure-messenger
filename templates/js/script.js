const chatMessages = document.getElementById('chat-messages');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');

sendButton.addEventListener('click', sendMessage);
messageInput.addEventListener('keyup', function(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
});

function sendMessage() {
    const messageText = messageInput.value.trim();
    if (messageText !== '') {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', 'sent');
        messageElement.textContent = messageText;
        chatMessages.appendChild(messageElement);
        messageInput.value = '';
        chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll to bottom
    }
    
    // Tampilkan halaman sukses
    document.getElementById('success-page').style.display = 'block';

    // Sembunyikan halaman sukses setelah beberapa detik (misalnya, 3 detik)
    setTimeout(() => {
        document.getElementById('success-page').style.display = 'none';
    }, 3000);
}
