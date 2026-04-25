const MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024;

const form = document.querySelector("#ask-form");
const imageInput = document.querySelector("#image");
const questionInput = document.querySelector("#question");
const submitButton = document.querySelector("#submit-button");
const statusMessage = document.querySelector("#status-message");
const errorMessage = document.querySelector("#error-message");
const answerSection = document.querySelector("#answer-section");
const answerText = document.querySelector("#answer-text");
const modelText = document.querySelector("#model-text");

imageInput.addEventListener("change", () => {
  clearMessages();

  const file = imageInput.files?.[0];
  if (!file) {
    return;
  }

  if (file.size > MAX_FILE_SIZE_BYTES) {
    showError("Please choose an image that is 5 MB or smaller.");
    imageInput.value = "";
  }
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearMessages();

  const file = imageInput.files?.[0];
  const question = questionInput.value.trim();

  if (!file) {
    showError("Please select an image before submitting.");
    return;
  }

  if (file.size > MAX_FILE_SIZE_BYTES) {
    showError("Please choose an image that is 5 MB or smaller.");
    return;
  }

  if (!question) {
    showError("Please enter a question about the image.");
    return;
  }

  const formData = new FormData();
  formData.append("image", file);
  formData.append("question", question);

  setLoadingState(true);

  try {
    const response = await fetch("/ask", {
      method: "POST",
      body: formData,
    });

    const payload = await response.json();

    if (!response.ok) {
      throw new Error(extractErrorMessage(payload));
    }

    answerText.textContent = payload.answer;

    if (payload.model) {
      modelText.textContent = `Model: ${payload.model}`;
      modelText.hidden = false;
    } else {
      modelText.textContent = "";
      modelText.hidden = true;
    }

    answerSection.hidden = false;
    statusMessage.textContent = "Request completed.";
  } catch (error) {
    statusMessage.textContent = "";
    const message =
      error instanceof Error
        ? error.message
        : "Something went wrong. Please try again.";
    showError(message);
  } finally {
    setLoadingState(false);
  }
});

function clearMessages() {
  errorMessage.hidden = true;
  errorMessage.textContent = "";
  statusMessage.textContent = "";
  answerSection.hidden = true;
  answerText.textContent = "";
  modelText.textContent = "";
  modelText.hidden = true;
}

function showError(message) {
  errorMessage.hidden = false;
  errorMessage.textContent = message;
}

function setLoadingState(isLoading) {
  imageInput.disabled = isLoading;
  questionInput.disabled = isLoading;
  submitButton.disabled = isLoading;
  submitButton.textContent = isLoading ? "Asking..." : "Ask";

  if (isLoading) {
    statusMessage.textContent = "Submitting image and question...";
  }
}

function extractErrorMessage(payload) {
  if (!payload || typeof payload !== "object") {
    return "Something went wrong. Please try again.";
  }

  const detail = payload.detail;

  if (typeof detail === "string" && detail.trim()) {
    return detail;
  }

  if (Array.isArray(detail) && detail.length > 0) {
    return "The request was rejected. Please check the form fields and try again.";
  }

  return "Something went wrong. Please try again.";
}
