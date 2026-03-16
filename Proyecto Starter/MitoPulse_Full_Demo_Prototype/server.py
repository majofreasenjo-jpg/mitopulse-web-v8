from http.server import BaseHTTPRequestHandler, HTTPServer
import json, time, random, statistics

EVENTS = []

def classify(score):
    if score >= 70:
        return "VERIFIED", "low"
    if score >= 45:
        return "REVIEW", "medium"
    return "BLOCK", "high"

def compute_score(events, start_ms):
    now_ms = int(time.time() * 1000)
    duration_s = max(0.1, (now_ms - int(start_ms)) / 1000.0)
    count = len(events)
    if count >= 2:
        diffs = [events[i] - events[i-1] for i in range(1, len(events))]
        variance = statistics.pvariance(diffs) if len(diffs) > 1 else 0
        avg = statistics.mean(diffs)
    else:
        variance = 0
        avg = 0

    score = 20
    score += min(25, count * 2.2)
    score += min(20, duration_s * 2.5)
    if 20 <= avg <= 800:
        score += 12
    if variance > 500:
        score += 18
    if count < 3:
        score -= 15
    if duration_s < 1.2:
        score -= 18
    score = max(0, min(100, round(score, 2)))
    verdict, risk = classify(score)
    return {
        "human_pulse_score": score,
        "verdict": verdict,
        "risk_band": risk,
        "event_count": count,
        "session_seconds": round(duration_s, 2),
        "avg_interval_ms": round(avg, 2) if avg else 0,
        "variance": round(variance, 2),
    }

def html_page(title, body):
    return """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>""" + title + """</title>
<style>
body { font-family: Arial, sans-serif; margin:0; background:#0f172a; color:#fff; }
.top { background:#111827; padding:16px 24px; display:flex; gap:16px; flex-wrap:wrap; align-items:center; }
.top a { color:#93c5fd; text-decoration:none; font-weight:bold; }
.wrap { max-width:1000px; margin:24px auto; padding:0 16px; }
.card { background:#1e293b; border-radius:14px; padding:20px; margin-bottom:20px; box-shadow:0 8px 24px rgba(0,0,0,.25); }
.btn { background:#22c55e; color:#fff; border:none; border-radius:10px; padding:12px 18px; font-size:15px; cursor:pointer; }
.btn2 { background:#3b82f6; }
.btn3 { background:#f59e0b; }
.grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:14px; }
.metric { background:#0b1220; border-radius:12px; padding:14px; }
small, .muted { opacity:.75; }
table { width:100%; border-collapse:collapse; }
th, td { text-align:left; padding:10px; border-bottom:1px solid #334155; font-size:14px; }
input, select { padding:10px; border-radius:10px; border:none; width:100%; max-width:320px; }
</style>
</head>
<body>
<div class="top">
  <a href="/">Inicio</a>
  <a href="/check">Human Check</a>
  <a href="/dashboard">Dashboard</a>
  <a href="/simulator">Simulator</a>
  <a href="/flows">Use Cases</a>
</div>
<div class="wrap">""" + body + """</div>
</body>
</html>"""

HOME = """
<div class="card">
  <h1>MitoPulse Full Demo Prototype</h1>
  <p>La solución simple para problemas complejos.</p>
  <p class="muted">Demo ejecutable para mostrar Human Presence Verification en fraudes telefónicos, login sensible, marketplace y transferencias.</p>
</div>

<div class="grid">
  <div class="card">
    <h3>1. Human Check</h3>
    <p>Prueba manual rápida de presencia humana.</p>
    <a href="/check"><button class="btn">Abrir demo</button></a>
  </div>
  <div class="card">
    <h3>2. Dashboard</h3>
    <p>Ve métricas, scores y eventos generados.</p>
    <a href="/dashboard"><button class="btn btn2">Abrir dashboard</button></a>
  </div>
  <div class="card">
    <h3>3. Simulator</h3>
    <p>Genera humanos, bots simples y bots avanzados.</p>
    <a href="/simulator"><button class="btn btn3">Abrir simulador</button></a>
  </div>
</div>
"""

