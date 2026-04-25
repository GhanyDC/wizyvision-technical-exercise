# Learning Log

Use this file as the honest project record for the submission. Replace the hour placeholders with actual values before submitting.

## Session 1

### Date / Day
- Day 1 [confirm/edit]

### Hours Spent
- [replace with actual hours]

### What I Worked On
- Set up the initial FastAPI project structure and served a plain HTML/CSS/vanilla JavaScript frontend from the same backend.
- Added the `/health` endpoint, the first `/ask` scaffold, environment-variable configuration, a minimal test, Render configuration, and the first project documentation.
- Kept the repo deliberately small so the code would stay easy to explain line by line.

### What I Got Stuck On
- The main challenge was deciding how much structure was enough for a hiring exercise without drifting into unnecessary infrastructure.

### How I Got Unstuck
- I kept the app as a single stateless web service with one backend, one static frontend, and no database, auth, or frontend framework.

### What AI Coding Tools Were Used For
- Generating the first scaffold pass, tightening file structure, and reviewing whether the code stayed simple enough for an interview setting.

### How AI-Generated Code Was Validated
- Ran the initial automated health test.
- Started the app locally and verified the frontend was served by FastAPI.
- Reviewed the generated files manually to remove unnecessary complexity.

### Decisions Made
- Use FastAPI for the backend and plain HTML/CSS/JS for the frontend.
- Serve the frontend from FastAPI to keep deployment and local startup simple.
- Keep the app stateless and single-purpose.

### Trade-Offs Accepted
- Skipped frontend frameworks, auth, database, and advanced infrastructure even though they could add polish, because they would make the exercise harder to explain.

### What I Would Do Differently With More Time
- Add stronger automated coverage earlier for the upload flow.
- Add a small browser-based test layer once the main behavior was stable.

## Session 2

### Date / Day
- Day 2 [confirm/edit]

### Hours Spent
- [replace with actual hours]

### What I Worked On
- Replaced the `/ask` stub with a real Gemini image-question workflow using the official `google-genai` Python SDK.
- Added backend validation for blank questions, missing files, unsupported MIME types, unreadable files, and the 5 MB upload cap.
- Updated the frontend so the answer, loading state, and error state worked cleanly with the real backend.
- Added lightweight tests for `/ask`, local startup fixes, and deployment-oriented documentation.
- Prepared the app for Render deployment, reviewed the deployment path, and kept the API key server-side only.

### What I Got Stuck On
- I needed to confirm the current official Gemini Python package and the correct async request shape for image plus text input.
- I also hit a local import/startup issue that affected pytest and local server startup reliability.

### How I Got Unstuck
- Checked the official Gemini documentation and inspected the installed SDK locally before writing the service layer.
- Added a simple top-level entrypoint and pytest import shim so the app and tests started reliably.

### What AI Coding Tools Were Used For
- Drafting the first pass of the Gemini service, validation flow, and test cases.
- Reviewing the structure to keep the API boundary small and interview-friendly.

### How AI-Generated Code Was Validated
- Ran `pytest`.
- Ran `python -m compileall`.
- Performed local request smoke tests.
- Confirmed `.env` stayed ignored and that no frontend file handled the API key.
- Verified the Render configuration matched the intended single-service deployment.

### Decisions Made
- Keep Gemini calls isolated in `app/gemini_service.py`.
- Load `GEMINI_API_KEY` only from environment variables.
- Return safe user-facing Gemini errors instead of raw provider payloads.

### Trade-Offs Accepted
- Trusted MIME type headers for upload validation instead of adding deeper file signature inspection in the first pass.
- Kept the Gemini client lifecycle simple rather than introducing a more elaborate service container.

### What I Would Do Differently With More Time
- Add deeper validation for uploaded files.
- Add more logging around provider failures in production.
- Add a small integration-test strategy around the Gemini client boundary.

## Session 3

### Date / Day
- Day 3 [confirm/edit]

### Hours Spent
- [replace with actual hours]

### What I Worked On
- Added Tier 2 Agentic Vision on a separate `/ask-agentic` endpoint so the Tier 1 `/ask` flow stayed stable.
- Used Gemini 3 Flash Preview with Code Execution enabled.
- Parsed mixed Gemini response parts into a readable Think -> Act -> Observe timeline.
- Displayed generated Python code, code execution output, and intermediate images when returned.
- Updated the frontend to toggle between normal mode and agentic mode without changing the Tier 1 UX.

### What I Got Stuck On
- The hardest part was keeping the agentic response parser simple while still handling text, code, output, and images in a useful order.

### How I Got Unstuck
- Checked the official Gemini code execution and thinking documentation, then inspected the SDK response types locally before writing the parser.
- Kept the parser flat and explicit instead of building a more abstract response-processing layer.

### What AI Coding Tools Were Used For
- Drafting the first pass of the agentic service, timeline schema, and frontend timeline rendering.
- Thinking through how to isolate Tier 2 from the required MVP path.

