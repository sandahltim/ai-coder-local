function sendMessage() {
    const input = document.getElementById("user-input").value;
    if (!input) return;

    const output = document.getElementById("chat-output");
    output.innerHTML += `<p><strong>You:</strong> ${escapeHtml(input)}</p>`;

    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input })
    })
    .then(response => response.json())
    .then(data => {
        const formattedResponse = formatResponse(data.response);
        output.innerHTML += `<p><strong>AI:</strong> ${formattedResponse}</p>`;
        Prism.highlightAll();
        output.scrollTop = output.scrollHeight;
    })
    .catch(error => console.error("Error:", error));

    document.getElementById("user-input").value = "";
}

function uploadFile() {
    const fileInput = document.getElementById("file-input");
    const file = fileInput.files[0];
    if (!file) return;

    const output = document.getElementById("chat-output");
    output.innerHTML += `<p><strong>You:</strong> Uploaded ${file.name}</p>`;

    const formData = new FormData();
    formData.append("file", file);

    fetch("/upload", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            output.innerHTML += `<p><strong>Error:</strong> ${data.error}</p>`;
        } else {
            const formattedResponse = formatResponse(data.response);
            output.innerHTML += `<p><strong>AI:</strong> ${formattedResponse}</p>`;
        }
        Prism.highlightAll();
        output.scrollTop = output.scrollHeight;
    })
    .catch(error => console.error("Error:", error));

    fileInput.value = "";
}

function checkGitStatus() {
    fetch("/git_status")
    .then(response => response.json())
    .then(data => {
        const output = document.getElementById("chat-output");
        output.innerHTML += `<p><strong>Git Status:</strong><br>${escapeHtml(data.status)}</p>`;
        output.scrollTop = output.scrollHeight;
    })
    .catch(error => console.error("Error:", error));
}

function escapeHtml(text) {
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

function formatResponse(text) {
    return text.replace(/```python\n([\s\S]*?)```/g, '<pre><code class="language-python">$1</code></pre>')
               .replace(/```\n([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
               .replace(/\n/g, '<br>');
}