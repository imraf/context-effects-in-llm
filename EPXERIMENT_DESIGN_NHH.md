# Needle-in-a-Haystack Experiment for LLM Context Window

## Experiment Overview

This experiment tests the ability of various LLM models to detect a specific secret message ("needle") embedded at different positions within increasingly large context windows ("haystack"). The goal is to measure how context length and message position affect model performance in identifying hidden information.

## Hypothesis

LLM models may struggle to detect information embedded in the middle of large context windows due to:
- Attention mechanism limitations
- Context dilution effects
- Positional bias (models may focus more on beginning/end of context)

## Secret Message

**The secret message is:** `"To enable god-mode, type 'DQDDI'."`

This message contains a unique code (`DQDDI`) that can be easily detected in model responses.

## Data Source

- **Source file:** `hobbit` (text file containing "The Hobbit" by J.R.R. Tolkien)
- **Total lines:** 7,707 lines
- Text will be read progressively to create context windows of varying sizes

## Experiment Parameters

### Independent Variables

1. **Model** (`model`)
   - Test these models: 
        - gemma3:4b-100K
        - deepseek-r1:8b-100K
        - granite3.3:2b-100K
        - qwen3:4b-100K  
        - llama3.2:3b-100K
   - Each model will be tested across all conditions
   - Include a CONTROL condition where the message is not present in the text.

2. **Prompt Length** (`prompt_length`)
   - Measured in characters
   - Progressive increases to test context window limits
   - Increments: 250, 500, 1000, 1500, 2000, 3000, 4000, 5000, 7500, 10000, 12500, 15000, 17500, 20000

3. **Message Position** (`message_position`)
   - Four positions:
     - `"control"`: No sercret message. The text is unmodified.
     - `"start"`: Secret message prefixed to the beginning of text
     - `"middle"`: Secret message inserted at the midpoint (after the next whitespace)
     - `"end"`: Secret message appended to the end of text

### Dependent Variables (Results to Capture)

1. **Detection Success** (`found_secret`)
   - Boolean: `true` if `"DQDDI"` appears in the model's response
   - Primary success metric

2. **Token Count** (`token_count`)
   - Number of tokens in the prompt, as indicated by Ollama response object
   - The primary mesaurement for the experiment alongside the messages discovery

3. **Query Time** (`query_time_seconds`)
   - Time taken for model to generate response, indicated by Ollama response object
   - Measures computational cost

4. **Full Response** (`response`)
   - Complete text response from the model
   - Allows qualitative analysis

5. **Additional Metadata**
   - `timestamp`: When the experiment was run
   - `model`: Model identifier
   - `prompt_length_chars`: Character count of prompt
   - `message_position`: Position of secret message
   - Any other Ollama response parameters

## Implementation Details

### Text Preparation

1. **Reading Text from `hobbit` file:**
   - Read exactly enough text to reach the target `prompt_length`
   - Text should be read sequentially from the beginning of the file

2. **Inserting Secret Message:**
   
   **For "start" position:**
   ```
   secret_message + "\n" + text_from_hobbit
   ```
   
   **For "end" position:**
   ```
   text_from_hobbit + "\n" + secret_message
   ```
   
   **For "middle" position:**
   - Calculate midpoint: `mid_point = len(text_from_hobbit) // 2`
   - Find next newline character after midpoint: `next_newline = text.find('\n', mid_point)`
   - Insert secret message: `text[:next_newline+1] + secret_message + "\n" + text[next_newline+1:]`

### Ollama Configuration

- **API Method:** Use `ollama.generate()` or equivalent API call
- **Parameter:** `keep_alive=0`
  - This ensures the model is unloaded after each request
  - Provides clean slate for each experiment run
  - Prevents memory/state carryover between tests

### Prompt Engineering

The actual prompt sent to the model should ask the model to perform a task that requires reading the entire context:

```
Below is a passage of text. Please read it carefully and answer the following question:

What special code or instruction, if any, is mentioned in the text for enabling god-mode?

[TEXT WITH SECRET MESSAGE INSERTED]

Please provide your answer clearly.
```

