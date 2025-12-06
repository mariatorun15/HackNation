<!doctype html>
<html>
<head><meta charset="utf-8"><title>Panel pracownika</title></head>
<body>
  <h1>Panel pracownika</h1>
  <form id="uploadForm">
    <label>Wybierz zdjęcie: <input type="file" name="file" id="file"></label>
    <button type="submit">Prześlij do analizy</button>
  </form>
  <div id="result"></div>

  <script>
    document.getElementById('uploadForm').onsubmit = async (e) => {
      e.preventDefault();
      const file = document.getElementById('file').files[0];
      if (!file) { alert("Wybierz plik"); return; }

      // Na początek można tylko pokazać, że plik został wybrany:
      document.getElementById('result').textContent = "Plik gotowy do wysłania (funkcja backendu jeszcze nie podpięta).";
    };
  </script>
  <p><a href="/">Wróć do chatbota</a></p>
</body>
</html>
