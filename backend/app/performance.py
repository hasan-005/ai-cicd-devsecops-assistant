import os
import time
import psutil


def measure_performance(function, *args, **kwargs):
    process = psutil.Process(os.getpid())

    memory_before = process.memory_info().rss / (1024 * 1024)

    start_time = time.perf_counter()

    result = function(*args, **kwargs)

    end_time = time.perf_counter()

    memory_after = process.memory_info().rss / (1024 * 1024)

    cpu_usage = process.cpu_percent(interval=0.1)

    execution_time = end_time - start_time
    memory_used = max(0, memory_after - memory_before)

    return {
        "result": result,
        "execution_time_seconds": round(execution_time, 6),
        "memory_used_mb": round(memory_used, 3),
        "cpu_usage_percent": round(cpu_usage, 2)
    }