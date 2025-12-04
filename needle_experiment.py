#!/usr/bin/env python3
"""
Needle-in-a-Haystack Experiment for LLM Context Windows

This script tests the ability of various LLM models to detect a secret message
embedded at different positions within increasingly large context windows.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Literal
import ollama


# Experiment Configuration
SECRET_MESSAGE = "To enable god-mode, type 'DQDDI'."
SOURCE_FILE = "hobbit"
MODELS = [
    "gemma3:4b-100K",
    "granite3.3:2b-100K",
    "qwen3:4b-100K",
    "llama3.2:3b-100K",
]
PROMPT_LENGTHS = [60000, 70000, 80000, 90000, 100000]
POSITIONS = ["control", "start", "middle", "end"]
OUTPUT_FILE = "experiment_results.json"

# Prompt template
PROMPT_TEMPLATE = """Below is a passage of text. Please read it carefully and answer the following question:

What special code or instruction, if any, is mentioned in the text for enabling god-mode?

{text}

Please provide your answer clearly."""


def load_text_from_file(filepath: str, max_chars: int) -> str:
    """Load text from file up to max_chars characters."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read(max_chars)
    return content


def insert_secret_message(
    text: str, 
    position: Literal["control", "start", "middle", "end"],
    secret: str
) -> str:
    """Insert secret message at specified position in text."""
    if position == "control":
        return text  # No modification for control
    elif position == "start":
        return secret + "\n" + text
    elif position == "end":
        return text + "\n" + secret
    elif position == "middle":
        mid_point = len(text) // 2
        # Find next whitespace character after midpoint
        next_whitespace = mid_point
        while next_whitespace < len(text) and not text[next_whitespace].isspace():
            next_whitespace += 1
        if next_whitespace >= len(text):  # No whitespace found, append at end
            print("\033[1;31mWarning: No whitespace found near midpoint; inserting at end.\033[0m")
            next_whitespace = len(text)
        return text[:next_whitespace+1] + secret + "\n" + text[next_whitespace+1:]
    else:
        raise ValueError(f"Invalid position: {position}")


def detect_secret_in_response(response: str, secret_code: str = "DQDDI") -> bool:
    """Check if the secret code appears in the response."""
    return response and secret_code in response.upper()


def run_experiment_trial(
    model: str,
    prompt_length: int,
    position: Literal["control", "start", "middle", "end"]
) -> dict:
    """Run a single experiment trial and return results."""
    
    # Load text
    base_text = load_text_from_file(SOURCE_FILE, prompt_length)
    
    # Insert secret message based on position (control = no secret)
    text_with_secret = insert_secret_message(base_text, position, SECRET_MESSAGE)
    include_secret = (position != "control")
    
    # Create full prompt
    full_prompt = PROMPT_TEMPLATE.format(text=text_with_secret)
    
    # Record start time
    start_time = time.time()
    
    # Call Ollama API
    try:
        response = ollama.generate(
            model=model,
            prompt=full_prompt,
            options={"num_ctx": 131072},  # Set large context window
            keep_alive=0  # Unload model after request
        )
        
        query_time = time.time() - start_time
        
        # Extract response text
        response_text = response.get('response', '')
        
        # Check if secret was found
        found_secret = detect_secret_in_response(response_text)
        
        # Build result dictionary
        result = {
            "experiment_id": f"{model}_{prompt_length}_{position}_{int(time.time())}",
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "prompt_length_chars": len(text_with_secret),
            "target_prompt_length": prompt_length,
            "message_position": position,
            "secret_message": SECRET_MESSAGE if include_secret else None,
            "include_secret": include_secret,
            "found_secret": found_secret,
            "token_count": response.get('prompt_eval_count', 0),
            "query_time_seconds": query_time,
            "response": response_text,
            "ollama_metadata": {
                "eval_count": response.get('eval_count'),
                "eval_duration": response.get('eval_duration'),
                "load_duration": response.get('load_duration'),
                "prompt_eval_count": response.get('prompt_eval_count'),
                "prompt_eval_duration": response.get('prompt_eval_duration'),
                "total_duration": response.get('total_duration'),
            },
            "error": None
        }
        
        return result
        
    except Exception as e:
        query_time = time.time() - start_time
        
        # Return error result
        result = {
            "experiment_id": f"{model}_{prompt_length}_{position}_{int(time.time())}_error",
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "prompt_length_chars": prompt_length,
            "target_prompt_length": prompt_length,
            "message_position": position,
            "secret_message": SECRET_MESSAGE if include_secret else None,
            "include_secret": include_secret,
            "found_secret": False,
            "token_count": 0,
            "query_time_seconds": query_time,
            "response": None,
            "ollama_metadata": None,
            "error": str(e)
        }
        
        return result


