from typing import List, Dict
import numpy as np

def lead_time(mito_ts: float, baseline_ts: float) -> float:
    return baseline_ts - mito_ts

def precision(tp: int, fp: int) -> float:
    return tp / (tp + fp) if (tp + fp) > 0 else 0.0

def false_rates(fp: int, fn: int, total: int) -> Dict:
    return {
        "fpr": fp / total if total else 0.0,
        "fnr": fn / total if total else 0.0
    }

def loss_prevented(events: List[Dict]) -> float:
    return sum(e["amount"] * e["probability"] for e in events)
