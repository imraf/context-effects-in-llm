import os
import json
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import config
from math import pi

# Set global style
sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
PALETTE = "viridis"

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
    pivot_df = df.pivot(index="Model", columns="Position", values="Accuracy")
    # Ensure columns exist before selecting
    available_cols = [c for c in ["Start", "Middle", "End"] if c in pivot_df.columns]
    pivot_df = pivot_df[available_cols]
    
    ax = sns.heatmap(pivot_df, annot=True, cmap="RdYlGn", vmin=0, vmax=1, fmt=".2f", 
                     linewidths=.5, cbar_kws={'label': 'Accuracy'})
    plt.title("Experiment 1: 'Lost in the Middle' Analysis", fontsize=16, pad=20)
    plt.ylabel("Model Name")
    plt.xlabel("Fact Position")
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
    
    # Create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Accuracy Plot
    sns.lineplot(data=df, x="Tokens", y="Accuracy", hue="Model", marker="o", linewidth=2.5, ax=ax1, palette=PALETTE)
    ax1.set_title("Accuracy vs Context Size", fontsize=14)
    ax1.set_ylim(-0.1, 1.1)
    ax1.grid(True, linestyle='--', alpha=0.7)

    # Latency Plot
    sns.lineplot(data=df, x="Tokens", y="Latency", hue="Model", marker="s", linewidth=2.5, ax=ax2, palette=PALETTE)
    ax2.set_title("Latency vs Context Size", fontsize=14)
    ax2.set_ylabel("Latency (seconds)")
    ax2.grid(True, linestyle='--', alpha=0.7)
    
    plt.suptitle("Experiment 2: Context Scaling Performance", fontsize=18)
    plt.tight_layout()
    plt.savefig(os.path.join(config.PLOTS_DIR, "exp2_scaling.png"), dpi=300)
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
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Latency
    sns.barplot(data=df, x="Model", y="Latency", hue="Method", ax=ax1, palette="muted")
    ax1.set_title("Latency Comparison (Lower is Better)", fontsize=14)
    ax1.set_ylabel("Seconds")
    ax1.set_yscale("log") # Log scale because differences can be huge
    
    # Accuracy
    sns.barplot(data=df, x="Model", y="Accuracy", hue="Method", ax=ax2, palette="muted")
    ax2.set_title("Accuracy Comparison (Higher is Better)", fontsize=14)
    ax2.set_ylim(0, 1.1)
    
    plt.suptitle("Experiment 3: RAG vs Full Context", fontsize=18)
    plt.tight_layout()
    plt.savefig(os.path.join(config.PLOTS_DIR, "exp3_rag_comparison.png"), dpi=300)
    plt.close()

def plot_radar_summary(results):
    categories = ['Needle Retrieval', 'Long Context', 'RAG Efficiency', 'Reasoning']
    N = len(categories)
    
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]
    
    plt.figure(figsize=(10, 10))
    ax = plt.subplot(111, polar=True)
    
    # Draw one axe per variable + add labels
    plt.xticks(angles[:-1], categories, color='grey', size=12)
    
    # Draw ylabels
    ax.set_rlabel_position(0)
    plt.yticks([0.25, 0.5, 0.75, 1.0], ["0.25", "0.5", "0.75", "1.0"], color="grey", size=10)
    plt.ylim(0, 1.0)
    
    # Color palette
    colors = sns.color_palette(PALETTE, len(results))

    for idx, res in enumerate(results):
        model = res['model']
        
        # Calculate scores (normalized 0-1)
        # 1. Needle: Avg accuracy
        exp1_vals = [v['accuracy'] for v in res['exp1_needle'].values()]
        s1 = np.mean(exp1_vals) if exp1_vals else 0
        
        # 2. Long Context: Avg accuracy weighted by token count? Or just raw avg accuracy.
        # Let's use avg accuracy for simplicity.
        exp2_vals = [v['accuracy'] for v in res['exp2_size']]
        s2 = np.mean(exp2_vals) if exp2_vals else 0
        
        # 3. RAG: Accuracy
        s3 = res.get('exp3_rag', {}).get('rag', {}).get('accuracy', 0)
        
        # 4. Reasoning: Exp 4 Write strategy accuracy
        s4 = 1.0 if res.get('exp4_strategies', {}).get('write', {}).get('correct') else 0.0
        
        values = [s1, s2, s3, s4]
        values += values[:1]
        
        ax.plot(angles, values, linewidth=2, linestyle='solid', label=model, color=colors[idx])
        ax.fill(angles, values, color=colors[idx], alpha=0.1)
        
    plt.title("Overall Model Capabilities", size=20, y=1.1)
    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    
    plt.tight_layout()
    plt.savefig(os.path.join(config.PLOTS_DIR, "benchmark_radar.png"), dpi=300)
    plt.close()

def main():
    results = load_results()
    if not results:
        print("No results found to analyze.")
        return

    print("Generating enhanced plots...")
    plot_exp1_needle(results)
    plot_exp2_size(results)
    plot_exp3_rag(results)
    plot_radar_summary(results)
    print(f"Plots saved to {config.PLOTS_DIR}")

if __name__ == "__main__":
    main()