### How AI-Generated Code Was Validated
- Added tests for `/ask-agentic`.
- Added a parser-focused test for the Gemini response mapping.
- Ran `pytest` and `python -m compileall`.
- Performed mocked endpoint smoke tests for `/health`, `/ask`, and `/ask-agentic`.

### Decisions Made
- Keep `/ask` as the stable Tier 1 endpoint and add `/ask-agentic` separately.
- Use the last meaningful non-thought text part as the final answer.
- Show agentic reasoning as a timeline instead of dumping raw provider output.

### Trade-Offs Accepted
- Agentic mode depends on a preview model and is therefore less predictable than the stable Tier 1 path.
- I did not build a richer orchestration layer because it would make the code harder to explain.

### What I Would Do Differently With More Time
- Add more parser coverage for unusual preview-model response layouts.
- Add a real opt-in live smoke test for agentic mode.
- Improve the timeline presentation for longer mixed responses.

## Session 4

### Date / Day
- Day 4 [confirm/edit]

### Hours Spent
- [replace with actual hours]

### What I Worked On
- Added low-risk Tier 3 polish without changing the core backend behavior.
- Added preset prompt templates for serial-number reading, counting visible items, PPE checks, and visible-damage inspection.
- Added server-generated request IDs for `/ask` and `/ask-agentic`.
- Included request IDs in successful responses and safe error responses where practical.
- Added minimal request logging with request ID, endpoint, mode, model, success/failure, and status code.
- Displayed the request ID in the frontend result area.

### What I Got Stuck On
- The main design question was how to add request IDs to errors without introducing a lot of custom infrastructure or changing working behavior too much.

### How I Got Unstuck
- Kept the solution small by generating request IDs in middleware and using lightweight JSON exception handlers.
- Avoided logging image content, question text, or sensitive configuration.

### What AI Coding Tools Were Used For
- Drafting the request ID plumbing, updating the response contract in tests, and keeping the frontend polish small and readable.

### How AI-Generated Code Was Validated
- Re-ran the full test suite after changing the response shape.
- Ran `python -m compileall app tests main.py`.
- Performed mocked smoke checks to verify request IDs appeared in both normal and agentic responses.
- Manually checked that prompt template buttons were wired correctly.

### Decisions Made
- Keep prompt templates as plain frontend buttons with explicit text.
- Return request IDs in JSON instead of introducing a second response-channel abstraction.
- Keep logging intentionally minimal and metadata-only.

### Trade-Offs Accepted
- I did not add browser automation for the prompt template buttons.
- I did not return request IDs in headers because JSON was enough for this exercise.

### What I Would Do Differently With More Time
- Add a tiny browser-based test harness for the prompt template UI.
- Consider adding a response header for request ID in addition to the JSON field.
- Add more structured logging if the app moved beyond exercise scope.

## Session 5

### Date / Day
- Final submission pass [confirm/edit]

### Hours Spent
- [replace with actual hours]

### What I Worked On
- Performed a final submission-readiness review of the repo, docs, ignore rules, example environment file, and static frontend files.
- Strengthened the README so it clearly explains the project overview, tiered feature set, architecture, security posture, local setup, Render deployment, testing approach, limitations, and future work.
- Added `SUBMISSION_CHECKLIST.md` to verify the stated exercise requirements against the implemented repo.
- Added `SUBMISSION_NOTE.md` with placeholders for the GitHub repository link and live Render URL.
- Cleaned up the learning log so it reflects the actual implementation path more honestly and completely.

### What I Got Stuck On
- The main challenge was keeping the final materials honest and concise while still covering the full scope from Tier 1 through Tier 3.

### How I Got Unstuck
- Used the commit history, current implementation, tests, and deployment configuration as the source of truth instead of relying on memory.

### What AI Coding Tools Were Used For
- Tightening documentation language, organizing the submission checklist, and cross-checking that the final materials matched the implemented code.

### How AI-Generated Code Was Validated
- Ran `pytest`.
- Ran `python -m compileall app tests main.py`.
- Ran `git grep GEMINI_API_KEY`.
- Ran `git status --ignored`.
- Confirmed `.env` remained ignored and untracked.
- Confirmed no frontend file contains secret handling or backend-only Gemini logic.

### Decisions Made
- Keep the final pass documentation-heavy and avoid introducing any new product features.
- Use placeholders for missing external links and actual hours instead of inventing values.

### Trade-Offs Accepted
- The final docs use placeholders for the public repository link, live URL, and hours where the repo itself cannot prove the exact value.

### What I Would Do Differently With More Time
- Add a short screen-recording or screenshot set for the submission.
- Add one final browser-based smoke test as part of the readiness checklist.

## Session Template

### Date / Day
- YYYY-MM-DD (Day X)

### Hours Spent
- [replace with actual hours]

### What I Worked On
- 

### What I Got Stuck On
- 

### How I Got Unstuck
- 

### What AI Coding Tools Were Used For
- 

### How AI-Generated Code Was Validated
- 

### Decisions Made
- 

### Trade-Offs Accepted
- 

### What I Would Do Differently With More Time
- 
