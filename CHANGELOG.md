# ExamForge Changelog

All notable development stages and improvements to ExamForge are documented here.

---

## 2026-11-22 — Milestone 2: Functional Question-Generation Prototype

> **Milestone 2 was reached through iterative implementation and testing.**

### AI connection and generation
- Configured the Gemini API client and environment-variable support.
- Verified available Gemini models and replaced an unavailable model with a supported model.
- Added bounded Gemini API retry handling with visible attempt progress and delays.
- Implemented prompt variants V1, V2 and V3 for prompt experimentation.
- Added prompt-version dependency updates so the active generator uses V3.

### Document processing
- Added PDF text extraction with PyMuPDF.
- Added TXT document support.
- Added page-by-page extraction progress.
- Added empty-document and unreadable-document validation.

### Question generation
- Reduced the project scope to question generation for faculty and teaching assistants.
- Added MCQ, True/False and Short Answer question types.
- Added individual question-count controls for each format.
- Added mixed-format question generation.
- Added generated-question and answer validation.
- Added a source-based 100-point structural quality score.
- Added quality dimensions for completeness, format, source relevance, clarity and specificity.

### Faculty question-bank experience
- Added a dedicated generated-questions page.
- Redesigned questions as readable academic question cards.
- Added clear question numbers, question types and quality scores.
- Added options, model answers and explanations.
- Added Copy All and TXT download actions.
- Added a button to create another question set.

### Interface and accessibility
- Redesigned the app as a professional educational interface.
- Consolidated overlapping CSS into a reusable theme system.
- Added light and dark themes with theme state persistence.
- Added a responsive top navigation bar.
- Replaced unreliable pill navigation with interactive buttons and callbacks.
- Improved contrast for inputs, dropdowns, file uploader, alerts, status widgets and navigation.
- Increased project-name, question and question-number typography.
- Added upload, extraction, generation and retry status updates.
- Fixed the uploaded-file success-text contrast issue.
- Removed generated HTML, Markdown fences and markup artifacts from model output.

### Project hosting and documentation
- Prepared the project for GitHub and Streamlit Community Cloud.
- Added Streamlit secrets support.
- Added a hosted prototype link.
- Expanded the README with setup, features, project structure and team members.
- Documented the team members and student IDs.

### Scope cleanup
- Removed student-examination submission and grading flows.
- Removed AI quality-evaluation API calls.
- Removed automatic question-refinement workflows.
- Kept the project focused on faculty question generation.

---

## 2026-11-21 — Setup and Integration Iteration

### Development environment
- Created the initial project structure.
- Created and activated a Python virtual environment.
- Added Streamlit, Google Gemini SDK, python-dotenv, PyMuPDF and Pandas dependencies.
- Created environment-variable support for `GEMINI_API_KEY`.

### Gemini integration
- Added Gemini client configuration.
- Tested API connectivity.
- Listed accessible Gemini models.
- Tested multiple listed models and selected a supported model.
- Investigated temporary 503 and 404 model responses.

### Initial application modules
- Added document processing modules.
- Added question-generation modules.
- Added an initial Streamlit interface.
- Added separate prompts and project configuration.

---

## 2026-10-11 — Milestone 1: Project Foundation

### Initial concept
- Defined ExamForge as an educational question-generation application.
- Identified the target users as faculty members and teaching assistants.
- Defined the project as a tool for generating assessment questions from uploaded study material.

### Foundation planning
- Planned a Streamlit-based Python application.
- Planned Gemini API integration.
- Planned PDF and TXT document support.
- Planned MCQ, True/False and Short Answer question formats.
- Established the core goal: reduce manual preparation of examination questions.

---

## Prompt Development

| Prompt | Purpose |
|---|---|
| `generation_v1.py` | Initial general question-generation prompt |
| `generation_v2.py` | Improved material grounding and format instructions |
| `generation_v3.py` | Active prompt with exact counts, plain-text output and anti-markup instructions |

---

## Team

- **Dishubh Singh** — S24CSEU0808
- **Gadde Tanishq** — S24CSEU0793

## Prototype

**[ExamForge · Streamlit](https://examforge.streamlit.app/)**
