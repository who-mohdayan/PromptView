# PromptView – AI Prompt Visualizer

A clean, professional prompt engineering and visualization web application that takes raw natural-language prompts and decomposes them into their five fundamental structural components using **Google Gemini API** structured JSON output.

---

## Features

- **Structural Decomposition**: Extracts and visually displays:
  - **Role**: Persona, tone, and domain perspective.
  - **Task**: The primary directive or core problem to solve.
  - **Context**: Background knowledge, reference data, and scenario details.
  - **Constraints**: Explicit rules, limitations, and negative constraints.
  - **Expected Output**: Deliverable schema, style, length, or format.
- **Clarity & Completeness Meter**: Scores prompt readiness (0–100%) and provides architectural prompt engineering recommendations.
- **Modern Design System**: Styled according to `DESIGN.md` using HP Electric Blue (`#024ad8`), crisp ink typography (`#1a1a1a`), 16px soft-radius cards, 4px uppercase CTA buttons, and geometric chevron motifs.
- **Interactive Example Library**: 1-click loading for Engineering, Marketing, Analytics, and Education prompts.
- **Export & Reconstruct**: Copy as formatted Markdown, raw structured JSON, or an optimized prompt reconstruction with a single click.
- **Fast & Secure**: Built with FastAPI, Pydantic, and Vanilla JS. API keys are stored server-side in `.env` and never exposed to the client.

---

## Tech Stack

- **Backend**: Python 3.12, FastAPI, Pydantic, Uvicorn
- **AI**: Google Gemini API (`gemini-3.8-flash`) via `google-genai`
- **Frontend**: Semantic HTML5, Vanilla CSS3 (tokenized), Vanilla JavaScript (ES6+)

---

## Quickstart

### 1. Configure Environment Variables
Copy `.env.example` to `.env` and insert your Gemini API key:
```bash
cp .env.example .env
```
Inside `.env`:
```ini
GEMINI_API_KEY=AIzaSy...your_gemini_api_key_here
GEMINI_MODEL=gemini-3.8-flash
PORT=8000
HOST=127.0.0.1
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Development Server
```bash
uvicorn app.main:app --reload --port 8000
```
Open your browser at: `http://127.0.0.1:8000`

---

## Running Tests
Run the backend test suite:
```bash
python -m unittest tests/test_api.py
```
