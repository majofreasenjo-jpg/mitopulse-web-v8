import sys, json
from pathlib import Path
from dataclasses import asdict, is_dataclass
from flask import Flask, render_template, jsonify, request, redirect

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages"))

from mitopulse_protocol.core.protocol_engine import ProtocolEngine
from mitopulse_protocol.storage.repository import (
    list_events, list_evaluations, list_votes, list_challenges, list_actions,
    list_policies, list_anchors, list_exchanges, list_entities, list_trust_profiles,
    list_users, list_tenants, create_policy, toggle_policy, update_action_approval, add_challenge
)
from mitopulse_protocol.replay.replayer import ReplayEngine
from mitopulse_protocol.storage.db import get_conn
from mitopulse_protocol.integration.v50_adapter import map_v50_like_payload
from mitopulse_protocol.federation.network_http import FederationNetworkHTTP
from mitopulse_protocol.connectors.crypto_live import fetch_crypto_signal
from mitopulse_protocol.connectors.market_live import fetch_market_signal
from mitopulse_protocol.connectors.banking_live import fetch_banking_signal
from mitopulse_protocol.ai_aux.semantic_ingestion import summarize_payload
from mitopulse_protocol.ai_aux.local_pattern_ai import detect_local_pattern
from mitopulse_protocol.ai_aux.explainability_ai import explain_result
from mitopulse_protocol.ai_aux.strategy_copilot import recommend_next_step
from mitopulse_protocol.evidence.registry import load_cases
from mitopulse_protocol.connectors.binance_real import get_24h_ticker, get_recent_klines
from mitopulse_protocol.benchmark.engine import baseline_signal, ml_simple_signal, to_protocol_payload, detect_lead_time_placeholder

app = Flask(__name__)
engine = ProtocolEngine()
replayer = ReplayEngine()

def ser(v):
    if v is None:
        return None
    if is_dataclass(v):
        return asdict(v)
    return v

@app.route("/")
def home():
    conn = get_conn()
    counts = {
        "events": conn.execute("SELECT COUNT(*) FROM events").fetchone()[0],
        "entities": conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0],
        "trust_profiles": conn.execute("SELECT COUNT(*) FROM trust_profiles").fetchone()[0],
        "evaluations": conn.execute("SELECT COUNT(*) FROM evaluations").fetchone()[0],
        "votes": conn.execute("SELECT COUNT(*) FROM votes").fetchone()[0],
        "challenges": conn.execute("SELECT COUNT(*) FROM challenges").fetchone()[0],
        "actions": conn.execute("SELECT COUNT(*) FROM actions").fetchone()[0],
        "policies": conn.execute("SELECT COUNT(*) FROM policies").fetchone()[0],
        "anchors": conn.execute("SELECT COUNT(*) FROM federation_anchors").fetchone()[0],
        "tenants": conn.execute("SELECT COUNT(*) FROM tenants").fetchone()[0],
        "users": conn.execute("SELECT COUNT(*) FROM users").fetchone()[0],
    }
    conn.close()
    return render_template("home.html", counts=counts)

@app.route("/executive")
def executive():
    conn = get_conn()
    kpis = {
        "NHI": 72,
        "TPI": 58,
        "SCR": 64,
        "MDI": 42
    }
    conn.close()
    return render_template("executive.html", kpis=kpis, cases=list_evaluations(20))

@app.route("/live")
def live():
    return render_template("live.html")

@app.route("/dynamics")
def dynamics():
    conn = get_conn()
    rows = [dict(r) for r in conn.execute("SELECT risk_state as stage, AVG(scr) as stage_scr, COUNT(*) as avg_load, AVG(validated) as avg_entropy, COUNT(*) as avg_coordination, AVG(scr) as avg_trust_break, AVG(scr) as avg_structural FROM evaluations GROUP BY risk_state LIMIT 10").fetchall()]
    conn.close()
    return render_template("dynamics.html", timeline=rows)

@app.route("/ontology")
def ontology():
    with open(ROOT / "data" / "seeds" / "ontology.json", "r", encoding="utf-8") as f:
        ontology = json.load(f)
    return render_template("ontology.html", ontology=ontology)

@app.route("/connectors")
def connectors():
    with open(ROOT / "data" / "seeds" / "connectors.json", "r", encoding="utf-8") as f:
        connectors = json.load(f)["connectors"]
    return render_template("connectors.html", connectors=connectors)

@app.route("/cases")
def cases():
    return render_template("cases.html", cases=list_evaluations(120))

