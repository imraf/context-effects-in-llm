# 🔭 Context Horizons: Benchmarking the Limits of Small-to-Mid Sized LLMs

![Benchmark Status](https://img.shields.io/badge/Benchmark-Complete-success) ![Python](https://img.shields.io/badge/Python-3.x-blue) ![License](https://img.shields.io/badge/License-MIT-green)

> **"In the ocean of context, some models swim, while others drown."**

## 📖 Abstract

As Large Language Models (LLMs) evolve, the promise of "infinite context" (100k+ tokens) has become a standard marketing claim. However, **effective context**—the ability to actually retrieve, reason, and manipulate information within that window—often lags behind the theoretical limit.

This project, **Context Horizons**, is a rigorous benchmarking suite designed to stress-test state-of-the-art open-source models. We evaluate the "Lost in the Middle" phenomenon, the degradation of reasoning as context scales, the efficacy of RAG (Retrieval Augmented Generation) in multi-lingual settings, and the impact of context engineering strategies.

## 🤖 The Contenders

We benchmarked the following models, representing a mix of parameter sizes and architectures, all running on an **NVIDIA A100 (80GB)** via Ollama:

| Model | Parameters | Context Limit | Family |
| :--- | :--- | :--- | :--- |
| **Llama 3.2** | 3B | 100k | Meta |
| **Granite 3.3** | 2B | 100k | IBM |
| **Gemma 3** | 4B | 100k | Google |
| **Qwen 3** | 4B | 100k | Alibaba |
| **GPT-OSS** | 20B | 100k | OpenAI |

---

## 📊 Key Findings & Analysis

### 1. The "Lost in the Middle" Phenomenon (Experiment 1)
*Goal: Detect accuracy drops when critical facts are buried in the middle of massive noise (~65k tokens).*

| Model | Start | Middle | End | Analysis |
| :--- | :---: | :---: | :---: | :--- |
| **Llama 3.2** | ✅ | ✅ | ✅ | **The Surprise Champion.** Despite being only 3B parameters, Llama 3.2 demonstrated perfect retrieval across all positions. |
| **GPT-OSS** | ✅ | ✅ | ✅ | **Reliable Heavyweight.** The 20B model handled the task effortlessly, though with higher latency. |
| **Granite 3.3** | ❌ | ✅ | ✅ | **Reverse Curve.** Unusually, it failed at the *Start* but recovered for Middle and End. |
| **Qwen 3** | ❌ | ❌ | ✅ | **Recency Bias.** Strongly favored the end of the context. It hallucinated "42" (Hitchhiker's Guide) when it couldn't find the needle at the start. |
| **Gemma 3** | ❌ | ❌ | ❌ | **Context Collapse.** Failed to retrieve the specific code "BLUE-ZEBRA-99", often hallucinating "42" or truncated versions like "BLUE-Z9". |

> **Insight:** The "42" hallucination observed in Qwen and Gemma suggests that when these models lose track of the context, they revert to strong training priors (associating "The answer" with "42").

### 2. Context Scaling & Latency (Experiment 2)
*Goal: Correlate context length (up to 50 documents / ~60k tokens) with performance.*

*   **The Scaling Wall:** Most small models (Llama, Granite, Gemma) hit a "wall" between **20 and 50 documents**. While they could process the tokens, their ability to extract the specific "Unique Reference ID" collapsed to 0% accuracy at 50 docs.
*   **The Exception:** **GPT-OSS (20B)** was the only model to maintain **100% accuracy** up to 50 documents. However, this came at a cost: ~221 seconds latency vs ~28s for the smaller models.
*   **Latency Profiles:** Latency scaled linearly for all models, but the slope for GPT-OSS was significantly steeper.

### 3. The Multi-Lingual RAG Divide (Experiment 3)
*Goal: Compare RAG vs. Full Context using Hebrew documents.*

This experiment revealed a stark divide in multi-lingual capabilities:

*   **The Polyglots (Gemma 3 & Qwen 3):** Both models achieved **100% accuracy** in both Full Context and RAG modes. They correctly processed the Hebrew query and returned the correct Hebrew response ("כן" / Yes).
*   **The Monolinguals (Llama, Granite, GPT-OSS):** Failed completely (0% accuracy).
    *   *Granite* hallucinated repetitive text about "web scraping" in Hebrew.
    *   *GPT-OSS* simply refused with "לא" (No) or returned empty strings.

> **Critical Insight:** For non-English RAG tasks, model architecture and training data distribution matter far more than parameter count. The 4B Gemma outperformed the 20B GPT-OSS significantly here.

### 4. Strategic Context Engineering (Experiment 4)
*Goal: Evaluate Select, Compress, and Write strategies.*

*   **Selection Works:** The "Select" strategy (retrieving only relevant history) consistently outperformed the Baseline across most models.
*   **Compression Risk:** The "Compress" strategy (summarizing history) worked well for GPT-OSS but caused information loss for smaller models like Llama 3.2.

---

## 📈 Visualizations

The following plots (generated in `plots/`) visualize these findings:

### 🎯 Needle in a Haystack Heatmap
*Visualizes the "Lost in the Middle" effect. Green = Success, Red = Failure.*
![Needle Heatmap](plots/exp1_heatmap.png)

### 📏 Context Scaling
*Accuracy and Latency vs. Token Count. Note the drop-off at 60k tokens for small models.*
![Context Scaling](plots/exp2_scaling.png)

### 🕸️ Model Capabilities Radar
*A holistic view of each model's strengths across Retrieval, Long Context, RAG, and Reasoning.*
![Radar Chart](plots/benchmark_radar.png)

---

## 💡 Recommendations for Future Work

Based on these results, we propose the following extensions:

1.  **Granular Needle Probing:** Increase the resolution of Experiment 1 to 10 or 20 intervals to pinpoint exactly where attention falls off.
2.  **"Needle" Variation:** Change the needle from a code ("BLUE-ZEBRA-99") to a logical statement to test reasoning, not just retrieval.
3.  **Token-per-Second (TPS) Analysis:** While we measured latency, a detailed TPS breakdown would help quantify the "cost of intelligence."
4.  **Additional Visualizations:**
    *   *Token/Sec vs. Accuracy Scatter Plot:* To identify the most efficient model.
    *   *Failure Mode Distribution:* A pie chart showing types of errors (Hallucination vs. Refusal vs. Truncation).

## 🚀 How to Run

1.  **Environment Setup:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Configuration:**
    Ensure your Ollama instance is running and accessible.
    ```bash
    export OLLAMA_HOST=http://your-ollama-server:11434
    ```

3.  **Run Benchmarks:**
    ```bash
    python main.py
    ```

4.  **Generate Report:**
    ```bash
    python analyze_results.py
    ```

---

*Generated by the Context Horizons Team, December 2025.*
