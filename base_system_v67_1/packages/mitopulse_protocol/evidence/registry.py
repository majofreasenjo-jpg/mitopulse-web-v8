import json
from pathlib import Path

def load_cases(root: Path):
    cases_dir = root / "data" / "examples" / "evidence_cases"
    cases = []
    for p in sorted(cases_dir.glob("*.json")):
        with open(p, "r", encoding="utf-8") as f:
            cases.append(json.load(f))
    return cases
