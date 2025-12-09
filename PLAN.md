# Implementation Plan: Context Windows Lab

## 1. Project Setup & Environment
- **Objective**: Prepare the execution environment for high-performance LLM inference and experimentation.
- **Environment**:
  - **Hardware**: NVIDIA A100 (80GB VRAM).
  - **Software**: Python 3.12+, Ollama (via `OLLAMA_HOST`).
  - **Model**: Custom model `lab-model` based on `llama3.2:3b` (or similar) with extended context window (128k) defined in `modelfile`.
- **Tasks**:
  1.  **Dependencies**: Update `requirements.txt` with `langchain`, `langchain-community`, `chromadb`, `pandas`, `matplotlib`, `seaborn`, `nomic` (or `sentence-transformers`).
  2.  **Model Creation**: Script to run `ollama create lab-model -f modelfile`.
  3.  **Utilities (`utils.py`)**:
      -   `get_llm()`: Returns a configured LangChain/Ollama client.
      -   `generate_text()`: Helper for synthetic data.
      -   `evaluate_answer()`: Helper to compare model output vs expected truth.
      -   `log_result()`: Standardized JSON logger.

## 2. Experiment 1: Needle in a Haystack ("Lost in the Middle")
- **Objective**: Demonstrate accuracy degradation when critical facts are buried in the middle of the context.
- **Data**: 5 synthetic documents (approx. 200 words each).
- **Methodology**:
  1.  Generate "filler" text.
  2.  Insert a specific "needle" (fact) at three positions: `start` (0%), `middle` (50%), `end` (100%).
  3.  Query the model for the needle.
  4.  Repeat $N$ times (e.g., 10 iterations) to ensure statistical significance.
- **Output**: `experiment_1_results.json` containing `{position, accuracy}`.

## 3. Experiment 2: Context Window Size Impact
- **Objective**: Quantify the relationship between context length and model performance (accuracy & latency).
- **Data**: Real text from `hobbit` or `lotr` files.
- **Methodology**:
  1.  Create context chunks of increasing size: equivalent to 2, 5, 10, 20, 50 "documents" (or token counts).
  2.  Formulate a question answerable only from the text.
  3.  Measure:
      -   **Accuracy**: Correctness of answer.
      -   **Latency**: Time to first token / total generation time.
      -   **Token Count**: Exact size of context.
- **Output**: `experiment_2_results.json` containing `{num_docs, tokens_used, latency, accuracy}`.

## 4. Experiment 3: RAG vs. Full Context
- **Objective**: Compare Retrieval-Augmented Generation against stuffing the entire context into the window.
- **Data**: 20 Hebrew documents (domains: Medicine, Law, Technology). *Note: Will generate synthetic Hebrew docs if not provided.*
- **Methodology**:
  1.  **Setup**:
      -   Chunk documents (size ~500 tokens).
      -   Embed using a local embedding model.
      -   Index in ChromaDB.
  2.  **Full Context Mode**: Concatenate all 20 docs into the prompt. Query.
  3.  **RAG Mode**: Retrieve top $k=3$ chunks. Query.
  4.  Compare Accuracy and Latency for both modes.
- **Output**: `experiment_3_results.json` containing `{mode, accuracy, latency}`.

## 5. Experiment 4: Context Engineering Strategies
- **Objective**: Evaluate advanced context management strategies for long-running tasks.
- **Data**: A simulated 10-step sequential task (e.g., a text-based logic puzzle or state tracking).
- **Strategies**:
  1.  **Select (RAG)**: Retrieve only relevant past steps.
  2.  **Compress**: Summarize history when it exceeds a threshold.
  3.  **Write (Scratchpad)**: Maintain a separate "key facts" list, updated at each step.
- **Methodology**:
  1.  Run the 10-step simulation for each strategy.
  2.  At each step, the model must perform an action based on history.
  3.  Evaluate success rate of valid actions/correct state tracking.
- **Output**: `experiment_4_results.json` containing `{strategy, step, success}`.

## 6. Analysis & Reporting
- **Objective**: Visualize results as requested in the lab manual.
- **Tasks**:
  1.  Update `analyze_results.py`.
  2.  **Exp 1**: Bar chart (Accuracy vs. Position).
  3.  **Exp 2**: Dual-axis chart (Accuracy & Latency vs. Context Size).
  4.  **Exp 3**: Grouped bar chart (RAG vs. Full Context).
  5.  **Exp 4**: Line chart or Table (Success Rate over Steps per Strategy).
  6.  Generate `EXPERIMENT_REPORT.md` summarizing findings.
