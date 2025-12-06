// frontend/scripts/chatbot.js

const chat = document.getElementById("chat");
const input = document.getElementById("input");
const send = document.getElementById("send");

function appendMessage(who, text) {
  const p = document.createElement("p");
  p.className = who;
  p.textContent = (who === "user" ? "Ty: " : "Bot: ") + text;
  chat.appendChild(p);
  chat.scrollTop = chat.scrollHeight;
}

// --- MOCK (na start) ---
// Zamiast wysyłać do backendu, najpierw zwracamy stałą odpowiedź.
// Połączy się z prawdziwym backendem dopiero gdy będzie dostępny.
async function askBotMock(question) {
  // symulacja opóźnienia
  await new Promise(r => setTimeout(r, 300));
  if (question.toLowerCase().includes("składki")) {
    return { answer: "Mock: Składki są do 10/15/20 dnia miesiąca."};
  }
  return { answer: "Mock: Nie wiem, spróbuj inaczej."};
}

// --- FUNKCJA DO PODŁĄCZENIA DO BACKENDU ---
async function askBotReal(question) {
  try {
    const res = await fetch("/ask", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({question})
    });
    return await res.json();
  } catch (err) {
    return { answer: "Błąd połączenia z serwerem." };
  }
}

// Użyj mocka teraz; kiedy backend będzie gotowy, zamień na askBotReal
const askBot = askBotMock;

send.onclick = async () => {
  const q = input.value.trim();
  if (!q) return;
  appendMessage("user", q);
  input.value = "";
  appendMessage("bot", "…pisze");
  const resp = await askBot(q);
  // usunięcie ostatniego "…pisze"
  chat.removeChild(chat.lastChild);
  appendMessage("bot", resp.answer);
};
