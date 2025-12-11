import glob
import json
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

import config

st.set_page_config(page_title="Context Benchmark Results", layout="wide")

st.title("Context Horizons: LLM Benchmark Results")


# Load data
@st.cache_data
def load_data():
    results = []
    if not os.path.exists(config.RESULTS_DIR):
        return []

    files = glob.glob(os.path.join(config.RESULTS_DIR, "*_results.json"))
    for f in files:
        # Skip detailed results for now, focus on summary
        if (
            "detailed" in os.path.basename(f)
            or "needle" in os.path.basename(f)
            and "results.json" in os.path.basename(f)
            and "exp" not in os.path.basename(f)
        ):
            # detailed files usually named "info_retrieval_results.json" or similar.
            # Summary files are "{model}_results.json"
            pass

        try:
            with open(f) as file:
                data = json.load(file)
                if "model" in data:
                    results.append(data)
        except Exception:
            pass

    return results


data = load_data()

if not data:
    st.warning("No results found in results/ directory.")
    st.info("Run 'python main.py' to generate results.")
    st.stop()

# Sidebar
model_names = sorted(list(set([d["model"] for d in data])))
selected_models = st.sidebar.multiselect("Select Models", model_names, default=model_names)

filtered_data = [d for d in data if d["model"] in selected_models]

if not filtered_data:
    st.warning("No models selected.")
    st.stop()

# Exp 1
st.header("Experiment 1: Needle in Haystack (Quick)")
exp1_data = []
for d in filtered_data:
    if "exp1_needle" in d and isinstance(d["exp1_needle"], dict):
        for pos, metrics in d["exp1_needle"].items():
            if isinstance(metrics, dict):
                exp1_data.append(
                    {
                        "Model": d["model"],
                        "Position": pos,
                        "Accuracy": metrics.get("accuracy", 0),
                        "Latency": metrics.get("latency", 0),
                    }
                )

if exp1_data:
    df1 = pd.DataFrame(exp1_data)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Accuracy by Position")
        try:
            pivot = df1.pivot(index="Model", columns="Position", values="Accuracy")
            fig, ax = plt.subplots()
            sns.heatmap(pivot, annot=True, cmap="RdYlGn", vmin=0, vmax=1, ax=ax)
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Could not plot heatmap: {e}")

    with col2:
        st.subheader("Latency by Position")
        try:
            pivot_lat = df1.pivot(index="Model", columns="Position", values="Latency")
            st.bar_chart(pivot_lat)
        except Exception:
            st.write(df1)

# Exp 2
st.header("Experiment 2: Context Size")
exp2_data = []
for d in filtered_data:
    if "exp2_size" in d and isinstance(d["exp2_size"], list):
        for res in d["exp2_size"]:
            exp2_data.append(
                {
                    "Model": d["model"],
                    "Doc Count": res.get("doc_count", 0),
                    "Accuracy": res.get("accuracy", 0),
                    "Latency": res.get("latency", 0),
                }
            )

if exp2_data:
    df2 = pd.DataFrame(exp2_data)
    st.subheader("Accuracy vs Context Size")
    st.line_chart(df2, x="Doc Count", y="Accuracy", color="Model")

    st.subheader("Latency vs Context Size")
    st.line_chart(df2, x="Doc Count", y="Latency", color="Model")

# Exp 3
st.header("Experiment 3: RAG vs Full")
exp3_data = []
for d in filtered_data:
    if "exp3_rag" in d and isinstance(d["exp3_rag"], dict):
        rag = d["exp3_rag"].get("rag", {})
        full = d["exp3_rag"].get("full_context", {})
        exp3_data.append(
            {
                "Model": d["model"],
                "RAG Accuracy": rag.get("accuracy", 0),
                "Full Accuracy": full.get("accuracy", 0),
                "RAG Latency": rag.get("latency", 0),
                "Full Latency": full.get("latency", 0),
            }
        )

if exp3_data:
    df3 = pd.DataFrame(exp3_data)
    st.dataframe(df3)

# Exp 4
st.header("Experiment 4: Strategies")
exp4_data = []
for d in filtered_data:
    if "exp4_strategies" in d and isinstance(d["exp4_strategies"], dict):
        row = {"Model": d["model"]}
        for strat, res in d["exp4_strategies"].items():
            if isinstance(res, dict):
                row[strat] = 1.0 if res.get("correct") else 0.0
        exp4_data.append(row)

if exp4_data:
    df4 = pd.DataFrame(exp4_data).set_index("Model")
    st.write(df4)
    fig, ax = plt.subplots()
    sns.heatmap(df4, annot=True, cmap="Blues", ax=ax, vmin=0, vmax=1)
    st.pyplot(fig)
