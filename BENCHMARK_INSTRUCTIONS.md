# Context Windows Benchmark Instructions

## Setup

1.  **Environment**:
    Ensure you have the virtual environment set up and dependencies installed:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Configuration**:
    Check `config.py` to ensure `OLLAMA_HOST` and `MODELS` are correct.
    The default `OLLAMA_HOST` is retrieved from your environment variable.

3.  **Data**:
    Ensure the `documents/` folder contains:
    -   `articles_english/` (150 .txt files)
    -   `articles_hebrew/` (20 .txt files)
    -   `articles_metadata.json`

## Running the Benchmark

To run the full suite of experiments across all models:

```bash
source .venv/bin/activate
python3 main.py
```

This will:
1.  Iterate through each model defined in `config.py`.
2.  Run Experiments 1-4.
3.  Save JSON results to `results/`.

## Analyzing Results

Once the benchmark is complete, generate the visualizations:

```bash
python3 analyze_results.py
```

This will read the JSON files from `results/` and generate plots in `plots/`:
-   `exp1_heatmap.png`: Accuracy by position.
-   `exp2_accuracy.png`: Accuracy vs Context Size.
-   `exp2_latency.png`: Latency vs Context Size.
-   `exp3_latency.png`: RAG vs Full Context Latency.
-   `benchmark_radar.png`: Overall model comparison.

## Logs

Check `results/benchmark.log` for detailed execution logs.
