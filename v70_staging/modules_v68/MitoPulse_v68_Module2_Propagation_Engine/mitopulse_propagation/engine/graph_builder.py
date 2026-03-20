from typing import Dict, List
import numpy as np

from mitopulse_propagation.analysis.returns import build_return_matrix
from mitopulse_propagation.analysis.correlation import correlation_matrix
from mitopulse_propagation.analysis.delay import delay_matrix
from mitopulse_propagation.utils.config import MAX_LAG, CORRELATION_THRESHOLD


def build_propagation_graph(price_series: Dict[str, List[float]]) -> Dict:
    symbols, returns = build_return_matrix(price_series)
    _, corr = correlation_matrix(price_series)
    lags, lag_scores = delay_matrix(returns, max_lag=MAX_LAG)

    nodes = [{"id": s} for s in symbols]
    edges = []
    for i, src in enumerate(symbols):
        for j, dst in enumerate(symbols):
            if i == j:
                continue
            weight = float(corr[i, j])
            if abs(weight) < CORRELATION_THRESHOLD:
                continue
            edges.append({
                "source": src,
                "target": dst,
                "correlation": round(weight, 4),
                "lag": int(lags[i, j]),
                "lag_score": round(float(lag_scores[i, j]), 4),
            })

    return {
        "nodes": nodes,
        "edges": edges,
        "correlation_matrix": corr.tolist(),
        "lag_matrix": lags.tolist(),
        "lag_score_matrix": lag_scores.tolist(),
    }
