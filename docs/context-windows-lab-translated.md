# Lab: Context Windows in Practice

Dr. Yoram Segal ©\
November 2025

------------------------------------------------------------------------

## 1. Introduction

This document explores context windows in LLMs.\
The experiments examine how models behave when:

-   Long contexts accumulate irrelevant material,
-   Important facts become buried,
-   Statistical structure becomes noisy,
-   And model accuracy declines as context grows.

The goal is to understand how to optimize context usage, measure model
behavior, and use statistical graphs and tables (as outputs) to reveal
key patterns.\
The lab also demonstrates how external memory, retrieval, and
context-engineering strategies can improve model performance in
long-context scenarios.

------------------------------------------------------------------------

## 2. Lab Objectives

This lab focuses on four central challenges in long-context LLM usage:

1.  Lost in the Middle --- Why accuracy drops when facts appear in the
    middle of a long context.\
2.  Context Accumulation Problem --- How growing context introduces
    noise and reduces retrieval accuracy.\
3.  RAG vs. Full-Context --- When retrieval-augmented generation is
    better than supplying the entire context.\
4.  Context Engineering --- Using strategies to control context size and
    relevance.

------------------------------------------------------------------------

## 3. Experiment 1: Needle in Haystack

### 3.1 Experiment Details

-   Duration: 15 minutes\
-   Difficulty: Basic\
-   Goal: Demonstrate the "Lost in the Middle" effect

### 3.2 Data

-   Five synthetic text documents, 200 words each\
-   Each document includes one embedded critical fact\
-   The fact appears in one of: "start", "middle", "end"

### 3.3 Pseudocode

    # Experiment 1: Lost in the Middle Simulation

    # Generate synthetic documents with embedded facts
    def create_documents(num_docs=5, words_per_doc=200):
        documents = []
        for i in range(num_docs):
            doc = generate_filler_text(words_per_doc)
            fact_position = random.choice(['start', 'middle', 'end'])
            doc = embed_critical_fact(doc, fact, fact_position)
            documents.append(doc)
        return documents

    # Query LLM and measure accuracy by fact position
    def measure_accuracy_by_position(documents, query):
        results = {'start': [], 'middle': [], 'end': []}
        for doc in documents:
            response = ollama_query(doc, query)
            accuracy = evaluate_response(response, expected_answer)
            results[doc.fact_position].append(accuracy)
        return calculate_averages(results)

    # Expected: High accuracy at start/end, low in middle

------------------------------------------------------------------------

## 4. Experiment 2: Context Window Size Impact

### 4.1 Experiment Details

-   Duration: 20 minutes\
-   Difficulty: Intermediate\
-   Goal: Measure how context window size affects accuracy

### 4.2 Data

Document counts tested: 2, 5, 10, 20, 50\
Measurement for each: - Accuracy\
- Latency\
- Tokens used

### 4.3 Pseudocode

    # Experiment 2: Context Window Size Analysis

    def analyze_context_sizes(doc_counts=[2, 5, 10, 20, 50]):
        results = []
        for num_docs in doc_counts:
            documents = load_documents(num_docs)
            context = concatenate_documents(documents)
            start_time = time.time()

            response = langchain_query(context, query)
            latency = time.time() - start_time

            results.append({
                'num_docs': num_docs,
                'tokens_used': count_tokens(context),
                'latency': latency,
                'accuracy': evaluate_accuracy(response)
            })
        return results

    # Expected: Accuracy decreases as window grows

------------------------------------------------------------------------

## 5. Experiment 3: RAG Impact

### 5.1 Experiment Details

-   Duration: 25 minutes\
-   Difficulty: Intermediate\
-   Goal: Compare RAG retrieval vs full-context ingestion

### 5.2 Data

-   20 Hebrew documents (medicine, law, technology, etc.)
-   Query example: "What are the findings of report X?"

### 5.3 Pseudocode

    # Experiment 3: RAG vs Full Context Comparison

    # 1. Chunk documents
    chunks = split_documents(documents, chunk_size=500)

    # 2. Embed chunks
    embeddings = nomic_embed_text(chunks)

    # 3. Store vectors
    vector_store = ChromaDB()
    vector_store.add(chunks, embeddings)

    # 4. Compare modes
    def compare_modes(query):
        full_response = query_with_full_context(all_documents, query)

        relevant_docs = vector_store.similarity_search(query, k=3)
        rag_response = query_with_context(relevant_docs, query)

        return {
            'full_accuracy': evaluate(full_response),
            'rag_accuracy': evaluate(rag_response),
            'full_latency': full_response.latency,
            'rag_latency': rag_response.latency
        }

    # Expected: RAG = accurate & fast; Full = noisy & slow

------------------------------------------------------------------------

## 6. Experiment 4: Context Engineering Strategies

### 6.1 Experiment Details

-   Duration: 30 minutes\
-   Difficulty: Advanced\
-   Goal: Evaluate Select, Compress, Write, and Isolate strategies

### 6.2 Data

-   10-step sequential action simulation\
-   Each step evaluated across strategies

### 6.3 Pseudocode

    # Experiment 4: Context Engineering Strategies

    # SELECT strategy (RAG)
    def select_strategy(history, query):
        relevant = rag_search(history, query, k=5)
        return query_llm(relevant, query)

    # COMPRESS strategy (summaries)
    def compress_strategy(history, query):
        if len(history) > MAX_TOKENS:
            history = summarize(history)
        return query_llm(history, query)

    # WRITE strategy (external scratchpad)
    def write_strategy(history, query, scratchpad):
        key_facts = extract_key_facts(history)
        scratchpad.store(key_facts)
        return query_llm(scratchpad.retrieve(query), query)

    # Benchmarking across 10 actions
    def benchmark_strategies(num_actions=10):
        results = {'select': [], 'compress': [], 'write': []}

        for action in range(num_actions):
            output = agent.execute(action)
            history.append(output)

            for strategy in ['select', 'compress', 'write']:
                result = evaluate_strategy(strategy, history)
                results[strategy].append(result)

        return results

------------------------------------------------------------------------

## 7. Summary Table

    | Experiment | Topic                | Tools                  | Time | Output                             |
    |-----------|----------------------|------------------------|------|------------------------------------|
    | 1         | Lost in the Middle   | Ollama + Python        | 15m  | Accuracy by position graph         |
    | 2         | Context Size         | Ollama + LangChain     | 20m  | Latency vs size graph              |
    | 3         | RAG Impact           | Ollama + ChromaDB      | 25m  | Performance comparison             |
    | 4         | Memory Engineering   | LangChain + Memory     | 30m  | Strategy performance table         |

------------------------------------------------------------------------

## 8. Summary

Key findings:

1.  Lost in the Middle: strong accuracy drop when facts are placed
    mid-context.\
2.  Larger context windows → lower accuracy and higher noise.\
3.  RAG improves accuracy and reduces latency compared to full-context
    ingestion.\
4.  Select, Compress, and Write strategies significantly improve
    long-context behavior.

------------------------------------------------------------------------

## 9. Submission Instructions

Submit all experiment outputs (graphs, tables, summaries) to the course
portal.\
Ensure clarity and correctness in all results.\
Submissions must reflect your own independent work.
