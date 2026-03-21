from typing import Dict, List, Tuple
import numpy as np


def best_lag(a: np.ndarray, b: np.ndarray, max_lag: int = 5) -> Tuple[int, float]:
    best = (0, -1.0)
    for lag in range(-max_lag, max_lag + 1):
        if lag < 0:
            x, y = a[:lag], b[-lag:]
        elif lag > 0:
            x, y = a[lag:], b[:-lag]
        else:
            x, y = a, b
        if len(x) < 5 or len(y) < 5:
            continue
        score = float(np.corrcoef(x, y)[0, 1])
        if abs(score) > abs(best[1]):
            best = (lag, score)
    return best


def delay_matrix(return_matrix: np.ndarray, max_lag: int = 5) -> Tuple[np.ndarray, np.ndarray]:
    n = return_matrix.shape[0]
    lags = np.zeros((n, n), dtype=int)
    scores = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            lag, score = best_lag(return_matrix[i], return_matrix[j], max_lag=max_lag)
            lags[i, j] = lag
            scores[i, j] = score
    return lags, scores
