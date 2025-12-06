const uploadBtn = document.getElementById("uploadBtn");
const fileInput = document.getElementById("fileInput");
const statusDiv = document.getElementById("status");
const missingList = document.getElementById("missing-fields");
const historyList = document.getElementById("historyList");

// Funkcja dodająca wpis do historii
function addToHistory(filename, result) {
    const li = document.createElement("li");
    li.textContent = `${filename} → ${result.status}`;
    historyList.appendChild(li);
}

// Obsługa kliknięcia przycisku "Wyślij"
uploadBtn.addEventListener("click", async () => {
    statusDiv.textContent = "";
    missingList.innerHTML = "";

    const file = fileInput.files[0];
    if (!file) {
        alert("Wybierz plik!");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("http://127.0.0.1:5000/upload", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (data.status === "ok") {
            statusDiv.textContent = "Dokument OK ✅";
        } else if (data.status === "wymaga_uzupełnienia") {
            statusDiv.textContent = "Dokument wymaga uzupełnienia ⚠️";
            data.missing.forEach(field => {
                const li = document.createElement("li");
                li.textContent = field;
                missingList.appendChild(li);
            });
        } else {
            statusDiv.textContent = "Błąd przy walidacji dokumentu ❌";
        }

        addToHistory(file.name, data);

    } catch (err) {
        console.error(err);
        statusDiv.textContent = "Błąd sieci lub backendu ❌";
    }
});