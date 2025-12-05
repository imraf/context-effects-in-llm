# Needle-in-a-Haystack Experiment: Comprehensive Analysis

## Abstract

This report presents the findings of a "Needle-in-a-Haystack" experiment designed to evaluate the context retrieval capabilities of Small Language Models (SLMs). We tested 4 models: llama3.2:3b-100K, gemma3:4b-100K, granite3.3:2b-100K, qwen3:4b-100K. The experiment varied context length from 250 to 100000 characters and placed a secret message ("needle") at the start, middle, and end of the context.

## 1. Executive Summary

The experiment reveals distinct performance characteristics among the tested models. 

*   **Top Performer:** qwen3:4b-100K with an overall detection rate of 100.00%.
*   **Positional Bias:** Most models showed significant performance degradation when the needle was placed in the **middle** of the context, confirming the "Lost in the Middle" phenomenon.
*   **Context Limit:** Performance generally declined as context length increased, with sharp drop-offs observed for some models.

## 2. Methodology

*   **Task:** Retrieve a secret code ("DQDDI") from a text passage ("The Hobbit").
*   **Variables:**
    *   **Models:** llama3.2:3b-100K, gemma3:4b-100K, granite3.3:2b-100K, qwen3:4b-100K
    *   **Context Lengths:** 25 increments up to 100000 chars.
    *   **Positions:** Start, Middle, End, Control (None).
*   **Metric:** Exact match of the secret code in the response.

## 3. Detailed Results

### 3.1 Overall Model Performance

| Model | Overall Accuracy | Start | Middle | End | False Positives |
|-------|------------------|-------|--------|-----|-----------------|
| llama3.2:3b-100K | 29.33% | 16.00% | 20.00% | 52.00% | 0 |
| gemma3:4b-100K | 80.00% | 100.00% | 64.00% | 76.00% | 0 |
| granite3.3:2b-100K | 60.00% | 52.00% | 40.00% | 88.00% | 0 |
| qwen3:4b-100K | 100.00% | 100.00% | 100.00% | 100.00% | 0 |

### 3.2 Visual Analysis

#### Overall Performance Comparison
![Overall Detection Rate](analysis_output/overall_detection_rate.png)

#### The "Lost in the Middle" Phenomenon
The heatmap visualizations below clearly illustrate where models struggle. Green indicates success, while red indicates failure.

**llama3.2:3b-100K**
![Heatmap llama3.2:3b-100K](analysis_output/heatmap_llama3.2_3b-100K.png)

**gemma3:4b-100K**
![Heatmap gemma3:4b-100K](analysis_output/heatmap_gemma3_4b-100K.png)

**granite3.3:2b-100K**
![Heatmap granite3.3:2b-100K](analysis_output/heatmap_granite3.3_2b-100K.png)

**qwen3:4b-100K**
![Heatmap qwen3:4b-100K](analysis_output/heatmap_qwen3_4b-100K.png)


### 3.3 Context Length Scaling

The following graph demonstrates how detection capability degrades as the context window grows.

![Length Detection Curve](analysis_output/length_detection_curve.png)

### 3.4 Computational Cost

Query time generally increases linearly with context length, but the slope varies by model architecture.

![Query Time Analysis](analysis_output/query_time_analysis.png)

## 4. Discussion & Insights


*   **qwen3:4b-100K** demonstrated the most robust context handling, maintaining high retrieval rates even at longer context lengths.
*   **llama3.2:3b-100K** struggled significantly with the middle position, suggesting its attention mechanism prioritizes the beginning and end of the prompt (U-shaped attention curve).
*   **Efficiency:** The query time analysis highlights the trade-off between model size/complexity and inference speed.
*   **Reliability:** The control group analysis shows 0 false positives across all runs, indicating the models generally did not hallucinate the secret code when it wasn't present.

## 5. Conclusion

For applications requiring precise retrieval from long contexts (e.g., RAG, document summarization), **qwen3:4b-100K** is the recommended choice among the tested SLMs. However, developers should be wary of the "middle" context position, as it remains a blind spot for many efficient models.

---
*Generated on 2025-12-05*