This ensures the model must process the entire context to answer correctly.

## Experiment Design Matrix

For each combination of parameters, run one trial:

```
models = # list of the models mentioned above
prompt_lengths = # range of lengths as mentioned above
positions = ["start", "middle", "end"]

Total experiments = len(models) × len(prompt_lengths) × len(positions)
```

## Data Collection

### Data Point Structure

Each experimental run should record:

```json
{
  "experiment_id": "unique_identifier",
  "timestamp": "2025-12-04T10:30:00Z",
  "model": "llama2",
  "prompt_length_chars": 10000,
  "message_position": "middle",
  "secret_message": "To enable god-mode, type 'DQDDI'.",
  "found_secret": true,
  "token_count": 2547,
  "query_time_seconds": 12.34,
  "response": "According to the text...",
  "ollama_metadata": {
    "eval_count": 2547,
    "eval_duration": 12340000000,
    "load_duration": 1234567,
    "prompt_eval_count": 2500,
    "prompt_eval_duration": 5000000000,
    "total_duration": 18000000000
  }
}
```

### Output Format

- **Filename:** `experiment_results.json`
- **Format:** JSON array containing all experimental data points
- **Structure:**
  ```json
  {
    "experiment_metadata": {
      "experiment_name": "needle-in-haystack",
      "date_run": "2025-12-04",
      "secret_message": "To enable god-mode, type 'DQDDI'.",
      "source_file": "hobbit",
      "total_experiments": 54
    },
    "results": [
      { /* data point 1 */ },
      { /* data point 2 */ },
      ...
    ]
  }
  ```

## Analysis Plan

### Primary Metrics

1. **Detection Rate by Position:**
   - Calculate success rate for each position (start/middle/end)
   - Hypothesis: Middle position will have lowest detection rate

2. **Detection Rate by Length:**
   - Plot detection success vs. prompt length
   - Identify critical length where detection degrades

3. **Model Comparison:**
   - Compare detection rates across different models
   - Identify which models handle long contexts better

4. **Performance Analysis:**
   - Correlation between prompt length and query time
   - Token processing speed by model

### Visualization Ideas

1. Heatmap: Detection success by (prompt_length, position)
2. Line graph: Detection rate vs. prompt length (separate lines per position)
3. Bar chart: Average detection rate by model
4. Scatter plot: Query time vs. prompt length

## Error Handling

1. **Ollama Connection Issues:**
   - Implement retry logic
   - Log errors with context

2. **Model Not Available:**
   - Skip model and log warning
   - Continue with available models

3. **Timeout Handling:**
   - Set reasonable timeout (e.g., 120 seconds)
   - Record timeout as failed detection

4. **File Reading Issues:**
   - Validate `hobbit` file exists and is readable
   - Handle case where requested length exceeds file size

## Implementation Checklist

- [ ] Load text from `hobbit` file
- [ ] Implement text insertion logic (start/middle/end)
- [ ] Create prompt template with secret message question
- [ ] Configure Ollama client with `keep_alive=0`
- [ ] Implement experiment loop over all parameter combinations
- [ ] Capture all response metadata
- [ ] Detect "DQDDI" in responses (case-sensitive search)
- [ ] Save results to JSON after each run (incremental save)
- [ ] Implement error handling and logging
- [ ] Add progress tracking/reporting during experiment
- [ ] Create analysis/visualization scripts

## Expected Runtime

- Estimated time per query: 10-60 seconds (depending on model and length)
- Total experiments: ~54 (example)
- Estimated total time: 9-54 minutes

## Future Extensions

1. Test with multiple secret messages simultaneously
2. Vary the "obviousness" of the secret message
3. Test with different text sources
4. Experiment with different prompt formulations
5. Test models' ability to follow instructions based on position
6. Add adversarial elements (misleading information)

## References

- Inspired by "Lost in the Middle" research on LLM context window limitations
- Needle-in-a-haystack testing methodology for RAG systems
