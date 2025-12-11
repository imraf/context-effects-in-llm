# Performance and Capacity

This document outlines the performance characteristics, capacity limits, and resource requirements for the Context Horizons benchmarking suite.

## Capacity Limits

### Context Length
The framework supports context lengths up to the maximum limit of the underlying hardware and model. 
- **Tested Maximum:** 200,000 tokens (approx. 150,000 words).
- **Hardware Limit:** Dependent on available VRAM. For an A100 80GB:
  - 7B models: ~128k context
  - 13B models: ~64k context (without quantization)

### Concurrency
The system utilizes Python's `multiprocessing` for parallel model evaluation and `asyncio` for concurrent I/O operations within a single model experiment.
- **Max Concurrent Models:** Defaults to `min(cpu_count, 4)`. Configurable via `--parallel`.
- **Max Concurrent Requests per Model:** Limited by the `Ollama` server's queue processing capabilities. The client implementation creates batches of requests (e.g., for all positions at a specific length) to maximize throughput.

## Resource Requirements

### Recommended Hardware
| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 16 GB | 64 GB |
| GPU VRAM | 8 GB (for <7B models) | 80 GB (for massive context testing) |
| Storage | 50 GB | 500 GB (SSD NVMe) |

### Memory Usage
- **System RAM:** Python process overhead is low (~100MB per process).
- **VRAM:** Linear scaling with context length for attention KV cache (unless PagedAttention/FlashAttention is used by the backend).

## Backend Considerations

The framework is backend-agnostic but optimized for `Ollama`.
- **Ollama:** Handles queueing and kv-cache management.
- **Switching Backends:** The `OllamaClient` can be extended or replaced to support vLLM, TGI, or OpenAI-compatible endpoints.

## Optimization Strategies

1. **Response Caching:** Hash-based deduplication prevents redundant API calls.
2. **Shared Embeddings:** ChromaDB utilizes a shared persistent directory to avoid re-computing embeddings for the same corpus.
3. **Async I/O:** `aiohttp` is used to prevent blocking on network requests, improving throughput for high-latency large-context queries.
