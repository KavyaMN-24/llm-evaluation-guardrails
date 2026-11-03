import json
from pathlib import Path

from app.evaluation.evaluator import evaluate_dataset

dataset_path = Path("data/sample/evaluation_cases.json")

with dataset_path.open("r", encoding="utf-8") as file:
    cases = json.load(file)

report = evaluate_dataset(cases)

print("\n===== LLM EVALUATION REPORT =====")
print(json.dumps(report, indent=4))