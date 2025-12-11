import argparse
import logging
import time
from functools import partial
from multiprocessing import Pool, cpu_count

logger = logging.getLogger("BenchmarkTest")
logging.basicConfig(level=logging.INFO)


def dummy_task(duration):
    """Simulate a task taking 'duration' seconds."""
    time.sleep(duration)
    return duration


def run_benchmark(num_tasks=8, task_duration=1.0):
    """Compare sequential vs parallel execution."""
    tasks = [task_duration] * num_tasks

    # Sequential
    logger.info(f"Starting Sequential Benchmark with {num_tasks} tasks of {task_duration}s...")
    start_seq = time.time()
    for t in tasks:
        dummy_task(t)
    end_seq = time.time()
    seq_time = end_seq - start_seq
    logger.info(f"Sequential Time: {seq_time:.2f}s")

    # Parallel
    num_processes = min(cpu_count(), 4)
    logger.info(f"Starting Parallel Benchmark with {num_processes} processes...")
    start_par = time.time()
    with Pool(processes=num_processes) as pool:
        pool.map(dummy_task, tasks)
    end_par = time.time()
    par_time = end_par - start_par
    logger.info(f"Parallel Time: {par_time:.2f}s")

    speedup = seq_time / par_time
    logger.info(f"Speedup: {speedup:.2f}x")

    return {"sequential": seq_time, "parallel": par_time, "speedup": speedup}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark Multiprocessing Overhead")
    parser.add_argument("--tasks", type=int, default=8)
    parser.add_argument("--duration", type=float, default=0.5)
    args = parser.parse_args()

    run_benchmark(args.tasks, args.duration)
