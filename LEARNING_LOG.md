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
