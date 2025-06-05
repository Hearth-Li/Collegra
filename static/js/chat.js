document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const chatWindow = document.getElementById('chat-window');
    const loadingIndicator = document.getElementById('loading-indicator');
    const modelSelect = document.getElementById('model-select');
    const chatToggle = document.getElementById('chat-toggle');
    const chatSidebar = document.getElementById('chat-sidebar');
    const closeSidebar = document.getElementById('close-sidebar');
    const sidebarChatInput = document.getElementById('sidebar-chat-input');
    const sidebarSendButton = document.getElementById('sidebar-send-button');
    const sidebarChatWindow = document.getElementById('sidebar-chat-window');
    const sidebarLoadingIndicator = document.getElementById('sidebar-loading-indicator');
    let lang = localStorage.getItem('language') || 'zh';

    console.log('chat.js loaded. Elements:', {
        chatInput: !!chatInput,
        sendButton: !!sendButton,
        chatWindow: !!chatWindow,
        loadingIndicator: !!loadingIndicator,
        modelSelect: !!modelSelect,
        chatToggle: !!chatToggle,
        chatSidebar: !!chatSidebar,
        closeSidebar: !!closeSidebar,
        sidebarChatInput: !!sidebarChatInput,
        sidebarSendButton: !!sidebarSendButton,
        sidebarChatWindow: !!sidebarChatWindow,
        sidebarLoadingIndicator: !!sidebarLoadingIndicator
    });

    function updateModelOptions() {
        if (!modelSelect) return;
        try {
            const translations = JSON.parse(modelSelect.dataset.translations || '{}');
            modelSelect.innerHTML = `
                <option value="V1">${translations.V1?.[lang] || 'Model V1'}</option>
                <option value="R3">${translations.R3?.[lang] || 'Model R3'}</option>
            `;
        } catch (e) {
            console.error('Failed to update model options:', e);
        }
    }

    function parseMarkdown(text) {
        return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    }

    function addMessage(content, isUser, isSystem = false, targetWindow) {
        if (!targetWindow) {
            console.error('Target window is undefined');
            return;
        }
        const messageContainer = document.createElement('div');
        messageContainer.classList.add('flex', 'items-start', 'mb-2', isUser ? 'justify-end' : 'justify-start');

        const messageDiv = document.createElement('div');
        messageDiv.classList.add(
            'p-2', 'rounded',
            isUser ? 'bg-blue-100' : 'bg-gray-100',
            'max-w-xs'
        );

        const textSpan = document.createElement('span');
        if (isSystem && !isUser) {
            textSpan.classList.add('italic');
            const prefix = lang === 'en' ? '[System Response]: ' : '[系统响应]：';
            textSpan.innerHTML = parseMarkdown(prefix + content);
        } else {
            textSpan.innerHTML = parseMarkdown(content);
        }

        const icon = document.createElement('img');
        icon.classList.add('h-6', 'w-6', isUser ? 'ml-2' : 'mr-2');
        icon.src = isUser ? '/static/icons/human.png' : '/static/icons/robot.png';
        icon.onerror = () => console.error(`Failed to load icon: ${icon.src}`);

        if (isUser) {
            messageContainer.appendChild(messageDiv);
            messageContainer.appendChild(icon);
        } else {
            messageContainer.appendChild(icon);
            messageContainer.appendChild(messageDiv);
        }
        messageDiv.appendChild(textSpan);

        targetWindow.appendChild(messageContainer);
        targetWindow.scrollTop = targetWindow.scrollHeight;
    }

    async function sendMessage(inputElement, buttonElement, loadingElement, targetWindow, model = 'V1', promptType = 'user') {
        if (!inputElement || !buttonElement || !loadingElement || !targetWindow) {
            console.error('Missing required elements:', { inputElement, buttonElement, loadingElement, targetWindow });
            return;
        }

        const message = inputElement.value.trim();
        if (!message) {
            console.log('Empty message, ignoring');
            return;
        }

        console.log('Sending message:', { message, model, promptType, language: lang });

        addMessage(message, true, false, targetWindow);
        inputElement.value = '';
        buttonElement.disabled = true;
        loadingElement.classList.remove('hidden');

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message, promptType, model, language: lang })
            });

            console.log(`Fetch response status: ${response.status}`);

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP error ${response.status}: ${errorText}`);
            }

            const data = await response.json();
            console.log('Received response:', data);

            if (data.error) {
                console.error('Server error:', data.error);
                addMessage(data.error, false, false, targetWindow);
            } else {
                addMessage(data.response, false, promptType === 'system', targetWindow);
            }
        } catch (error) {
            console.error('Error sending message:', error.message);
            const errorMessage = lang === 'en' ? `Error: ${error.message}` : `错误：${error.message}`;
            addMessage(errorMessage, false, false, targetWindow);
        } finally {
            buttonElement.disabled = false;
            loadingElement.classList.add('hidden');
        }
    }

    if (modelSelect) {
        updateModelOptions();
    }

    window.addEventListener('languageChange', () => {
        lang = localStorage.getItem('language') || 'zh';
        if (modelSelect) {
            updateModelOptions();
        }
    });

    if (sendButton && chatInput && chatWindow && loadingIndicator) {
        sendButton.addEventListener('click', () => {
            console.log('Main chat send button clicked');
            const promptType = document.querySelector('input[name="prompt-type"]:checked')?.value || 'user';
            const model = modelSelect?.value || 'V1';
            sendMessage(chatInput, sendButton, loadingIndicator, chatWindow, model, promptType);
        });
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                console.log('Main chat input enter key pressed');
                const promptType = document.querySelector('input[name="prompt-type"]:checked')?.value || 'user';
                const model = modelSelect?.value || 'V1';
                sendMessage(chatInput, sendButton, loadingIndicator, chatWindow, model, promptType);
            }
        });
    } else {
        console.warn('Main chat elements missing:', { sendButton, chatInput, chatWindow, loadingIndicator });
    }

    if (chatToggle && chatSidebar && closeSidebar && sidebarChatInput && sidebarSendButton && sidebarChatWindow && sidebarLoadingIndicator) {
        chatToggle.addEventListener('click', () => {
            console.log('Chat toggle clicked');
            chatSidebar.classList.toggle('open');
        });
        closeSidebar.addEventListener('click', () => {
            console.log('Close sidebar clicked');
            chatSidebar.classList.remove('open');
        });
        sidebarSendButton.addEventListener('click', () => {
            console.log('Sidebar send button clicked');
            sendMessage(sidebarChatInput, sidebarSendButton, sidebarLoadingIndicator, sidebarChatWindow, 'V3', 'user');
        });
        sidebarChatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                console.log('Sidebar chat input enter key pressed');
                sendMessage(sidebarChatInput, sidebarSendButton, sidebarLoadingIndicator, sidebarChatWindow, 'V3', 'user');
            }
        });
    } else {
        console.error('Sidebar elements missing:', {
            chatToggle: !!chatToggle,
            chatSidebar: !!chatSidebar,
            closeSidebar: !!closeSidebar,
            sidebarChatInput: !!sidebarChatInput,
            sidebarSendButton: !!sidebarSendButton,
            sidebarChatWindow: !!sidebarChatWindow,
            sidebarLoadingIndicator: !!sidebarLoadingIndicator
        });
    }
});