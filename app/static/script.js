const MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024;
const ALLOWED_IMAGE_TYPES = new Set(["image/jpeg", "image/png", "image/webp"]);

const form = document.querySelector("#ask-form");
const imageInput = document.querySelector("#image");
const questionInput = document.querySelector("#question");
const agenticModeInput = document.querySelector("#agentic-mode");
const submitButton = document.querySelector("#submit-button");
const statusMessage = document.querySelector("#status-message");
const errorMessage = document.querySelector("#error-message");
const answerSection = document.querySelector("#answer-section");
const answerText = document.querySelector("#answer-text");
const modelText = document.querySelector("#model-text");
const timelineSection = document.querySelector("#timeline-section");
const timelineList = document.querySelector("#timeline-list");

imageInput.addEventListener("change", () => {
  clearMessages();

  const file = imageInput.files?.[0];
  if (!file) {
    return;
  }

  if (!ALLOWED_IMAGE_TYPES.has(file.type)) {
    showError("Please choose a JPG, PNG, or WEBP image.");
    imageInput.value = "";
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

  if (!ALLOWED_IMAGE_TYPES.has(file.type)) {
    showError("Please choose a JPG, PNG, or WEBP image.");
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
  const isAgenticMode = agenticModeInput.checked;
  const endpoint = isAgenticMode ? "/ask-agentic" : "/ask";

  setLoadingState(true);

  try {
    const response = await fetch(endpoint, {
      method: "POST",
      body: formData,
    });

    const payload = await readJsonSafely(response);

    if (!response.ok) {
      throw new Error(extractErrorMessage(payload));
    }

    renderResponse(payload);
    statusMessage.textContent =
      payload.mode === "agentic"
        ? "Agentic Vision request completed."
        : "Request completed.";
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
  timelineSection.hidden = true;
  timelineList.replaceChildren();
}

function showError(message) {
  errorMessage.hidden = false;
  errorMessage.textContent = message;
}

function setLoadingState(isLoading) {
  imageInput.disabled = isLoading;
  questionInput.disabled = isLoading;
  agenticModeInput.disabled = isLoading;
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

async function readJsonSafely(response) {
  const contentType = response.headers.get("content-type") || "";

  if (!contentType.includes("application/json")) {
    return null;
  }

  try {
    return await response.json();
  } catch {
    return null;
  }
}

function renderResponse(payload) {
  answerText.textContent = payload.answer || "No answer returned.";

  const labels = [];
  if (payload.model) {
    labels.push(`Model: ${payload.model}`);
  }
  if (payload.mode === "agentic") {
    labels.push("Mode: Agentic Vision");
  }

  if (labels.length > 0) {
    modelText.textContent = labels.join(" | ");
    modelText.hidden = false;
  } else {
    modelText.textContent = "";
    modelText.hidden = true;
  }

  answerSection.hidden = false;

  if (payload.mode === "agentic" && Array.isArray(payload.timeline)) {
    renderTimeline(payload.timeline);
  }
}

function renderTimeline(items) {
  timelineList.replaceChildren();

  for (const item of items) {
    const entry = document.createElement("article");
    entry.className = "timeline-item";

    const label = document.createElement("p");
    label.className = "timeline-label";
    label.textContent = getTimelineLabel(item);
    entry.appendChild(label);

    if (item.type === "think") {
      const paragraph = document.createElement("p");
      paragraph.className = "timeline-text";
      paragraph.textContent = item.content || "";
      entry.appendChild(paragraph);
    }

    if (item.type === "act") {
      const meta = document.createElement("p");
      meta.className = "timeline-meta";
      meta.textContent = item.language ? `Language: ${item.language}` : "Language: python";
      entry.appendChild(meta);

      const pre = document.createElement("pre");
      const code = document.createElement("code");
      code.textContent = item.code || "";
      pre.appendChild(code);
      entry.appendChild(pre);
    }

    if (item.type === "observe") {
      if (item.outcome) {
        const meta = document.createElement("p");
        meta.className = "timeline-meta";
        meta.textContent = `Outcome: ${item.outcome}`;
        entry.appendChild(meta);
      }

      const pre = document.createElement("pre");
      pre.textContent = item.output || "";
      entry.appendChild(pre);
    }

    if (item.type === "image") {
      const image = document.createElement("img");
      image.className = "timeline-image";
      image.alt = "Intermediate image generated during agentic vision processing";
      image.src = `data:${item.mime_type};base64,${item.data}`;
      entry.appendChild(image);
    }

    timelineList.appendChild(entry);
  }

  timelineSection.hidden = items.length === 0;
}

function getTimelineLabel(item) {
  if (item.type === "think") {
    return "Think";
  }

  if (item.type === "act") {
    return "Act";
  }

  if (item.type === "observe") {
    return "Observe";
  }

  if (item.type === "image") {
    return "Intermediate Image";
  }

  return "Step";
}