CHECK = """
<div class="card">
  <h2>Human Check</h2>
  <p>Muévete, haz clic, espera unos segundos y luego analiza la sesión.</p>
  <div style="display:flex; gap:12px; flex-wrap:wrap; align-items:center;">
    <button class="btn" id="analyzeBtn">Analyze Session</button>
    <span class="muted">Tiempo sugerido: 5–10 segundos</span>
  </div>
  <div id="result" style="margin-top:18px;"></div>
</div>

<script>
let events = [];
let started = Date.now();
document.addEventListener("mousemove", () => events.push(Date.now()));
document.addEventListener("click", () => events.push(Date.now()));
document.addEventListener("scroll", () => events.push(Date.now()));
document.addEventListener("touchstart", () => events.push(Date.now()), {passive:true});

document.getElementById("analyzeBtn").onclick = async () => {
  const r = await fetch("/api/analyze", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify({events: events, start_ms: started, profile:"manual"})
  });
  const d = await r.json();
  document.getElementById("result").innerHTML = `
    <div class="card">
      <h3>Resultado</h3>
      <p><b>Score:</b> ${d.human_pulse_score}</p>
      <p><b>Verdict:</b> ${d.verdict}</p>
      <p><b>Risk:</b> ${d.risk_band}</p>
      <p><b>Events:</b> ${d.event_count}</p>
      <p><b>Session:</b> ${d.session_seconds}s</p>
      <p><b>Avg interval:</b> ${d.avg_interval_ms} ms</p>
      <p><b>Variance:</b> ${d.variance}</p>
    </div>`;
};
</script>
"""

FLOWS = """
<div class="card">
  <h2>Casos de uso demo</h2>
  <div class="grid">
    <div class="metric">
      <h3>Estafa telefónica</h3>
      <p>“Envíame tu MitoPulse antes de transferir.”</p>
    </div>
    <div class="metric">
      <h3>Marketplace</h3>
      <p>“Sin MitoPulse, no pago / no entrego.”</p>
    </div>
    <div class="metric">
      <h3>Login sensible</h3>
      <p>“Password + MitoPulse Check.”</p>
    </div>
    <div class="metric">
      <h3>Transferencia</h3>
      <p>“Antes de enviar, verifica presencia humana.”</p>
    </div>
  </div>
</div>
"""

SIMULATOR = """
<div class="card">
  <h2>Attack Simulator</h2>
  <p>Genera sesiones sintéticas para probar la separación entre humanos y automatización.</p>
  <div style="display:flex; gap:14px; flex-wrap:wrap;">
    <button class="btn" onclick="runBatch('human', 20)">20 Human</button>
    <button class="btn btn2" onclick="runBatch('simple_bot', 20)">20 Simple Bot</button>
    <button class="btn btn3" onclick="runBatch('advanced_bot', 20)">20 Advanced Bot</button>
    <button class="btn" style="background:#8b5cf6" onclick="runBatch('mixed', 60)">Mixed Batch</button>
  </div>
  <div id="simResult" style="margin-top:18px;"></div>
</div>

<script>
async function runBatch(type, n){
  const r = await fetch("/api/simulate", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify({type:type, n:n})
  });
  const d = await r.json();
  document.getElementById("simResult").innerHTML = `
    <div class="card">
      <h3>Simulation Summary</h3>
      <p><b>Type:</b> ${d.type}</p>
      <p><b>Total:</b> ${d.total}</p>
      <p><b>VERIFIED:</b> ${d.counts.VERIFIED}</p>
      <p><b>REVIEW:</b> ${d.counts.REVIEW}</p>
      <p><b>BLOCK:</b> ${d.counts.BLOCK}</p>
      <p><b>Avg score:</b> ${d.avg_score}</p>
    </div>`;
}
</script>
"""

