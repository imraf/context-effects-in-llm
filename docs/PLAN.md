# Implementation Plan: Context Windows Benchmarking Suite

## Phase 1: Environment & Infrastructure Setup
**Goal:** Establish a robust, isolated development environment.

1.  **Virtual Environment:**
    -   Create `.venv` using `python -m venv .venv`.
    -   Create activation helper script (optional) or documentation.
2.  **Dependencies:**
    -   Create `requirements.txt` including:
        -   `langchain`, `langchain-community`, `langchain-chroma`
        -   `ollama` (Python client)
        -   `chromadb`
        -   `pandas`, `numpy`
        -   `matplotlib`, `seaborn` (for static high-quality plots)
        -   `tqdm` (for progress bars)
3.  **Configuration:**
    -   Create `config.py` to manage:
        -   `OLLAMA_HOST` retrieval from env.
        -   List of Models.
        -   Experiment parameters (seeds, document counts, etc.).

## Phase 2: Data Generation Module
**Goal:** Create reproducible datasets for all experiments.

1.  **Synthetic Text Generator (Exp 1 & 2):**
    -   Implement `generate_filler_text(word_count)` using a lorem ipsum library or simple dictionary.
    -   Implement `embed_fact(text, fact, position)` to inject needles.
2.  **Document Loading (Exp 3):**
    -   Load the 20 Hebrew documents from `documents/articles_hebrew/`.
    -   Load the 150 English articles from `documents/articles_english/` (if needed for other experiments).
    -   Ensure metadata is loaded from `documents/articles_metadata.json`.
3.  **Sequential Task Simulator (Exp 4):**
    -   Design a simple state-machine or logic puzzle that requires remembering previous steps (e.g., "I put the apple in the box", "I moved the box to the kitchen").

## Phase 3: Core Experiment Implementation
**Goal:** Implement the logic for each experiment, decoupled from the specific model.

1.  **LLM Interface:**
    -   Create a wrapper class `OllamaClient` that respects `OLLAMA_HOST` and handles retries/timeouts.
2.  **Experiment 1 (Needle):**
    -   Script `exp1_needle.py`: Loop through [Start, Middle, End] positions.
    -   Output: `results/exp1_{model}.json`.
3.  **Experiment 2 (Context Size):**
    -   Script `exp2_size.py`: Loop through doc counts [2, 5, 10, 20, 50]. Measure time and check answer correctness.
    -   Output: `results/exp2_{model}.json`.
4.  **Experiment 3 (RAG):**
    -   Script `exp3_rag.py`:
        -   Setup ChromaDB.
        -   Run "Full Context" query.
        -   Run "RAG" query.
    -   Output: `results/exp3_{model}.json`.
5.  **Experiment 4 (Strategies):**
    -   Script `exp4_strategies.py`: Implement the `Select`, `Compress`, and `Write` logic flows.
    -   Output: `results/exp4_{model}.json`.

## Phase 4: Orchestration & Execution
**Goal:** Run the full suite across all models automatically.

1.  **Master Runner:**
    -   Create `main.py` or `run_benchmark.py`.
    -   Iterate through the model list defined in PRD.
    -   For each model, run Exp 1-4 sequentially.
    -   Handle model loading/unloading (if necessary via API) or warm-up calls.
    -   **Crucial:** Save intermediate results to disk immediately to prevent data loss on crash.

## Phase 5: Visualization & Reporting Engine
**Goal:** Transform raw JSON data into publication-quality assets.

1.  **Data Aggregation:**
    -   Script `analyze_results.py` to load all JSONs into a unified Pandas DataFrame.
2.  **Plot Generation (The "Wow" Factor):**
    -   **Style:** Set global matplotlib style (e.g., `plt.style.use('seaborn-v0_8-paper')`).
    -   **Plot 1: The "Lost in the Middle" Heatmap:** X-axis=Context Size, Y-axis=Model, Color=Accuracy Drop in Middle.
    -   **Plot 2: Performance Scaling:** Multi-line chart (Accuracy vs Tokens) for all models.
    -   **Plot 3: RAG Efficiency:** Grouped Bar Chart (Latency & Accuracy) comparing RAG vs Full.
    -   **Plot 4: The "Model Radar":** A normalized radar chart comparing the 5 models on:
        -   Retrieval Accuracy
        -   Reasoning (Exp 4)
        -   Speed
        -   Context Tolerance
3.  **Report Generation:**
    -   Auto-generate `BENCHMARK_REPORT.md` that includes the generated images and summary tables.

## Phase 6: Verification
1.  Verify `.venv` usage.
2.  Verify `OLLAMA_HOST` connectivity.
3.  Dry run with a small model (or one of the target models) to ensure pipeline stability.
