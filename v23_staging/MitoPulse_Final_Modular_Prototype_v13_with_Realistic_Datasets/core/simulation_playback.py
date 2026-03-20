import pandas as pd

class SimulationPlayback:
    def run_steps(self, events_df):
        if events_df.empty:
            return []

        out = []
        df = events_df.copy()
        if "timestamp" in df.columns:
            df = df.sort_values("timestamp")

        max_steps = min(len(df), 60)
        for i in range(max_steps):
            subset = df.iloc[:i+1]
            active_nodes = len(set(subset["source_id"].astype(str).tolist() + subset["target_id"].astype(str).tolist()))
            event_count = len(subset)
            amount_sum = float(subset["amount"].fillna(0).astype(float).sum()) if "amount" in subset.columns else 0.0

            out.append({
                "step": i + 1,
                "events_processed": event_count,
                "active_nodes": active_nodes,
                "timestamp": str(subset.iloc[-1]["timestamp"]) if "timestamp" in subset.columns else "",
                "cumulative_amount": round(amount_sum, 2),
                "phase": "emergence" if i < max_steps * 0.33 else ("propagation" if i < max_steps * 0.66 else "criticality")
            })
        return out
