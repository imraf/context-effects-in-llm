# Product Requirements Document (PRD): Context Windows & Long-Context LLM Benchmarking Suite

## 1. Overview
This project aims to implement a comprehensive suite of experiments to analyze the behavior of Large Language Models (LLMs) under varying context conditions. Based on the "Context Windows in Practice" lab, we will evaluate "Lost in the Middle" phenomena, context size impact, RAG effectiveness, and context engineering strategies. The project places a strong emphasis on comparative benchmarking across multiple state-of-the-art open-source models and generating publication-quality visualizations.

## 2. Objectives
-   **Analyze Context Behavior:** Quantify how models handle information retrieval and reasoning as context grows and noise increases.
-   **Compare Models:** Benchmark five specific LLMs (`llama3.2:3b-100K`, `granite3.3:2b-100K`, `gpt-oss:20b-100K`, `gemma3:12b-100K`, `qwen3:14b-100K`) against each other.
-   **Visualize Results:** Produce high-quality, insightful, and aesthetic visualizations (graphs, heatmaps) suitable for academic or professional publication.
-   **Evaluate Strategies:** Determine the efficacy of RAG and specific context engineering techniques (Select, Compress, Write).

## 3. Technical Constraints & Environment
-   **Interpreter:** Strict usage of a virtual environment (`.venv`). **No changes to the system interpreter are allowed.**
-   **LLM Backend:** All model inference must be performed via an Ollama server.
    -   **Connection:** Must use the `OLLAMA_HOST` environment variable.
    -   **Hardware Context:** The server is backed by an A100 (80GB VRAM), allowing for high-throughput and large context handling.
-   **Language:** Python 3.x.
-   **Libraries:** LangChain (orchestration), ChromaDB (vector store), Matplotlib/Seaborn/Plotly (visualization), Pandas (data analysis).

## 4. Target Models
The suite must support and iterate through the following models:
1.  `llama3.2:3b-100K`
2.  `granite3.3:2b-100K`
3.  `gpt-oss:20b-100K`
4.  `gemma3:12b-100K`
5.  `qwen3:14b-100K`

## 5. Experiment Specifications

### Experiment 1: Needle in a Haystack (Lost in the Middle)
-   **Goal:** Detect accuracy drops when critical facts are buried in the middle of the context.
-   **Method:** Insert a specific fact into synthetic documents at Start, Middle, and End positions.
-   **Metric:** Retrieval Accuracy % by position.

### Experiment 2: Context Window Size Impact
-   **Goal:** Correlate context length with performance metrics.
-   **Method:** Query models with increasing document counts (2, 5, 10, 20, 50).
-   **Metrics:** Accuracy, Latency (ms), Token Count.

### Experiment 3: RAG vs. Full Context
-   **Goal:** Compare Retrieval-Augmented Generation against stuffing the full context.
-   **Data:** 20 Hebrew documents from `documents/articles_hebrew/` covering diverse topics.
-   **Method:**
    -   **Full Context:** Concatenate all docs.
    -   **RAG:** Chunk, Embed (Nomic), Store (ChromaDB), Retrieve top-k.
-   **Metrics:** Accuracy, Latency.

### Experiment 4: Context Engineering Strategies
-   **Goal:** Evaluate memory management strategies in a sequential task.
-   **Scenario:** 10-step sequential action simulation.
-   **Strategies:**
    -   **Select:** RAG-based selection of history.
    -   **Compress:** Summarization of history when limit reached.
    -   **Write:** External scratchpad for key facts.
-   **Metric:** Task success rate / Logic consistency.

## 6. Visualization & Reporting Requirements
The output must be "eye-catching, beautiful, and insightful."
-   **Needle in a Haystack:** Heatmaps showing accuracy vs. position (and potentially context depth).
-   **Context Scaling:** Line charts with confidence intervals for Accuracy and Latency vs. Token Count.
-   **RAG Comparison:** Grouped bar charts comparing RAG vs. Full Context across models.
-   **Model Benchmark:** Radar charts comparing the 5 models across all key metrics (Speed, Short-Context Accuracy, Long-Context Accuracy, RAG Performance).
-   **Style:** Use a consistent, professional color palette (e.g., Seaborn `deep` or custom publication theme).

## 7. Deliverables
1.  **Codebase:** Modular Python scripts for running experiments.
2.  **Data:** Raw JSON/CSV logs of all experiment runs.
3.  **Visualizations:** High-resolution PNG/SVG files.
4.  **Final Report:** A Markdown summary embedding the visualizations and interpreting the results.
