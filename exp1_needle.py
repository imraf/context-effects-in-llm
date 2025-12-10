import time
import logging
import json
import os
from typing import Dict, List
import config
from utils import OllamaClient, generate_filler_text, embed_fact, load_english_articles

logger = logging.getLogger(__name__)

class NeedleExperiment:
    def __init__(self, model: str):
        self.model = model
        self.client = OllamaClient(model)
        self.articles = load_english_articles()
        self.fact = "The secret code is BLUE-ZEBRA-99."
        self.question = "What is the secret code mentioned in the text? Return only the code."
        self.expected_answer = "BLUE-ZEBRA-99"

    def run(self) -> Dict[str, float]:
        logger.info(f"Starting Experiment 1 (Needle) for {self.model}")
        results = {}
        
        # Base context size
        context_length_words = 50000 
        base_context = generate_filler_text(context_length_words, self.articles)

        for position in config.EXP1_NEEDLE_POSITIONS:
            logger.info(f"Testing position: {position}")
            context = embed_fact(base_context, self.fact, position)
            
            start_time = time.time()
            response = self.client.generate(
                prompt=f"Context:\n{context}\n\nQuestion: {self.question}",
                temperature=0.1 # Low temp for factual retrieval
            )
            latency = time.time() - start_time
            
            # Evaluation
            is_correct = self.expected_answer.lower() in response.lower()
            
            results[position] = {
                "accuracy": 1.0 if is_correct else 0.0,
                "latency": latency,
                "response": response
            }
            logger.info(f"Position {position}: Correct={is_correct}, Latency={latency:.2f}s")

        return results

if __name__ == "__main__":
    # Test run
    exp = NeedleExperiment(config.MODELS[0])
    print(json.dumps(exp.run(), indent=2))
