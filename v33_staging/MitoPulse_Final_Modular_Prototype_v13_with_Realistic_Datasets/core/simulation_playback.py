
class SimulationPlayback:
    def run_steps(self, events_df, rfdc_result=None):
        steps = []
        for i in range(min(len(events_df), 50)):
            subset = events_df.iloc[:i+1]
            nodes = list(set(subset["source_id"]).union(set(subset["target_id"])))
            edges = subset[["source_id","target_id"]].to_dict("records")

            steps.append({
                "step": i+1,
                "nodes": nodes,
                "edges": edges
            })
        return steps
