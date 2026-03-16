
import React, { useEffect, useMemo, useRef, useState } from "react";

function clamp(x, lo=0, hi=1){ return Math.max(lo, Math.min(hi, x)); }

function uuidv4(){
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, c => {
    const r = Math.random()*16|0, v = c==="x" ? r : (r&0x3|0x8);
    return v.toString(16);
  });
}

export default function App(){
  const [backend, setBackend] = useState(localStorage.getItem("mp_backend") || "http://127.0.0.1:8000");
  const [user, setUser] = useState(localStorage.getItem("mp_user") || "manuel");
  const [device, setDevice] = useState(localStorage.getItem("mp_device") || "pwa-device-01");
  const [apiKey, setApiKey] = useState(localStorage.getItem("mp_apikey") || "");

  const [hr, setHr] = useState(72);
  const [hrv, setHrv] = useState(45);
  const [spo2, setSpo2] = useState(98);
  const [sleep, setSleep] = useState(80);
  const [load, setLoad] = useState(1.0);

  const [alt, setAlt] = useState(120);
  const [temp, setTemp] = useState(22);
  const [hum, setHum] = useState(45);
  const [press, setPress] = useState(1012);

  const [log, setLog] = useState([]);
  const [live, setLive] = useState(false);
  const liveRef = useRef(null);

  useEffect(() => {
    localStorage.setItem("mp_backend", backend);
    localStorage.setItem("mp_user", user);
    localStorage.setItem("mp_device", device);
    localStorage.setItem("mp_apikey", apiKey);
  }, [backend, user, device, apiKey]);

  const headers = useMemo(() => {
    const h = { "Content-Type": "application/json" };
    if(apiKey) h["X-API-Key"] = apiKey;
    return h;
  }, [apiKey]);

  async function postEvent(){
    const ts = Math.floor(Date.now()/1000);
    const body = {
      user_id: user,
      device_id: device,
      ts,
      request_id: uuidv4(),
      tier: (hrv && spo2) ? "tier3" : (hrv ? "tier2" : "tier1"),
      index_value: null,
      slope: 0.0,
      risk: 0,
      coercion: false,
      dynamic_id: "demo",
      hr: Number(hr),
      hrv_rmssd: Number(hrv),
      spo2: Number(spo2),
      sleep_score: Number(sleep),
      load: Number(load),
      altitude_m: Number(alt),
      temp_c: Number(temp),
      humidity_pct: Number(hum),
      pressure_hpa: Number(press),
      human_confidence: 0.9
    };

    const res = await fetch(`${backend}/v1/identity-events`, {
      method: "POST",
      headers,
      body: JSON.stringify(body)
    });

    const txt = await res.text();
    setLog(l => [{t: new Date().toLocaleTimeString(), msg: `POST /v1/identity-events -> ${res.status} ${txt}`}, ...l].slice(0,80));
  }

  async function getState(){
    const res = await fetch(`${backend}/v2/identity/state?user_id=${encodeURIComponent(user)}&device_id=${encodeURIComponent(device)}`, { headers: apiKey ? {"X-API-Key": apiKey} : {} });
    const txt = await res.text();
    setLog(l => [{t: new Date().toLocaleTimeString(), msg: `GET /v2/identity/state -> ${res.status} ${txt}`}, ...l].slice(0,80));
  }

  async function getHumanProof(){
    const res = await fetch(`${backend}/v2/identity/human-proof?user_id=${encodeURIComponent(user)}&device_id=${encodeURIComponent(device)}`, { headers: apiKey ? {"X-API-Key": apiKey} : {} });
    const txt = await res.text();
    setLog(l => [{t: new Date().toLocaleTimeString(), msg: `GET /v2/identity/human-proof -> ${res.status} ${txt}`}, ...l].slice(0,80));
  }

  useEffect(() => {
    if(!live) {
      if(liveRef.current) clearInterval(liveRef.current);
      liveRef.current = null;
      return;
    }
    liveRef.current = setInterval(() => {
      setHr(x => clamp(x + (Math.random()*6-3), 45, 160));
      setHrv(x => clamp(x + (Math.random()*6-3), 10, 120));
      setSpo2(x => clamp(x + (Math.random()*1.2-0.6), 88, 100));
      setSleep(x => clamp(x + (Math.random()*4-2), 0, 100));
      setLoad(x => clamp(x + (Math.random()*0.8-0.4), 0, 10));
      postEvent();
    }, 5000);
    return () => {
      if(liveRef.current) clearInterval(liveRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [live]);

  return (
    <div style={{maxWidth:1100, margin:"0 auto", padding:16}}>
      <h1 style={{margin:0}}>MitoPulse v2.5 — Pilot PWA</h1>
      <div style={{opacity:0.75, marginTop:6}}>Send events + read stability/human confidence from anywhere (tunnel-friendly).</div>

      <div style={{display:"grid", gridTemplateColumns:"1fr 1fr", gap:12, marginTop:16}}>
        <div style={card}>
          <h3 style={h3}>Connection</h3>
          <label style={lab}>Backend URL</label>
          <input style={inp} value={backend} onChange={e=>setBackend(e.target.value)} />
          <div style={{display:"grid", gridTemplateColumns:"1fr 1fr", gap:10, marginTop:10}}>
            <div>
              <label style={lab}>user_id</label>
              <input style={inp} value={user} onChange={e=>setUser(e.target.value)} />
            </div>
            <div>
              <label style={lab}>device_id</label>
              <input style={inp} value={device} onChange={e=>setDevice(e.target.value)} />
            </div>
          </div>
          <label style={lab}>API Key (optional)</label>
          <input style={inp} value={apiKey} onChange={e=>setApiKey(e.target.value)} />
          <div style={{display:"flex", gap:10, marginTop:12, flexWrap:"wrap"}}>
            <button style={btn} onClick={postEvent}>Send DEMO Event</button>
            <button style={btn2} onClick={getState}>Get State</button>
            <button style={btn2} onClick={getHumanProof}>Human Proof</button>
            <button style={live ? btnWarn : btn2} onClick={()=>setLive(v=>!v)}>{live ? "LIVE MODE: ON" : "LIVE MODE: OFF"}</button>
          </div>
          <div style={{opacity:0.7, fontSize:12, marginTop:10}}>
            Dashboard: <a href={`${backend}/dashboard`} target="_blank" rel="noreferrer" style={{color:"#7dd3fc"}}>{backend}/dashboard</a>
          </div>
        </div>

        <div style={card}>
          <h3 style={h3}>Signals</h3>
          <Grid>
            <Field label="HR" value={hr} setValue={setHr} />
            <Field label="HRV (RMSSD)" value={hrv} setValue={setHrv} />
            <Field label="SpO2" value={spo2} setValue={setSpo2} />
            <Field label="Sleep score" value={sleep} setValue={setSleep} />
            <Field label="Load" value={load} setValue={setLoad} step={0.1} />
          </Grid>
          <h3 style={{...h3, marginTop:14}}>Environment</h3>
          <Grid>
            <Field label="Altitude (m)" value={alt} setValue={setAlt} step={10} />
            <Field label="Temp (°C)" value={temp} setValue={setTemp} step={0.5} />
            <Field label="Humidity (%)" value={hum} setValue={setHum} />
            <Field label="Pressure (hPa)" value={press} setValue={setPress} />
          </Grid>
        </div>
      </div>

      <div style={{...card, marginTop:12}}>
        <h3 style={h3}>Logs</h3>
        <div style={{fontFamily:"ui-monospace, SFMono-Regular", fontSize:12, opacity:0.9, maxHeight:260, overflow:"auto", border:"1px solid #1d2733", borderRadius:10, padding:10, background:"#0b0f14"}}>
          {log.length === 0 ? <div style={{opacity:0.7}}>No logs yet…</div> : log.map((x,i)=>(
            <div key={i}><span style={{opacity:0.6}}>[{x.t}]</span> {x.msg}</div>
          ))}
        </div>
      </div>
    </div>
  );
}

function Grid({children}){
  return <div style={{display:"grid", gridTemplateColumns:"repeat(2, 1fr)", gap:10}}>{children}</div>;
}

function Field({label, value, setValue, step=1}){
  return (
    <div>
      <label style={{display:"block", fontSize:12, opacity:0.7}}>{label}</label>
      <input style={inp} type="number" value={value} step={step}
        onChange={e=>setValue(Number(e.target.value))}/>
    </div>
  );
}

const card = { background:"#111826", border:"1px solid #1d2733", borderRadius:14, padding:14, boxShadow:"0 6px 20px rgba(0,0,0,0.25)" };
const h3 = { margin:"0 0 10px 0", fontSize:14, opacity:0.9 };
const lab = { display:"block", fontSize:12, opacity:0.7, marginTop:10 };
const inp = { width:"100%", padding:"10px 10px", borderRadius:10, border:"1px solid #1d2733", background:"#0b0f14", color:"#dbe2ea", outline:"none" };
const btn = { padding:"10px 12px", borderRadius:10, border:"1px solid #2b3a4c", background:"#0f2a1e", color:"#dbe2ea", cursor:"pointer" };
const btn2 = { padding:"10px 12px", borderRadius:10, border:"1px solid #2b3a4c", background:"#0b0f14", color:"#dbe2ea", cursor:"pointer" };
const btnWarn = { padding:"10px 12px", borderRadius:10, border:"1px solid #6b2f18", background:"#2b1a12", color:"#dbe2ea", cursor:"pointer" };
