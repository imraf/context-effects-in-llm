from base import ExperimentBase
import time
import logging
import json
import random
from typing import Dict, List, Any
import config
from utils import OllamaClient, load_english_articles, count_tokens

logger = logging.getLogger(__name__)


class ContextSizeExperiment(ExperimentBase):
    ID = 2
    NAME = "Context Size"

    def __init__(self, model: str, **kwargs):
        super().__init__(model, **kwargs)
        self.client = OllamaClient(model)
        self.articles = load_english_articles()

    def run(self) -> List[Dict[str, Any]]:
        logger.info(f"Starting Experiment 2 (Context Size) for {self.model}")
        results = []

        for doc_count in config.EXP2_DOC_COUNTS:
            if doc_count > len(self.articles):
                logger.warning(f"Not enough articles for count {doc_count}")
                continue

            # Select documents
            selected_docs = random.sample(self.articles, doc_count)

            # Pick a target fact from one of the documents (e.g., the title or first sentence)
            # Since we have raw text, let's pick the middle document and ask about its content.
            target_doc_idx = len(selected_docs) // 2
            target_doc = selected_docs[target_doc_idx]

            # Extract a "fact" - let's assume the first line is the title/header
            lines = target_doc.strip().split("\n")
            fact = lines[0] if lines else "Unknown"
            # If the first line is "Title: ...", extract it.
            if fact.startswith("Title: "):
                fact = fact.replace("Title: ", "")

            # Construct context
            context = "\n\n".join(selected_docs)
            token_count = count_tokens(context)

            query = f"What is the title of the document that discusses '{fact[:20]}...'? Return only the full title."
            # Actually, that's cheating if I give the title.
            # Let's ask: "What is the title of the document mentioned in the middle of the text?" -> Too vague.
            # Let's inject a specific unique ID into one document.

            unique_id = f"ID-{random.randint(*config.EXP2_ID_RANGE)}"
            selected_docs[target_doc_idx] += f"\n\nUnique Reference ID: {unique_id}"
            context = "\n\n".join(selected_docs)

            query = "What is the Unique Reference ID mentioned in the text? Return only the ID."

            start_time = time.time()
            response = self.client.generate(prompt=f"Context:\n{context}\n\nQuestion: {query}", temperature=0.1)
            latency = time.time() - start_time

            is_correct = unique_id in response

            logger.info(f"Docs: {doc_count}, Tokens: {token_count:.0f}, Correct: {is_correct}, Latency: {latency:.2f}s")

            results.append(
                {
                    "doc_count": doc_count,
                    "token_count": token_count,
                    "latency": latency,
                    "accuracy": 1.0 if is_correct else 0.0,
                    "response": response,
                }
            )

        return results


if __name__ == "__main__":
    exp = ContextSizeExperiment(config.MODELS[0])
    print(json.dumps(exp.run(), indent=2))
