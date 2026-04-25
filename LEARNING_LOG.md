# Learning Log

Use one entry per work session. Keep it honest, short, and specific enough to discuss in a review or interview.

## Session Entry

### Date / Day
- 2026-04-26 (Day 2)

### Hours Spent
- 2.5

### What I Worked On
- Replaced the Gemini stub with a real server-side integration using the official `google-genai` Python SDK.
- Added explicit backend validation for missing files, blank questions, allowed MIME types, and the 5 MB upload cap.
- Kept the frontend simple while tightening the user flow around loading and error states.

### What I Got Stuck On
- I needed to confirm the current official Gemini Python package and the right async request shape for image + text input.

### How I Got Unstuck
- I checked the current Google AI docs and inspected the installed SDK locally before writing the service layer.

### What AI Helped With
- Drafting the first pass of the Gemini service and refining validation/test coverage ideas.

### How I Validated the Output
- Ran automated tests for `/health` and `/ask`.
- Ran syntax checks with `python -m compileall`.
- Manually checked that the frontend still submits `multipart/form-data` and contains no secret handling.

### Trade-Offs I Chose
- I kept MIME validation simple and explainable instead of adding deeper file signature inspection right now.
- I returned safe user-facing Gemini errors instead of detailed provider error payloads.
- I kept the Gemini client creation inside the service call to avoid extra lifecycle complexity in a small app.

### What I Would Do Differently With More Time
- Add a few more backend tests around malformed uploads and provider edge cases.
- Add better production logging around failed Gemini requests.
- Add stronger file-content validation beyond trusting the content type header.

## Session Entry

### Date / Day
- 2026-04-26 (Day 3)

### Hours Spent
- 3.0

### What I Worked On
- Added a separate `/ask-agentic` endpoint so Tier 2 could be implemented without changing the stable `/ask` Tier 1 path.
- Implemented Gemini 3 Flash Preview with Code Execution and a simple parser for thought summaries, executable code, execution results, and intermediate images.
- Updated the vanilla frontend to add an Agentic Vision toggle and render a Think -> Act -> Observe timeline.

### What I Got Stuck On
- The main difficulty was making the Gemini response parsing simple enough to explain while still handling mixed response parts in a useful order.

### How I Got Unstuck
- I checked the official Gemini code execution and thinking docs, then inspected the SDK response types locally before writing the parser.

### What AI Helped With
- Drafting the first pass of the timeline rendering and helping think through how to keep Tier 2 isolated from the MVP path.

### How I Validated the Output
- Ran the existing test suite plus new `/ask-agentic` and parser-focused tests.
- Ran `python -m compileall app tests`.
- Manually verified that the frontend still points normal mode to `/ask` and agentic mode to `/ask-agentic`.
- Checked that no frontend file contains the Gemini API key.

### Trade-Offs I Chose
- I isolated Tier 2 behind `/ask-agentic` instead of folding it into `/ask` to avoid breaking the required MVP.
- I used the last meaningful non-thought text part as the final answer instead of building a more complex response ranking layer.
- I kept the timeline schema flat and explicit so it would stay interview-friendly.

### What I Would Do Differently With More Time
- Add a live end-to-end agentic smoke test behind an explicit opt-in environment flag.
- Improve timeline rendering for multiple text segments that are not final answers.
- Add a more robust parser fallback for unusual preview-model response layouts.

## Session Entry

### Date / Day
- 2026-04-26 (Day 4)

### Hours Spent
- 1.5

### What I Worked On
- Added low-risk Tier 3 polish without changing the core request flow.
- Added preset field-operations prompt template buttons to the frontend.
- Added server-generated request IDs to `/ask` and `/ask-agentic` responses plus minimal server-side request logging.
- Added request ID display in the frontend result area.

### What I Got Stuck On
- The main design choice was deciding how to add request IDs to errors without introducing a lot of custom infrastructure.

### How I Got Unstuck
- I kept the solution small by generating request IDs in FastAPI middleware and using lightweight exception handlers for safe JSON error responses.

### What AI Helped With
- Drafting the first pass of the request ID plumbing and helping keep the frontend additions small and readable.

### How I Validated the Output
- Ran the full test suite after changing the response shape.
- Ran `python -m compileall app tests main.py`.
- Manually checked that prompt buttons populate the textarea and that normal and agentic responses both surface request IDs.

### Trade-Offs I Chose
- I kept request logging minimal and avoided logging questions or image contents.
- I did not add streaming or multi-turn chat because the exercise is easier to reason about and review as a stateless single-request app.
- I kept the prompt templates as plain frontend buttons instead of adding any more elaborate preset management.

### What I Would Do Differently With More Time
- Add a tiny browser-based test harness for template button behavior.
- Consider returning the request ID in a response header as well as JSON.
- Add more structured log formatting if this moved beyond exercise scope.

## Session Template

### Date / Day
- YYYY-MM-DD (Day X)

### Hours Spent
- 0.0

### What I Worked On
- 

### What I Got Stuck On
- 

### How I Got Unstuck
- 

### What AI Helped With
- 

### How I Validated the Output
- 

### Trade-Offs I Chose
- 

### What I Would Do Differently With More Time
- 