@app.route("/case/<case_id>")
def case_detail(case_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM evaluations WHERE entity_id = ? ORDER BY id DESC LIMIT 1", (case_id,)).fetchone()
    conn.close()
    case = dict(row) if row else {"id": case_id, "title": case_id, "status": "n/a", "risk": 0}
    return render_template("case_detail.html", case=case)

@app.route("/memory")
def memory():
    with open(ROOT / "data" / "seeds" / "memory.json", "r", encoding="utf-8") as f:
        memory = json.load(f)
    return render_template("memory.html", memory=memory)


@app.route("/verify-v2")
def verify_v2():
    return render_template("verify_v2.html")

@app.route("/simulation")
def simulation():
    conn = get_conn()
    timeline = [dict(r) for r in conn.execute("SELECT event_type as stage, COUNT(*) as stage_scr FROM events GROUP BY event_type LIMIT 20").fetchall()]
    conn.close()
    return render_template("simulation.html", timeline=timeline, kpis={"SCR": 64})

@app.route("/actions")
def legacy_actions():
    return render_template("actions_legacy.html", actions=list_actions(80), cases=list_evaluations(80))

@app.route("/vertical")
def vertical():
    return render_template("vertical.html", cases=list_evaluations(40))

@app.route("/protocol/console")
def protocol_console():
    conn = get_conn()
    nodes = [dict(r) for r in conn.execute("SELECT * FROM graph_nodes LIMIT 1000").fetchall()]
    links = [dict(r) for r in conn.execute("SELECT source as s, target as t FROM graph_links LIMIT 9000").fetchall()]
    conn.close()
    return render_template(
        "protocol_console.html",
        evaluations=list_evaluations(120),
        entities=list_entities(50),
        trust_profiles=list_trust_profiles(50),
        votes=list_votes(80),
        challenges=list_challenges(80),
        actions=list_actions(80),
        policies=list_policies(),
        anchors=list_anchors(),
        exchanges=list_exchanges(80),
        tenants=list_tenants(),
        users=list_users(),
        replay=replayer.replay_summary(1200),
        nodes=nodes,
        links=links
    )

@app.route("/protocol/evaluate", methods=["GET","POST"])
def protocol_evaluate():
    if request.method == "POST":
        payload = request.json or {}
        result = engine.evaluate(payload)
        return jsonify({k: ser(v) for k,v in result.items()})
    return render_template("protocol_evaluate.html")

@app.route("/protocol/evaluate_v50", methods=["POST"])
def evaluate_v50():
    payload = request.json or {}
    mapped = map_v50_like_payload(payload)
    result = engine.evaluate(mapped)
    return jsonify({k: ser(v) for k,v in result.items()})

@app.route("/protocol/events")
def protocol_events():
    return render_template("protocol_events.html", events=list_events(300))

@app.route("/protocol/replay/<entity_id>")
def protocol_replay(entity_id):
    return render_template("protocol_replay.html", entity_id=entity_id, steps=replayer.replay_steps(entity_id, 150))

@app.route("/protocol/spec")
def protocol_spec():
    spec_text = (ROOT / "docs" / "spec" / "MitoPulse_Protocol_Spec_v1_3.md").read_text(encoding="utf-8")
    return render_template("protocol_spec.html", spec=spec_text)

@app.route("/protocol/policies", methods=["GET","POST"])
def protocol_policies():
    if request.method == "POST":
        form = request.form
        create_policy({
            "policy_id": form["policy_id"],
            "name": form["name"],
            "condition_text": form["condition_text"],
            "action_text": form["action_text"],
            "confidence_required": float(form["confidence_required"]),
            "quorum_required": float(form["quorum_required"]),
            "severity_band": form["severity_band"],
            "enabled": 1,
            "version": int(form["version"]),
            "explanation": form["explanation"]
        })
        return redirect("/protocol/policies")
    return render_template("protocol_policies.html", policies=list_policies())

@app.route("/protocol/policies/<policy_id>/toggle", methods=["POST"])
def toggle(policy_id):
    enabled = int(request.form.get("enabled", "1"))
    toggle_policy(policy_id, enabled)
    return redirect("/protocol/policies")

@app.route("/protocol/challenge", methods=["POST"])
def challenge():
    form = request.form
    add_challenge(form["challenge_id"], int(form["evaluation_id"]), form["reason"], "open", form["ts"])
    return redirect("/protocol/console")

@app.route("/protocol/actions/<action_id>/approve", methods=["POST"])
def approve_action(action_id):
    update_action_approval(action_id, 1)
    return redirect("/protocol/console")

@app.route("/protocol/federate_demo", methods=["POST"])
def federate_demo():
    nodes = ["http://127.0.0.1:9002", "http://127.0.0.1:9003"]
    net = FederationNetworkHTTP(nodes=nodes)
    return jsonify(net.broadcast(request.json or {}))

@app.route("/api/graph")
def api_graph():
    conn = get_conn()
    nodes = [dict(r) for r in conn.execute("SELECT * FROM graph_nodes LIMIT 1000").fetchall()]
    links = [dict(r) for r in conn.execute("SELECT source as s, target as t FROM graph_links LIMIT 9000").fetchall()]
    conn.close()
    return jsonify({"nodes": nodes, "links": links})


@app.route("/cinematic-replay")
def cinematic_replay():
    return render_template("cinematic_replay.html")

@app.route("/evidence-cases")
def evidence_cases():
    cases = load_cases(ROOT)
    return render_template("evidence_cases.html", cases=cases)

@app.route("/connectors-live")
def connectors_live():
    return render_template("connectors_live.html")

@app.route("/ai-copilot")
def ai_copilot():
    return render_template("ai_copilot.html")

@app.route("/api/connector/<kind>")
def api_connector(kind):
    if kind == "crypto":
        payload = fetch_crypto_signal("BTCUSDT")
    elif kind == "market":
        payload = fetch_market_signal("SPY")
    else:
        payload = fetch_banking_signal("txn_high_value")
    result = engine.evaluate(payload)
    return jsonify({"payload": payload, "result": {k: ser(v) for k,v in result.items()}})

@app.route("/api/ai_copilot", methods=["POST"])
def api_ai_copilot():
    payload = request.json or {}
    semantic = summarize_payload(payload)
    local_pattern = detect_local_pattern(payload)
    result = engine.evaluate(payload)
    explanation = explain_result(result)
    strategy = recommend_next_step(result)
    return jsonify({
        "semantic_ingestion": semantic,
        "local_pattern_ai": local_pattern,
        "protocol_result": {k: ser(v) for k,v in result.items()},
        "explainability_ai": explanation,
        "strategy_copilot": strategy
    })


@app.route("/reality-mode")
def reality_mode():
    return render_template("reality_mode.html")

@app.route("/api/live/crypto/binance")
def api_live_crypto_binance():
    symbol = request.args.get("symbol", "BTCUSDT")
    ticker = get_24h_ticker(symbol)
    klines = get_recent_klines(symbol, "1m", 60)
    baseline = baseline_signal(ticker)
    ml = ml_simple_signal(ticker, klines)
    payload = to_protocol_payload(ticker, klines, symbol)
    result = engine.evaluate(payload)

    risk = result.get("risk")
    validation = result.get("validation")
    policy = result.get("policy")
    benchmark = detect_lead_time_placeholder(baseline, ml, result)

    protocol_summary = {
        "risk_state": getattr(risk, "risk_state", "UNKNOWN"),
        "scr": getattr(risk, "scr", None),
        "quorum_score": getattr(validation, "quorum_score", None),
        "validated": getattr(validation, "validated", False),
        "policy_name": getattr(policy, "name", None) if policy else None,
        "protocol_triggered": getattr(risk, "risk_state", "UNKNOWN") in {"PRESSURE","INSTABILITY","CRITICAL","COLLAPSE"},
        "full_result": {k: ser(v) for k,v in result.items()}
    }
    return jsonify({
        "ticker": ticker,
        "klines": klines,
        "baseline": baseline,
        "ml": ml,
        "protocol": protocol_summary,
        "benchmark": benchmark,
        "normalized_payload": payload
    })

@app.route("/api/benchmark/run")
def api_benchmark_run():
    symbol = request.args.get("symbol", "BTCUSDT")
    ticker = get_24h_ticker(symbol)
    klines = get_recent_klines(symbol, "1m", 60)
    baseline = baseline_signal(ticker)
    ml = ml_simple_signal(ticker, klines)
    payload = to_protocol_payload(ticker, klines, symbol)
    result = engine.evaluate(payload)
    return jsonify({
        "symbol": symbol,
        "baseline": baseline,
        "ml": ml,
        "protocol": {k: ser(v) for k,v in result.items()},
        "benchmark": detect_lead_time_placeholder(baseline, ml, result)
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8067, debug=False)
