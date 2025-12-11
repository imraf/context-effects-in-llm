import os
import json
import glob
import logging
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import config
from math import pi
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set global style
sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
PALETTE = "viridis"


def load_results() -> List[Dict[str, Any]]:
    """Load all experiment results from JSON files.

    Reads both standard and detailed result files from the configured
    RESULTS_DIR and identifies their type.

    Returns:
        List of result dictionaries with type indicators (standard or detailed_needle).
    """
    results = []
    files = glob.glob(os.path.join(config.RESULTS_DIR, "*_results.json"))
    for f in files:
        try:
            with open(f, "r") as file:
                data = json.load(file)
                # Check if this is a detailed needle experiment result
                if "experiment_metadata" in data and "results" in data:
                    # This is a detailed format (info_retrieval or anomaly_detection)
                    results.append(
                        {
                            "type": "detailed_needle",
                            "metadata": data["experiment_metadata"],
                            "results": data["results"],
                        }
                    )
                else:
                    # This is the original format
                    results.append({"type": "standard", "data": data})
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON from {f}")
        except Exception as e:
            logger.error(f"Error loading {f}: {e}")

    return results


def plot_exp1_needle(results: List[Dict[str, Any]]):
    """Generate heatmap for needle-in-haystack experiment.

    Args:
        results: List of experiment results

    Saves:
        exp1_heatmap.png to plots directory
    """
    data = []
    for res in results:
        if res.get("type") == "standard":
            model = res["data"]["model"]
            for pos, metrics in res["data"]["exp1_needle"].items():
                data.append(
                    {
                        "Model": model,
                        "Position": pos.capitalize(),
                        "Accuracy": metrics["accuracy"],
                    }
                )

    if not data:
        return

    df = pd.DataFrame(data)

    plt.figure(figsize=(10, 6))
    pivot_df = df.pivot(index="Model", columns="Position", values="Accuracy")
    # Ensure columns exist before selecting
    available_cols = [c for c in ["Start", "Middle", "End"] if c in pivot_df.columns]
    pivot_df = pivot_df[available_cols]

    ax = sns.heatmap(
        pivot_df,
        annot=True,
        cmap="RdYlGn",
        vmin=0,
        vmax=1,
        fmt=".2f",
        linewidths=0.5,
        cbar_kws={"label": "Accuracy"},
    )
    plt.title(
        "Experiment 1: 'Lost in the Middle' Analysis - Model Comparison",
        fontsize=16,
        pad=20,
    )
    plt.ylabel("Model Name")
    plt.xlabel("Fact Position")
    plt.tight_layout()
    plt.savefig(os.path.join(config.PLOTS_DIR, "exp1_heatmap.png"), dpi=300)
    plt.close()


def plot_exp2_size(results: List[Dict[str, Any]]):
    """Generate scaling plots for context size experiment.

    Creates two plots: Accuracy vs Context Size and Latency vs Context Size.

    Args:
        results: List of experiment results

    Saves:
        exp2_scaling.png to plots directory
    """
    data = []
    for res in results:
        if res.get("type") == "standard":
            model = res["data"]["model"]
            for entry in res["data"]["exp2_size"]:
                data.append(
                    {
                        "Model": model,
                        "Tokens": entry["token_count"],
                        "Accuracy": entry["accuracy"],
                        "Latency": entry["latency"],
                    }
                )

    if not data:
        return

    df = pd.DataFrame(data)

    # Create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Accuracy Plot
    sns.lineplot(
        data=df,
        x="Tokens",
        y="Accuracy",
        hue="Model",
        marker="o",
        linewidth=2.5,
        ax=ax1,
        palette=PALETTE,
    )
    ax1.set_title("Accuracy vs Context Size", fontsize=14)
    ax1.set_ylim(-0.1, 1.1)
    ax1.grid(True, linestyle="--", alpha=0.7)

    # Latency Plot
    sns.lineplot(
        data=df,
        x="Tokens",
        y="Latency",
        hue="Model",
        marker="s",
        linewidth=2.5,
        ax=ax2,
        palette=PALETTE,
    )
    ax2.set_title("Latency vs Context Size", fontsize=14)
    ax2.set_ylabel("Latency (seconds)")
    ax2.grid(True, linestyle="--", alpha=0.7)

    plt.suptitle(
        "Experiment 2: Context Scaling Performance - Model Comparison", fontsize=18
    )
    plt.tight_layout()
    plt.savefig(os.path.join(config.PLOTS_DIR, "exp2_scaling.png"), dpi=300)
    plt.close()


