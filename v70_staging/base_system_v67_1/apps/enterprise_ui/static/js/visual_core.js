
(() => {
  const seed = window.__VISUAL_CORE_SEED__ || {nodes:[],links:[],timeline:[],kpis:{}};
  const canvas = document.getElementById('visualCoreCanvas');
  const tCanvas = document.getElementById('timelineCanvas');
  const focusPanel = document.getElementById('focusPanel');
  if (!canvas || !tCanvas) return;

  const ctx = canvas.getContext('2d');
  const tctx = tCanvas.getContext('2d');

  const state = {
    nodes: seed.nodes.map(n => ({...n, baseX:n.x, baseY:n.y, pulse:Math.random()*Math.PI*2})),
    links: seed.links,
    timeline: seed.timeline,
    playing: true,
    showHeat: true,
    showSignals: true,
    storm: false,
    intensity: 64,
    speed: 0.52,
    time: 0,
    waves: [],
    focused: null,
  };

  const nodeIndex = new Map(state.nodes.map(n => [n.id, n]));
  const hotNodes = [...state.nodes].sort((a,b)=>b.risk-a.risk).slice(0, 24).map(n=>n.id);

  function colorForRisk(risk){
    if(risk >= 75) return '#ff6b6b';
    if(risk >= 40) return '#ffd166';
    return '#4cc9f0';
  }

  function lerp(a,b,t){ return a + (b-a)*t; }

  function dist(ax, ay, bx, by){
    const dx = ax-bx, dy = ay-by;
    return Math.sqrt(dx*dx+dy*dy);
  }

  function triggerWave(){
    const candidates = state.nodes.filter(n => n.risk > 65);
    const source = candidates[Math.floor(Math.random()*candidates.length)] || state.nodes[Math.floor(Math.random()*state.nodes.length)];
    state.waves.push({
      x: source.x,
      y: source.y,
      r: 0,
      maxR: 950,
      power: state.intensity / 100,
    });
    state.focused = source.id;
    renderFocus(source);
  }

  function renderFocus(n){
    if(!focusPanel || !n) return;
    focusPanel.innerHTML = `
      <strong>${n.label}</strong><br>
      Node ID: ${n.id}<br>
      Risk: ${n.risk}<br>
      Position: (${Math.round(n.x)}, ${Math.round(n.y)})<br>
      Identity state: ${n.risk > 75 ? 'CRITICAL_CLUSTER' : n.risk > 40 ? 'PRESSURE_NODE' : 'STABLE_NODE'}<br>
      Trust state: ${n.risk > 75 ? 'DEGRADED' : 'ACTIVE'}<br>
      Visual note: ${n.risk > 75 ? 'High propagation source candidate' : 'Secondary field node'}
    `;
  }

  function togglePlay(){ state.playing = !state.playing; }
  function toggleHeat(){ state.showHeat = !state.showHeat; }
  function toggleSignals(){ state.showSignals = !state.showSignals; }
  function toggleStorm(){ state.storm = !state.storm; }
  function setIntensity(v){ state.intensity = Number(v); }
  function setSpeed(v){ state.speed = Number(v)/100; }

  function update(){
    state.time += state.playing ? state.speed : 0;
    for(const n of state.nodes){
      const wobble = state.storm ? 2.4 : 1.0;
      n.x = n.baseX + Math.cos(state.time + n.pulse) * wobble * (n.risk/100);
      n.y = n.baseY + Math.sin(state.time*1.2 + n.pulse) * wobble * (n.risk/100);
    }
    for(const w of state.waves){
      w.r += 6 + state.speed*8 + state.intensity/60;
    }
    state.waves = state.waves.filter(w => w.r < w.maxR);
  }

  function drawBackground(){
    ctx.clearRect(0,0,canvas.width,canvas.height);
    const grad = ctx.createRadialGradient(canvas.width*0.5, canvas.height*0.5, 60, canvas.width*0.5, canvas.height*0.5, canvas.width*0.6);
    grad.addColorStop(0, 'rgba(22,34,68,0.95)');
    grad.addColorStop(1, 'rgba(5,10,20,1)');
    ctx.fillStyle = grad;
    ctx.fillRect(0,0,canvas.width,canvas.height);

    if(state.showHeat){
      for(const id of hotNodes){
        const n = nodeIndex.get(id);
        if(!n) continue;
        const rg = ctx.createRadialGradient(n.x, n.y, 10, n.x, n.y, 120);
        const alpha = 0.12 + (n.risk/100)*0.18;
        rg.addColorStop(0, `rgba(255,80,80,${alpha})`);
        rg.addColorStop(1, 'rgba(255,80,80,0)');
        ctx.fillStyle = rg;
        ctx.beginPath();
        ctx.arc(n.x, n.y, 120, 0, Math.PI*2);
        ctx.fill();
      }
    }

    if(state.storm){
      ctx.save();
      ctx.globalAlpha = 0.08;
      for(let i=0;i<4;i++){
        ctx.beginPath();
        const cx = canvas.width*0.5 + Math.cos(state.time*0.3+i)*180;
        const cy = canvas.height*0.5 + Math.sin(state.time*0.35+i)*110;
        ctx.strokeStyle = '#b05cff';
        ctx.lineWidth = 2;
        ctx.arc(cx, cy, 90 + i*28 + Math.sin(state.time+i)*8, 0, Math.PI*2);
        ctx.stroke();
      }
      ctx.restore();
    }
  }

  function drawLinks(){
    ctx.save();
    ctx.lineWidth = 1;
    for(const l of state.links){
      const a = nodeIndex.get(l.s);
      const b = nodeIndex.get(l.t);
      if(!a || !b) continue;
      const d = dist(a.x,a.y,b.x,b.y);
      const alpha = Math.max(0.04, 0.18 - d/5000);
      ctx.strokeStyle = `rgba(100,140,255,${alpha})`;
      if(state.showSignals && (a.risk > 72 || b.risk > 72)){
        ctx.strokeStyle = `rgba(174,102,255,${Math.min(0.45, alpha+0.18)})`;
      }
      ctx.beginPath();
      ctx.moveTo(a.x,a.y);
      ctx.lineTo(b.x,b.y);
      ctx.stroke();
    }
    ctx.restore();
  }

  function drawSignals(){
    if(!state.showSignals) return;
    ctx.save();
    for(const l of state.links.slice(0, 900)){
      const a = nodeIndex.get(l.s);
      const b = nodeIndex.get(l.t);
      if(!a || !b) continue;
      if(!(a.risk > 68 || b.risk > 68)) continue;
      const t = ((state.time*0.4) + ((a.id+b.id)%17)/17) % 1;
      const x = lerp(a.x, b.x, t);
      const y = lerp(a.y, b.y, t);
      ctx.beginPath();
      ctx.arc(x, y, 1.8 + ((a.risk+b.risk)%5)/3, 0, Math.PI*2);
      ctx.fillStyle = a.risk > 80 || b.risk > 80 ? 'rgba(255,90,90,0.85)' : 'rgba(126,210,255,0.8)';
      ctx.fill();
    }
    ctx.restore();
  }

  function drawWaves(){
    ctx.save();
    for(const w of state.waves){
      const alpha = Math.max(0, 0.6 - w.r/w.maxR);
      ctx.beginPath();
      ctx.arc(w.x, w.y, w.r, 0, Math.PI*2);
      ctx.strokeStyle = `rgba(255,255,255,${alpha*0.5})`;
      ctx.lineWidth = 1.5 + w.power*2;
      ctx.stroke();

      ctx.beginPath();
      ctx.arc(w.x, w.y, w.r*0.7, 0, Math.PI*2);
      ctx.strokeStyle = `rgba(120,210,255,${alpha*0.55})`;
      ctx.stroke();
    }
    ctx.restore();
  }

  function drawNodes(){
    for(const n of state.nodes){
      const radius = 2.8 + (n.risk/100)*5 + (Math.sin(state.time*2+n.pulse)+1)*0.4;
      ctx.beginPath();
      ctx.arc(n.x, n.y, radius, 0, Math.PI*2);
      ctx.fillStyle = colorForRisk(n.risk);
      ctx.fill();

      if(n.risk > 75){
        ctx.beginPath();
        ctx.arc(n.x, n.y, radius + 6 + Math.sin(state.time*3+n.pulse)*2, 0, Math.PI*2);
        ctx.strokeStyle = 'rgba(255,100,100,0.35)';
        ctx.lineWidth = 1;
        ctx.stroke();
      }
      if(state.focused === n.id){
        ctx.beginPath();
        ctx.arc(n.x, n.y, radius + 10, 0, Math.PI*2);
        ctx.strokeStyle = 'rgba(255,255,255,0.8)';
        ctx.lineWidth = 1.5;
        ctx.stroke();
      }
    }
  }

  function drawOverlay(){
    ctx.save();
    ctx.fillStyle = 'rgba(220,235,255,0.85)';
    ctx.font = '14px Arial';
    ctx.fillText('Visual Core — Wave / Signal / Pressure / Storm', 18, 28);
    ctx.fillStyle = 'rgba(180,198,230,0.85)';
    ctx.fillText(`Time ${state.time.toFixed(1)}  |  Intensity ${state.intensity}  |  Waves ${state.waves.length}  |  Storm ${state.storm ? 'ON' : 'OFF'}`, 18, 50);
    ctx.restore();
  }

  function drawTimeline(){
    tctx.clearRect(0,0,tCanvas.width,tCanvas.height);
    const pad = 22;
    const w = tCanvas.width - pad*2;
    const h = tCanvas.height - pad*2;
    tctx.fillStyle = '#0b1327';
    tctx.fillRect(0,0,tCanvas.width,tCanvas.height);

    const items = state.timeline.slice(0, 18);
    const maxVal = Math.max(...items.map(i=>i.magnitude), 1);

    tctx.strokeStyle = 'rgba(255,255,255,0.1)';
    tctx.beginPath();
    tctx.moveTo(pad, pad+h);
    tctx.lineTo(pad+w, pad+h);
    tctx.stroke();

    items.forEach((item, i) => {
      const x = pad + (i / Math.max(1, items.length-1)) * w;
      const barH = (item.magnitude/maxVal) * (h-24);
      const y = pad + h - barH;
      tctx.fillStyle = item.magnitude/maxVal > 0.66 ? '#ff6b6b' : item.magnitude/maxVal > 0.4 ? '#ffd166' : '#4cc9f0';
      tctx.fillRect(x-10, y, 20, barH);
      if(Math.abs((state.time*2) % items.length - i) < 0.6){
        tctx.strokeStyle = 'rgba(255,255,255,0.75)';
        tctx.strokeRect(x-12, y-2, 24, barH+4);
      }
    });
  }

  function detectNodeClick(mx, my){
    for(const n of state.nodes){
      const r = 8;
      if(dist(mx,my,n.x,n.y) <= r){
        state.focused = n.id;
        renderFocus(n);
        return;
      }
    }
  }

  canvas.addEventListener('click', (e)=>{
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const mx = (e.clientX - rect.left) * scaleX;
    const my = (e.clientY - rect.top) * scaleY;
    detectNodeClick(mx,my);
  });

  function frame(){
    update();
    drawBackground();
    drawLinks();
    drawSignals();
    drawWaves();
    drawNodes();
    drawOverlay();
    drawTimeline();
    requestAnimationFrame(frame);
  }

  window.VC = { togglePlay, triggerWave, toggleHeat, toggleSignals, toggleStorm, setIntensity, setSpeed };
  renderFocus(state.nodes.sort((a,b)=>b.risk-a.risk)[0]);
  triggerWave();
  frame();
})();