def dashboard_html():
    total = len(EVENTS)
    verified = sum(1 for e in EVENTS if e["verdict"] == "VERIFIED")
    review = sum(1 for e in EVENTS if e["verdict"] == "REVIEW")
    block = sum(1 for e in EVENTS if e["verdict"] == "BLOCK")
    avg = round(sum(e["human_pulse_score"] for e in EVENTS) / total, 2) if total else 0
    rows = []
    for e in list(reversed(EVENTS[-100:])):
        rows.append(
            "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                e["id"], e["profile"], e["human_pulse_score"], e["verdict"], e["risk_band"], e["event_count"], e["session_seconds"]
            )
        )
    table = "".join(rows) or "<tr><td colspan='7'>Sin eventos todavía.</td></tr>"
    body = """
    <div class="card">
      <h2>Dashboard</h2>
      <div class="grid">
        <div class="metric"><b>Total</b><div>{}</div></div>
        <div class="metric"><b>Avg Score</b><div>{}</div></div>
        <div class="metric"><b>Verified</b><div>{}</div></div>
        <div class="metric"><b>Review</b><div>{}</div></div>
        <div class="metric"><b>Block</b><div>{}</div></div>
      </div>
    </div>
    <div class="card">
      <h3>Últimos eventos</h3>
      <table>
        <thead><tr><th>ID</th><th>Profile</th><th>Score</th><th>Verdict</th><th>Risk</th><th>Events</th><th>Session(s)</th></tr></thead>
        <tbody>{}</tbody>
      </table>
    </div>
    """.format(total, avg, verified, review, block, table)
    return body

def add_event(result, profile):
    item = dict(result)
    item["id"] = "evt_{}".format(len(EVENTS) + 1)
    item["profile"] = profile
    EVENTS.append(item)

def make_profile(profile_type):
    now = int(time.time() * 1000)
    if profile_type == "human":
        count = random.randint(14, 35)
        t = now - random.randint(5000, 15000)
        points = []
        current = t
        for _ in range(count):
            current += random.randint(80, 900)
            points.append(current)
        return points, t
    if profile_type == "simple_bot":
        count = random.randint(2, 5)
        t = now - random.randint(100, 900)
        points = []
        current = t
        for _ in range(count):
            current += 100
            points.append(current)
        return points, t
    if profile_type == "advanced_bot":
        count = random.randint(10, 18)
        t = now - random.randint(1000, 3000)
        points = []
        current = t
        for _ in range(count):
            current += random.randint(90, 130)
            points.append(current)
        return points, t
    return make_profile(random.choice(["human", "simple_bot", "advanced_bot"]))

class Handler(BaseHTTPRequestHandler):
    def send_html(self, body, title="MitoPulse Demo"):
        page = html_page(title, body)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(page.encode("utf-8"))

    def send_json(self, payload):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def do_GET(self):
        if self.path == "/":
            return self.send_html(HOME, "MitoPulse Home")
        if self.path == "/check":
            return self.send_html(CHECK, "MitoPulse Human Check")
        if self.path == "/dashboard":
            return self.send_html(dashboard_html(), "MitoPulse Dashboard")
        if self.path == "/simulator":
            return self.send_html(SIMULATOR, "MitoPulse Simulator")
        if self.path == "/flows":
            return self.send_html(FLOWS, "MitoPulse Use Cases")
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        data = json.loads(raw or "{}")

        if self.path == "/api/analyze":
            result = compute_score(data.get("events", []), data.get("start_ms", int(time.time() * 1000)))
            add_event(result, data.get("profile", "manual"))
            return self.send_json(result)

        if self.path == "/api/simulate":
            kind = data.get("type", "mixed")
            n = int(data.get("n", 20))
            counts = {"VERIFIED": 0, "REVIEW": 0, "BLOCK": 0}
            scores = []
            for _ in range(n):
                profile = kind if kind != "mixed" else random.choice(["human", "simple_bot", "advanced_bot"])
                events, start = make_profile(profile)
                result = compute_score(events, start)
                add_event(result, profile)
                counts[result["verdict"]] += 1
                scores.append(result["human_pulse_score"])
            payload = {
                "type": kind,
                "total": n,
                "counts": counts,
                "avg_score": round(sum(scores)/len(scores), 2) if scores else 0
            }
            return self.send_json(payload)

        self.send_response(404)
        self.end_headers()

if __name__ == "__main__":
    print("MitoPulse demo running on http://localhost:8080")
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
