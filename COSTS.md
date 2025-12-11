# Cost Analysis

## Token Usage Per Experiment

Based on experiment results:

### Experiment 1: Needle in Haystack
- **Quick Mode**: ~65,000 tokens per position per model
- **Detailed Mode**: ~5,000 - 200,000 tokens depending on context length
- **Total per model**: ~450,000 tokens

### Experiment 2: Context Size
- **2 documents**: ~2,000 tokens
- **50 documents**: ~65,000 tokens
- **Total per model**: ~150,000 tokens

### Experiment 3: RAG vs Full Context
- **Full Context**: ~30,000 tokens
- **RAG**: ~5,000 tokens
- **Total per model**: ~35,000 tokens

### Experiment 4: Strategies
- **Per strategy**: ~20,000 tokens
- **Total per model**: ~80,000 tokens

## Total Benchmark Cost

**Per model**: ~715,000 tokens
**All 7 models**: ~5,000,000 tokens

**With local Ollama**: $0 (using local GPU resources)
**If using cloud API** (e.g., at $0.50 per 1M tokens): ~$2.50 total

## Optimization Strategies

1. **Caching**: Reuse ChromaDB embeddings across models
2. **Sampling**: Run detailed experiments on subset of models
3. **Early stopping**: Terminate failed experiments quickly
