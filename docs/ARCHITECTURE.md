# Architecture Overview

## System Context Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Context Horizons System                   │
│                                                              │
│  ┌─────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Config    │───▶│ Experiments  │───▶│   Results    │  │
│  └─────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                    │          │
│         │                   ▼                    ▼          │
│         │            ┌──────────────┐    ┌──────────────┐  │
│         └───────────▶│ OllamaClient │    │  Analyzer    │  │
│                      └──────────────┘    └──────────────┘  │
│                             │                    │          │
│                             ▼                    ▼          │
│                      ┌──────────────┐    ┌──────────────┐  │
│                      │  Ollama API  │    │ Visualizer   │  │
│                      └──────────────┘    └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

1. **Configuration Phase**: Load models, parameters, and paths from config.py
2. **Experiment Execution**: 
   - For each model in MODELS list
   - Run experiments 1-4 sequentially
   - Save results to JSON immediately
3. **Analysis Phase**:
   - Load all JSON results
   - Aggregate and pivot data
   - Generate visualizations
   - Save plots as PNG

## Component Descriptions

### OllamaClient
- **Purpose**: Interface to Ollama API
- **Methods**: generate(), generate_with_stats(), embed()
- **Dependencies**: requests, config

### Experiment Classes
- **NeedleExperiment**: Tests "Lost in the Middle" phenomenon
- **ContextSizeExperiment**: Evaluates scaling behavior
- **RagExperiment**: Compares RAG vs. Full Context
- **StrategiesExperiment**: Tests context engineering strategies

### Analyzer
- **Purpose**: Transform raw results into insights
- **Functions**: Aggregation, pivoting, statistical analysis
- **Output**: DataFrame summaries, calculated metrics

### Visualizer
- **Purpose**: Generate publication-quality plots
- **Library**: Seaborn + Matplotlib
- **Output**: 300 DPI PNG files
