/**
 * PromptView - AI Prompt Visualizer
 * Client-side Controller (Vanilla ES6+)
 */

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const promptInput = document.getElementById("promptInput");
  const charCounter = document.getElementById("charCounter");
  const analyzeBtn = document.getElementById("analyzeBtn");
  const clearBtn = document.getElementById("clearBtn");
  const examplesContainer = document.getElementById("examplesContainer");
  const loadingPanel = document.getElementById("loadingPanel");
  const resultsSection = document.getElementById("resultsSection");
  const alertBanner = document.getElementById("alertBanner");
  const alertTitle = document.getElementById("alertTitle");
  const alertDesc = document.getElementById("alertDesc");
  const alertCloseBtn = document.getElementById("alertCloseBtn");
  const toast = document.getElementById("toast");
  const toastText = document.getElementById("toastText");

  // Visual Breakdown Elements
  const summaryText = document.getElementById("summaryText");
  const scoreCircle = document.getElementById("scoreCircle");
  const scoreStatus = document.getElementById("scoreStatus");
  const roleHighlight = document.getElementById("roleHighlight");
  const roleDescription = document.getElementById("roleDescription");
  const taskMain = document.getElementById("taskMain");
  const contextBody = document.getElementById("contextBody");
  const constraintsList = document.getElementById("constraintsList");
  const outputBox = document.getElementById("outputBox");
  const suggestionsCard = document.getElementById("suggestionsCard");
  const suggestionsList = document.getElementById("suggestionsList");

  // Export Action Buttons
  const copyMarkdownBtn = document.getElementById("copyMarkdownBtn");
  const copyJsonBtn = document.getElementById("copyJsonBtn");
  const copyOptimizedBtn = document.getElementById("copyOptimizedBtn");

  // Application State
  let currentBreakdown = null;
  let curatedExamples = [];
  let loadingInterval = null;

  // 1. Initialize API Health Check
  async function checkApiHealth() {
    try {
      const res = await fetch("/api/health");
      if (!res.ok) throw new Error("Health check failed");
      const data = await res.json();

      if (!data.api_key_configured) {
        showAlert(
          "API Key Required",
          "Gemini API key is not configured. Add your <code>GEMINI_API_KEY=your_key</code> in the <code>.env</code> file in the project root to analyze live prompts.",
          "warning"
        );
      }
    } catch (err) {
      // Backend service unreachable
    }
  }

  // 2. Load Curated Examples
  async function loadExamples() {
    try {
      const res = await fetch("/api/examples");
      if (!res.ok) return;
      curatedExamples = await res.json();
      renderExampleChips(curatedExamples);
    } catch (err) {
      console.warn("Could not load examples from backend:", err);
    }
  }

  function renderExampleChips(examples) {
    if (!examples || !examples.length) return;
    examplesContainer.innerHTML = '<span class="examples-title">Try Example:</span>';
    
    examples.forEach((item) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "example-chip";
      button.dataset.exampleId = item.id;
      button.innerHTML = `
        <span class="chip-cat">${escapeHtml(item.category)}</span>
        <span>${escapeHtml(item.title)}</span>
      `;
      button.addEventListener("click", () => {
        promptInput.value = item.prompt;
        updateCharCounter();
        hideAlert();
        promptInput.focus();
        // Visual feedback on selected chip
        document.querySelectorAll(".example-chip").forEach(c => c.style.borderColor = "");
        button.style.borderColor = "var(--color-primary)";
      });
      examplesContainer.appendChild(button);
    });
  }

  // 3. Textarea Input Handlers
  function updateCharCounter() {
    const len = promptInput.value.length;
    charCounter.textContent = `${len.toLocaleString()} / 10,000`;
  }

  promptInput.addEventListener("input", () => {
    updateCharCounter();
    hideAlert();
  });

  promptInput.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      analyzeBtn.click();
    }
  });

  clearBtn.addEventListener("click", () => {
    promptInput.value = "";
    updateCharCounter();
    hideAlert();
    resultsSection.style.display = "none";
    currentBreakdown = null;
    promptInput.focus();
  });

  // 4. Alert Helpers
  function showAlert(title, description, type = "error") {
    alertTitle.textContent = title;
    alertDesc.innerHTML = description;
    alertBanner.className = `alert-banner ${type}`;
    alertBanner.style.display = "flex";
  }

  function hideAlert() {
    alertBanner.style.display = "none";
  }

  alertCloseBtn.addEventListener("click", hideAlert);

  // 5. Toast Feedback
  function showToast(message) {
    toastText.textContent = message;
    toast.classList.add("show");
    setTimeout(() => {
      toast.classList.remove("show");
    }, 2800);
  }

  // 6. Loading Animation Step Cycle
  const loadingSubtitles = [
    "Deconstructing Role, Task, Context, Constraints, and Expected Output via Gemini...",
    "Analyzing prompt tone, persona, and directive boundaries...",
    "Extracting schema rules and negative constraints...",
    "Evaluating prompt completeness and structural quality..."
  ];

  function startLoadingState() {
    analyzeBtn.disabled = true;
    loadingPanel.style.display = "block";
    resultsSection.style.display = "none";
    hideAlert();

    const subtitleEl = document.getElementById("loadingSubtitle");
    let stepIndex = 0;
    loadingInterval = setInterval(() => {
      stepIndex = (stepIndex + 1) % loadingSubtitles.length;
      if (subtitleEl) subtitleEl.textContent = loadingSubtitles[stepIndex];
    }, 1200);

    loadingPanel.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function stopLoadingState() {
    analyzeBtn.disabled = false;
    loadingPanel.style.display = "none";
    if (loadingInterval) {
      clearInterval(loadingInterval);
      loadingInterval = null;
    }
  }

  // 7. Analyze Prompt
  async function handleAnalyze() {
    const rawPrompt = promptInput.value.trim();
    if (!rawPrompt) {
      showAlert("Empty Prompt", "Please enter or paste a prompt above to analyze.", "warning");
      promptInput.focus();
      return;
    }

    startLoadingState();

    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: rawPrompt }),
      });

      const result = await response.json();

      if (!response.ok) {
        const errorDetail = result.detail || "Unable to analyze prompt. Please try again.";
        throw new Error(errorDetail);
      }

      if (result.success && result.data) {
        currentBreakdown = result.data;
        renderBreakdown(result.data);
      } else {
        throw new Error(result.error || "Unexpected response format from server.");
      }
    } catch (err) {
      showAlert("Analysis Error", escapeHtml(err.message), "error");
    } finally {
      stopLoadingState();
    }
  }

  analyzeBtn.addEventListener("click", handleAnalyze);

  // 8. Render Structural Breakdown Cards
  function renderBreakdown(data) {
    // Summary
    summaryText.textContent = data.summary || "Structural decomposition complete.";

    // Score Circle & Status
    const score = data.completeness_score ?? 85;
    scoreCircle.textContent = `${score}%`;
    if (score >= 90) {
      scoreStatus.textContent = "Production Grade";
      scoreCircle.style.color = "var(--color-success)";
      scoreCircle.style.borderColor = "var(--color-success)";
    } else if (score >= 75) {
      scoreStatus.textContent = "Well-Structured";
      scoreCircle.style.color = "var(--color-primary)";
      scoreCircle.style.borderColor = "var(--color-primary)";
    } else {
      scoreStatus.textContent = "Needs Context";
      scoreCircle.style.color = "var(--color-bloom-coral)";
      scoreCircle.style.borderColor = "var(--color-bloom-coral)";
    }

    // Role
    roleHighlight.textContent = data.role || "General AI Assistant (Implied)";
    roleDescription.textContent = data.role
      ? "Target persona and expertise profile defined in the prompt."
      : "No explicit persona specified; defaults to standard helpful AI voice.";

    // Task
    taskMain.textContent = data.task || "No primary task detected.";

    // Context
    contextBody.textContent = data.context || "No specific background context or domain data provided.";

    // Constraints
    constraintsList.innerHTML = "";
    if (data.constraints && data.constraints.length > 0) {
      data.constraints.forEach((rule) => {
        const li = document.createElement("li");
        li.className = "constraint-item";
        li.innerHTML = `<span class="constraint-bullet">•</span><span>${escapeHtml(rule)}</span>`;
        constraintsList.appendChild(li);
      });
    } else {
      const li = document.createElement("li");
      li.className = "constraint-item";
      li.style.borderLeftColor = "var(--color-steel)";
      li.innerHTML = '<span style="color: var(--color-graphite);">No explicit restrictions or negative constraints specified.</span>';
      constraintsList.appendChild(li);
    }

    // Expected Output
    outputBox.textContent = data.expected_output || "Unspecified (Freeform text response)";

    // Suggestions Drawer
    if (data.suggestions && data.suggestions.length > 0) {
      suggestionsList.innerHTML = "";
      data.suggestions.forEach((item) => {
        const li = document.createElement("li");
        li.className = "suggestion-item";
        li.innerHTML = `<span class="suggestion-icon">→</span><span>${escapeHtml(item)}</span>`;
        suggestionsList.appendChild(li);
      });
      suggestionsCard.style.display = "block";
    } else {
      suggestionsCard.style.display = "none";
    }

    // Display Results Section with smooth entrance
    resultsSection.style.display = "block";
    resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  // 9. Export & Copy Actions
  copyMarkdownBtn.addEventListener("click", () => {
    if (!currentBreakdown) return;
    const md = [
      `# Prompt Specification Breakdown`,
      `**Summary**: ${currentBreakdown.summary}`,
      `**Completeness Score**: ${currentBreakdown.completeness_score}%`,
      ``,
      `### 1. Role & Persona`,
      `${currentBreakdown.role}`,
      ``,
      `### 2. Core Task`,
      `${currentBreakdown.task}`,
      ``,
      `### 3. Context & Background`,
      `${currentBreakdown.context}`,
      ``,
      `### 4. Constraints & Rules`,
      ...(currentBreakdown.constraints || []).map((c) => `- ${c}`),
      ``,
      `### 5. Expected Output`,
      `${currentBreakdown.expected_output}`,
    ].join("\n");

    copyToClipboard(md, "Markdown specification copied!");
  });

  copyJsonBtn.addEventListener("click", () => {
    if (!currentBreakdown) return;
    const jsonStr = JSON.stringify(currentBreakdown, null, 2);
    copyToClipboard(jsonStr, "Structured JSON copied!");
  });

  copyOptimizedBtn.addEventListener("click", () => {
    if (!currentBreakdown) return;
    const reconstructed = [
      `[Role]: Act as ${currentBreakdown.role}.`,
      `[Task]: ${currentBreakdown.task}`,
      `[Context]: ${currentBreakdown.context}`,
      `[Constraints]:`,
      ...(currentBreakdown.constraints || []).map((c) => `  - ${c}`),
      `[Expected Output]: ${currentBreakdown.expected_output}`,
    ].join("\n");

    copyToClipboard(reconstructed, "Reconstructed prompt copied!");
  });

  function copyToClipboard(text, successMsg) {
    navigator.clipboard.writeText(text).then(
      () => showToast(successMsg),
      () => {
        // Fallback for older browsers
        const temp = document.createElement("textarea");
        temp.value = text;
        document.body.appendChild(temp);
        temp.select();
        document.execCommand("copy");
        document.body.removeChild(temp);
        showToast(successMsg);
      }
    );
  }

  function escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // Kickoff on load
  checkApiHealth();
  loadExamples();
  updateCharCounter();
});
