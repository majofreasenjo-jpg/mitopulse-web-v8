import pandas as pd

class SimulationPlayback:
    def run_steps(self, events_df, rfdc_result=None):
        if events_df.empty:
            return []

        out = []
        df = events_df.copy()
        if "timestamp" in df.columns:
            df = df.sort_values("timestamp")

        max_steps = min(len(df), 60)

        hidden_count = 0
        mdi = 0
        decision = {}
        metrics = {}
        if rfdc_result:
            hidden_count = len(rfdc_result.get("hidden_clusters", []))
            metrics = rfdc_result.get("metrics", {})
            mdi = metrics.get("mdi", 0)
            decision = rfdc_result.get("decision", {})

        for i in range(max_steps):
            subset = df.iloc[:i+1]
            active_nodes = len(set(subset["source_id"].astype(str).tolist() + subset["target_id"].astype(str).tolist()))
            event_count = len(subset)
            amount_sum = float(subset["amount"].fillna(0).astype(float).sum()) if "amount" in subset.columns else 0.0

            progress = (i + 1) / max_steps
            if progress < 0.33:
                phase = "emergence"
            elif progress < 0.66:
                phase = "propagation"
            else:
                phase = "criticality"

            action_triggered = False
            if decision.get("action") in ["review_and_limit", "block_or_freeze"] and progress > 0.72:
                action_triggered = True

            out.append({
                "step": i + 1,
                "events_processed": event_count,
                "active_nodes": active_nodes,
                "timestamp": str(subset.iloc[-1]["timestamp"]) if "timestamp" in subset.columns else "",
                "cumulative_amount": round(amount_sum, 2),
                "phase": phase,
                "mdi_snapshot": round(float(mdi) * progress, 3),
                "hidden_cluster_snapshot": int(max(1, hidden_count * progress)) if hidden_count else 0,
                "scr_snapshot": round(float(metrics.get("scr", 0)) * progress, 3),
                "tpi_snapshot": round(float(metrics.get("tpi", 0)) * progress, 3),
                "nhi_snapshot": round(max(0, 100 - ((100 - float(metrics.get("nhi", 70))) * progress)), 3),
                "action_triggered": action_triggered,
                "recommended_action": decision.get("action", "monitor")
            })
        return out
