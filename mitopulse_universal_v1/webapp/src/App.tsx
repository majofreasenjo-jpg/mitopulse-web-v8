import React, { useMemo, useState } from 'react'

type Env = { altitude_m:number; temp_c:number; humidity:number; pressure_hpa:number }
type Signals = { hr?:number; hrv_rmssd?:number; spo2?:number; sleep_score?:number; accel_load?:number }

function clamp(x:number, lo:number, hi:number){ return Math.max(lo, Math.min(hi, x)) }
function normalize(x:number, lo:number, hi:number){ if(hi<=lo) return 0.5; return clamp((x-lo)/(hi-lo), 0, 1) }

function cEnv(env:Env){
  const alt = env.altitude_m/1000
  const t = Math.abs(env.temp_c-22)
  const h = Math.abs(env.humidity-50)/50
  const p = Math.abs(env.pressure_hpa-1013.25)/100
  const raw = 1 / (1 + 0.012*alt + 0.008*t + 0.005*h + 0.003*p)
  return clamp(raw, 0.85, 1.15)
}
function pickTier(s:Signals){
  if(s.hrv_rmssd !== undefined && s.hrv_rmssd !== null) return 'tier2'
  return 'tier1'
}
function fusedIndex(s:Signals, env:Env){
  const b_hr = 1 - normalize(s.hr ?? 75, 45, 140)
  const b_hrv = normalize(s.hrv_rmssd ?? 25, 5, 120)
  const b_spo2 = normalize(s.spo2 ?? 96, 85, 100)
  const b_sleep = normalize(s.sleep_score ?? 70, 0, 100)
  const b_load = 1 - normalize(s.accel_load ?? 0.3, 0, 1.5)
  const tier = pickTier(s)
  let f = 0
  if(tier==='tier1'){
    f = 0.35*b_hr + 0.25*b_spo2 + 0.20*b_sleep + 0.20*b_load
  }else{
    f = 0.25*b_hr + 0.30*b_hrv + 0.20*b_spo2 + 0.15*b_sleep + 0.10*b_load
  }
  return clamp(f*cEnv(env), 0, 1)
}

export default function App(){
  const [baseUrl,setBaseUrl] = useState('http://127.0.0.1:8000')
  const [userId,setUserId] = useState('manuel')
  const [deviceId,setDeviceId] = useState('web-pwa')
  const [hr,setHr] = useState(72)
  const [hrv,setHrv] = useState<number|undefined>(38)
  const [spo2,setSpo2] = useState<number|undefined>(97)
  const [sleep,setSleep] = useState<number|undefined>(78)
  const [load,setLoad] = useState<number|undefined>(0.35)
  const [env,setEnv] = useState<Env>({altitude_m:520,temp_c:22,humidity:50,pressure_hpa:1013})
  const [lastDynamic,setLastDynamic] = useState<string>('')
  const [log,setLog] = useState<string>('')

  const signals:Signals = useMemo(()=>({hr, hrv_rmssd:hrv, spo2, sleep_score:sleep, accel_load:load}),[hr,hrv,spo2,sleep,load])
  const tier = pickTier(signals)
  const idx = fusedIndex(signals, env)

  async function sendDemo(){
    const ts = Math.floor(Date.now()/1000)
    const request_id = crypto.randomUUID()
    // En web, por defecto NO guardamos secret real. En demo, mandamos dynamic_id dummy.
    // El flujo “real” usa secret en dispositivo (Android/iOS). Aquí sirve para probar backend/dashboard.
    const dynamic_id = btoa(`demo:${userId}:${deviceId}:${ts}:${idx.toFixed(3)}`).replace(/=+$/,'')
    const payload:any = { ts, user_id:userId, device_id:deviceId, request_id, tier_used:tier, index_value:idx, slope:0, dynamic_id, risk:0, coercion:false, signature:null }
    const r = await fetch(`${baseUrl}/v1/identity-events`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)})
    const txt = await r.text()
    setLastDynamic(dynamic_id)
    setLog(prev=>`POST ${r.status} ${txt}\n`+prev)
  }
  async function verify(){
    const request_id = crypto.randomUUID()
    const payload = { user_id:userId, device_id:deviceId, request_id, dynamic_id:lastDynamic }
    const r = await fetch(`${baseUrl}/v1/verify`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)})
    const txt = await r.text()
    setLog(prev=>`VERIFY ${r.status} ${txt}\n`+prev)
  }

  return (
    <div className="container">
      <h1>MitoPulse PWA (PC / Notebook / Tablet / Mobile)</h1>
      <div className="card">
        <div className="row">
          <div>
            <div>Backend URL</div>
            <input value={baseUrl} onChange={e=>setBaseUrl(e.target.value)} style={{width:320}}/>
          </div>
          <div>
            <div>User</div>
            <input value={userId} onChange={e=>setUserId(e.target.value)}/>
          </div>
          <div>
            <div>Device</div>
            <input value={deviceId} onChange={e=>setDeviceId(e.target.value)}/>
          </div>
        </div>
      </div>

      <div className="card">
        <h3>Inputs</h3>
        <div className="row">
          <label>HR <input type="number" value={hr} onChange={e=>setHr(Number(e.target.value))}/></label>
          <label>HRV <input type="number" value={hrv ?? ''} onChange={e=>setHrv(e.target.value===''?undefined:Number(e.target.value))}/></label>
          <label>SpO2 <input type="number" value={spo2 ?? ''} onChange={e=>setSpo2(e.target.value===''?undefined:Number(e.target.value))}/></label>
          <label>Sleep <input type="number" value={sleep ?? ''} onChange={e=>setSleep(e.target.value===''?undefined:Number(e.target.value))}/></label>
          <label>Load <input type="number" step="0.01" value={load ?? ''} onChange={e=>setLoad(e.target.value===''?undefined:Number(e.target.value))}/></label>
        </div>

        <h3>Env</h3>
        <div className="row">
          <label>Alt(m) <input type="number" value={env.altitude_m} onChange={e=>setEnv({...env, altitude_m:Number(e.target.value)})}/></label>
          <label>Temp(C) <input type="number" value={env.temp_c} onChange={e=>setEnv({...env, temp_c:Number(e.target.value)})}/></label>
          <label>Hum(%) <input type="number" value={env.humidity} onChange={e=>setEnv({...env, humidity:Number(e.target.value)})}/></label>
          <label>Press(hPa) <input type="number" value={env.pressure_hpa} onChange={e=>setEnv({...env, pressure_hpa:Number(e.target.value)})}/></label>
        </div>

        <div style={{marginTop:12}}>
          <span className="badge">tier: {tier}</span>{' '}
          <span className="badge">index: {idx.toFixed(3)}</span>{' '}
          <span className={lastDynamic ? "badge ok":"badge"}>dynamic_id: <span className="mono">{lastDynamic ? lastDynamic.slice(0,18)+'…' : '(none)'}</span></span>
        </div>

        <div className="row" style={{marginTop:12}}>
          <button onClick={sendDemo}>Send DEMO Event</button>
          <button onClick={verify} disabled={!lastDynamic}>Verify</button>
          <a href={`${baseUrl}/dashboard`} target="_blank" rel="noreferrer">Open Dashboard</a>
        </div>
      </div>

      <div className="card">
        <h3>Log</h3>
        <pre className="mono" style={{whiteSpace:'pre-wrap'}}>{log || '(sin acciones aún)'}</pre>
      </div>
    </div>
  )
}
