# WizyVision Technical Exercise

Small stateless web app scaffold for an image question-answering exercise. A user uploads an image, asks a natural-language question about it, and the backend will eventually send both to Gemini and return the answer.

Current status: the foundation is complete. FastAPI serves a plain HTML/CSS/JavaScript frontend, `/health` is live, `/ask` accepts validated multipart form data, and Gemini integration is intentionally left as a stub.

## Why This Stack

- FastAPI keeps the backend small, explicit, and easy to test.
- Plain HTML, CSS, and vanilla JavaScript keep the frontend easy to explain line by line.
- No database, auth, or frontend framework because the exercise does not need them.
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
- `app/gemini_service.py` is the future integration seam for Gemini.
- `app/config.py` centralizes environment-based configuration.
- `app/static/` contains a single-page frontend that posts multipart form data to `/ask`.

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
   uvicorn app.main:app --reload
   ```

5. Open `http://127.0.0.1:8000`.

## Environment Variables

- `APP_NAME`: display name for the FastAPI app.
- `APP_ENVIRONMENT`: environment label such as `development` or `production`.
- `GEMINI_API_KEY`: Gemini API key. Keep this server-side only.
- `MAX_UPLOAD_SIZE_BYTES`: backend upload limit. Default is `5242880` for 5 MB.
- `REQUEST_TIMEOUT_SECONDS`: reserved for the future Gemini client call.

## Current API Surface

- `GET /health`
  - Returns `{"status": "ok"}`
- `POST /ask`
  - Accepts multipart form data with:
    - `image`
    - `question`
  - Validates:
    - image exists
    - image is `image/*`
    - image is not empty
    - image stays within the configured size limit
    - question is not blank
  - Returns a temporary stub response:

    ```json
    {
      "answer": "Gemini integration not implemented yet.",
      "model": null
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
- The health check points at `/health`.

## Gemini Integration: What Remains

1. Implement the real Gemini call inside `app/gemini_service.py`.
2. Choose the exact model (`Gemini 2.5 Flash` or `Gemini 3 Flash`).
3. Return the real model name in the API response.
4. Add focused tests for validation failures and the happy path.
5. Confirm Render environment variables and end-to-end deployment behavior.

## If I Had More Time

- Add backend tests for `/ask` validation branches.
- Improve logging and request tracing for deployment debugging.
- Add stricter content validation beyond MIME type checks.
- Add a small integration boundary around the Gemini client for easier mocking.
- Add a few basic accessibility and usability refinements to the frontend.
