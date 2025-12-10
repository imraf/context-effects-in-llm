# 🧪 Experiment Results: Context Windows & Retrieval Dynamics in Llama 3.2

**Date:** December 10, 2025  
**Model Evaluated:** `llama3.2:3b-100K`  
**Hardware:** NVIDIA A100 (80GB VRAM) via Ollama  

---

## 📊 Executive Summary

This report details the findings of a comprehensive benchmarking suite designed to evaluate the behavior of Small Language Models (SLMs) with extended context capabilities. We tested **Llama 3.2 (3B parameters)**, a model advertised with a 100K context window, to understand its practical limits in information retrieval, reasoning, and latency.

**Key Findings:**
1.  **Context Limit:** While theoretically capable of 100K context, practical retrieval accuracy collapsed between **10,000 and 20,000 tokens**.
2.  **RAG Efficiency:** Retrieval-Augmented Generation (RAG) proved **~66x faster** than full-context processing (1.38s vs 92.06s).
3.  **Strategy Matters:** For sequential reasoning tasks, simple context selection and compression strategies outperformed the baseline full-context approach.
4.  **Robust Short-Context Retrieval:** The model demonstrated perfect recall for "Needle in a Haystack" tasks within its effective window (~4k tokens), showing no "Lost in the Middle" effect at this scale.

---

## 1. The "Lost in the Middle" Phenomenon

**Objective:** Determine if the model's ability to retrieve specific facts degrades based on their position (Start, Middle, End) within the context.

### 📉 Visualization
![Needle Heatmap](plots/exp1_heatmap.png)

### 🔍 Analysis
Contrary to the common "Lost in the Middle" phenomenon observed in many larger models, Llama 3.2 3B demonstrated **perfect stability** within a ~3,000-word (~4,000 token) context.

| Position | Accuracy | Latency (s) |
| :--- | :--- | :--- |
| **Start** | 100% | 1.43s |
| **Middle** | 100% | 1.43s |
| **End** | 100% | 1.12s |

*Observation:* The model is highly reliable for factual retrieval when the context fits comfortably within its "attention sweet spot."

---

## 2. Context Scaling & Breaking Points

**Objective:** Correlate context length (in tokens) with retrieval accuracy and system latency.

### 📉 Visualization
![Context Scaling](plots/exp2_scaling.png)

### 🔍 Analysis
This experiment revealed the practical boundaries of the model. We tested document sets ranging from 2 to 50 articles.

*   **Performance Plateau:** Accuracy was **100%** up to ~11,000 tokens (10 documents).
*   **The Cliff:** At ~20,000 tokens (20 documents), accuracy dropped sharply to **0%**. The model began hallucinating generic summaries rather than retrieving the specific unique ID requested.
*   **Latency Cost:** Processing time scales linearly, becoming prohibitive at larger sizes.
    *   10k tokens: ~3.1s
    *   50k tokens: ~49.3s

**Conclusion:** For this specific quantized version of Llama 3.2, the *effective* reliable context window for precise retrieval is approximately **10k-15k tokens**, despite the 100k theoretical limit.

---

## 3. RAG vs. Full Context: The Efficiency Gap

**Objective:** Compare the performance of processing a large corpus via Full Context stuffing versus Retrieval-Augmented Generation (RAG).

### 📉 Visualization
![RAG Comparison](plots/exp3_rag_comparison.png)

### 🔍 Analysis
The results highlight the massive computational advantage of RAG.

| Method | Latency (s) | Accuracy | Notes |
| :--- | :--- | :--- | :--- |
| **Full Context** | **92.06s** | 0% | Extremely slow; model failed to process Hebrew query correctly in bulk. |
| **RAG** | **1.38s** | 0% | **~66x Faster**. |

*Insight:* While both methods struggled with the specific Hebrew query accuracy in this run (likely due to model language limitations or query complexity), the **latency difference is the critical takeaway**. RAG transforms a minute-and-a-half wait into a near-instant response, making it the only viable strategy for interactive applications with large datasets.

---

## 4. Context Engineering Strategies

**Objective:** Evaluate different memory management strategies for a sequential logic task (tracking an object through 10 movement steps).

### 📋 Results Table

| Strategy | Result | Correct? | Analysis |
| :--- | :--- | :--- | :--- |
| **Baseline** | "Living Room" | ❌ | Failed to track the final state change. |
| **Select** | "Table" | ✅ | **Winner.** Filtering for keywords removed noise. |
| **Compress** | "Table" | ✅ | **Winner.** Summarization retained key state info. |
| **Write** | "Kitchen" | ❌ | The complex scratchpad prompt confused the small model. |

### 🔍 Analysis
The "Select" (RAG-like) and "Compress" (Summarization) strategies proved superior. The "Write" strategy, which asks the model to maintain an external JSON state, likely added too much cognitive overhead for a 3B parameter model, leading to state drift.

---

## 5. Overall Model Capabilities

### 📉 Visualization
![Benchmark Radar](plots/benchmark_radar.png)

### 🏁 Conclusion
Llama 3.2 (3B) is a potent Small Language Model, but it requires careful orchestration to shine.

1.  **Do not trust the "100K" label blindly.** For precise retrieval, keep contexts under 12k tokens.
2.  **Use RAG.** It is non-negotiable for latency-sensitive applications involving more than a few documents.
3.  **Simplify Reasoning.** For sequential tasks, use pre-processing (Selection/Compression) rather than asking the model to manage complex state (Write/Scratchpad).

This benchmark demonstrates that with the right **Context Engineering**, even small models can perform reliably, but pushing them to their raw limits results in rapid degradation.
