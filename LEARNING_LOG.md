# Learning Log

This file documents my honest work process for the WizyVision technical exercise.

## Final Implementation and Validation Session

### Date / Day
- April 26, 2026

### Hours Spent
- Approximately 6 continuous hours

### What I Worked On
- Built and finalized a stateless image Q&A web application for the WizyVision technical exercise.
- Used a FastAPI backend with a plain HTML/CSS/vanilla JavaScript frontend.
- Implemented the Tier 1 MVP where a user can upload an image, ask a natural-language question, and receive a Gemini-generated answer.
- Added client-side and server-side validation for image uploads, including the 5 MB file-size limit and accepted image formats.
- Kept Gemini API calls on the backend so the API key is never exposed in the frontend.
- Deployed the application publicly on Render.
- Added Tier 2 Agentic Vision mode using Gemini 3 Flash Preview with code execution.
- Rendered the Agentic Vision output as a readable Think → Act → Observe timeline.
- Displayed Python code execution, execution output, and intermediate images when returned by the model.
- Added Tier 3 polish features, including field-operations prompt templates and request ID display/logging.
- Strengthened the README, learning log, and submission materials.
- Ran local and deployed validation checks before finalizing the submission.

### Technologies Used
- FastAPI
- Python
- HTML
- CSS
- Vanilla JavaScript
- Gemini API
- Gemini 3 Flash Preview with Code Execution
- Render
- Git and GitHub
- Codex
- ChatGPT

### Prior Familiarity
I chose technologies and workflows that I was already familiar with so I could focus on stability, security, and explainability instead of spending time learning an unfamiliar stack during the exercise.

I was also already familiar with the general shape of this exercise because of my thesis/project experience. Our project, **PawSense: An AI-Enabled Mobile App Using YOLO for Pet Skin Disease Screening and Care Guidance**, integrates computer vision and large language model support. That experience helped me understand image-based AI workflows, model-assisted interpretation, and the importance of presenting AI-generated outputs clearly and responsibly to users.

### What I Got Stuck On
The main challenge was time management rather than one major technical blocker. I had a busy week because of our campus election last Monday, where I monitored and maintained a self-deployed Campus Election Management System that I built. Since there was limited time for a formal MIS deployment, I handled the deployment and monitoring myself. The system ran successfully, and it became one of my first real production deployment experiences.

Another time constraint was our campus Search for Best Thesis. Our project, PawSense, won the Technological Category, and we are currently preparing for the university-level search scheduled on Monday.

On the technical side, the most careful part was implementing Agentic Vision without breaking the already working Tier 1 MVP. I also needed to keep the response parsing simple while still displaying text, Python code, execution output, and intermediate images in a readable way.

### How I Got Unstuck
- I kept the application intentionally simple and stateless.
- I used FastAPI and plain frontend files instead of adding extra frameworks.
- I preserved the stable Tier 1 `/ask` endpoint and added Agentic Vision separately through `/ask-agentic`.
- I used a branch-based workflow to preserve the stable Tier 1 version while implementing Tier 2 and Tier 3 features.
- I relied on the actual working code, test results, and deployed behavior as the source of truth when finalizing the documentation.

### What AI Coding Tools Were Used For
I used Codex and ChatGPT as planning and development assistants. They helped me:
- plan the architecture;
- generate implementation drafts;
- structure the FastAPI backend and static frontend;
- design the validation flow;
- plan the Gemini integration;
- implement and refine the Agentic Vision timeline;
- prepare the README, checklist, and learning log;
- review testing and deployment steps.

I did not treat AI-generated code as automatically correct. I reviewed the implementation, tested the behavior, and kept the code simple enough for me to explain during a technical walkthrough.

### How AI-Generated Code Was Validated
I validated the work through both automated and manual checks.

Automated and code-level validation included:
- running `pytest`;
- running `python -m compileall app tests main.py`;
- checking that `.env` remained ignored;
- checking that the Gemini API key was not committed;
- checking that frontend files did not contain Gemini API key logic;
- checking that Gemini calls happen server-side only.

Manual validation included:
- testing the `/health` endpoint;
- testing the normal Tier 1 image Q&A flow;
- testing the Tier 2 Agentic Vision mode;
- testing image upload behavior;
- testing blank question validation;
- testing invalid file type validation;
- testing the 5 MB upload limit;
- testing prompt template buttons;
- checking that request IDs appeared in responses;
- testing the deployed Render URL after redeployment.

### Decisions Made
- I used FastAPI because it is simple, readable, and easy to explain.
- I used plain HTML/CSS/vanilla JavaScript because the exercise did not require frontend polish or a frontend framework.
- I kept the app stateless because the brief did not require authentication, user accounts, or a database.
- I kept Gemini calls on the backend to protect the API key.
- I kept `/ask` as the stable Tier 1 endpoint and added `/ask-agentic` separately for Agentic Vision.
- I implemented Tier 3 as small, low-risk polish rather than adding complex features.
- I added request IDs for easier debugging without storing user data.

### Trade-Offs Accepted
- I did not use React, Next.js, Tailwind, authentication, or a database because they would add unnecessary complexity.
- I did not implement streaming because it could introduce more risk near the deadline.
- I did not implement multi-turn image chat because the exercise requested a stateless app.
- I kept logging minimal and metadata-focused to avoid logging sensitive information.
- I prioritized a stable, secure, explainable deployment over a highly polished interface.

### What I Would Do Differently With More Time
- Add browser automation tests for the prompt templates and full upload flow.
- Add more structured logging for production use.
- Add request ID response headers in addition to JSON responses.
- Improve the Agentic Vision timeline UI for longer outputs.
- Add more tests for unusual Gemini response shapes.
- Prepare a short demo video or screenshot set for reviewers.