def plot_exp3_rag(results: List[Dict[str, Any]]):
    """Generate comparison plots for RAG vs Full Context.

    Args:
        results: List of experiment results

    Saves:
        exp3_rag_comparison.png to plots directory
    """
    data = []
    for res in results:
        if res.get("type") == "standard":
            model = res["data"]["model"]
            rag_data = res["data"].get("exp3_rag", {})
            if not rag_data:
                continue

            data.append(
                {
                    "Model": model,
                    "Method": "Full Context",
                    "Latency": rag_data.get("full_context", {}).get("latency", 0),
                    "Accuracy": rag_data.get("full_context", {}).get("accuracy", 0),
                }
            )
            data.append(
                {
                    "Model": model,
                    "Method": "RAG",
                    "Latency": rag_data.get("rag", {}).get("latency", 0),
                    "Accuracy": rag_data.get("rag", {}).get("accuracy", 0),
                }
            )

    if not data:
        return

    df = pd.DataFrame(data)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Latency
    sns.barplot(data=df, x="Model", y="Latency", hue="Method", ax=ax1, palette="muted")
    ax1.set_title("Latency Comparison (Lower is Better)", fontsize=14)
    ax1.set_ylabel("Seconds")
    ax1.set_yscale("log")  # Log scale because differences can be huge

    # Accuracy
    sns.barplot(data=df, x="Model", y="Accuracy", hue="Method", ax=ax2, palette="muted")
    ax2.set_title("Accuracy Comparison (Higher is Better)", fontsize=14)
    ax2.set_ylim(0, 1.1)

    plt.suptitle("Experiment 3: RAG vs Full Context - Model Comparison", fontsize=18)
    plt.tight_layout()
    plt.savefig(os.path.join(config.PLOTS_DIR, "exp3_rag_comparison.png"), dpi=300)
    plt.close()


def plot_radar_summary(results: List[Dict[str, Any]]):
    """Generate radar chart summarizing overall model capabilities.

    Dimensions: Needle Retrieval, Long Context, RAG Efficiency, Reasoning.

    Args:
        results: List of experiment results

    Saves:
        benchmark_radar.png to plots directory
    """
    categories = ["Needle Retrieval", "Long Context", "RAG Efficiency", "Reasoning"]
    N = len(categories)

    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]

    plt.figure(figsize=(10, 10))
    ax = plt.subplot(111, polar=True)

    # Draw one axe per variable + add labels
    plt.xticks(angles[:-1], categories, color="grey", size=12)

    # Draw ylabels
    ax.set_rlabel_position(0)
    plt.yticks(
        [0.25, 0.5, 0.75, 1.0], ["0.25", "0.5", "0.75", "1.0"], color="grey", size=10
    )
    plt.ylim(0, 1.0)

    # Color palette
    standard_results = [r for r in results if r.get("type") == "standard"]
    colors = sns.color_palette(PALETTE, len(standard_results))

    for idx, res in enumerate(standard_results):
        model = res["data"]["model"]

        # Calculate scores (normalized 0-1)
        # 1. Needle: Avg accuracy
        exp1_vals = [v["accuracy"] for v in res["data"]["exp1_needle"].values()]
        s1 = np.mean(exp1_vals) if exp1_vals else 0

        # 2. Long Context: Avg accuracy weighted by token count? Or just raw avg accuracy.
        # Let's use avg accuracy for simplicity.
        exp2_vals = [v["accuracy"] for v in res["data"]["exp2_size"]]
        s2 = np.mean(exp2_vals) if exp2_vals else 0

        # 3. RAG: Accuracy
        s3 = res["data"].get("exp3_rag", {}).get("rag", {}).get("accuracy", 0)

        # 4. Reasoning: Exp 4 Write strategy accuracy
        s4 = (
            1.0
            if res["data"].get("exp4_strategies", {}).get("write", {}).get("correct")
            else 0.0
        )

        values = [s1, s2, s3, s4]
        values += values[:1]

        ax.plot(
            angles,
            values,
            linewidth=2,
            linestyle="solid",
            label=model,
            color=colors[idx],
        )
        ax.fill(angles, values, color=colors[idx], alpha=0.1)

    plt.title("Overall Model Capabilities Comparison", size=20, y=1.1)
    plt.legend(loc="upper right", bbox_to_anchor=(0.1, 0.1))

    plt.tight_layout()
    plt.savefig(os.path.join(config.PLOTS_DIR, "benchmark_radar.png"), dpi=300)
    plt.close()


