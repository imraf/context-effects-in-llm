import os
import random
import logging
import requests
import hashlib
import json
import aiohttp
import asyncio
from typing import List, Dict, Any, Protocol
from abc import ABC, abstractmethod
import config

logger = logging.getLogger(__name__)


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    def generate(self, prompt: str, system: str = "", temperature: float = 0.7, max_tokens: int = 2048) -> str:
        pass

    @abstractmethod
    def generate_with_stats(
        self, prompt: str, system: str = "", temperature: float = 0.7, max_tokens: int = 2048
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def generate_with_stats_async(
        self, prompt: str, system: str = "", temperature: float = 0.7, max_tokens: int = 2048
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def embed(self, text: str) -> List[float]:
        pass


class OllamaClient(LLMClient):
    """Client for interacting with Ollama API."""

    def __init__(self, model: str, host: str = config.OLLAMA_HOST):
        self.model = model
        self.host = host
        self.api_generate = f"{host}/api/generate"
        self.api_embeddings = f"{host}/api/embeddings"
        self.cache_dir = config.CACHE_DIR

    def _get_cache_path(self, payload: Dict[str, Any]) -> str:
        """Generate cache file path based on payload hash."""
        payload_str = json.dumps(payload, sort_keys=True)
        payload_hash = hashlib.md5(payload_str.encode("utf-8")).hexdigest()
        return os.path.join(self.cache_dir, f"{payload_hash}.json")

    def _get_from_cache(self, cache_path: str) -> Any:
        """Retrieve data from cache if it exists."""
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to read cache {cache_path}: {e}")
        return None

    def _save_to_cache(self, cache_path: str, data: Any):
        """Save data to cache."""
        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except Exception as e:
            logger.warning(f"Failed to write cache {cache_path}: {e}")

    def generate(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """Generate text response from model."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "keep_alive": 0,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }

        # Check cache
        cache_path = self._get_cache_path(payload)
        cached_response = self._get_from_cache(cache_path)
        if cached_response:
            logger.info("Cache hit for generate request")
            return cached_response.get("response", "")

        try:
            response = requests.post(self.api_generate, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            # Save to cache
            self._save_to_cache(cache_path, result)
            return result.get("response", "")
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama generation failed: {e}")
            return ""

    def generate_with_stats(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> Dict[str, Any]:
        """Generate text response with full statistics."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "keep_alive": 0,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }

        # Check cache
        cache_path = self._get_cache_path(payload)
        cached_response = self._get_from_cache(cache_path)
        if cached_response:
            logger.info("Cache hit for generate_with_stats request")
            return cached_response

        try:
            response = requests.post(self.api_generate, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            # Save to cache
            self._save_to_cache(cache_path, result)
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama generation failed: {e}")
            return {}

    async def generate_with_stats_async(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> Dict[str, Any]:
        """Generate text response with full statistics asynchronously."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "keep_alive": 0,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }

        # Check cache (synchronous check is fine for local FS usually, or could make async)
        cache_path = self._get_cache_path(payload)
        cached_response = self._get_from_cache(cache_path)
        if cached_response:
            logger.info("Cache hit for generate_with_stats_async request")
            return cached_response

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_generate, json=payload, timeout=30) as response:
                    response.raise_for_status()
                    result = await response.json()

                    # Save to cache
                    self._save_to_cache(cache_path, result)
                    return result
        except Exception as e:
            logger.error(f"Ollama async generation failed: {e}")
            return {}

    def embed(self, text: str) -> List[float]:
        """Generate embeddings for text."""
        payload = {
            "model": "nomic-embed-text",  # Assuming this model is available for embeddings
            "prompt": text,
            "keep_alive": 0,
        }
        try:
            response = requests.post(self.api_embeddings, json=payload, timeout=30)
            response.raise_for_status()
            return response.json().get("embedding", [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama embedding failed: {e}")
            return []


def load_english_articles(limit: int = 150) -> List[str]:
    """Load English articles from the configured directory.

    Args:
        limit: Maximum number of articles to load.

    Returns:
        List of article contents.
    """
    articles = []
    if not os.path.exists(config.ENGLISH_ARTICLES_DIR):
        logger.warning(f"English articles dir not found: {config.ENGLISH_ARTICLES_DIR}")
        return []

    files = sorted(os.listdir(config.ENGLISH_ARTICLES_DIR))[:limit]
    for f in files:
        if f.endswith(".txt"):
            try:
                with open(os.path.join(config.ENGLISH_ARTICLES_DIR, f), "r", encoding="utf-8") as file:
                    articles.append(file.read())
            except Exception as e:
                logger.warning(f"Failed to read {f}: {e}")
    return articles


def load_hebrew_articles(limit: int = 20) -> List[str]:
    """Load Hebrew articles from the configured directory.

    Args:
        limit: Maximum number of articles to load.

    Returns:
        List of article contents.
    """
    articles = []
    if not os.path.exists(config.HEBREW_ARTICLES_DIR):
        logger.warning(f"Hebrew articles dir not found: {config.HEBREW_ARTICLES_DIR}")
        return []

    files = sorted(os.listdir(config.HEBREW_ARTICLES_DIR))[:limit]
    for f in files:
        if f.endswith(".txt"):
            try:
                with open(os.path.join(config.HEBREW_ARTICLES_DIR, f), "r", encoding="utf-8") as file:
                    articles.append(file.read())
            except Exception as e:
                logger.warning(f"Failed to read {f}: {e}")
    return articles


def generate_filler_text(word_count: int, source_texts: List[str]) -> str:
    """Generates filler text by sampling from source texts.

    Args:
        word_count: Target word count for generated text.
        source_texts: List of texts to sample from.

    Returns:
        Generated text string.
    """
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
            chunk = words[start : start + chunk_size]
        else:
            chunk = words

        collected_words.extend(chunk)
        current_count += len(chunk)

        # Add paragraph break
        collected_words.append("\n\n")

    return " ".join(collected_words[:word_count])


def embed_fact(context: str, fact: str, position: str) -> str:
    """Embeds a fact into the context at a specific position.

    Args:
        context: The base context text.
        fact: The fact to insert.
        position: 'start', 'middle', or 'end'.

    Returns:
        Context with embedded fact.
    """
    words = context.split()
    total_words = len(words)

    if position == "start":
        insert_idx = 0
    elif position == "end":
        insert_idx = total_words
    elif position == "middle":
        insert_idx = total_words // 2
    else:
        # Default to start but maybe we should warn?
        # For now, following logic, default to start.
        insert_idx = 0

    words.insert(insert_idx, f"\n\nIMPORTANT FACT: {fact}\n\n")
    return " ".join(words)


def count_tokens(text: str) -> int:
    """Estimate token count for a given text.

    Args:
        text: Input text.

    Returns:
        Estimated token count.
    """
    # Simple approximation
    if not text:
        return 0
    return int(len(text.split()) * 1.3)


def load_text_from_file(filepath: str, max_chars: int) -> str:
    """Load text from file up to max_chars characters.

    Args:
        filepath: Path to the file.
        max_chars: Maximum characters to read.

    Returns:
        File content or empty string if failed.
    """
    if not os.path.exists(filepath):
        logger.warning(f"Text file not found: {filepath}")
        return ""

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read(max_chars)
        return content
    except Exception as e:
        logger.error(f"Error loading text from {filepath}: {e}")
        return ""


def insert_secret_message(text: str, position: str, secret: str) -> str:
    """Insert secret message at specified position in text.

    Args:
        text: Base text content
        position: One of "control", "start", "middle", "end"
        secret: Secret message to insert

    Returns:
        Modified text with secret inserted (or original if position is "control")

    Raises:
        ValueError: If position is invalid.
        TypeError: If inputs are not strings.
    """
    if not isinstance(text, str) or not isinstance(position, str) or not isinstance(secret, str):
        raise TypeError("All arguments must be strings")

    valid_positions = ["control", "start", "middle", "end"]
    if position not in valid_positions:
        raise ValueError(f"Invalid position: {position}. Must be one of {valid_positions}")

    if position == "control":
        return text  # No modification for control
    elif position == "start":
        return secret + "\n" + text
    elif position == "end":
        return text + "\n" + secret
    elif position == "middle":
        mid_point = len(text) // 2
        # Find next whitespace character after midpoint
        next_whitespace = mid_point
        while next_whitespace < len(text) and not text[next_whitespace].isspace():
            next_whitespace += 1
        if next_whitespace >= len(text):
            logger.warning("No whitespace found near midpoint; inserting at end.")
            next_whitespace = len(text)
        return text[: next_whitespace + 1] + secret + "\n" + text[next_whitespace + 1 :]
    else:
        # This should be unreachable due to check above
        raise ValueError(f"Invalid position: {position}")
