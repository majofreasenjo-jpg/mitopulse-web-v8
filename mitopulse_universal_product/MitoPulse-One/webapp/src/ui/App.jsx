import React, { useMemo, useState, useEffect } from "react";

const DEFAULT_BACKEND = import.meta.env.VITE_BACKEND_DEFAULT || "http://127.0.0.1:8000";
const API_KEY = "demo-key";

const clamp = (x,a,b)=>Math.max(a, Math.min(b,x));

function chooseTier(s){
  if (s.hrv_rmssd != null && s.hrv_rmssd !== "") return "tier2";
  if (s.spo2 != null && s.spo2 !== "") return "tier1";
  return "tier1";
}

function computeIndex(s, env){
  const hr = Number(s.hr), hrv = Number(s.hrv_rmssd), spo2 = Number(s.spo2),
        sleep = Number(s.sleep_score), load = Number(s.load);
  const n_hr = clamp(1 - (hr - 50) / 120, 0, 1);
  const n_hrv = isFinite(hrv) ? clamp((hrv - 10) / 90, 0, 1) : 0.5;
  const n_spo2 = isFinite(spo2) ? clamp((spo2 - 85) / 15, 0, 1) : 0.7;
  const n_sleep = isFinite(sleep) ? clamp(sleep / 100, 0, 1) : 0.6;
  const n_load = isFinite(load) ? clamp(1 - load / 10, 0, 1) : 0.6;
  const F = 0.30*n_hrv + 0.20*n_spo2 + 0.20*n_sleep + 0.15*n_hr + 0.15*n_load;

  const alt = Number(env.altitude_m ?? 0);
  const temp = Number(env.temp_c ?? 22);
  const hum = Number(env.humidity_pct ?? 50);

  const C = 1 / (1 + 0.012*(alt/1000) + 0.008*Math.abs(temp-22) + 0.005*Math.abs(hum-50));
  return clamp(F * C, 0, 1);
}

