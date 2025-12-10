import os
import json
import random
import time
import logging
import requests
from typing import List, Dict, Any, Optional
import config

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self, model: str, host: str = config.OLLAMA_HOST):
        self.model = model
        self.host = host
        self.api_generate = f"{host}/api/generate"
        self.api_embeddings = f"{host}/api/embeddings"

    def generate(self, prompt: str, system: str = "", temperature: float = 0.7, max_tokens: int = 2048) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        try:
            response = requests.post(self.api_generate, json=payload)
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama generation failed: {e}")
            return ""

    def embed(self, text: str) -> List[float]:
        payload = {
            "model": "nomic-embed-text", # Assuming this model is available for embeddings
            "prompt": text
        }
        try:
            response = requests.post(self.api_embeddings, json=payload)
            response.raise_for_status()
            return response.json().get("embedding", [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama embedding failed: {e}")
            return []

def load_english_articles(limit: int = 150) -> List[str]:
    articles = []
    if not os.path.exists(config.ENGLISH_ARTICLES_DIR):
        logger.warning(f"English articles dir not found: {config.ENGLISH_ARTICLES_DIR}")
        return []
    
    files = sorted(os.listdir(config.ENGLISH_ARTICLES_DIR))[:limit]
    for f in files:
        if f.endswith(".txt"):
            with open(os.path.join(config.ENGLISH_ARTICLES_DIR, f), "r", encoding="utf-8") as file:
                articles.append(file.read())
    return articles

def load_hebrew_articles(limit: int = 20) -> List[str]:
    articles = []
    if not os.path.exists(config.HEBREW_ARTICLES_DIR):
        logger.warning(f"Hebrew articles dir not found: {config.HEBREW_ARTICLES_DIR}")
        return []

    files = sorted(os.listdir(config.HEBREW_ARTICLES_DIR))[:limit]
    for f in files:
        if f.endswith(".txt"):
            with open(os.path.join(config.HEBREW_ARTICLES_DIR, f), "r", encoding="utf-8") as file:
                articles.append(file.read())
    return articles

def generate_filler_text(word_count: int, source_texts: List[str]) -> str:
    """Generates filler text by sampling from source texts."""
    # Filter out empty texts
    valid_texts = [t for t in source_texts if t and t.strip()]
    
    if not valid_texts:
        return " ".join(["Lorem", "ipsum", "dolor", "sit", "amet"] * (word_count // 5 + 1))
    
    collected_words = []
    current_count = 0
    
    while current_count < word_count:
        sample = random.choice(valid_texts)
        words = sample.split()
        
        if not words:
            continue
            
        # Take a random chunk
        chunk_size = 200
        if len(words) > chunk_size:
            start = random.randint(0, len(words) - chunk_size)
            chunk = words[start:start+chunk_size]
        else:
            chunk = words
            
        collected_words.extend(chunk)
        current_count += len(chunk)
        
        # Add paragraph break
        collected_words.append("\n\n")
    
    return " ".join(collected_words[:word_count])

def embed_fact(context: str, fact: str, position: str) -> str:
    """Embeds a fact into the context at a specific position."""
    words = context.split()
    total_words = len(words)
    
    if position == "start":
        insert_idx = 0
    elif position == "end":
        insert_idx = total_words
    elif position == "middle":
        insert_idx = total_words // 2
    else:
        insert_idx = 0 # Default to start
        
    words.insert(insert_idx, f"\n\nIMPORTANT FACT: {fact}\n\n")
    return " ".join(words)

def count_tokens(text: str) -> int:
    # Simple approximation
    return len(text.split()) * 1.3 
