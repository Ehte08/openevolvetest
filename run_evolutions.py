from pathlib import Path
from openevolve import run_evolution

project_dir = Path(__file__).resolve().parent

result = run_evolution(
    initial_program=project_dir / "initial_program.py",
    evaluator=project_dir / "evaluator.py",
    config=project_dir / "config.yaml",
    iterations=30,
    output_dir=project_dir / "runs/bubblesort",
)

print("best score:", result.best_score)
# …inspect result.history, result.best_program_code, etc.