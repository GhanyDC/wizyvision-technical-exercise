# WizyVision Technical Exercise

Small stateless web app for an image question-answering exercise. A user uploads an image, asks a natural-language question about it, and the backend sends both to Gemini and returns the answer.

Current status: Tier 1, Tier 2, and a low-risk Tier 3 polish pass are implemented. The stable `/ask` endpoint remains the Tier 1 MVP path, `/ask-agentic` adds optional Agentic Vision, and the UI now includes prompt templates plus request ID visibility for easier testing and debugging.

## Why This Stack

- FastAPI keeps the backend small, explicit, and easy to test.
- Plain HTML, CSS, and vanilla JavaScript keep the frontend easy to explain line by line.
- No database, auth, or frontend framework because the exercise does not need them.
- The official `google-genai` SDK keeps Gemini integration current and isolated.
- Render is a simple deployment target for a single public web service.

## Project Structure

```text
app/
  config.py
  gemini_service.py
  main.py
  validators.py
  static/
    index.html
    script.js
    style.css
tests/
  conftest.py
  test_ask.py
  test_ask_agentic.py
  test_gemini_service.py
  test_health.py
.env.example
.gitignore
LEARNING_LOG.md
README.md
main.py
render.yaml
requirements.txt
```

## Architecture Summary

- `app/main.py` wires the FastAPI app, static file serving, and the HTTP endpoints.
- `app/main.py` also generates per-request IDs for image analysis requests and logs minimal request metadata.
- `app/validators.py` handles shared request validation.
- `app/gemini_service.py` contains both the stable Tier 1 Gemini call and the isolated Tier 2 agentic parser.
- `app/config.py` centralizes environment-based configuration.
- `app/static/` contains a single-page frontend that can switch between `/ask` and `/ask-agentic`, apply preset prompts, and display request IDs.

## Gemini API Setup

1. Create a Gemini API key in Google AI Studio.
2. Copy `.env.example` to `.env`.
3. Set `GEMINI_API_KEY` in `.env`.
4. Keep the key server-side only. The browser never receives it.

Current default models:
- Tier 1: `gemini-2.5-flash`
- Tier 2 Agentic Vision: `gemini-3-flash-preview`

The app sends Gemini requests from the backend only. There is no Gemini SDK code in the frontend and no API key is exposed to the browser.

## Local Setup

Python version: `3.12`

1. Create and activate a virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

   On PowerShell:

   ```powershell
   Copy-Item .env.example .env
   ```

4. Start the app:

   ```bash
   python -m uvicorn main:app --reload
   ```

5. Open `http://127.0.0.1:8000`.

If port `8000` is already in use, start on another port:

```bash
python -m uvicorn main:app --reload --port 8010
```

## Environment Variables

- `APP_NAME`: display name for the FastAPI app.
- `APP_ENVIRONMENT`: environment label such as `development` or `production`.
- `GEMINI_API_KEY`: Gemini API key. Keep this server-side only.
- `MODEL_NAME`: Tier 1 model name. Default is `gemini-2.5-flash`.
- `AGENTIC_MODEL_NAME`: Tier 2 agentic model. Default is `gemini-3-flash-preview`.
- `MAX_UPLOAD_SIZE_BYTES`: backend upload limit. Default is `5242880` for 5 MB.
- `REQUEST_TIMEOUT_SECONDS`: timeout for Gemini API calls.

## API Surface

- `GET /health`
  - Returns `{"status": "ok"}`
- `POST /ask`
  - Stable Tier 1 endpoint.
  - Accepts multipart form data with `image` and `question`.
  - Validates supported image type, file presence, file size, and question content.
  - Calls Gemini server-side and returns:

    ```json
    {
      "answer": "The serial number appears to be AX-2048.",
      "model": "gemini-2.5-flash",
      "request_id": "req_8f3c91b2"
    }
    ```

- `POST /ask-agentic`
  - Optional Tier 2 endpoint.
  - Accepts the same multipart payload as `/ask`.
  - Uses Gemini 3 Flash Preview with Code Execution enabled.
  - Returns the final answer plus a timeline of any thought summaries, generated Python code, execution output, intermediate images returned by Gemini, and a request ID.

## Tier 3 Polish

- Prompt templates fill the question box with concise field-operations prompts for:
  - reading serial numbers
  - counting visible items
  - checking PPE or safety gear
  - inspecting visible damage
- Each `/ask` and `/ask-agentic` request gets a server-generated request ID in the format `req_<short-id>`.
- Successful responses include `request_id`, and error responses include it where practical so debugging stays simple without exposing sensitive data.
- Server logs include only minimal metadata: request ID, endpoint, mode, model, success or failure, and status code.

## Tier 2 Agentic Vision

- Normal mode uses `/ask` and preserves the stable Tier 1 MVP behavior.
- Agentic Vision uses `/ask-agentic` and keeps the more experimental Gemini 3 flow isolated from the required MVP path.
- The backend enables Code Execution and requests thought summaries so the frontend can render a readable Think -> Act -> Observe timeline instead of one raw response blob.

## How To Test

Normal mode:
- Start the app.
- Leave `Use Agentic Vision mode` unchecked.
- Upload a JPG, PNG, or WEBP image and submit a question.

Agentic Vision mode:
- Start the app.
- Check `Use Agentic Vision mode`.
- Upload a supported image and ask a question where zooming, counting, or inspection may help.
- Confirm the UI shows:
  - final answer
  - timeline entries
  - generated Python code when present
  - execution output when present
  - intermediate images when Gemini returns them

Tier 3 polish:
- Click each prompt template button and confirm it fills the question textarea.
- Submit in normal mode and confirm the answer card shows `Request ID: req_<...>`.
- Submit in agentic mode and confirm the answer card also shows the request ID.
- Trigger a validation error and confirm the frontend still shows a clean error message.

## Running Tests

```bash
pytest
```

## Render Deployment Notes

- `render.yaml` is included for a single Python web service.
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Set `GEMINI_API_KEY` in Render as a secret environment variable.
- `MODEL_NAME` controls the stable Tier 1 path.
- `AGENTIC_MODEL_NAME` controls the Tier 2 agentic path.
- The health check points at `/health`.
- Request IDs are generated at runtime and do not require any extra Render configuration.

## Known Limitations

- MIME type validation is based on the uploaded content type and does not inspect file signatures.
- The app handles one image and one question at a time.
- There is minimal request logging but no analytics or rate limiting yet.
- Agentic Vision depends on a preview model and may be less predictable than the Tier 1 path.
- Not every agentic response will include code, execution output, or images.
- The app uses Gemini thought summaries and tool output directly rather than a richer custom workflow engine.
- Streaming and multi-turn chat were intentionally not implemented to keep the exercise stateless, easier to review, and easier to explain in an interview.

## Future Work

- Add drag-and-drop uploads and a small image preview.
- Add stronger server-side file validation beyond MIME type headers.
- Add structured logging export or tracing beyond the current lightweight request ID logging.
- Add more agentic parsing coverage around unusual Gemini response shapes.
- Add a clearer deployment checklist after the first public Render deploy.
