# Submission Checklist

Status: Ready for submission after manual placeholder replacement.

## Tier 1 MVP

- [x] Image upload
- [x] Max 5 MB client-side validation
- [x] Server-side file validation
- [x] Text question input
- [x] Backend endpoint calls Gemini with image plus prompt
- [x] Answer rendered in the UI
- [x] Loading state
- [x] Error state
- [x] Public deployment
  - Note: the project is described as already deployed on Render. Replace the live URL placeholders before submitting.
- [x] README includes local run instructions
- [x] README includes deployment notes
- [x] README includes architecture choices
- [x] README includes what I would do with more time

## Non-Negotiables

- [x] Gemini API key is not committed
- [x] Gemini API key is not exposed in frontend files
- [x] Gemini calls happen server-side only
- [x] Public GitHub repository is ready
  - Note: add the final repository URL to `SUBMISSION_NOTE.md`.
- [x] Meaningful commit history exists
- [x] `LEARNING_LOG.md` exists at repo root
- [x] `README.md` exists at repo root

## Tier 2

- [x] Gemini 3 Flash Preview / Agentic Vision mode exists
- [x] Code execution is enabled for agentic mode
- [x] Python code generated/executed by the model is displayed
- [x] Code execution output is displayed
- [x] Intermediate images are displayed when returned
- [x] Think -> Act -> Observe timeline is rendered clearly
- [x] Tier 1 stable flow remains available separately

## Tier 3

- [x] Preset prompt templates exist
- [x] Request ID is generated server-side
- [x] Request ID is returned in responses
- [x] Request ID is displayed in the UI
- [x] Minimal safe request logging exists

## Final Validation Notes

- [x] `.env` is ignored by git
- [x] `.env.example` contains placeholder values only
- [x] Frontend files do not contain Gemini secret handling
- [x] Automated tests pass
- [x] App code compiles

## Manual Placeholders To Replace Before Submission

- [ ] Replace `[PASTE_LIVE_RENDER_URL]` in `README.md`
- [ ] Replace `[PASTE_GITHUB_REPO_LINK]` in `SUBMISSION_NOTE.md`
- [ ] Replace `[PASTE_LIVE_RENDER_URL]` in `SUBMISSION_NOTE.md`
- [ ] Replace hour placeholders in `LEARNING_LOG.md`
