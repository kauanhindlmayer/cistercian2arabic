document.addEventListener("DOMContentLoaded", () => {
  const numberInput = document.getElementById("number-input");
  const convertButton = document.getElementById("convert-button");
  const cistercianResult = document.getElementById("cistercian-result");
  const conversionError = document.getElementById("conversion-error");
  const conversionLoading = document.getElementById("conversion-loading");
  const fileInput = document.getElementById("file-input");
  const dragDropArea = document.getElementById("drag-drop-area");
  const recognizeButton = document.getElementById("recognize-button");
  const recognitionResult = document.getElementById("recognition-result");
  const recognitionError = document.getElementById("recognition-error");
  const recognitionLoading = document.getElementById("recognition-loading");

  let debounceTimeout;

  if (convertButton) {
    convertButton.addEventListener("click", convertToCistercian);
  }

  if (numberInput) {
    numberInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        clearTimeout(debounceTimeout);
        debounceTimeout = setTimeout(convertToCistercian, 200);
      }
    });
  }

  if (fileInput) {
    fileInput.addEventListener("change", handleFileSelect);
  }

  if (dragDropArea) {
    dragDropArea.addEventListener("dragover", handleDragOver);
    dragDropArea.addEventListener("dragleave", handleDragLeave);
    dragDropArea.addEventListener("drop", handleDrop);
    dragDropArea.addEventListener("click", () => fileInput.click());
  }

  if (recognizeButton) {
    recognizeButton.addEventListener("click", recognizeCistercian);
  }

  async function convertToCistercian() {
    const number = numberInput.value.trim();
    if (!/^\d+$/.test(number) || number < 0 || number > 9999) {
      showError(conversionError, "Please enter a number between 0 and 9999");
      return;
    }

    clearError(conversionError);
    setLoading(conversionLoading, true);
    convertButton.disabled = true;

    try {
      const response = await fetch("/convert-to-cistercian", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ number: number, include_segments: true }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Failed to convert number");
      }

      cistercianResult.innerHTML = `
        <div class="row">
          <div class="col-md-12">
            <img src="${data.image}" alt="Cistercian numeral for ${data.number}" class="cistercian-image img-fluid">
          </div>
        </div>`;
    } catch (err) {
      showError(conversionError, err.message);
    } finally {
      setLoading(conversionLoading, false);
      convertButton.disabled = false;
    }
  }

  function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) validateAndProcessFile(file);
  }

  function handleDragOver(event) {
    event.preventDefault();
    event.stopPropagation();
    dragDropArea.classList.add("active");
  }

  function handleDragLeave(event) {
    event.preventDefault();
    event.stopPropagation();
    dragDropArea.classList.remove("active");
  }

  function handleDrop(event) {
    event.preventDefault();
    event.stopPropagation();
    dragDropArea.classList.remove("active");
    const file = event.dataTransfer.files[0];
    if (file) validateAndProcessFile(file);
  }

  function isValidImage(file) {
    return (
      file && file.type.startsWith("image/") && file.size <= 5 * 1024 * 1024
    );
  }

  function validateAndProcessFile(file) {
    if (!isValidImage(file)) {
      showError(recognitionError, "Please select a valid image file (max 5MB)");
      return;
    }

    const fileNameDisplay = document.getElementById("file-name");
    if (fileNameDisplay) fileNameDisplay.textContent = file.name;
    if (recognizeButton) recognizeButton.disabled = false;
  }

  async function recognizeCistercian() {
    const file = fileInput.files[0];
    if (!file) {
      showError(recognitionError, "Please select an image file first");
      return;
    }

    clearError(recognitionError);
    recognitionResult.innerHTML = "";
    setLoading(recognitionLoading, true);
    recognizeButton.disabled = true;

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("/recognize-cistercian", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (!response.ok)
        throw new Error(data.error || "Failed to recognize Cistercian numeral");

      const reader = new FileReader();
      reader.onload = function (e) {
        recognitionResult.innerHTML = `
          <div class="alert alert-success">
            <strong>Recognized Number:</strong> ${data.number}
          </div>
          <div class="row mt-3">
            <div class="col-md-12">
              <div class="card">
                <div class="card-header">
                  <h5 class="mb-0">Analyzed Image</h5>
                </div>
                <div class="card-body text-center">
                  <img src="${e.target.result}" alt="Analyzed Cistercian numeral" class="img-fluid mb-2" style="max-height: 300px;">
                </div>
              </div>
            </div>
          </div>`;
      };
      reader.readAsDataURL(file);
    } catch (error) {
      showError(recognitionError, error.message);
    } finally {
      setLoading(recognitionLoading, false);
      recognizeButton.disabled = false;
    }
  }

  function setLoading(element, state) {
    element.style.display = state ? "block" : "none";
  }

  function showError(element, message) {
    element.textContent = message;
    element.style.display = "block";
  }

  function clearError(element) {
    element.textContent = "";
    element.style.display = "none";
  }
});
