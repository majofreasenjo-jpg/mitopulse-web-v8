import networkx as nx

def build_graph(customers, devices, events, signals):
    G = nx.Graph()
    for _, row in customers.iterrows():
        G.add_node(row["customer_id"], node_type="customer", segment=row.get("segment", "unknown"), region=row.get("region", "unknown"), created_at=row.get("created_at"))
    for _, row in devices.iterrows():
        dev = row["device_id"]; cust = row["customer_id"]
        if dev not in G:
            G.add_node(dev, node_type="device", channel=row.get("channel", "unknown"))
        if cust not in G:
            G.add_node(cust, node_type="customer")
        G.add_edge(cust, dev, edge_type="owns_device", label=row.get("risk_hint", "normal"), weight=0.20)
    for _, row in events.iterrows():
        a = row["source_id"]; b = row["target_id"]
        if a not in G: G.add_node(a, node_type="external")
        if b not in G: G.add_node(b, node_type="external")
        G.add_edge(a, b, edge_type=row["event_type"], context=row["context"], amount=float(row["amount"]), label=row.get("label", "normal"), weight=min(float(row["amount"]) / 1000.0, 2.5), timestamp=row.get("timestamp"))
    for _, row in signals.iterrows():
        ent = row["entity_id"]
        if ent in G:
            G.nodes[ent]["signal_type"] = row["signal_type"]
            G.nodes[ent]["signal_severity"] = float(row["severity"])
            G.nodes[ent]["signal_source"] = row.get("source", "unknown")
            G.nodes[ent]["signal_timestamp"] = row.get("timestamp")
    return G
