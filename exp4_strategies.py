import json
import logging
from typing import Any, Dict

import config
from base import ExperimentBase
from utils import OllamaClient

logger = logging.getLogger(__name__)


class StrategiesExperiment(ExperimentBase):
    ID = 4
    NAME = "Context Strategies"

    def __init__(self, model: str, **kwargs):
        super().__init__(model, **kwargs)
        self.client = OllamaClient(model)
        self.actions = [
            "I enter the Kitchen.",
            "I pick up the Apple.",
            "I move to the Living Room.",
            "I put the Apple on the Table.",
            "I move to the Bedroom.",
            "I pick up the Book.",
            "I move to the Kitchen.",
            "I put the Book in the Fridge.",  # Nonsense action to test memory
            "I move to the Garden.",
            "I pick up the Ball.",
        ]
        self.final_question = "Where is the Apple?"
        self.expected_answer = "Table"  # Living Room Table

    def run(self) -> Dict[str, Any]:
        logger.info(f"Starting Experiment 4 (Strategies) for {self.model}")
        results = {}

        # 1. Baseline (Full History)
        history = "\n".join(self.actions)
        prompt = f"History:\n{history}\n\nQuestion: {self.final_question}\n" "Answer with just the location name."
        resp = self.client.generate(prompt)
        results["baseline"] = {
            "response": resp,
            "correct": self.expected_answer.lower() in resp.lower(),
        }

        # 2. Select (Simulated RAG - picking relevant lines)
        # Ideally we use embeddings, but for this simple list, keyword matching is a proxy
        keywords = ["Apple", "put", "pick"]
        selected = [a for a in self.actions if any(k in a for k in keywords)]
        history_select = "\n".join(selected)
        prompt = (
            f"Relevant History:\n{history_select}\n\n"
            f"Question: {self.final_question}\nAnswer with just the location name."
        )
        resp = self.client.generate(prompt)
        results["select"] = {
            "response": resp,
            "correct": self.expected_answer.lower() in resp.lower(),
        }

        # 3. Compress (Summarize every 3 steps)
        summary = ""
        chunk_size = 3
        for i in range(0, len(self.actions), chunk_size):
            chunk = "\n".join(self.actions[i : i + chunk_size])
            # Ask model to update summary
            prompt = (
                f"Current Summary: {summary}\nNew Actions:\n{chunk}\n\n"
                "Update the summary of where items are located. Keep it brief."
            )
            summary = self.client.generate(prompt)

        prompt = (
            f"Summary of Events:\n{summary}\n\nQuestion: {self.final_question}\n" "Answer with just the location name."
        )
        resp = self.client.generate(prompt)
        results["compress"] = {
            "response": resp,
            "correct": self.expected_answer.lower() in resp.lower(),
        }

        # 4. Write (Scratchpad - update state after each step)
        scratchpad = "Current State: {}"
        for action in self.actions:
            prompt = (
                f"{scratchpad}\nAction: {action}\n\n"
                "Update the Current State JSON to reflect item locations. Return only JSON."
            )
            scratchpad = self.client.generate(prompt)

        prompt = (
            f"Final State:\n{scratchpad}\n\nQuestion: {self.final_question}\n" "Answer with just the location name."
        )
        resp = self.client.generate(prompt)
        results["write"] = {
            "response": resp,
            "correct": self.expected_answer.lower() in resp.lower(),
        }

        return results


if __name__ == "__main__":
    exp = StrategiesExperiment(config.MODELS[0])
    print(json.dumps(exp.run(), indent=2))
