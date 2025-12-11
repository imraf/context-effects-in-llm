# Prompt Documentation

This document lists the system prompts and user queries used in the Context Horizons benchmarking suite.

## Experiment 1: Needle in Haystack

### Quick Mode
**User Prompt:**
```text
Context:
{context}

Question: {question}
```
*Note: `{context}` contains the generated filler text with the embedded fact. `{question}` asks for the embedded fact.*

### Detailed Mode (Information Retrieval / Anomaly Detection)
**User Prompt:**
```text
Below is a passage of text. Please read it carefully and answer the following question:

{question}

<TEXT>
{text_with_secret}
</TEXT>

Please provide your answer clearly.
```

## Experiment 2: Context Size

**User Prompt:**
```text
Context:
{context}

Question: {query}
```
*Note: `{query}` is "What is the Unique Reference ID mentioned in the text? Return only the ID."*

## Experiment 3: RAG vs Full Context

### Full Context & RAG
**User Prompt:**
```text
Context:
{context}

Question: {query}
```
*Note: `{query}` is a Hebrew query: "האם הטקסט מזכיר את המשפט הבא: '{fact}'? השב בכן או לא."*

## Experiment 4: Strategies

### 1. Baseline (Full History)
**User Prompt:**
```text
History:
{history}

Question: {question}
Answer with just the location name.
```

### 2. Select (Simulated RAG)
**User Prompt:**
```text
Relevant History:
{history_select}

Question: {question}
Answer with just the location name.
```

### 3. Compress (Summarization)
**Summary Update Prompt:**
```text
Current Summary: {summary}
New Actions:
{chunk}

Update the summary of where items are located. Keep it brief.
```

**Final Question Prompt:**
```text
Summary of Events:
{summary}

Question: {question}
Answer with just the location name.
```

### 4. Write (Scratchpad/State Tracking)
**State Update Prompt:**
```text
{scratchpad}
Action: {action}

Update the Current State JSON to reflect item locations. Return only JSON.
```

**Final Question Prompt:**
```text
Final State:
{scratchpad}

Question: {question}
Answer with just the location name.
```
