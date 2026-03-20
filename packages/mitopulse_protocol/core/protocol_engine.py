import json
from datetime import datetime
from mitopulse_protocol.core.identity_engine import IdentityEngine
from mitopulse_protocol.core.trust_engine import TrustEngine
from mitopulse_protocol.core.risk_engine import RiskEngine
from mitopulse_protocol.core.validation_engine import ValidationEngine
from mitopulse_protocol.core.action_engine import ActionEngine
from mitopulse_protocol.core.recovery_engine import RecoveryEngine
from mitopulse_protocol.policies.registry import select_policy
from mitopulse_protocol.storage.repository import insert_event, save_evaluation, insert_action, list_anchors
from mitopulse_protocol.federation.exchange import record_exchange

class ProtocolEngine:
    def __init__(self):
        self.identity_engine = IdentityEngine()
        self.trust_engine = TrustEngine()
        self.risk_engine = RiskEngine()
        self.validation_engine = ValidationEngine()
        self.action_engine = ActionEngine()
        self.recovery_engine = RecoveryEngine()
        self._counter = 0

    def _id(self, prefix):
        self._counter += 1
        return f"{prefix}_{self._counter}_{int(datetime.now().timestamp())}"

    def evaluate(self, payload: dict):
        entity_id = payload["entity_id"]
        now = datetime.now().isoformat()
        insert_event(self._id("EV"), "input_received", entity_id, json.dumps(payload), now)

        identity = self.identity_engine.evaluate(entity_id, payload.get("entity_type","entity"), float(payload.get("evidence_score",0.5)))
        insert_event(self._id("EV"), "identity_evaluated", entity_id, json.dumps({"identity_state": identity.identity_state}), now)

        trust = self.trust_engine.compute(entity_id, float(payload.get("trust_score",0.5)), float(payload.get("trust_velocity",0.0)), float(payload.get("trust_volatility",0.0)))
        insert_event(self._id("EV"), "trust_computed", entity_id, json.dumps({"trust_state": trust.trust_state, "trust_score": trust.trust_score}), now)

        risk = self.risk_engine.assess(float(payload.get("load_dev",0.0)), float(payload.get("entropy_dev",0.0)), float(payload.get("coordination_signal",0.0)), float(payload.get("trust_break",0.0)), float(payload.get("structural_distortion",0.0)))
        insert_event(self._id("EV"), "risk_assessed", entity_id, json.dumps({"risk_state": risk.risk_state, "scr": risk.scr}), now)

        evaluation_id = save_evaluation(entity_id, identity.identity_state, trust.trust_state, risk.risk_state, risk.scr, 0, None, None)
        anchors = list_anchors(20)
        validation = self.validation_engine.validate(evaluation_id, float(payload.get("confidence",0.75)), anchors)
        insert_event(self._id("EV"), "validation_computed", entity_id, json.dumps({"validated": validation.validated, "confidence": validation.confidence, "quorum": validation.quorum_score}), now)

        policy = select_policy(risk.scr)
        action = None
        if policy:
            insert_event(self._id("EV"), "policy_selected", entity_id, json.dumps({"policy_id": policy.policy_id, "action": policy.action_text}), now)

        if policy and validation.validated and validation.confidence >= policy.confidence_required and validation.quorum_score >= policy.quorum_required:
            action = self.action_engine.create_action(self._id("ACT"), entity_id, policy.action_text, policy.explanation, policy.policy_id)
            insert_action(action.action_id, evaluation_id, entity_id, action.action_type, 0, action.explanation, action.policy_id, now)
            insert_event(self._id("EV"), "action_created", entity_id, json.dumps({"action_type": action.action_type, "policy_id": action.policy_id}), now)

        recovery = None
        if risk.risk_state in {"CRITICAL", "COLLAPSE"}:
            recovery = self.recovery_engine.recover(float(payload.get("recovery_stability_score",0.0)))
            insert_event(self._id("EV"), "recovery_computed", entity_id, json.dumps({"recovery_state": recovery.recovery_state}), now)

        record_exchange("ANCHOR_A", "evaluation_notice", f"{entity_id}:{risk.risk_state}:{risk.scr}")
        record_exchange("ANCHOR_B", "trust_notice", f"{entity_id}:{trust.trust_state}:{trust.trust_score}")

        return {
            "identity": identity,
            "trust": trust,
            "risk": risk,
            "validation": validation,
            "policy": policy,
            "action": action,
            "recovery": recovery,
            "evaluation_id": evaluation_id
        }
