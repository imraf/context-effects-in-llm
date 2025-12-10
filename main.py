import os
import json
import logging
import argparse
import config
from exp1_needle import NeedleExperiment
from exp2_size import ContextSizeExperiment
from exp3_rag import RagExperiment
from exp4_strategies import StrategiesExperiment

logger = logging.getLogger("BenchmarkRunner")

def run_benchmark(models=None, experiments=None, exp1_mode="quick"):
    """Run benchmark suite.
    
    Args:
        models: List of models to test (default: all from config)
        experiments: List of experiment numbers to run (default: all)
        exp1_mode: Mode for experiment 1 - "quick", "info_retrieval", or "anomaly_detection"
    """
    logger.info("Starting Full Benchmark Suite")
    
    if models is None:
        models = config.MODELS
    
    if experiments is None:
        experiments = [1, 2, 3, 4]
    
    for model in models:
        logger.info(f"========================================")
        logger.info(f"Processing Model: {model}")
        logger.info(f"========================================")
        
        model_results = {
            "model": model,
            "exp1_needle": {},
            "exp2_size": [],
            "exp3_rag": {},
            "exp4_strategies": {}
        }
        
        try:
            if 1 in experiments:
                # Experiment 1
                logger.info(f"Running Exp 1: Needle in Haystack (mode={exp1_mode})...")
                exp1 = NeedleExperiment(model, mode=exp1_mode)
                results = exp1.run()
                
                if exp1_mode == "quick":
                    model_results["exp1_needle"] = results
                else:
                    # For detailed modes, save separately
                    exp1.save_detailed_results(results)
                    logger.info(f"Detailed results saved separately for {exp1_mode}")
        except Exception as e:
            logger.error(f"Exp 1 failed for {model}: {e}")

        try:
            if 2 in experiments:
                # Experiment 2
                logger.info(f"Running Exp 2: Context Size...")
                exp2 = ContextSizeExperiment(model)
                model_results["exp2_size"] = exp2.run()
        except Exception as e:
            logger.error(f"Exp 2 failed for {model}: {e}")

        try:
            if 3 in experiments:
                # Experiment 3
                logger.info(f"Running Exp 3: RAG vs Full...")
                exp3 = RagExperiment(model)
                model_results["exp3_rag"] = exp3.run()
        except Exception as e:
            logger.error(f"Exp 3 failed for {model}: {e}")

        try:
            if 4 in experiments:
                # Experiment 4
                logger.info(f"Running Exp 4: Strategies...")
                exp4 = StrategiesExperiment(model)
                model_results["exp4_strategies"] = exp4.run()
        except Exception as e:
            logger.error(f"Exp 4 failed for {model}: {e}")

        # Save results for this model (for quick mode and exp2-4)
        if exp1_mode == "quick" or any(e in experiments for e in [2, 3, 4]):
            output_file = os.path.join(config.RESULTS_DIR, f"{model.replace(':', '_')}_results.json")
            with open(output_file, "w") as f:
                json.dump(model_results, f, indent=2)
            logger.info(f"Saved results to {output_file}")

    logger.info("Benchmark Suite Complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run LLM context benchmarking experiments")
    parser.add_argument("--models", nargs="+", help="Models to test (default: all from config)")
    parser.add_argument("--experiments", nargs="+", type=int, choices=[1, 2, 3, 4],
                       help="Experiments to run (default: all)")
    parser.add_argument("--exp1-mode", choices=["quick", "info_retrieval", "anomaly_detection"],
                       default="quick", help="Mode for Experiment 1 (default: quick)")
    
    args = parser.parse_args()
    
    run_benchmark(
        models=args.models,
        experiments=args.experiments,
        exp1_mode=args.exp1_mode
    )
