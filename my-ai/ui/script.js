const chatWindow = document.getElementById('chat-window');
const chatForm = document.getElementById('chat-form');
const messageInput = document.getElementById('message');
const allowWebToggle = document.getElementById('allow-web');
const timerDisplay = document.getElementById('timer');
const fileInput = document.getElementById('file-input');
const template = document.getElementById('message-template');

function appendMessage(role, content, sources = []) {
  const clone = template.content.cloneNode(true);
  clone.querySelector('.role').textContent = role;
  clone.querySelector('.time').textContent = new Date().toLocaleTimeString();
  clone.querySelector('.content').textContent = content;

  const sourceList = clone.querySelector('.sources');
  sources.forEach((src) => {
    const li = document.createElement('li');
    const link = document.createElement('a');
    link.href = src.url;
    link.textContent = src.title || src.url;
    link.target = '_blank';
    li.appendChild(link);
    sourceList.appendChild(li);
  });

  chatWindow.appendChild(clone);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function sendMessage(event) {
  event.preventDefault();
  const message = messageInput.value.trim();
  if (!message) return;
  appendMessage('Vous', message);

  const payload = {
    message,
    allow_web: allowWebToggle.checked,
  };

  const start = performance.now();
  try {
    const response = await fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    appendMessage('IA', data.answer, data.sources || []);
  } catch (error) {
    appendMessage('Erreur', 'Impossible de contacter le serveur.');
    console.error(error);
  } finally {
    const elapsed = ((performance.now() - start) / 1000).toFixed(1);
    timerDisplay.textContent = `${elapsed}s`;
    messageInput.value = '';
  }
}

async function uploadFile(event) {
  const file = event.target.files[0];
  if (!file) return;
  const formData = new FormData();
  formData.append('file', file);

  appendMessage('Système', `Téléversement de ${file.name}...`);
  try {
    const response = await fetch('http://localhost:8000/ingest_file', {
      method: 'POST',
      body: formData,
    });
    const data = await response.json();
    appendMessage('Système', data.detail || 'Ingestion terminée.');
  } catch (error) {
    appendMessage('Erreur', "Échec du téléversement.");
    console.error(error);
  } finally {
    event.target.value = '';
  }
}

chatForm.addEventListener('submit', sendMessage);
fileInput.addEventListener('change', uploadFile);
