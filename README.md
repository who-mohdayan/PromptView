# PromptView – AI Prompt Visualizer

PromptView is an AI-powered web application that analyzes natural-language prompts and presents their key components in a clear and visual format.

---

## Features

- **Prompt Analysis**: Analyzes a natural-language prompt and identifies key elements such as Role, Task, Context, Constraints, and Expected Output.
- **Visual Breakdown**: Presents the analyzed prompt in a clear and structured visual format for easier understanding.
- **AI-Powered Analysis**: Uses an LLM to process prompts and return structured information.
- **Example Prompts**: Includes ready-to-use examples from different categories to quickly explore the application.
- **Simple & Responsive Interface**: Provides a clean interface for entering prompts and viewing their analysis.
- **Secure API Integration**: Keeps the AI API key on the server and manages requests through the backend.
---

## Tech Stack

- **Backend**: Python 3.12, FastAPI, Pydantic, Uvicorn
- **AI**: Google Gemini API (`gemini-3.8-flash`) via `google-genai`
- **Frontend**: HTML, CSS, JavaScript

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
