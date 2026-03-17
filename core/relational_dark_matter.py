
import pandas as pd

class RelationalDarkMatter:

    def compute_mdi(self, events_df):
        if events_df.empty:
            return 0

        freq = events_df["source_id"].value_counts(normalize=True)
        concentration = freq.max()

        coordination = len(freq[freq > 0.1])

        mdi = (concentration * 100) + (coordination * 5)
        return round(mdi, 2)

    def detect_hidden_clusters(self, events_df):
        if events_df.empty:
            return []

        grouped = events_df.groupby("timestamp")
        clusters = []

        for ts, g in grouped:
            if len(g) > 3:
                clusters.append({
                    "timestamp": ts,
                    "entities": list(g["source_id"].unique()),
                    "size": len(g)
                })

        return clusters
