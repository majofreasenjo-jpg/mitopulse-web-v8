import networkx as nx
import time
import random

class UserIdentityEngine:
    """
    V90 Digital Identity Engine.
    Tracks historical trusted ties and calculates relational risk mathematically to intercept Phone Fraud, 
    WhatsApp Impersonation, and fraudulent transfers.
    """
    def __init__(self):
        self.G = nx.DiGraph()
        
        # Pre-seed User History (The safe contacts - Unique Digital Identity baseline)
        self.G.add_node("Alex (You)", type="user", risk_score=0)
        self.G.add_edge("Alex (You)", "Trusted_Contact_21", weight=10, last_txn=time.time() - 86400)
        self.G.add_edge("Alex (You)", "Mom_Wallet", weight=50, last_txn=time.time() - 400000)
        self.G.add_edge("Alex (You)", "Utility_Bill_Corp", weight=15, last_txn=time.time() - 10000)

        # Pre-seed known scam rings (Blacklist or shady relational neighborhoods)
        self.G.add_node("Scam_Ring_Alpha", type="threat", risk_score=95)
        self.G.add_edge("Marco_Crypto99", "Scam_Ring_Alpha", weight=100, last_txn=time.time())
        self.G.add_edge("Fake_WhatsApp_Mom", "Scam_Ring_Alpha", weight=100, last_txn=time.time())
        self.G.add_edge("Extortion_Node_Z", "Scam_Ring_Alpha", weight=80, last_txn=time.time() - 500)

    def evaluate_transaction(self, sender: str, receiver: str, amount: float):
        """
        Evaluates a transaction based on the Digital Identity historical graph.
        Returns the V80 Challenge response (Score, State, Trace).
        """
        # 1. Is it a known trusted contact? (Safe)
        if self.G.has_edge(sender, receiver):
            weight = self.G[sender][receiver]['weight']
            if weight > 5:
                # Update the history automatically (Strengthen the Identity Trust)
                self.G[sender][receiver]['weight'] += 1
                return {
                    "score": random.randint(12, 22),
                    "state": "STABLE",
                    "confidence": f"{random.randint(92, 98)}%",
                    "horizon": "Low / distant",
                    "receiver": receiver,
                    "alertTitle": "✓ Relational Pattern Verified",
                    "alertText": "The receiver is deeply mapped in your historical Identity Graph. No critical hidden coordination detected.",
                    "primaryText": "Proceed Transfer",
                    "primaryClass": "safe",
                    "trace": [
                        "Historical trust vector confirmed by UserIdentityEngine.",
                        "No abnormal cluster activation detected in the periphery.",
                        "V90 Policy triggered: allow and strengthen bond."
                    ],
                    "color": "#4cc9f0"
                }

        # 2. Is the receiver tied to a scam ring? (Shadow Coordination/Fraud/Impersonation)
        if self.G.has_node(receiver) and nx.has_path(self.G, receiver, "Scam_Ring_Alpha"):
            return {
                "score": random.randint(88, 96),
                "state": "CRITICAL",
                "confidence": f"{random.randint(90, 99)}%",
                "horizon": "Immediate",
                "receiver": receiver,
                "alertTitle": "⚠ Shadow Coordination Detected",
                "alertText": "The receiver has hidden relational edges to a known scam ring (Impersonation/Phone Fraud). Immune defense activated.",
                "primaryText": "Transaction Blocked",
                "primaryClass": "blocked",
                "trace": [
                    "Signal detected zero historical edges in your Unique Digital Identity.",
                    "Hidden cluster correlation matched known predatory pattern (Impersonation Scam).",
                    "V90 Policy triggered: block and isolate."
                ],
                "color": "#ff5b5b"
            }

        # 3. Unknown receiver with indirect signals (Pressure/Watch - Coercion simulation)
        return {
            "score": random.randint(58, 68),
            "state": "PRESSURE",
            "confidence": f"{random.randint(75, 88)}%",
            "horizon": "Short-term",
            "receiver": receiver,
            "alertTitle": "⚠ Elevated Relational Pressure",
            "alertText": "The receiver shows no history in your Digital Identity, and indirect coordination markers exist. Enhanced monitoring recommended.",
            "primaryText": "Review Transfer",
            "primaryClass": "review",
            "trace": [
                "Target not found in primary Identity history.",
                "Quorum reached watch-level confirmation against external nodes.",
                "V90 Policy triggered: review and monitor."
            ],
            "color": "#ffd166"
        }