async function hmacSha256Hex(keyStr, msgStr){
  const enc = new TextEncoder();
  const keyData = enc.encode(keyStr);
  const msg = enc.encode(msgStr);
  const cryptoKey = await crypto.subtle.importKey("raw", keyData, { name:"HMAC", hash:"SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", cryptoKey, msg);
  return [...new Uint8Array(sig)].map(b=>b.toString(16).padStart(2,"0")).join("");
}

function randId(){
  return crypto.getRandomValues(new Uint8Array(16)).reduce((s,b)=>s + b.toString(16).padStart(2,"0"), "");
}

function Btn({children,onClick,kind}){
  const bg = kind==="danger" ? "#ff4d4d" : "#1a2440";
  return <button onClick={onClick} style={{background:bg,color:"#e8eefc",border:"1px solid #1f2a44",borderRadius:12,padding:"10px 12px",cursor:"pointer",fontWeight:800,fontSize:12}}>{children}</button>
}

function Panel({title, children, full}){
  return <div style={{gridColumn: full ? "1 / -1" : undefined, background:"#121a2a", border:"1px solid #1f2a44", borderRadius:14, padding:12}}>
    <div style={{fontSize:12,color:"#99a3b3",fontWeight:800,textTransform:"uppercase",letterSpacing:.2,marginBottom:8}}>{title}</div>
    {children}
  </div>
}

function RowInput({label,value,onChange}){
  return <div style={{display:"flex",gap:10,alignItems:"center",marginBottom:8}}>
    <div style={{width:110,fontSize:12,color:"#99a3b3"}}>{label}</div>
    <input value={value} onChange={e=>onChange(e.target.value)} style={{flex:1,padding:"8px 10px",borderRadius:10,border:"1px solid #1f2a44",background:"#0b0f17",color:"#e8eefc"}} />
  </div>
}

function Slider({label,k,v,set,min,max,step}){
  return <div style={{display:"flex",gap:10,alignItems:"center",margin:"8px 0"}}>
    <div style={{width:120,fontSize:12,color:"#99a3b3"}}>{label}</div>
    <input type="range" min={min} max={max} step={step} value={v} onChange={e=>set(o=>({...o,[k]:Number(e.target.value)}))} style={{flex:1}} />
    <div style={{width:60,fontFamily:"monospace"}}>{Number(v).toFixed(step<1?1:0)}</div>
  </div>
}

export default function App(){
  const [backend, setBackend] = useState(DEFAULT_BACKEND);
  const [userId, setUserId] = useState("demo-user");
  const [deviceId, setDeviceId] = useState("demo-device");
  const [live, setLive] = useState(false);

  const [signals, setSignals] = useState({ hr:72, hrv_rmssd:42, spo2:97, sleep_score:78, load:3 });
  const [env, setEnv] = useState({ altitude_m:0, temp_c:22, humidity_pct:50, pressure_hpa:1013 });

  const tier = useMemo(()=>chooseTier(signals), [signals]);
  const idx = useMemo(()=>computeIndex(signals, env), [signals, env]);

  const [logs, setLogs] = useState([]);
  const log = (kind, status, data)=>setLogs(l=>[{ts:new Date().toISOString(), kind, status, data}, ...l].slice(0,80));

  async function sendEvent(){
    const ts = Math.floor(Date.now()/1000);
    const request_id = randId();
    const dynamic_id = await hmacSha256Hex("device-secret-demo", JSON.stringify({userId, deviceId, ts, idx, tier}));
    const signature = await hmacSha256Hex(API_KEY, `${userId}|${deviceId}|${ts}|${dynamic_id}`);

    let risk = 0;
    if (signals.hrv_rmssd < 18) risk += 25;
    if (signals.hr > 120) risk += 25;
    if (signals.spo2 < 90) risk += 25;
    if (idx < 0.20) risk += 25;
    risk = clamp(risk,0,100);

    const payload = { ts, user_id:userId, device_id:deviceId, request_id, tier, index:idx, slope:0.0, risk, coercion:risk>=60,
      stability:1.0, human_conf:0.9, dynamic_id, signature, signals, env };

    const res = await fetch(`${backend}/identity/event`, { method:"POST",
      headers: {"Content-Type":"application/json", "X-API-Key": API_KEY}, body: JSON.stringify(payload) });
    const data = await res.json().catch(()=>({}));
    log("POST /identity/event", res.status, data);
  }

  async function verify(){
    const ts = Math.floor(Date.now()/1000);
    const request_id = randId();
    const dynamic_id = await hmacSha256Hex(API_KEY, JSON.stringify({userId, deviceId, ts, idx, tier}));
    const signature = await hmacSha256Hex(API_KEY, `${userId}|${deviceId}|${ts}|${dynamic_id}`);
    const res = await fetch(`${backend}/identity/verify`, { method:"POST",
      headers: {"Content-Type":"application/json", "X-API-Key": API_KEY},
      body: JSON.stringify({ts, user_id:userId, device_id:deviceId, request_id, dynamic_id, signature}) });
    const data = await res.json().catch(()=>({}));
    log("POST /identity/verify", res.status, data);
  }

  async function getState(){
    const q = new URLSearchParams({user_id:userId, device_id:deviceId});
    const res = await fetch(`${backend}/identity/state?${q}`, { headers: {"X-API-Key": API_KEY} });
    const data = await res.json().catch(()=>({}));
    log("GET /identity/state", res.status, data);
  }

  async function human(){
    const q = new URLSearchParams({user_id:userId, device_id:deviceId});
    const res = await fetch(`${backend}/identity/human-proof?${q}`, { headers: {"X-API-Key": API_KEY} });
    const data = await res.json().catch(()=>({}));
    log("GET /identity/human-proof", res.status, data);
  }

  useEffect(()=>{
    if(!live) return;
    const id = setInterval(()=>sendEvent(), 4000);
    return ()=>clearInterval(id);
  }, [live, backend, userId, deviceId, idx, tier, signals, env]);

  return (
    <div style={{minHeight:"100vh", background:"#0b0f17", color:"#e8eefc", fontFamily:"system-ui", padding:16}}>
      <div style={{maxWidth:1100, margin:"0 auto"}}>
        <h1 style={{margin:"0 0 6px 0", fontSize:18}}>MitoPulse One — Universal Demo (PWA)</h1>
        <div style={{color:"#99a3b3", fontSize:12, marginBottom:14}}>
          Backend URL + LIVE MODE. Dashboard at <span style={{fontFamily:"monospace"}}>{backend}/dashboard</span>
        </div>

        <div style={{display:"grid", gridTemplateColumns:"1fr 1fr", gap:12}}>
          <Panel title="Connection">
            <RowInput label="Backend URL" value={backend} onChange={setBackend}/>
            <RowInput label="User ID" value={userId} onChange={setUserId}/>
            <RowInput label="Device ID" value={deviceId} onChange={setDeviceId}/>
            <div style={{display:"flex", gap:10, alignItems:"center", marginTop:8}}>
              <Btn kind={live?"danger":undefined} onClick={()=>setLive(v=>!v)}>{live?"STOP LIVE MODE":"START LIVE MODE (4s)"}</Btn>
              <div style={{fontSize:12, color:"#99a3b3"}}>tier <span style={{fontFamily:"monospace"}}>{tier}</span> • index <span style={{fontFamily:"monospace"}}>{idx.toFixed(3)}</span></div>
            </div>
          </Panel>

          <Panel title="Actions">
            <div style={{display:"flex", gap:10, flexWrap:"wrap"}}>
              <Btn onClick={sendEvent}>Send Identity Event</Btn>
              <Btn onClick={verify}>Verify</Btn>
              <Btn onClick={getState}>Get State</Btn>
              <Btn onClick={human}>Human Proof</Btn>
            </div>
          </Panel>

          <Panel title="Signals">
            <Slider label="HR" k="hr" v={signals.hr} set={setSignals} min={35} max={200} step={1}/>
            <Slider label="HRV (RMSSD)" k="hrv_rmssd" v={signals.hrv_rmssd} set={setSignals} min={5} max={150} step={1}/>
            <Slider label="SpO2" k="spo2" v={signals.spo2} set={setSignals} min={80} max={100} step={1}/>
            <Slider label="Sleep score" k="sleep_score" v={signals.sleep_score} set={setSignals} min={0} max={100} step={1}/>
            <Slider label="Load" k="load" v={signals.load} set={setSignals} min={0} max={10} step={0.5}/>
          </Panel>

          <Panel title="Environment">
            <Slider label="Altitude (m)" k="altitude_m" v={env.altitude_m} set={setEnv} min={0} max={4000} step={10}/>
            <Slider label="Temp (°C)" k="temp_c" v={env.temp_c} set={setEnv} min={-10} max={45} step={1}/>
            <Slider label="Humidity (%)" k="humidity_pct" v={env.humidity_pct} set={setEnv} min={0} max={100} step={1}/>
            <Slider label="Pressure (hPa)" k="pressure_hpa" v={env.pressure_hpa} set={setEnv} min={850} max={1100} step={1}/>
          </Panel>

          <Panel title="Logs" full>
            <div style={{fontFamily:"monospace", fontSize:12, whiteSpace:"pre-wrap"}}>
              {logs.map((l,i)=>(
                <div key={i} style={{borderBottom:"1px solid #1f2a44", padding:"8px 0"}}>
                  <div style={{color:"#99a3b3"}}>{l.ts} • {l.kind} • {l.status}</div>
                  <div>{JSON.stringify(l.data)}</div>
                </div>
              ))}
            </div>
          </Panel>
        </div>
      </div>
    </div>
  );
}
