
import pandas as pd

class RelationalWaveEngine:

    def propagate(self, events_df):
        if events_df.empty:
            return []

        events_df = events_df.sort_values("timestamp")
        waves = []

        prev = None
        for _, row in events_df.iterrows():
            if prev is not None:
                wave = abs(row["amount"] - prev)
                waves.append(wave)
            prev = row["amount"]

        return waves
