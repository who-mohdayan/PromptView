from pathlib import Path
from typing import Annotated
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_gemini_model, is_api_key_configured
from app.gemini_service import analyze_prompt_with_gemini
from app.models import (
    AnalyzeRequest,
    AnalyzeResponse,
    ExamplePrompt,
    HealthResponse,
    PromptBreakdown,
)

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(
    title="PromptView – AI Prompt Visualizer",
    description="Deconstructs natural language prompts into structural components (Role, Task, Context, Constraints, Expected Output) using Gemini API structured JSON.",
    version="1.0.0",
)

# Enable CORS for local development flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CURATED_EXAMPLES: list[ExamplePrompt] = [
    ExamplePrompt(
        id="code-refactor",
        title="Python Code Refactoring",
        category="Engineering",
        prompt=(
            "Act as a Principal Python Architect. Refactor the following legacy synchronous data processing script "
            "into clean, modern async Python code using asyncio and httpx. Keep memory usage strictly below 250MB, "
            "do not use third-party libraries outside httpx, and adhere to PEP 8 standards. "
            "Output the final refactored code with explanatory docstrings followed by a markdown table summarizing time complexity improvements."
        ),
    ),
    ExamplePrompt(
        id="marketing-campaign",
        title="B2B SaaS Product Launch",
        category="Marketing",
        prompt=(
            "You are a seasoned B2B Growth Marketer specializing in developer tooling. "
            "Draft a 3-part email launch sequence announcing our new API observability product to 10,000 backend engineers. "
            "Context: Our users care about sub-millisecond overhead, open telemetry compliance, and self-hosting options. "
            "Avoid buzzwords like 'revolutionary', 'game-changing', or 'next-gen'. Keep each email under 150 words. "
            "Provide the subject line, preview text, and email body formatted in clean Markdown."
        ),
    ),
    ExamplePrompt(
        id="data-analyst",
        title="Executive KPI Synthesis",
        category="Analytics",
        prompt=(
            "You are a Senior Financial Data Analyst. Analyze the Q3 churn rate and customer lifetime value figures "
            "provided in the attached CSV extract. Identify the top 3 drivers of enterprise churn and compare them against SMB cohort benchmarks. "
            "Do not speculate on unverified external factors. State all numbers to one decimal place. "
            "Deliver an executive summary bullet list followed by a 4-row markdown table of prioritized remediation actions."
        ),
    ),
    ExamplePrompt(
        id="socratic-tutor",
        title="Socratic Physics Tutor",
        category="Education",
        prompt=(
            "Act as a patient, encouraging Socratic Physics Professor. Guide a high-school student to understand "
            "Newton's Third Law of Motion without directly giving them the definition or textbook answer. "
            "Ask guiding questions based on everyday experiences like walking on ice or jumping off a boat. "
            "Limit your response to two conversational paragraphs ending with a single reflective question."
        ),
    ),
]


@app.get("/api/health")
async def check_health() -> HealthResponse:
    """Return the health status of PromptView and check API key configuration."""
    return HealthResponse(
        status="healthy",
        api_key_configured=is_api_key_configured(),
        model=get_gemini_model(),
    )


@app.get("/api/examples")
async def get_examples() -> list[ExamplePrompt]:
    """Return pre-configured example prompts for demonstration and testing."""
    return CURATED_EXAMPLES


@app.post(
    "/api/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_prompt(request: AnalyzeRequest) -> AnalyzeResponse:
    """Analyze a user prompt and return structured components."""
    clean_text = request.prompt.strip()
    if not clean_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prompt text cannot be empty or only whitespace.",
        )

    try:
        breakdown: PromptBreakdown = analyze_prompt_with_gemini(clean_text)
        return AnalyzeResponse(success=True, data=breakdown, error=None)
    except ValueError as ve:
        # Configuration or validation issues (e.g., missing API key, empty text)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )
    except RuntimeError as re:
        # Upstream service errors, rate limits, network timeouts
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(re),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during prompt analysis: {str(exc)}",
        )


# Mount static files and serve frontend
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"message": "PromptView frontend is under construction."}
