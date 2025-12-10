import os
import json
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import config

# Set style
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("deep")

def load_results():
    results = []
    files = glob.glob(os.path.join(config.RESULTS_DIR, "*_results.json"))
    for f in files:
        with open(f, "r") as file:
            results.append(json.load(file))
    return results

def plot_exp1_needle(results):
    data = []
    for res in results:
        model = res['model']
        for pos, metrics in res['exp1_needle'].items():
            data.append({
                "Model": model,
                "Position": pos.capitalize(),
                "Accuracy": metrics['accuracy']
            })
    
    if not data: return

    df = pd.DataFrame(data)
    
    plt.figure(figsize=(10, 6))
    # Pivot for heatmap
    pivot_df = df.pivot(index="Model", columns="Position", values="Accuracy")
    # Reorder columns
    pivot_df = pivot_df[["Start", "Middle", "End"]]
    
    sns.heatmap(pivot_df, annot=True, cmap="RdYlGn", vmin=0, vmax=1, fmt=".2f")
    plt.title("Experiment 1: Lost in the Middle (Accuracy)")
    plt.tight_layout()
    plt.savefig(os.path.join(config.PLOTS_DIR, "exp1_heatmap.png"), dpi=300)
    plt.close()

def plot_exp2_size(results):
    data = []
    for res in results:
        model = res['model']
        for entry in res['exp2_size']:
            data.append({
                "Model": model,
                "Tokens": entry['token_count'],
                "Accuracy": entry['accuracy'],
                "Latency": entry['latency']
            })
    
    if not data: return

    df = pd.DataFrame(data)
    
    # Accuracy vs Tokens
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x="Tokens", y="Accuracy", hue="Model", marker="o")
    plt.title("Experiment 2: Accuracy vs Context Size")
    plt.ylabel("Accuracy")
    plt.xlabel("Context Tokens")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(config.PLOTS_DIR, "exp2_accuracy.png"), dpi=300)
    plt.close()

    # Latency vs Tokens
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x="Tokens", y="Latency", hue="Model", marker="s")
    plt.title("Experiment 2: Latency vs Context Size")
    plt.ylabel("Latency (s)")
    plt.xlabel("Context Tokens")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(config.PLOTS_DIR, "exp2_latency.png"), dpi=300)
    plt.close()

def plot_exp3_rag(results):
    data = []
    for res in results:
        model = res['model']
        rag_data = res.get('exp3_rag', {})
        if not rag_data: continue
        
        data.append({
            "Model": model,
            "Method": "Full Context",
            "Latency": rag_data.get('full_context', {}).get('latency', 0),
            "Accuracy": rag_data.get('full_context', {}).get('accuracy', 0)
        })
        data.append({
            "Model": model,
            "Method": "RAG",
            "Latency": rag_data.get('rag', {}).get('latency', 0),
            "Accuracy": rag_data.get('rag', {}).get('accuracy', 0)
        })
    
    if not data: return

    df = pd.DataFrame(data)
    
    # Latency Comparison
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x="Model", y="Latency", hue="Method")
    plt.title("Experiment 3: RAG vs Full Context (Latency)")
    plt.ylabel("Latency (s)")
    plt.tight_layout()
    plt.savefig(os.path.join(config.PLOTS_DIR, "exp3_latency.png"), dpi=300)
    plt.close()

def plot_radar_summary(results):
    # Normalize metrics for radar chart
    # Metrics: Exp1 Avg Acc, Exp2 Avg Acc, Exp3 RAG Acc, Exp4 Write Acc
    categories = ['Needle Acc', 'Long Context Acc', 'RAG Acc', 'Reasoning Acc']
    
    data = []
    for res in results:
        model = res['model']
        
        # Exp 1 Avg
        exp1_vals = [v['accuracy'] for v in res['exp1_needle'].values()]
        exp1_score = np.mean(exp1_vals) if exp1_vals else 0
        
        # Exp 2 Avg (Long Context)
        exp2_vals = [v['accuracy'] for v in res['exp2_size']]
        exp2_score = np.mean(exp2_vals) if exp2_vals else 0
        
        # Exp 3 RAG
        exp3_score = res.get('exp3_rag', {}).get('rag', {}).get('accuracy', 0)
        
        # Exp 4 Write Strategy (Proxy for reasoning)
        exp4_score = 1.0 if res.get('exp4_strategies', {}).get('write', {}).get('correct') else 0.0
        
        data.append({
            "Model": model,
            "Scores": [exp1_score, exp2_score, exp3_score, exp4_score]
        })

    if not data: return

    # Radar Chart Logic
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    
    plt.figure(figsize=(8, 8))
    ax = plt.subplot(111, polar=True)
    
    plt.xticks(angles[:-1], categories)
    
    for entry in data:
        values = entry['Scores']
        values += values[:1]
        ax.plot(angles, values, linewidth=1, linestyle='solid', label=entry['Model'])
        ax.fill(angles, values, alpha=0.1)
        
    plt.title("Model Capabilities Benchmark")
    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    plt.tight_layout()
    plt.savefig(os.path.join(config.PLOTS_DIR, "benchmark_radar.png"), dpi=300)
    plt.close()

def main():
    results = load_results()
    if not results:
        print("No results found to analyze.")
        return

    print("Generating plots...")
    plot_exp1_needle(results)
    plot_exp2_size(results)
    plot_exp3_rag(results)
    plot_radar_summary(results)
    print(f"Plots saved to {config.PLOTS_DIR}")

if __name__ == "__main__":
    main()
