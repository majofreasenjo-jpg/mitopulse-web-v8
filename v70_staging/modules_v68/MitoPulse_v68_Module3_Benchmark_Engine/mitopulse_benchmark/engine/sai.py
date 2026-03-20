from mitopulse_benchmark.utils.config import WEIGHTS

def compute_sai(lead_time: float, precision_gain: float, loss_prevented: float) -> float:
    return (
        WEIGHTS["lead_time"] * lead_time +
        WEIGHTS["precision_gain"] * precision_gain +
        WEIGHTS["loss_prevented"] * loss_prevented
    )