def plot_detailed_needle_experiments(results: List[Dict[str, Any]]):
    """Generate visualizations for detailed needle experiments.

    Creates multiple plots: Overall Detection Rate, Detection Rate by Position,
    Heatmaps per model, Length Detection Curve, and Query Time Analysis.

    Args:
        results: List of experiment results

    Saves:
        Various .png files to plots directory
    """
    detailed_results = [r for r in results if r.get("type") == "detailed_needle"]

    for exp_result in detailed_results:
        metadata = exp_result["metadata"]
        exp_data = exp_result["results"]
        exp_name = metadata.get("experiment_name", "unknown")

        df = pd.DataFrame(exp_data)

        # Filter out control for some analyses
        test_df = df[df["message_position"] != "control"]

        if len(test_df) == 0:
            continue

        # 1. Overall Detection Rate by Model
        plt.figure(figsize=(10, 6))
        model_accuracy = test_df.groupby("model")["found_secret"].mean().reset_index()
        sns.barplot(data=model_accuracy, x="model", y="found_secret", palette="viridis")
        plt.title(f"Overall Secret Detection Rate - {exp_name}")
        plt.ylabel("Detection Rate")
        plt.ylim(0, 1.0)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(
            os.path.join(config.PLOTS_DIR, f"overall_detection_{exp_name}.png"), dpi=300
        )
        plt.close()

        # 2. Detection Rate by Position
        plt.figure(figsize=(12, 6))
        pos_accuracy = (
            test_df.groupby(["model", "message_position"])["found_secret"]
            .mean()
            .reset_index()
        )
        sns.barplot(
            data=pos_accuracy,
            x="model",
            y="found_secret",
            hue="message_position",
            palette="deep",
        )
        plt.title(f"Detection Rate by Position - {exp_name}")
        plt.ylabel("Detection Rate")
        plt.ylim(0, 1.0)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(
            os.path.join(config.PLOTS_DIR, f"position_detection_{exp_name}.png"),
            dpi=300,
        )
        plt.close()

        # 3. Heatmaps per model
        models = test_df["model"].unique()
        for model in models:
            model_data = test_df[test_df["model"] == model]
            pivot_table = model_data.pivot_table(
                index="message_position",
                columns="target_prompt_length",
                values="found_secret",
                aggfunc="mean",
            )
            # Reorder index
            pivot_table = pivot_table.reindex(["start", "middle", "end"])

            plt.figure(figsize=(12, 4))
            sns.heatmap(
                pivot_table,
                annot=True,
                cmap="RdYlGn",
                vmin=0,
                vmax=1,
                cbar_kws={"label": "Detection Rate"},
                fmt=".2f",
            )
            plt.title(f"Needle Detection Heatmap: {model} - {exp_name}")
            plt.xlabel("Context Length (chars)")
            plt.ylabel("Needle Position")
            plt.tight_layout()
            safe_model_name = model.replace(":", "_")
            plt.savefig(
                os.path.join(
                    config.PLOTS_DIR, f"heatmap_{safe_model_name}_{exp_name}.png"
                ),
                dpi=300,
            )
            plt.close()

        # 4. Length Detection Curve
        plt.figure(figsize=(12, 6))
        length_accuracy = (
            test_df.groupby(["model", "target_prompt_length"])["found_secret"]
            .mean()
            .reset_index()
        )
        sns.lineplot(
            data=length_accuracy,
            x="target_prompt_length",
            y="found_secret",
            hue="model",
            marker="o",
            linewidth=2.5,
        )
        plt.title(f"Detection Rate vs Context Length - {exp_name}")
        plt.xlabel("Context Length (chars)")
        plt.ylabel("Detection Rate")
        plt.ylim(-0.05, 1.05)
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.tight_layout()
        plt.savefig(
            os.path.join(config.PLOTS_DIR, f"length_curve_{exp_name}.png"), dpi=300
        )
        plt.close()

        # 5. Query Time Analysis
        plt.figure(figsize=(12, 6))
        sns.scatterplot(
            data=df,
            x="target_prompt_length",
            y="query_time_seconds",
            hue="model",
            alpha=0.6,
            s=100,
        )
        plt.title(f"Query Time vs Context Length - {exp_name}")
        plt.xlabel("Context Length (chars)")
        plt.ylabel("Time (seconds)")
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.tight_layout()
        plt.savefig(
            os.path.join(config.PLOTS_DIR, f"query_time_{exp_name}.png"), dpi=300
        )
        plt.close()


def main():
    """Main function to generate all plots from results."""
    results = load_results()
    if not results:
        print("No results found to analyze.")
        return

    print("Generating enhanced plots...")
    plot_exp1_needle(results)
    plot_exp2_size(results)
    plot_exp3_rag(results)
    plot_radar_summary(results)
    plot_detailed_needle_experiments(results)
    print(f"Plots saved to {config.PLOTS_DIR}")


if __name__ == "__main__":
    main()
