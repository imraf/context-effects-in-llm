import os
import json
import logging
import argparse
from multiprocessing import Pool, cpu_count
from functools import partial
import time
import config
from exp1_needle import NeedleExperiment
from exp2_size import ContextSizeExperiment
from exp3_rag import RagExperiment
from exp4_strategies import StrategiesExperiment

logger = logging.getLogger("BenchmarkRunner")


def run_single_model(model: str, experiments: list = None, exp1_mode: str = "quick"):
    """Run all selected experiments for a single model.

    Args:
        model: Model identifier.
        experiments: List of experiment IDs to run.
        exp1_mode: Mode for Experiment 1.

    Returns:
        Dictionary containing results for the model.
    """
    logger.info(f"========================================")
    logger.info(f"Processing Model: {model}")
    logger.info(f"========================================")

    model_results = {
        "model": model,
        "exp1_needle": {},
        "exp2_size": [],
        "exp3_rag": {},
        "exp4_strategies": {},
    }

    if experiments is None:
        experiments = [1, 2, 3, 4]

    try:
        if 1 in experiments:
            # Experiment 1
            logger.info(
                f"[{model}] Running Exp 1: Needle in Haystack (mode={exp1_mode})..."
            )
            exp1 = NeedleExperiment(model, mode=exp1_mode)
            results = exp1.run()

            if exp1_mode == "quick":
                model_results["exp1_needle"] = results
            else:
                # For detailed modes, save separately
                exp1.save_detailed_results(results)
                logger.info(
                    f"[{model}] Detailed results saved separately for {exp1_mode}"
                )
    except Exception as e:
        logger.error(f"Exp 1 failed for {model}: {e}")

    try:
        if 2 in experiments:
            # Experiment 2
            logger.info(f"[{model}] Running Exp 2: Context Size...")
            exp2 = ContextSizeExperiment(model)
            model_results["exp2_size"] = exp2.run()
    except Exception as e:
        logger.error(f"Exp 2 failed for {model}: {e}")

    try:
        if 3 in experiments:
            # Experiment 3
            logger.info(f"[{model}] Running Exp 3: RAG vs Full...")
            exp3 = RagExperiment(model)
            model_results["exp3_rag"] = exp3.run()
    except Exception as e:
        logger.error(f"Exp 3 failed for {model}: {e}")

    try:
        if 4 in experiments:
            # Experiment 4
            logger.info(f"[{model}] Running Exp 4: Strategies...")
            exp4 = StrategiesExperiment(model)
            model_results["exp4_strategies"] = exp4.run()
    except Exception as e:
        logger.error(f"Exp 4 failed for {model}: {e}")

    # Save results for this model (for quick mode and exp2-4)
    if exp1_mode == "quick" or any(e in experiments for e in [2, 3, 4]):
        safe_model_name = model.replace(":", "_")
        output_file = os.path.join(
            config.RESULTS_DIR, f"{safe_model_name}_results.json"
        )
        try:
            with open(output_file, "w") as f:
                json.dump(model_results, f, indent=2)
            logger.info(f"[{model}] Saved results to {output_file}")
        except Exception as e:
            logger.error(f"[{model}] Failed to save results: {e}")

    return model_results


def run_benchmark(models=None, experiments=None, exp1_mode="quick", parallel=False):
    """Run benchmark suite.

    Args:
        models: List of models to test (default: all from config)
        experiments: List of experiment numbers to run (default: all)
        exp1_mode: Mode for experiment 1 - "quick", "info_retrieval", or "anomaly_detection"
        parallel: Whether to run models in parallel processes
    """
    logger.info("Starting Full Benchmark Suite")
    start_time = time.time()

    if models is None:
        models = config.MODELS

    if experiments is None:
        experiments = [1, 2, 3, 4]

    if parallel and len(models) > 1:
        # Limit processes to CPU count or number of models, whichever is smaller
        # Note: If running against local Ollama, too many parallel requests might choke it.
        # But for benchmarking against a robust server or API, this is great.
        num_processes = min(cpu_count(), len(models))
        # Cap at 4 to be safe for typical local setups unless explicitly overridden
        num_processes = min(num_processes, 4)

        logger.info(f"Running benchmark with {num_processes} parallel processes")

        func = partial(run_single_model, experiments=experiments, exp1_mode=exp1_mode)

        with Pool(processes=num_processes) as pool:
            pool.map(func, models)
    else:
        logger.info("Running benchmark sequentially")
        for model in models:
            run_single_model(model, experiments, exp1_mode)

    end_time = time.time()
    duration = end_time - start_time
    logger.info(f"Benchmark Suite Complete. Total time: {duration:.2f}s")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run LLM context benchmarking experiments"
    )
    parser.add_argument(
        "--models", nargs="+", help="Models to test (default: all from config)"
    )
    parser.add_argument(
        "--experiments",
        nargs="+",
        type=int,
        choices=[1, 2, 3, 4],
        help="Experiments to run (default: all)",
    )
    parser.add_argument(
        "--exp1-mode",
        choices=["quick", "info_retrieval", "anomaly_detection"],
        default="quick",
        help="Mode for Experiment 1 (default: quick)",
    )
    parser.add_argument(
        "--parallel", action="store_true", help="Run models in parallel"
    )

    args = parser.parse_args()

    run_benchmark(
        models=args.models,
        experiments=args.experiments,
        exp1_mode=args.exp1_mode,
        parallel=args.parallel,
    )
