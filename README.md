# WizyVision Technical Exercise

Live demo: [PASTE_LIVE_RENDER_URL]

Small stateless web app for image question-answering. A user uploads an image, asks a natural-language question about it, and the backend sends both to Gemini and returns an answer. The project is intentionally simple: one FastAPI service, one plain frontend, no auth, no database, and no hidden backend complexity.

## Feature Summary

### Tier 1 MVP
- Image upload with 5 MB client-side validation
- Server-side upload validation for required file, allowed MIME types, and max size
- Natural-language question input
- Gemini image + prompt request handled server-side
- Answer rendering with loading and error states
- Render deployment configuration

### Tier 2 Agentic Vision
- Separate `/ask-agentic` endpoint to preserve the stable Tier 1 `/ask` flow
- Gemini 3 Flash Preview with Code Execution enabled
- Think -> Act -> Observe timeline rendering
- Generated Python code display
- Code execution output display
- Intermediate image display when Gemini returns one

### Tier 3 Polish
- Preset prompt templates for common field-operations questions
- Server-generated request IDs in success and safe error responses
- Request ID display in the UI
- Minimal safe request logging for debugging

## Tech Stack

- Backend: FastAPI
- Frontend: plain HTML, CSS, and vanilla JavaScript
- AI integration: Google `google-genai` SDK
- Tests: pytest
- Deployment: Render

## Architecture

- FastAPI serves both the API and the static frontend so the app stays same-origin and easy to deploy.
- `POST /ask` is the stable Tier 1 endpoint for standard image Q&A.
- `POST /ask-agentic` is the isolated Tier 2 endpoint for agentic image inspection.
- Gemini-specific code is isolated in `app/gemini_service.py`.
- Validation stays in `app/validators.py` so request rules are explicit and testable.

## Security

- `GEMINI_API_KEY` must be stored in environment variables only.
- Gemini API calls happen server-side only.
- No API key is exposed in the frontend bundle.
- `.env` is ignored by git.
- Request logging is intentionally minimal and does not include image contents, API keys, or raw provider internals.

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

4. Add your Gemini API key to `.env`.
5. Start the app:

   ```bash
   python -m uvicorn main:app --reload
   ```

6. Open `http://127.0.0.1:8000`.

If port `8000` is already in use:

```bash
python -m uvicorn main:app --reload --port 8010
```

## Environment Variables

- `APP_NAME`: display name for the FastAPI app
- `APP_ENVIRONMENT`: environment label such as `development` or `production`
- `GEMINI_API_KEY`: Gemini API key, required for real requests
- `MODEL_NAME`: Tier 1 model, default `gemini-2.5-flash`
- `AGENTIC_MODEL_NAME`: Tier 2 model, default `gemini-3-flash-preview`
- `MAX_UPLOAD_SIZE_BYTES`: upload limit, default `5242880`
- `REQUEST_TIMEOUT_SECONDS`: Gemini request timeout

## How To Test

### Normal Mode
- Start the app.
- Leave `Use Agentic Vision mode` unchecked.
- Upload a JPG, PNG, or WEBP image.
- Enter a question or use a prompt template.
- Submit and confirm the answer, loading state, error handling, and request ID display.

### Agentic Vision Mode
- Start the app.
- Check `Use Agentic Vision mode`.
- Upload a supported image.
- Ask a question where zooming, counting, or closer inspection may help.
- Confirm the final answer appears along with the Think -> Act -> Observe timeline.
- If Gemini returns them, confirm Python code, execution output, and intermediate images are displayed.

## Render Deployment Notes

- `render.yaml` configures a single Python web service.
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Set `GEMINI_API_KEY` as a secret environment variable in Render.
- `MODEL_NAME` controls Tier 1.
- `AGENTIC_MODEL_NAME` controls Tier 2.
- Request IDs are generated at runtime and do not need extra deployment setup.

## Known Limitations

- MIME type validation relies on the uploaded content type and does not inspect file signatures.
- The app handles one image and one question at a time.
- Agentic Vision depends on a preview model, so it is less predictable than the stable Tier 1 flow.
- Not every agentic response will include code, execution output, or images.
- Streaming and multi-turn chat were intentionally not implemented to keep the app stateless, easier to review, and easier to explain.

## What I Would Do With More Time

- Add stronger server-side file validation beyond MIME type headers.
- Add more parser coverage around unusual Gemini preview-model responses.
- Add browser-level smoke tests for the prompt template UI and result rendering.
- Add richer production logging or tracing beyond the current lightweight request ID logging.
