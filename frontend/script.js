// When your FastAPI backend is running, set this to its /chat URL,
// e.g. "http://localhost:8000/chat". Leave as null to use placeholder replies.
const BACKEND_URL = null;

const messagesEl = document.getElementById("messages");
const form = document.getElementById("chat-form");
const input = document.getElementById("input");
const sendBtn = document.getElementById("send");
const suggestionsEl = document.getElementById("suggestions");

function addMessage(text, who) {
  const div = document.createElement("div");
  div.className = "msg " + who;
  div.textContent = text; // textContent keeps user input safe from HTML injection
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return div;
}

function showTyping() {
  const div = document.createElement("div");
  div.className = "msg bot";
  div.innerHTML =
    '<div class="typing" aria-label="Pixie is typing"><span></span><span></span><span></span></div>';
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return div;
}

// Sends the message to the backend (expects { "reply": "..." } back),
// or returns a placeholder if no backend is connected yet.
async function getBotReply(message) {
  if (!BACKEND_URL) {
    await new Promise((r) => setTimeout(r, 1000));
    return "This is a placeholder answer. Once my brain is connected, I’ll suggest majors and schools just for you!";
  }
  const res = await fetch(BACKEND_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) throw new Error("Server error " + res.status);
  const data = await res.json();
  return data.reply;
}

async function handleSend(text) {
  const message = text.trim();
  if (!message) return;

  suggestionsEl.hidden = true; // hide the chips after the first message
  addMessage(message, "user");
  input.value = "";
  sendBtn.disabled = true;

  const typing = showTyping();
  try {
    const reply = await getBotReply(message);
    typing.remove();
    addMessage(reply, "bot");
  } catch (err) {
    typing.remove();
    addMessage(
      "Oops, my magic fizzled. I couldn’t reach the server. Check that it’s running and try again.",
      "bot",
    );
    console.error(err);
  } finally {
    sendBtn.disabled = false;
    input.focus();
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  handleSend(input.value);
});

suggestionsEl.addEventListener("click", (e) => {
  if (e.target.classList.contains("chip")) handleSend(e.target.textContent);
});

// Welcome message
addMessage(
  "Hi! I’m Pixie. I can help you explore college majors and find schools that fit you. What do you enjoy doing, or what subjects do you like in school?",
  "bot",
);
