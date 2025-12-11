import os
import json
import logging
import argparse
from multiprocessing import Pool, cpu_count
from functools import partial
import time
import config
from plugins import PluginRegistry

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
    logger.info("========================================")
    logger.info(f"Processing Model: {model}")
    logger.info("========================================")

    # Discover experiments
    PluginRegistry.discover_experiments()
    all_experiments = PluginRegistry.get_all_experiments()

    if experiments is None:
        experiments = list(all_experiments.keys())

    model_results = {
        "model": model,
    }

    # Compatibility mapping for result keys
    key_map = {
        1: "exp1_needle",
        2: "exp2_size",
        3: "exp3_rag",
        4: "exp4_strategies",
    }

    experiments.sort()

    for exp_id in experiments:
        if exp_id not in all_experiments:
            logger.warning(f"Experiment ID {exp_id} not found in registry.")
            continue

        ExpClass = all_experiments[exp_id]
        key = key_map.get(exp_id, f"exp{exp_id}")

        logger.info(f"[{model}] Running Exp {exp_id}: {ExpClass.NAME}...")

        try:
            # Prepare arguments
            kwargs = {}
            if exp_id == 1:
                kwargs["mode"] = exp1_mode

            # Initialize and run
            experiment = ExpClass(model, **kwargs)
            results = experiment.run()

            # Handle results
            if exp_id == 1 and exp1_mode != "quick":
                # Detailed mode: save separately
                if hasattr(experiment, "save_detailed_results"):
                    experiment.save_detailed_results(results)
                    logger.info(
                        f"[{model}] Detailed results saved separately for {exp1_mode}"
                    )
                else:
                    logger.warning(
                        f"[{model}] Detailed results generated but save method missing."
                    )
            else:
                # Standard mode: add to model results
                model_results[key] = results

        except Exception as e:
            logger.error(f"Exp {exp_id} failed for {model}: {e}")

    # Save results for this model (if not just running detailed exp1)
    # Logic: If running quick mode OR any other experiment, save the summary JSON.
    should_save = exp1_mode == "quick" or any(e != 1 for e in experiments)
    
    if should_save:
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
        # Default to all discovered experiments
        PluginRegistry.discover_experiments()
        experiments = list(PluginRegistry.get_all_experiments().keys())

    if parallel and len(models) > 1:
        # Limit processes to CPU count or number of models, whichever is smaller
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