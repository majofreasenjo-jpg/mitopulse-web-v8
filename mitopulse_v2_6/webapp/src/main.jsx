
import React,{useState} from "react"
import {createRoot} from "react-dom/client"

function App(){

const [backend,setBackend]=useState("http://127.0.0.1:8000")
const [user,setUser]=useState("manuel")
const [device,setDevice]=useState("browser-v26")
const [log,setLog]=useState([])
const [live,setLive]=useState(false)

async function sendEvent(){

 const res=await fetch(backend+"/v1/identity-events",{
  method:"POST",
  headers:{"Content-Type":"application/json"},
  body:JSON.stringify({
   user_id:user,
   device_id:device
  })
 })

 setLog(l=>["event sent",...l])
}

async function getState(){

 const r=await fetch(`${backend}/v2/identity/state?user_id=${user}&device_id=${device}`)
 const t=await r.text()

 setLog(l=>[t,...l])
}

async function humanProof(){

 const r=await fetch(`${backend}/v2/human-proof?user_id=${user}&device_id=${device}`)
 const t=await r.text()

 setLog(l=>[t,...l])
}

function toggleLive(){

 if(!live){

  setLive(true)

  window.liveTimer=setInterval(()=>{
   sendEvent()
  },4000)

 }else{

  setLive(false)
  clearInterval(window.liveTimer)

 }

}

return(

<div style={{padding:40}}>

<h1>MitoPulse v2.6</h1>

<div>

<input value={backend} onChange={e=>setBackend(e.target.value)}/>

</div>

<div>

<button onClick={sendEvent}>Send Event</button>
<button onClick={getState}>Get State</button>
<button onClick={humanProof}>Human Proof</button>
<button onClick={toggleLive}>{live?"LIVE ON":"LIVE OFF"}</button>

</div>

<div style={{marginTop:20}}>

{log.map((x,i)=>(
<div key={i}>{x}</div>
))}

</div>

</div>

)

}

createRoot(document.getElementById("root")).render(<App/>)
