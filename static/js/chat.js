document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const chatWindow = document.getElementById('chat-window');
    const loadingIndicator = document.getElementById('loading-indicator');
    const modelSelect = document.getElementById('model-select');
    const lang = localStorage.getItem('language') || 'zh';

    function addMessage(content, isUser, isSystem = false) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add(
            'mb-2', 'p-2', 'rounded',
            isUser ? 'bg-blue-100' : 'bg-gray-100',
            isUser ? 'ml-auto' : 'mr-auto',
            'max-w-xs'
        );
        if (isSystem && !isUser) {
            messageDiv.classList.add('italic');
            const prefix = lang === 'en' ? '[System Response]: ' : '[系统响应]：';
            messageDiv.textContent = prefix + content;
        } else {
            messageDiv.textContent = content;
        }
        chatWindow.appendChild(messageDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    async function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        const promptType = document.querySelector('input[name="prompt-type"]:checked').value;
        const isSystem = promptType === 'system';
        const model = modelSelect.value;

        addMessage(message, true, isSystem);
        chatInput.value = '';
        sendButton.disabled = true;
        loadingIndicator.classList.remove('hidden');

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message, promptType, model, language: lang })
            });
            const data = await response.json();
            if (data.error) {
                addMessage(data.error, false);
            } else {
                addMessage(data.response, false, isSystem);
            }
        } catch (error) {
            const errorMessage = lang === 'en' ? 'Error: Unable to connect to AI service.' : '错误：无法连接到AI服务。';
            addMessage(errorMessage, false);
        } finally {
            sendButton.disabled = false;
            loadingIndicator.classList.add('hidden');
        }
    }

    sendButton.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
});