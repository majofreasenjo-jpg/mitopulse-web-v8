from typing import List, Dict


def default_validators() -> List[Dict]:
    return [
        {"node_id": "anchor_a", "label": "Anchor A", "trust_weight": 0.92, "active": True},
        {"node_id": "anchor_b", "label": "Anchor B", "trust_weight": 0.88, "active": True},
        {"node_id": "anchor_c", "label": "Anchor C", "trust_weight": 0.81, "active": True},
        {"node_id": "anchor_d", "label": "Anchor D", "trust_weight": 0.76, "active": True},
    ]
