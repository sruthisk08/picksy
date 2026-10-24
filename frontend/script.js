// Backend URL. "/chat" works when FastAPI serves this site (see main.py).
// Use "/chat-mock" to test without the model, or null for placeholder replies.
// If opening index.html separately (e.g. Live Server), use "http://localhost:8000/chat".
const BACKEND_URL = "/chat";

const messagesEl = document.getElementById("messages");
const form = document.getElementById("chat-form");
const input = document.getElementById("input");
const sendBtn = document.getElementById("send");
const suggestionsEl = document.getElementById("suggestions");
const stateEl = document.getElementById("state");   // optional filters (Step 5)
const priceEl = document.getElementById("price");

// The server remembers nothing, so we send the whole conversation each time.
const history = [];

// Shows **bold** text from the model without allowing HTML injection.
function renderLite(el, text) {
  text.split(/\*\*(.+?)\*\*/g).forEach((part, i) => {
    if (i % 2 === 1) {
      const strong = document.createElement("strong");
      strong.textContent = part;
      el.appendChild(strong);
    } else {
      el.appendChild(document.createTextNode(part));
    }
  });
}

function addMessage(text, who) {
  const div = document.createElement("div");
  div.className = "msg " + who;
  if (who === "bot") {
    renderLite(div, text);
  } else {
    div.textContent = text; // textContent keeps user input safe from HTML injection
  }
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

// -1 or missing means the data isn't reported
const money = (n) =>
  n == null || n < 0 ? "not reported" : "$" + Math.round(n).toLocaleString();
const pct = (n) =>
  n == null || n < 0 ? "not reported" : Math.round(n * 100) + "%";

function addCards(cards) {
  if (!cards || !cards.length) return;
  const wrap = document.createElement("div");
  wrap.className = "cards";

  cards.forEach((c) => {
    const card = document.createElement("div");
    card.className = "card";

    const title = document.createElement("h3");
    title.textContent = c.name;

    const place = document.createElement("p");
    place.className = "card-place";
    place.textContent =
      [c.city, c.state].filter(Boolean).join(", ") +
      (c.ownership ? " · " + c.ownership : "");

    const stats = document.createElement("ul");
    [
      ["Net price per year", money(c.net_price)],
      ["Graduation rate", pct(c.grad_rate)],
      ["Earnings after 10 yrs", money(c.earnings)],
    ].forEach(([label, value]) => {
      const li = document.createElement("li");
      li.textContent = label + ": " + value;
      stats.appendChild(li);
    });

    card.append(title, place, stats);

    if (c.website && /^https?:\/\//.test(c.website)) {
      const link = document.createElement("a");
      link.href = c.website;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.textContent = "Visit website";
      card.appendChild(link);
    }
    wrap.appendChild(card);
  });

  messagesEl.appendChild(wrap);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

// Shows which majors, schools, and model produced the answer
function addSources(data) {
  const majors = data.sources && data.sources.majors;
  if (!majors || !majors.length) return;
  const p = document.createElement("p");
  p.className = "sources";
  p.textContent =
    "Majors considered: " + majors.join(", ") +
    " · Data: US Dept. of Education College Scorecard" +
    " · Model: " + (data.model || "unknown") + " (open-weight)";
  messagesEl.appendChild(p);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

// Sends the full conversation to the backend and returns the response object,
// or a placeholder if no backend is connected yet.
async function getBotReply() {
  if (!BACKEND_URL) {
    await new Promise((r) => setTimeout(r, 1000));
    return {
      reply:
        "This is a placeholder answer. Once my brain is connected, I’ll suggest majors and schools just for you!",
      school_cards: [],
    };
  }
  const res = await fetch(BACKEND_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      messages: history,
      state: stateEl && stateEl.value.trim() ? stateEl.value.trim() : null,
      max_net_price: priceEl && priceEl.value ? Number(priceEl.value) : null,
    }),
  });
  if (!res.ok) throw new Error("Server error " + res.status);
  return await res.json();
}

async function handleSend(text) {
  const message = text.trim();
  if (!message) return;

  suggestionsEl.hidden = true; // hide the chips after the first message
  addMessage(message, "user");
  history.push({ role: "user", content: message });
  input.value = "";
  sendBtn.disabled = true;

  const typing = showTyping();
  try {
    const data = await getBotReply();
    typing.remove();
    addMessage(data.reply, "bot");
    history.push({ role: "assistant", content: data.reply });
    addCards(data.school_cards);
    addSources(data);
  } catch (err) {
    typing.remove();
    history.pop(); // remove the failed user message so history stays in sync
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

// Welcome message (shown only, not sent to the model)
addMessage(
  "Hi! I’m Pixie. I can help you explore college majors and find schools that fit you. What do you enjoy doing, or what subjects do you like in school?",
  "bot",
);