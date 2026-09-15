from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    prompt: str = Field(
        min_length=1,
        max_length=10000,
        description="The natural language prompt to analyze.",
    )


class PromptBreakdown(BaseModel):
    role: str = Field(
        description="The persona, role, or perspective the AI is asked to adopt (e.g. 'Senior Python Architect', 'Compassionate Medical Assistant'). If unspecified, explains the implied role.",
    )
    task: str = Field(
        description="The primary action, directive, or core problem to solve.",
    )
    context: str = Field(
        description="Background details, domain knowledge, input materials, or situational circumstances provided in the prompt.",
    )
    constraints: list[str] = Field(
        default_factory=list,
        description="Explicit or implicit limitations, rules, what to avoid, formatting restrictions, or tone boundaries.",
    )
    expected_output: str = Field(
        description="The requested output format, deliverable structure, length, or artifact type (e.g. 'Markdown table', 'JSON payload', '3-paragraph email').",
    )
    summary: str = Field(
        description="A concise one-sentence executive summary of what this prompt achieves.",
    )
    completeness_score: int = Field(
        ge=0,
        le=100,
        description="Score between 0 and 100 assessing how well-engineered and specific this prompt is across all five core components.",
    )
    suggestions: list[str] = Field(
        default_factory=list,
        description="Key prompt engineering recommendations to enhance missing or weak elements of this prompt.",
    )


class AnalyzeResponse(BaseModel):
    success: bool = Field(default=True)
    data: PromptBreakdown | None = None
    error: str | None = None


class ExamplePrompt(BaseModel):
    id: str
    title: str
    category: str
    prompt: str


class HealthResponse(BaseModel):
    status: str
    api_key_configured: bool
    model: str
