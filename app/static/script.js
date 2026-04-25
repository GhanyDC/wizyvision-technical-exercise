const MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024;
const ALLOWED_IMAGE_TYPES = new Set(["image/jpeg", "image/png", "image/webp"]);
const PROMPT_TEMPLATES = {
  "serial-number":
    "Read the equipment label or nameplate in the image. What serial number, model number, or product code is visible? Only answer with visible text and say if anything is unreadable.",
  "count-items":
    "Count the clearly visible items relevant to the image. Be precise and mention if any items are partially hidden or uncertain.",
  "check-ppe":
    "Check whether the visible worker is wearing required safety gear such as a hard hat, safety vest, gloves, or eye protection. Only answer based on visible evidence.",
  "inspect-damage":
    "Inspect the image for visible damage, missing parts, unsafe conditions, or anomalies. Be concise and mention only what can be seen.",
};

class RequestError extends Error {
  constructor(message, requestId = null) {
    super(message);
    this.name = "RequestError";
    this.requestId = requestId;
  }
}

const form = document.querySelector("#ask-form");
const imageInput = document.querySelector("#image");
const questionInput = document.querySelector("#question");
const agenticModeInput = document.querySelector("#agentic-mode");
const templateButtons = document.querySelectorAll(".template-button");
const submitButton = document.querySelector("#submit-button");
const statusMessage = document.querySelector("#status-message");
const errorMessage = document.querySelector("#error-message");
const answerSection = document.querySelector("#answer-section");
const answerText = document.querySelector("#answer-text");
const modelText = document.querySelector("#model-text");
const requestIdText = document.querySelector("#request-id-text");
const timelineSection = document.querySelector("#timeline-section");
const timelineList = document.querySelector("#timeline-list");

templateButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const templateKey = button.dataset.templateKey;
    const template = templateKey ? PROMPT_TEMPLATES[templateKey] : "";

    if (!template) {
      return;
    }

    clearMessages();
    questionInput.value = template;
    questionInput.focus();
    questionInput.setSelectionRange(template.length, template.length);
  });
});

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
      const errorPayload = extractErrorMessage(payload);
      throw new RequestError(errorPayload.message, errorPayload.requestId);
    }

    renderResponse(payload);
    statusMessage.textContent =
      payload.mode === "agentic"
        ? "Agentic Vision request completed."
        : "Request completed.";
  } catch (error) {
    statusMessage.textContent = "";

    if (error instanceof RequestError) {
      showError(error.message, error.requestId);
      return;
    }

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
  requestIdText.textContent = "";
  requestIdText.hidden = true;
  timelineSection.hidden = true;
  timelineList.replaceChildren();
}

function showError(message, requestId = null) {
  errorMessage.hidden = false;
  errorMessage.textContent = requestId ? `${message} Request ID: ${requestId}` : message;
}

function setLoadingState(isLoading) {
  imageInput.disabled = isLoading;
  questionInput.disabled = isLoading;
  agenticModeInput.disabled = isLoading;
  templateButtons.forEach((button) => {
    button.disabled = isLoading;
  });
  submitButton.disabled = isLoading;
  submitButton.textContent = isLoading ? "Asking..." : "Ask";

  if (isLoading) {
    statusMessage.textContent = "Submitting image and question...";
  }
}

function extractErrorMessage(payload) {
  if (!payload || typeof payload !== "object") {
    return {
      message: "Something went wrong. Please try again.",
      requestId: null,
    };
  }

  const detail = payload.detail;
  const requestId =
    typeof payload.request_id === "string" && payload.request_id.trim()
      ? payload.request_id
      : null;

  if (typeof detail === "string" && detail.trim()) {
    return { message: detail, requestId };
  }

  if (Array.isArray(detail) && detail.length > 0) {
    return {
      message: "The request was rejected. Please check the form fields and try again.",
      requestId,
    };
  }

  return {
    message: "Something went wrong. Please try again.",
    requestId,
  };
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

  if (payload.request_id) {
    requestIdText.textContent = `Request ID: ${payload.request_id}`;
    requestIdText.hidden = false;
  } else {
    requestIdText.textContent = "";
    requestIdText.hidden = true;
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
