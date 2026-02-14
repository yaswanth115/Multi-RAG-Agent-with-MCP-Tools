const BASE_URL = "http://127.0.0.1:8000";
const SESSION_ID = "session1";

// DOM Elements
const fileInput = document.getElementById("fileInput");
const uploadArea = document.getElementById("uploadArea");
const uploadBtn = document.getElementById("uploadBtn");
const uploadStatus = document.getElementById("uploadStatus");
const chatBox = document.getElementById("chatBox");
const queryInput = document.getElementById("queryInput");
const sendBtn = document.getElementById("sendBtn");
const typingIndicator = document.getElementById("typingIndicator");

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    setupDragAndDrop();
});

function setupEventListeners() {
    // Enter key for sending messages
    queryInput.addEventListener('keypress', handleKeyPress);

    // File input change
    fileInput.addEventListener('change', handleFileSelect);
}

function setupDragAndDrop() {
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, unhighlight, false);
    });

    uploadArea.addEventListener('drop', handleDrop, false);
    uploadArea.addEventListener('click', () => fileInput.click());
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function highlight() {
    uploadArea.classList.add('dragover');
}

function unhighlight() {
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;

    if (files.length > 0) {
        fileInput.files = files;
        handleFileSelect();
    }
}

function handleFileSelect() {
    const file = fileInput.files[0];
    if (file) {
        const fileName = file.name;
        const fileSize = (file.size / 1024 / 1024).toFixed(2);
        uploadArea.innerHTML = `
            <div class="upload-content">
                <i class="fas fa-file-alt"></i>
                <p><strong>${fileName}</strong> (${fileSize} MB)</p>
                <p>Click upload to process this document</p>
            </div>
        `;
        uploadBtn.disabled = false;
    }
}

async function uploadFile() {
    if (!fileInput.files.length) {
        showStatus("Please select a file first.", "error");
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("file", file);

    // Update UI
    uploadBtn.disabled = true;
    uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Uploading...';
    showStatus("Uploading document...", "loading");

    try {
        const response = await fetch(`${BASE_URL}/upload`, {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            showStatus("Document uploaded successfully!", "success");
            resetUploadArea();
        } else {
            throw new Error(data.message || "Upload failed");
        }
    } catch (error) {
        showStatus(`Upload failed: ${error.message}`, "error");
        console.error(error);
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.innerHTML = '<i class="fas fa-upload"></i> Upload Document';
    }
}

function resetUploadArea() {
    uploadArea.innerHTML = `
        <div class="upload-content">
            <i class="fas fa-file-alt"></i>
            <p>Drag & drop your document here or <span class="upload-link">browse files</span></p>
            <input type="file" id="fileInput" accept=".pdf,.txt,.doc,.docx">
        </div>
    `;
    fileInput.value = '';
    setupDragAndDrop();
}

function showStatus(message, type) {
    uploadStatus.textContent = message;
    uploadStatus.className = `upload-status ${type}`;
}

function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendQuery();
    }
}

async function sendQuery() {
    const query = queryInput.value.trim();

    if (!query) return;

    // Add user message
    addMessage(query, "user");
    queryInput.value = "";

    // Disable input while processing
    sendBtn.disabled = true;
    queryInput.disabled = true;

    // Show typing indicator
    showTypingIndicator();

    try {
        const response = await fetch(`${BASE_URL}/query`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                query: query,
                session_id: SESSION_ID
            })
        });

        const data = await response.json();

        if (response.ok) {
            addMessage(data.answer, "bot", data.source);
        } else {
            throw new Error(data.message || "Query failed");
        }
    } catch (error) {
        addMessage("Sorry, I encountered an error while processing your question. Please try again.", "bot");
        console.error(error);
    } finally {
        hideTypingIndicator();
        sendBtn.disabled = false;
        queryInput.disabled = false;
        queryInput.focus();
    }
}

function showTypingIndicator() {
    typingIndicator.style.display = 'flex';
    chatBox.scrollTop = chatBox.scrollHeight;
}

function hideTypingIndicator() {
    typingIndicator.style.display = 'none';
}

function addMessage(text, sender, source = null) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", sender);

    const avatarDiv = document.createElement("div");
    avatarDiv.classList.add("bot-avatar");

    if (sender === "bot") {
        avatarDiv.innerHTML = '<i class="fas fa-robot"></i>';
    } else {
        avatarDiv.innerHTML = '<i class="fas fa-user"></i>';
    }

    const contentDiv = document.createElement("div");
    contentDiv.classList.add("message-content");

    // Format the text (basic markdown-like formatting)
    const formattedText = formatMessage(text);
    contentDiv.innerHTML = formattedText;

    if (source) {
        const sourceDiv = document.createElement("div");
        sourceDiv.classList.add("source");
        sourceDiv.innerHTML = `<i class="fas fa-link"></i> Source: ${source}`;
        contentDiv.appendChild(sourceDiv);
    }

    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);

    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function formatMessage(text) {
    // Basic formatting for code blocks and line breaks
    return text
        .replace(/\n/g, '<br>')
        .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
        .replace(/`([^`]+)`/g, '<code>$1</code>');
}

function clearChat() {
    // Keep only the welcome message
    const welcomeMessage = chatBox.querySelector('.welcome-message');
    chatBox.innerHTML = '';
    if (welcomeMessage) {
        chatBox.appendChild(welcomeMessage);
    }
}

// Add some CSS for dragover state
const dragOverStyle = document.createElement('style');
dragOverStyle.textContent = `
    .upload-area.dragover {
        border-color: #764ba2;
        background: rgba(118, 75, 162, 0.2);
        transform: scale(1.02);
    }
`;
document.head.appendChild(dragOverStyle);
