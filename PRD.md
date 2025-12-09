# Product Requirements Document (PRD): Context Windows Lab

**Author**: Dr. Yoram Segal (Lab Instructor) / Copilot (Implementation)  
**Date**: December 9, 2025  
**Version**: 1.0  

## 1. Introduction
This project is a laboratory exercise designed to explore the practical limitations and engineering strategies associated with Large Language Model (LLM) context windows. As models support larger contexts, developers face challenges such as "Lost in the Middle," increased latency, and noise accumulation. This lab provides a framework to measure these effects and evaluate mitigation strategies like RAG and Context Engineering.

## 2. Objectives
The primary objectives of this software suite are:
1.  **Quantify "Lost in the Middle"**: Empirically demonstrate how information retrieval degrades based on position in the context.
2.  **Measure Scaling Costs**: Correlate context size with latency and accuracy degradation.
3.  **Evaluate RAG Efficacy**: Determine when Retrieval-Augmented Generation outperforms full-context prompting.
4.  **Test Engineering Strategies**: Compare different methods (Select, Compress, Write) for managing long-term context in sequential tasks.

## 3. Scope
The system will consist of four distinct Python experiments and one analysis module. It will utilize a local LLM server (Ollama) running on high-performance hardware (NVIDIA A100).

## 4. Functional Requirements

### 4.1. General System
-   **FR-01**: The system MUST communicate with an Ollama instance via the `OLLAMA_HOST` environment variable.
-   **FR-02**: The system MUST use a custom model definition (`modelfile`) that supports at least 128k context tokens.
-   **FR-03**: All experiments MUST output results in JSON format to a standardized directory.

### 4.2. Experiment 1: Needle in a Haystack
-   **FR-1.1**: Generate synthetic documents totaling ~1000 words.
-   **FR-1.2**: Insert a specific fact at the start, middle, or end of the text.
-   **FR-1.3**: Query the model and evaluate if the fact was correctly retrieved.
-   **FR-1.4**: Output accuracy metrics per position.

### 4.3. Experiment 2: Context Size Impact
-   **FR-2.1**: Load text from provided literary sources (`hobbit`, `lotr`).
-   **FR-2.2**: Construct contexts of varying lengths (2, 5, 10, 20, 50 document equivalents).
-   **FR-2.3**: Measure and record:
    -   Time to first token (latency).
    -   Total tokens used.
    -   Accuracy of response to a control question.

### 4.4. Experiment 3: RAG vs. Full Context
-   **FR-3.1**: Manage a corpus of 20 Hebrew documents (synthetic or provided).
-   **FR-3.2**: Implement a Vector Store (ChromaDB) for the RAG approach.
-   **FR-3.3**: Execute queries using "Full Context" (concatenation) and "RAG" (retrieval).
-   **FR-3.4**: Compare and record accuracy and latency for both methods.

### 4.5. Experiment 4: Context Engineering
-   **FR-4.1**: Simulate a multi-step agent task (10 steps).
-   **FR-4.2**: Implement three context strategies:
    -   *Select*: Retrieve relevant history.
    -   *Compress*: Summarize old history.
    -   *Write*: Maintain an external scratchpad.
-   **FR-4.3**: Record the success rate of the agent at each step for each strategy.

### 4.6. Analysis & Visualization
-   **FR-5.1**: Parse JSON results from all experiments.
-   **FR-5.2**: Generate the following visualizations:
    -   Accuracy vs. Position (Exp 1).
    -   Latency/Accuracy vs. Context Size (Exp 2).
    -   RAG vs. Full Context Comparison (Exp 3).
    -   Strategy Performance Table/Chart (Exp 4).

## 5. Non-Functional Requirements
-   **NFR-01 Performance**: The system should leverage the available 80GB VRAM to maximize batching or context throughput where possible.
-   **NFR-02 Reproducibility**: Random seeds should be fixed or logged to ensure experiments can be reproduced.
-   **NFR-03 Modularity**: Shared code (Ollama client, evaluation logic) should be abstracted into a utility module.

## 6. Data Requirements
-   **Input Data**:
    -   `hobbit` / `lotr` (English text for Exp 2).
    -   Synthetic Hebrew text (for Exp 3).
-   **Output Data**:
    -   JSON logs for raw data.
    -   PNG/SVG files for charts.
    -   Markdown report.

## 7. Assumptions & Constraints
-   The `OLLAMA_HOST` is accessible and the model `lab-model` has been pulled/created.
-   The environment has sufficient memory to hold the vector store and large contexts in RAM.
-   Hebrew language support in the base model (`llama3.2`) is sufficient for Exp 3, or a multilingual variant is used.

## 8. Success Criteria
-   All four experiments run without error.
-   `analysis_output/` contains 4 distinct visualization files.
-   `EXPERIMENT_REPORT.md` is generated with a summary of findings.
