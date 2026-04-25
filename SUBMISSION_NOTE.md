# Submission Note

GitHub repository: [PASTE_GITHUB_REPO_LINK]

Live deployed app: [PASTE_LIVE_RENDER_URL]

This project went well because I kept the scope intentionally tight and built the exercise in layers. The core Tier 1 path is a simple stateless image question-answering app, Tier 2 adds an isolated Agentic Vision mode without disturbing the stable MVP flow, and Tier 3 focuses on small usability and debugging improvements rather than new product complexity. I am especially happy with the separation between the stable `/ask` path and the more experimental `/ask-agentic` path because it keeps the code easier to reason about and safer to demo.

The hardest part was balancing capability with explainability. Gemini integration, code execution parsing, and frontend result rendering can become complicated quickly, so I deliberately chose a plain FastAPI plus vanilla JavaScript architecture and kept the response parsing logic flat and explicit. I also kept request validation, error handling, and security decisions visible in small files so the implementation can be explained line by line during review.

AI assistance was used as a coding accelerant, not as an autopilot. I used AI tools to help scaffold code, refine tests, improve docs, and think through small design decisions, but I validated the output with pytest, compile checks, local request smoke tests, manual repo review, and secret-hygiene checks. I kept the app simple on purpose because the goal of the exercise is not to show the most infrastructure possible, but to ship a clean, secure, review-friendly solution that I can confidently explain.
