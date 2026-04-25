# WizyVision Technical Exercise

Small stateless web app for an image question-answering exercise. A user uploads an image, asks a natural-language question about it, and the backend sends both to Gemini and returns the answer.

Current status: Tier 1 is implemented. FastAPI serves a plain HTML/CSS/JavaScript frontend, `/health` is live, `/ask` accepts validated multipart form data, and Gemini is called server-side through the official Google Gen AI SDK.

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
  test_health.py
.env.example
.gitignore
LEARNING_LOG.md
README.md
render.yaml
requirements.txt
```

## Architecture Summary

- `app/main.py` wires the FastAPI app, static file serving, and the two HTTP endpoints.
- `app/validators.py` handles request validation that should stay outside the route body.
- `app/gemini_service.py` contains the only Gemini-specific code and keeps the API key server-side.
- `app/config.py` centralizes environment-based configuration.
- `app/static/` contains a single-page frontend that posts multipart form data to `/ask`.

## Gemini API Setup

1. Create a Gemini API key in Google AI Studio.
2. Copy `.env.example` to `.env`.
3. Set `GEMINI_API_KEY` in `.env`.
4. Keep the key server-side only. The browser never receives it.

Current default model: `gemini-2.5-flash`

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
- `MODEL_NAME`: Gemini model name. Default is `gemini-2.5-flash`.
- `MAX_UPLOAD_SIZE_BYTES`: backend upload limit. Default is `5242880` for 5 MB.
- `REQUEST_TIMEOUT_SECONDS`: timeout for Gemini API calls.

## Current API Surface

- `GET /health`
  - Returns `{"status": "ok"}`
- `POST /ask`
  - Accepts multipart form data with:
    - `image`
    - `question`
  - Validates:
    - image exists
    - image is one of `image/jpeg`, `image/png`, `image/webp`
    - image is not empty
    - image stays within the configured size limit
    - question exists and is not blank
  - Calls Gemini server-side and returns:

    ```json
    {
      "answer": "The serial number appears to be AX-2048.",
      "model": "gemini-2.5-flash"
    }
    ```

## Running Tests

```bash
pytest
```

## Render Deployment Notes

- `render.yaml` is included for a single Python web service.
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Set `GEMINI_API_KEY` in Render as a secret environment variable.
- Optionally override `MODEL_NAME` in Render if you want to switch models later without code changes.
- The health check points at `/health`.

## Known Limitations

- MIME type validation is based on the uploaded content type and does not inspect file signatures.
- The app handles one image and one question at a time.
- There is no rate limiting, request logging, or analytics yet.
- Gemini responses are plain text only and not structured.

## Remaining Tier 2 Stretch Work

- Add drag-and-drop uploads and a small image preview.
- Add stronger server-side file validation beyond MIME type headers.
- Add structured logging for failed Gemini calls in production.
- Add more `/ask` test coverage around missing fields and file read failures.
- Add a clearer deployment checklist after the first public Render deploy.
