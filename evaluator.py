import importlib.util
import math
import os
import random
import statistics
import time
from dataclasses import dataclass

# OpenEvolve evaluators typically return structured metrics/artifacts.
# The docs mention an EvaluationResult object, but returning a dict of metrics
# is also supported in the API examples. We'll keep it simple and rich in feedback.
# (If your installed version requires EvaluationResult, I’ll show that variant too.)
# See: evaluation result / quick start docs. 
# NOTE: Must define evaluate(program_path) function.

def _load_program(program_path: str):
    spec = importlib.util.spec_from_file_location("candidate_program", program_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    if not hasattr(mod, "sort_fn"):
        raise AttributeError("Program must define sort_fn(arr) -> sorted list")
    return mod.sort_fn

def _gen_cases(seed=123, sizes=(64, 128, 256, 512), cases_per_size=8):
    rng = random.Random(seed)
    cases = []
    for n in sizes:
        for _ in range(cases_per_size):
            arr = [rng.randrange(-10**6, 10**6) for _ in range(n)]
            cases.append(arr)
    return cases

def _time_sort(sort_fn, arr, repeats=3):
    # Time multiple repeats and take median (more stable)
    times = []
    for _ in range(repeats):
        a = list(arr)
        t0 = time.perf_counter()
        out = sort_fn(a)
        t1 = time.perf_counter()
        times.append(t1 - t0)
        # Correctness check (fast)
        if out != sorted(arr):
            raise ValueError("Incorrect sort output.")
    return statistics.median(times)

def _estimate_scaling(sizes, med_times):
    """
    Estimate scaling exponent k from log(time) ~ k*log(n) + b
    For O(n^k). Bubble sort should drift near k~2 for large n (roughly).
    """
    xs, ys = [], []
    for n, t in zip(sizes, med_times):
        if t <= 0:
            continue
        xs.append(math.log(n))
        ys.append(math.log(t))
    if len(xs) < 2:
        return float("inf")
    # simple least squares slope
    xbar = sum(xs) / len(xs)
    ybar = sum(ys) / len(ys)
    num = sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys))
    den = sum((x - xbar) ** 2 for x in xs)
    return num / den if den > 0 else float("inf")

def evaluate(program_path: str):
    sort_fn = _load_program(program_path)

    # Benchmark sizes (keep modest so runs don’t explode)
    sizes = [64, 128, 256, 512]
    cases_per_size = 6

    # Build cases grouped by size
    rng_seed = 123
    grouped = {n: [] for n in sizes}
    rng = random.Random(rng_seed)
    for n in sizes:
        for _ in range(cases_per_size):
            grouped[n].append([rng.randrange(-10**6, 10**6) for _ in range(n)])

    med_times = []
    notes = []
    try:
        for n in sizes:
            ts = []
            for arr in grouped[n]:
                ts.append(_time_sort(sort_fn, arr, repeats=3))
            med = statistics.median(ts)
            med_times.append(med)
            notes.append(f"n={n}: median={med:.6f}s")
    except Exception as e:
        # Hard fail => terrible score; include error for LLM feedback
        return {
            "score": -1e9,
            "runtime_score": -1e9,
            "scaling_score": -1e9,
            "artifacts": {
                "error": repr(e),
            },
        }

    # Metrics
    total_time = sum(med_times)  # lower is better
    scaling_k = _estimate_scaling(sizes, med_times)  # lower is better

    # Convert to "higher is better" scores
    # runtime_score ~ -total_time, scaling_score ~ -k
    runtime_score = -total_time
    scaling_score = -scaling_k

    # Combine: weight runtime heavily, but reward better scaling too
    score = (10.0 * runtime_score) + (1.0 * scaling_score)

    return {
        "score": score,
        "runtime_score": runtime_score,
        "scaling_k": scaling_k,
        "artifacts": {
            "timings": notes,
            "total_time_s": total_time,
            "scaling_exponent_k": scaling_k,
            "hint": (
                "Must remain correct sort_fn(arr)->sorted list. "
                "Improving algorithm (e.g., O(n log n)) will reduce scaling_k."
            ),
        },
    }