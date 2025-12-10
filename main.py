import os
import json
import logging
import config
from exp1_needle import NeedleExperiment
from exp2_size import ContextSizeExperiment
from exp3_rag import RagExperiment
from exp4_strategies import StrategiesExperiment

logger = logging.getLogger("BenchmarkRunner")

def run_benchmark():
    logger.info("Starting Full Benchmark Suite")
    
    for model in config.MODELS:
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
            # Experiment 1
            logger.info(f"Running Exp 1: Needle in Haystack...")
            exp1 = NeedleExperiment(model)
            model_results["exp1_needle"] = exp1.run()
        except Exception as e:
            logger.error(f"Exp 1 failed for {model}: {e}")

        try:
            # Experiment 2
            logger.info(f"Running Exp 2: Context Size...")
            exp2 = ContextSizeExperiment(model)
            model_results["exp2_size"] = exp2.run()
        except Exception as e:
            logger.error(f"Exp 2 failed for {model}: {e}")

        try:
            # Experiment 3
            logger.info(f"Running Exp 3: RAG vs Full...")
            exp3 = RagExperiment(model)
            model_results["exp3_rag"] = exp3.run()
        except Exception as e:
            logger.error(f"Exp 3 failed for {model}: {e}")

        try:
            # Experiment 4
            logger.info(f"Running Exp 4: Strategies...")
            exp4 = StrategiesExperiment(model)
            model_results["exp4_strategies"] = exp4.run()
        except Exception as e:
            logger.error(f"Exp 4 failed for {model}: {e}")

        # Save results for this model
        output_file = os.path.join(config.RESULTS_DIR, f"{model.replace(':', '_')}_results.json")
        with open(output_file, "w") as f:
            json.dump(model_results, f, indent=2)
        logger.info(f"Saved results to {output_file}")

    logger.info("Benchmark Suite Complete.")

if __name__ == "__main__":
    run_benchmark()
