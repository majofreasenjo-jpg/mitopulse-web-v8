from typing import Dict, List, Tuple
import numpy as np

from mitopulse_propagation.analysis.returns import build_return_matrix


def correlation_matrix(price_series: Dict[str, List[float]]) -> Tuple[list[str], np.ndarray]:
    symbols, matrix = build_return_matrix(price_series)
    corr = np.corrcoef(matrix)
    return symbols, corr