def save_results(results: list, filepath: str):
    """Save results to JSON file."""
    output = {
        "experiment_metadata": {
            "experiment_name": "needle-in-haystack",
            "date_run": datetime.now().isoformat(),
            "secret_message": SECRET_MESSAGE,
            "source_file": SOURCE_FILE,
            "total_experiments": len(results),
            "models": MODELS,
            "prompt_lengths": PROMPT_LENGTHS,
            "positions": POSITIONS
        },
        "results": results
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved {len(results)} results to {filepath}")


def main():
    """Run the complete experiment."""
    
    print("=" * 70)
    print("NEEDLE-IN-A-HAYSTACK EXPERIMENT")
    print("=" * 70)
    print(f"Secret Message: {SECRET_MESSAGE}")
    print(f"Models: {len(MODELS)}")
    print(f"Prompt Lengths: {len(PROMPT_LENGTHS)} ({min(PROMPT_LENGTHS)} to {max(PROMPT_LENGTHS)})")
    print(f"Positions: {len(POSITIONS)}")
    
    total_experiments = len(MODELS) * len(PROMPT_LENGTHS) * len(POSITIONS)
    print(f"Total Experiments: {total_experiments}")
    print("=" * 70)
    print()
    
    # Check if source file exists
    if not Path(SOURCE_FILE).exists():
        print(f"ERROR: Source file '{SOURCE_FILE}' not found!")
        return
    
    # Initialize results list
    results = []
    completed = 0
    
    # Run experiments
    for model in MODELS:
        print(f"\n{'='*70}")
        print(f"Testing Model: {model}")
        print(f"{'='*70}")
        
        for prompt_length in PROMPT_LENGTHS:
            for position in POSITIONS:
                completed += 1
                progress = (completed / total_experiments) * 100
                
                print(f"\n[{completed}/{total_experiments}] ({progress:.1f}%) ", end="")
                print(f"Model: {model}, Length: {prompt_length}, Position: {position}")
                
                # Run trial
                result = run_experiment_trial(model, prompt_length, position)
                results.append(result)

                # Print result
                if result['error']:
                    print(f"  ✗ ERROR: {result['error']}")
                else:
                    status = "✓ FOUND" if result['found_secret'] else "✗ NOT FOUND"
                    print(f"  {status} | Tokens: {result['token_count']} | Time: {result['query_time_seconds']:.2f}s")
                
                # Save incrementally every 10 results
                if completed % 10 == 0:
                    save_results(results, OUTPUT_FILE)
    
    # Final save
    save_results(results, OUTPUT_FILE)
    
    print("\n" + "=" * 70)
    print("EXPERIMENT COMPLETE!")
    print("=" * 70)
    print(f"Total experiments run: {len(results)}")
    print(f"Results saved to: {OUTPUT_FILE}")
    
    # Summary statistics
    successful = sum(1 for r in results if r['error'] is None)
    found_count = sum(1 for r in results if r['found_secret'])
    
    print(f"\nSummary:")
    print(f"  Successful runs: {successful}/{len(results)}")
    print(f"  Secret detected: {found_count}/{successful} ({found_count/successful*100:.1f}%)")
    print()


if __name__ == "__main__":
    main()
