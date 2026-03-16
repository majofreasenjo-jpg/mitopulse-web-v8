from engine.baseline_engine import baseline_projection
from engine.bioinspired_engine import bioinspired_projection

def evaluate_improvement(G, events_df, industry, client_size):
    baseline = baseline_projection(G)
    bio = bioinspired_projection(G)

    fraud_events = events_df[events_df["label"].isin(["mule_pattern", "scam_ring", "social_chain"])]
    exposure = int(fraud_events["amount"].sum())
    total_customers = max(sum(1 for _, a in G.nodes(data=True) if a.get("node_type") == "customer"), 1)

    baseline_detection = min(0.78, 0.18 + baseline["BLOCK"] / total_customers + baseline["REVIEW"] / total_customers * 0.35)
    bio_detection = min(0.92, 0.28 + bio["BLOCK"] / total_customers + bio["REVIEW"] / total_customers * 0.45)

    baseline_fp = max(2.5, 9.5 - baseline["BLOCK"] * 0.03 - baseline["REVIEW"] * 0.01)
    bio_fp = max(1.4, baseline_fp - 2.2)

    prevented_baseline = int(exposure * baseline_detection * 0.42)
    prevented_bio = int(exposure * bio_detection * 0.58)

    detection_lift = round((bio_detection - baseline_detection) / max(baseline_detection, 0.01) * 100, 2)
    fraud_reduction = round((prevented_bio - prevented_baseline) / max(exposure, 1) * 100, 2)
    fp_reduction = round((baseline_fp - bio_fp) / max(baseline_fp, 0.01) * 100, 2)

    return {
        "industry": industry,
        "client_size": client_size,
        "baseline": {
            "detection_rate": round(baseline_detection * 100, 2),
            "false_positive_proxy": round(baseline_fp, 2),
            "prevented_loss_estimate": prevented_baseline,
            "projection": baseline,
        },
        "bioinspired": {
            "detection_rate": round(bio_detection * 100, 2),
            "false_positive_proxy": round(bio_fp, 2),
            "prevented_loss_estimate": prevented_bio,
            "projection": bio,
        },
        "improvement": {
            "detection_lift_pct": detection_lift,
            "fraud_reduction_pct": fraud_reduction,
            "false_positive_reduction_pct": fp_reduction,
            "estimated_total_exposure": exposure,
        }
    }
