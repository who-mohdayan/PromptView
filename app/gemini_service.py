import logging
from google import genai
from app.config import get_gemini_api_key, get_gemini_model, is_api_key_configured
from app.models import PromptBreakdown

logger = logging.getLogger(__name__)

ANALYSIS_SYSTEM_INSTRUCTION = """
You are an expert Prompt Engineering Architect and Prompt Visualization Engine.
Your job is to analyze any natural-language prompt provided by a user and deconstruct it into its fundamental structural components:

1. Role: The persona, identity, tone, or specific professional domain the AI is instructed or implied to act as.
2. Task: The single core objective, instruction, or problem the prompt directs the AI to perform.
3. Context: The background information, reference data, scenario, domain constraints, or inputs supplied.
4. Constraints: Explicit or implicit boundaries, negative constraints (what NOT to do), length caps, tone guidelines, and rule restrictions.
5. Expected Output: The concrete format, deliverable structure, style, or artifact requested (e.g., Markdown table, JSON schema, bulleted summary).
6. Summary: A crystal-clear 1-sentence synopsis of what the prompt achieves.
7. Completeness Score: A realistic quality score (0 to 100) assessing how comprehensive, unambiguous, and production-ready this prompt is.
8. Suggestions: 1 to 3 specific, actionable recommendations on how the author can improve this prompt (e.g. adding missing constraints, specifying output formats, or defining edge cases).

Ensure every field is thoroughly populated with clear, concise, actionable text.
"""


def analyze_prompt_with_gemini(prompt: str) -> PromptBreakdown:
    """
    Analyzes a prompt using the Google Gemini API with structured JSON output.
    Raises ValueError or RuntimeError with clear messages if errors occur.
    """
    if not is_api_key_configured():
        raise ValueError(
            "Gemini API key is not configured. Please add your GEMINI_API_KEY to the .env file."
        )

    clean_prompt = prompt.strip()
    if not clean_prompt:
        raise ValueError("Prompt cannot be empty.")

    api_key = get_gemini_api_key()
    configured_model = get_gemini_model()
    client = genai.Client(api_key=api_key)

    # Models to try (in case primary model experiences transient 503 high demand spikes)
    models_to_try = [configured_model]
    if configured_model != "gemini-3.5-flash-lite":
        models_to_try.append("gemini-3.5-flash-lite")

    last_error = None
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=f"{ANALYSIS_SYSTEM_INSTRUCTION}\n\nDeconstruct this prompt into the structured schema:\n```\n{clean_prompt}\n```",
                config={
                    "response_mime_type": "application/json",
                    "response_schema": PromptBreakdown,
                },
            )
            if response.text:
                return PromptBreakdown.model_validate_json(response.text)
        except Exception as err:
            err_str = str(err)
            logger.warning("Gemini generation attempt with %s failed: %s", model_name, err_str)
            last_error = err
            # If invalid API key, fail fast without trying other models
            if any(k in err_str.lower() for k in ["api_key_invalid", "invalid api key", "unauthenticated", "401"]):
                raise ValueError("Invalid Gemini API key. Please check your key in the .env file.")
            # If 503 or transient spike, loop continues to the next candidate model
            continue

    err_msg = str(last_error)
    if "RESOURCE_EXHAUSTED" in err_msg or "quota" in err_msg.lower() or "429" in err_msg:
        raise RuntimeError("Gemini API rate limit or quota exceeded. Please try again in a few moments.")
    raise RuntimeError(f"Gemini API analysis failed: {err_msg}")
