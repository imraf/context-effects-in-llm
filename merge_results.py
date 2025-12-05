import json
import glob
import os
from datetime import datetime

def merge_results():
    # Find all result files
    files = glob.glob("experiment_results_*.json")
    # Exclude the merged file if it already exists to avoid recursion
    files = [f for f in files if "merged" not in f]
    files.sort()
    
    if not files:
        print("No experiment_results_*.json files found.")
        return

    print(f"Found {len(files)} files to merge: {files}")

    merged_results = []
    
    # Metadata accumulators
    all_models = set()
    all_lengths = set()
    all_positions = set()
    total_experiments_count = 0
    
    # Base metadata from the first file (will be updated)
    base_metadata = {}

    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Merge results
                if "results" in data:
                    merged_results.extend(data["results"])
                
                # Merge metadata info
                if "experiment_metadata" in data:
                    meta = data["experiment_metadata"]
                    
                    # Keep the first file's static metadata as base
                    if not base_metadata:
                        base_metadata = meta.copy()
                    
                    # Accumulate dynamic fields
                    if "models" in meta:
                        all_models.update(meta["models"])
                    if "prompt_lengths" in meta:
                        all_lengths.update(meta["prompt_lengths"])
                    if "positions" in meta:
                        all_positions.update(meta["positions"])
                    
        except json.JSONDecodeError:
            print(f"Warning: Could not decode JSON from {file_path}. Skipping.")
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    # Update total count based on actual merged results
    total_experiments_count = len(merged_results)

    # Construct final metadata
    final_metadata = base_metadata
    final_metadata["date_run"] = datetime.now().isoformat() # Update timestamp to merge time
    final_metadata["total_experiments"] = total_experiments_count
    final_metadata["models"] = sorted(list(all_models))
    final_metadata["prompt_lengths"] = sorted(list(all_lengths))
    final_metadata["positions"] = sorted(list(all_positions))
    
    # Create final structure
    final_output = {
        "experiment_metadata": final_metadata,
        "results": merged_results
    }

    output_filename = "experiment_results_merged.json"
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)

    print(f"Successfully merged {total_experiments_count} results into {output_filename}")

if __name__ == "__main__":
    merge_results()
