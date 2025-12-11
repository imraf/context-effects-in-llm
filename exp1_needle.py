import asyncio
import json
import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union, cast

import config
from base import ExperimentBase
from utils import (
    OllamaClient,
    embed_fact,
    generate_filler_text,
    insert_secret_message,
    load_english_articles,
    load_text_from_file,
)

logger = logging.getLogger(__name__)


class NeedleExperiment(ExperimentBase):
    ID = 1
    NAME = "Needle in Haystack"

    def __init__(self, model: str, mode: Literal["quick", "info_retrieval", "anomaly_detection"] = "quick", **kwargs):
        """Initialize needle experiment.

        Args:
            model: Model identifier
            mode: Experiment mode - "quick", "info_retrieval", or "anomaly_detection"
        """
        super().__init__(model, mode=mode, **kwargs)
        self.client = OllamaClient(model)
        self.mode = mode

        if mode not in config.NEEDLE_EXPERIMENTS:
            raise ValueError(f"Invalid mode: {mode}. Must be one of {list(config.NEEDLE_EXPERIMENTS.keys())}")

        self.exp_config = config.NEEDLE_EXPERIMENTS[mode]

        # Load articles for quick mode
        if mode == "quick":
            self.articles = load_english_articles()

    def run(self) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Run the needle experiment based on the configured mode."""
        if self.mode == "quick":
            return self.run_quick()
        else:
            return self.run_detailed()

    def run_quick(self) -> Dict[str, Any]:
        """Run quick needle experiment (original implementation)."""
        logger.info(f"Starting Experiment 1 (Needle - Quick Mode) for {self.model}")
        results: Dict[str, Any] = {}

        exp_cfg = cast(Dict[str, Any], self.exp_config)
        fact: str = exp_cfg["fact"]
        question: str = exp_cfg["question"]
        expected_answer: str = exp_cfg["expected_answer"]
        context_words: int = exp_cfg["context_words"]
        positions: List[str] = exp_cfg["positions"]

        # Base context size
        base_context = generate_filler_text(context_words, self.articles)

        for position in positions:
            logger.info(f"Testing position: {position}")
            context = embed_fact(base_context, fact, position)

            start_time = time.time()
            response_data = self.client.generate_with_stats(
                prompt=f"Context:\n{context}\n\nQuestion: {question}", temperature=0.1
            )
            latency = time.time() - start_time

            response_text = response_data.get("response", "")
            prompt_eval_count = response_data.get("prompt_eval_count", 0)

            # Evaluation
            is_correct = expected_answer.lower() in response_text.lower()

            results[position] = {
                "accuracy": 1.0 if is_correct else 0.0,
                "latency": latency,
                "response": response_text,
                "prompt_tokens": prompt_eval_count,
            }
            logger.info(f"Position {position}: Correct={is_correct}, Latency={latency:.2f}s")

        return results

    async def _run_single_trial(
        self,
        prompt_length: int,
        position: str,
        secret_message: str,
        question: str,
        expected_answer: str,
        source_file: str,
    ) -> Optional[Dict[str, Any]]:
        """Run a single async trial."""
        logger.info(f"Testing length={prompt_length}, position={position}")

        # Load text (sync I/O is acceptable here as it's fast)
        base_text = load_text_from_file(source_file, prompt_length)

        if not base_text:
            logger.warning(f"Could not load text from {source_file}, skipping")
            return None

        # Insert secret message
        text_with_secret = insert_secret_message(base_text, position, secret_message)
        include_secret = position != "control"

        # Create prompt
        prompt = f"""Below is a passage of text. Please read it carefully and answer the following question:

{question}

<TEXT>
{text_with_secret}
</TEXT>

