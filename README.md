# openevolvetest

Experimental sandbox for [**OpenEvolve**](https://github.com/codelion/openevolve) — an evolutionary code optimization framework that uses LLMs to iteratively rewrite code blocks toward a measurable objective. This repo evolves a Python `sort_fn` baseline (bubble sort) into a faster algorithm by scoring candidates on runtime and asymptotic scaling.

The goal isn't the sorting itself — it's exploring **how well an LLM-in-the-loop search can rediscover better algorithms** when given only a correctness oracle and a performance metric.

---

## How It Works

1. **Initial program** (`initial_program.py`) — `sort_fn(arr)` with an `# EVOLVE-BLOCK` marking the region OpenEvolve is allowed to rewrite. Starts as a bubble sort.
2. **Evaluator** (`evaluator.py`) — runs each candidate against batches of random arrays at sizes `[64, 128, 256, 512]`, takes the median runtime per size, checks correctness against `sorted()`, and fits a scaling exponent `k` via least-squares on `log(time) ~ k·log(n)`.
3. **Score** — `score = 10·(−total_time) + 1·(−k)`. Lower runtime *and* lower scaling exponent both push the score up. Incorrect output → hard fail.
4. **Configuration** (`config.yaml`) — Gemini 2.5 Flash as the evolving LLM, 50-individual population, 3 islands, migration every 10 generations.

---

## Quickstart

```bash
pip install openevolve
python run_evolutions.py
```

Runs and intermediate populations are saved to `runs/`.

---

## File Layout

| File | Purpose |
|---|---|
| `initial_program.py` | Baseline `sort_fn` with the `EVOLVE-BLOCK` marker |
| `evaluator.py` | Runtime + scaling benchmark with correctness oracle |
| `config.yaml` | OpenEvolve config (LLM, population, islands, migration) |
| `run_evolutions.py` | Entry point — kicks off the evolution loop |

---

## What I'm Learning

- Designing **shaped reward functions** for code-search agents (runtime alone isn't enough; scaling exponent matters)
- How **population + island migration** affects exploration vs. exploitation in LLM-driven search
- Practical limits of evolutionary code optimization for non-trivial algorithms

---

## Tech

- [OpenEvolve](https://github.com/codelion/openevolve) — evolutionary loop
- Gemini 2.5 Flash — code rewriter LLM
- Python standard library only inside the EVOLVE block (no numpy/sort cheats)
