let ws = null;

function badgeClass(state){
  if(state === "coherent") return "good";
  if(state === "stressed" || state === "compensating") return "warn";
  return "bad";
}

function renderDrivers(list, targetId, badgeText){
  const root = document.getElementById(targetId);
  root.innerHTML = "";
  (list || []).forEach((item, idx) => {
    const div = document.createElement("div");
    div.className = "driver";
    div.innerHTML = `<span>${idx+1}. ${item}</span><span class="badge ${badgeClass(badgeText)}">${badgeText}</span>`;
    root.appendChild(div);
  });
}

function renderGraph(nodes){
  const root = document.getElementById("graphNodes");
  root.innerHTML = "";
  (nodes || []).forEach(n => {
    const div = document.createElement("div");
    div.className = "node";
    div.innerHTML = `
      <div class="label">${n.zone}</div>
      <div style="font-size:18px;font-weight:800;margin-top:8px">${n.id}</div>
      <div class="muted">role: ${n.role}</div>
      <div class="muted">risk: ${n.risk}</div>
      <div class="muted">coherence: ${n.coherence}</div>
    `;
    root.appendChild(div);
  });
}

function renderActions(actions, state){
  const root = document.getElementById("actionsList");
  root.innerHTML = "";
  (actions || []).forEach((item, idx) => {
    const div = document.createElement("div");
    div.className = "driver";
    div.innerHTML = `<span>${idx+1}. ${item}</span><span class="badge ${badgeClass(state)}">${state}</span>`;
    root.appendChild(div);
  });
}

function renderPayload(payload){
  const s = payload.state;
  const p = payload.protocol;
  const raw = payload.raw;

  document.getElementById("nhi").textContent = s.nhi.toFixed(3);
  document.getElementById("tpi").textContent = s.tpi.toFixed(3);
  document.getElementById("scr").textContent = s.scr.toFixed(3);
  document.getElementById("aci").textContent = s.aci.toFixed(3);
  document.getElementById("avs").textContent = s.avs.toFixed(3);

  document.getElementById("stateBadge").innerHTML = `<span class="badge ${badgeClass(s.state)}">${s.state}</span>`;
  document.getElementById("explanation").textContent = s.explanation;

  renderDrivers(s.top_drivers, "drivers", s.state);
  renderGraph(payload.graph);
  renderActions(s.actions, s.state);

  document.getElementById("fdi").textContent = s.fdi.toFixed(3);
  document.getElementById("ssi").textContent = s.ssi.toFixed(3);
  document.getElementById("cfi").textContent = s.cfi.toFixed(3);
  document.getElementById("fpi").textContent = s.fpi.toFixed(3);
  document.getElementById("sei").textContent = s.sei.toFixed(3);
  document.getElementById("msi").textContent = s.msi.toFixed(3);

  document.getElementById("bpi").textContent = s.behavioral_predation_index.toFixed(3);
  document.getElementById("crr").textContent = s.cycle_recurrence_risk.toFixed(3);
  document.getElementById("metabolicLoad").textContent = s.metabolic_load.toFixed(3);

  document.getElementById("collapseProbability").textContent = s.collapse_probability.toFixed(3);
  document.getElementById("ttc").textContent = `${s.time_to_criticality.toFixed(2)} h-eq`;
  document.getElementById("band").textContent = `${s.confidence_low.toFixed(2)} – ${s.confidence_high.toFixed(2)}`;

  document.getElementById("rawSignals").textContent = JSON.stringify(raw, null, 2);
  document.getElementById("protocolBox").textContent = JSON.stringify(p, null, 2);
  document.getElementById("viabilityBox").textContent = JSON.stringify({
    state: s.state,
    collapse_probability: s.collapse_probability,
    time_to_criticality: s.time_to_criticality,
    explanation: s.explanation
  }, null, 2);
}

async function refreshState(){
  const res = await fetch("/api/state");
  const data = await res.json();
  renderPayload(data);
  await refreshHistory();
}

async function refreshHistory(){
  const res = await fetch("/api/history");
  const data = await res.json();
  const compact = (data.items || []).slice(-10).map(x => ({
    tick: x.state.tick,
    state: x.state.state,
    nhi: x.state.nhi,
    scr: x.state.scr
  }));
  document.getElementById("historyBox").textContent = JSON.stringify(compact, null, 2);
}

async function projectForward(){
  const res = await fetch("/api/project?horizon=24h");
  const data = await res.json();
  document.getElementById("projection").textContent = JSON.stringify(data, null, 2);
  document.getElementById("simulationBox").textContent = JSON.stringify(data.projected_state, null, 2);
}

async function resetRuntime(){
  await fetch("/api/reset", {method:"POST"});
  document.getElementById("projection").textContent = "Reset ejecutado.";
  document.getElementById("historyBox").textContent = "—";
  await refreshState();
}

function bindTabs(){
  document.querySelectorAll(".tab").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach(x => x.classList.remove("active"));
      document.querySelectorAll(".tabpanel").forEach(x => x.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById(`tab-${btn.dataset.tab}`).classList.add("active");
    });
  });
}

function openWS(){
  const proto = location.protocol === "https:" ? "wss" : "ws";
  ws = new WebSocket(`${proto}://${location.host}/ws`);
  ws.onmessage = (ev) => {
    const payload = JSON.parse(ev.data);
    renderPayload(payload);
    refreshHistory();
  };
  ws.onclose = () => setTimeout(openWS, 2500);
}

bindTabs();
openWS();
refreshState();