Please provide your answer clearly."""

        # Run query
        experiment_id = f"{self.model}_{prompt_length}_{position}_{int(time.time())}"

        start_time = time.time()
        try:
            # Use async generation
            response_data = await self.client.generate_with_stats_async(prompt=prompt, temperature=0.1, max_tokens=500)
            query_time = time.time() - start_time

            response_text = response_data.get("response", "")
            token_count = response_data.get("prompt_eval_count", 0)

            # Detection
            found_secret = expected_answer.upper() in response_text.upper()

            result = {
                "experiment_id": experiment_id,
                "timestamp": datetime.now().isoformat(),
                "model": self.model,
                "mode": self.mode,
                "prompt_length_chars": len(text_with_secret),
                "target_prompt_length": prompt_length,
                "message_position": position,
                "secret_message": secret_message if include_secret else None,
                "include_secret": include_secret,
                "found_secret": found_secret,
                "token_count": token_count,
                "query_time_seconds": query_time,
                "response": response_text,
                "ollama_metadata": {
                    "eval_count": response_data.get("eval_count", 0),
                    "eval_duration": response_data.get("eval_duration", 0),
                    "load_duration": response_data.get("load_duration", 0),
                    "prompt_eval_count": response_data.get("prompt_eval_count", 0),
                    "prompt_eval_duration": response_data.get("prompt_eval_duration", 0),
                    "total_duration": response_data.get("total_duration", 0),
                },
            }

            logger.info(f"Result: found={found_secret}, tokens={token_count}, time={query_time:.2f}s")
            return result

        except Exception as e:
            logger.error(f"Error in trial {experiment_id}: {e}")
            return None

    async def _run_detailed_async(self) -> List[Dict[str, Any]]:
        """Async implementation of detailed run."""
        exp_cfg = cast(Dict[str, Any], self.exp_config)
        secret_message: str = exp_cfg["secret_message"]
        question: str = exp_cfg["question"]
        expected_answer: str = exp_cfg["expected_answer"]
        source_file: str = exp_cfg["source_file"]
        prompt_lengths: List[int] = exp_cfg["prompt_lengths"]
        positions: List[str] = exp_cfg["positions"]

        tasks = []
        for prompt_length in prompt_lengths:
            for position in positions:
                tasks.append(
                    self._run_single_trial(
                        prompt_length, position, secret_message, question, expected_answer, source_file
                    )
                )

        # Gather all results
        results = await asyncio.gather(*tasks)
        # Filter out None results
        return [r for r in results if r is not None]

    def run_detailed(self) -> List[Dict[str, Any]]:
        """Run detailed needle experiment with multiple context lengths."""
        logger.info(f"Starting Experiment 1 (Needle - {self.mode.replace('_', ' ').title()} Mode) for {self.model}")
        # Run the async loop
        return asyncio.run(self._run_detailed_async())

    def save_detailed_results(self, results: List[Dict[str, Any]], output_dir: Optional[str] = None):
        """Save detailed experiment results to JSON."""
        if output_dir is None:
            output_dir = config.RESULTS_DIR

        output_file = os.path.join(output_dir, f"{self.mode}_results.json")

        exp_cfg = cast(Dict[str, Any], self.exp_config)
        output = {
            "experiment_metadata": {
                "experiment_name": f"needle-in-haystack-{self.mode}",
                "date_run": datetime.now().isoformat(),
                "secret_message": exp_cfg["secret_message"],
                "source_file": exp_cfg.get("source_file", "N/A"),
                "total_experiments": len(results),
                "models": [self.model],
                "prompt_lengths": exp_cfg["prompt_lengths"],
                "positions": exp_cfg["positions"],
            },
            "results": results,
        }

        with open(output_file, "w") as f:
            json.dump(output, f, indent=2)

        logger.info(f"Saved {len(results)} results to {output_file}")


if __name__ == "__main__":
    import sys

    # Test run
    mode_arg = sys.argv[1] if len(sys.argv) > 1 else "quick"
    if mode_arg not in ["quick", "info_retrieval", "anomaly_detection"]:
        print(f"Invalid mode: {mode_arg}")
        sys.exit(1)
    
    mode: Literal["quick", "info_retrieval", "anomaly_detection"] = mode_arg  # type: ignore
    model = config.MODELS[0] if config.MODELS else "llama3.2:3b-100K"

    exp = NeedleExperiment(model, mode=mode)
    results = exp.run()

    if mode == "quick":
        if isinstance(results, dict):
            print(json.dumps(results, indent=2))
    else:
        if isinstance(results, list):
            exp.save_detailed_results(results)
            print(f"Completed {len(results)} experiments")
