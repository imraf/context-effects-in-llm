# Mathematical Foundations

This document outlines the mathematical formulas and statistical methods used in the Context Horizons benchmarking suite.

## Accuracy Calculation

For the Needle In A Haystack experiments, accuracy is calculated as a binary classification metric:

$$
\text{Accuracy} = \frac{\text{TP} + \text{TN}}{\text{Total Samples}}
$$

Where:
- **TP (True Positive)**: The model correctly identified the secret message/needle.
- **TN (True Negative)**: The model correctly identified that no needle was present (in control cases).
- **Total Samples**: The total number of queries performed for a specific configuration.

In many experiments, we focus specifically on the retrieval rate for positive cases:

$$
\text{Retrieval Rate} = \frac{\text{Correct Retrievals}}{\text{Total Needle Insertions}}
$$

## Token Estimation

We use a heuristic for estimating token counts when exact tokenizer access is not available or for quick estimation:

$$ 
\text{Tokens} \approx 1.3 \times \text{Word Count}
$$ 

This approximation is based on the average token-to-word ratio for English text in BPE-based tokenizers (like GPT-4, Llama).

## Statistical Aggregation

### Mean Accuracy per Position

To analyze the "Lost in the Middle" phenomenon, we aggregate accuracy by position bucket:

$$ 
\text{Accuracy}_{pos} = \frac{1}{N_{pos}} \sum_{i=1}^{N_{pos}} \mathbb{I}(\text{result}_i = \text{correct})
$$ 

Where $N_{pos}$ is the number of experiments run at position $pos$.

## Performance Metrics

### Latency

Latency is measured as the wall-clock time from sending the request to receiving the full response:

$$ 
\text{Latency} = t_{end} - t_{start}
$$ 

### Throughput (implied)

$$ 
\text{Throughput} = \frac{\text{Total Tokens Generated}}{\text{Total Generation Time}}
$$ 

## Confidence Intervals (Future Work)

For future versions, we plan to calculate Wilson Score Intervals for accuracy to determine statistical significance:

$$ 
\text{CI} = \frac{ \hat{p} + \frac{z^2}{2n} \pm z \sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}} }{ 1 + \frac{z^2}{n} }
$$