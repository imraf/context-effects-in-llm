# ADR 001: Use Shared ChromaDB Directory

## Status
Accepted

## Context
RAG experiment requires embedding Hebrew documents. Embedding is expensive
(time and compute). Multiple models use the same documents.

## Decision
Use single shared ChromaDB directory for all models. First model creates
embeddings, subsequent models reuse them.

## Consequences
- Positive: 10x faster execution after first model
- Positive: Consistent embeddings across models
- Negative: Must manage directory lifecycle
- Negative: Cannot test different embedding models easily
