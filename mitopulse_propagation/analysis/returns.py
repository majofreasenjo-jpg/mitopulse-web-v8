from typing import Dict, List
import numpy as np


def closes_to_returns(closes: List[float]) -> np.ndarray:
    arr = np.array(closes, dtype=float)
    if len(arr) < 2:
        return np.array([], dtype=float)
    return np.diff(arr) / arr[:-1]


def build_return_matrix(price_series: Dict[str, List[float]]) -> tuple[list[str], np.ndarray]:
    symbols = list(price_series.keys())
    returns = [closes_to_returns(price_series[s]) for s in symbols]
    min_len = min(len(r) for r in returns)
    trimmed = np.array([r[-min_len:] for r in returns], dtype=float)
    return symbols, trimmed
