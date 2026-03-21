
(() => {
  const scenarios = window.__VERIFY_SCENARIOS__ || {};
  const ring = document.getElementById('verifyRing');
  const tl = document.getElementById('verifyTimeline');
  const mg = document.getElementById('verifyMicroGraph');
  if (!ring || !tl || !mg) return;

  const rctx = ring.getContext('2d');
  const tctx = tl.getContext('2d');
  const gctx = mg.getContext('2d');

  const state = {
    scenario: scenarios.critical,
    time: 0,
    playing: true
  };

  function drawRing(){
    const c = ring.width / 2;
    const score = state.scenario.score;
    const pct = score / 100;
    rctx.clearRect(0,0,ring.width,ring.height);

    const bg = rctx.createRadialGradient(c,c,20,c,c,160);
    bg.addColorStop(0, 'rgba(11,18,40,1)');
    bg.addColorStop(1, 'rgba(5,10,22,1)');
    rctx.fillStyle = bg;
    rctx.fillRect(0,0,ring.width,ring.height);

    const wavePulse = (Math.sin(state.time*2)+1)/2;
    const aura = 18 + wavePulse * 14;
    const ag = rctx.createRadialGradient(c,c,10,c,c,130+aura);
    const col = state.scenario.color;
    const alpha = state.scenario.state === 'CRITICAL' ? 0.35 : state.scenario.state === 'PRESSURE' ? 0.22 : 0.18;
    ag.addColorStop(0, hexToRgba(col, alpha));
    ag.addColorStop(1, 'rgba(0,0,0,0)');
    rctx.fillStyle = ag;
    rctx.beginPath();
    rctx.arc(c,c,130+aura,0,Math.PI*2);
    rctx.fill();

    rctx.beginPath();
    rctx.arc(c,c,108,0,Math.PI*2);
    rctx.strokeStyle = 'rgba(140,170,230,0.22)';
    rctx.lineWidth = 10;
    rctx.stroke();

    rctx.beginPath();
    rctx.arc(c,c,108,-Math.PI/2, -Math.PI/2 + Math.PI*2*pct);
    rctx.strokeStyle = col;
    rctx.lineWidth = 10;
    rctx.stroke();

    rctx.beginPath();
    rctx.arc(c,c,132 + Math.sin(state.time*3)*4,0,Math.PI*2);
    rctx.strokeStyle = hexToRgba(col, 0.28);
    rctx.lineWidth = 3;
    rctx.stroke();

    rctx.fillStyle = '#ffffff';
    rctx.textAlign = 'center';
    rctx.font = 'bold 64px Arial';
    rctx.fillStyle = col;
    rctx.fillText(String(score), c, c+12);

    rctx.font = 'bold 18px Arial';
    rctx.fillStyle = '#dce7ff';
    rctx.fillText(state.scenario.state, c, c+52);
  }

  function drawTimeline(){
    tctx.clearRect(0,0,tl.width,tl.height);
    tctx.fillStyle = '#0b1327';
    tctx.fillRect(0,0,tl.width,tl.height);

    const items = [
      {label:'signal', v:0.45},
      {label:'cluster', v:0.76},
      {label:'quorum', v:0.84},
      {label:'policy', v:0.92},
      {label:'action', v:0.96}
    ];

    const pad = 26;
    const w = tl.width - pad*2;
    const baseY = 120;
    tctx.strokeStyle = 'rgba(255,255,255,0.1)';
    tctx.beginPath();
    tctx.moveTo(pad, baseY);
    tctx.lineTo(pad+w, baseY);
    tctx.stroke();

    items.forEach((it, i) => {
      const x = pad + i * (w/(items.length-1));
      const y = baseY - it.v*68;
      tctx.beginPath();
      tctx.arc(x, y, 7, 0, Math.PI*2);
      tctx.fillStyle = state.scenario.color;
      tctx.fill();

      if(i < items.length-1){
        const nx = pad + (i+1) * (w/(items.length-1));
        const ny = baseY - items[i+1].v*68;
        tctx.beginPath();
        tctx.moveTo(x,y);
        tctx.lineTo(nx,ny);
        tctx.strokeStyle = hexToRgba(state.scenario.color, 0.65);
        tctx.lineWidth = 2.5;
        tctx.stroke();
      }

      tctx.fillStyle = '#dce7ff';
      tctx.font = '12px Arial';
      tctx.textAlign = 'center';
      tctx.fillText(it.label, x, 145);

      const pulseIndex = Math.floor((state.time*2) % items.length);
      if(pulseIndex === i){
        tctx.beginPath();
        tctx.arc(x, y, 14 + Math.sin(state.time*4)*2, 0, Math.PI*2);
        tctx.strokeStyle = 'rgba(255,255,255,0.8)';
        tctx.lineWidth = 1;
        tctx.stroke();
      }
    });
  }

  function drawMicroGraph(){
    gctx.clearRect(0,0,mg.width,mg.height);
    gctx.fillStyle = '#0b1327';
    gctx.fillRect(0,0,mg.width,mg.height);

    const nodes = [
      {x:90,y:90,r:24,label:'You',risk:14},
      {x:220,y:86,r:18,label:'R1',risk:40},
      {x:348,y:92,r:22,label:'R2',risk:62},
      {x:482,y:82,r:30,label:'Target',risk:state.scenario.score},
      {x:560,y:128,r:18,label:'C1',risk:88},
      {x:430,y:132,r:16,label:'C2',risk:74},
      {x:300,y:128,r:14,label:'C3',risk:51},
    ];
    const links = [[0,1],[1,2],[2,3],[3,4],[3,5],[2,6],[5,6]];

    links.forEach(([a,b], idx) => {
      const na = nodes[a], nb = nodes[b];
      gctx.beginPath();
      gctx.moveTo(na.x,na.y);
      gctx.lineTo(nb.x,nb.y);
      gctx.strokeStyle = idx >= 3 ? hexToRgba('#ff5b5b',0.38) : 'rgba(110,145,230,0.35)';
      gctx.lineWidth = idx >= 3 ? 2.5 : 1.4;
      gctx.stroke();

      const t = ((state.time*0.65)+idx*0.13)%1;
      const px = na.x + (nb.x-na.x)*t;
      const py = na.y + (nb.y-na.y)*t;
      gctx.beginPath();
      gctx.arc(px, py, 2.4, 0, Math.PI*2);
      gctx.fillStyle = idx >= 3 ? '#ff5b5b' : '#7bdcff';
      gctx.fill();
    });

    nodes.forEach(n => {
      gctx.beginPath();
      gctx.arc(n.x,n.y,n.r,0,Math.PI*2);
      gctx.fillStyle = n.risk >= 75 ? '#ff6b6b' : n.risk >= 40 ? '#ffd166' : '#4cc9f0';
      gctx.fill();
      gctx.fillStyle = '#eef3ff';
      gctx.font = '12px Arial';
      gctx.textAlign = 'center';
      gctx.fillText(n.label, n.x, n.y + n.r + 16);
    });

    if(state.scenario.state === 'CRITICAL'){
      const target = nodes[3];
      gctx.beginPath();
      gctx.arc(target.x,target.y,46 + Math.sin(state.time*3)*4,0,Math.PI*2);
      gctx.strokeStyle = 'rgba(255,91,91,0.44)';
      gctx.lineWidth = 2;
      gctx.stroke();
    }
  }

  function hexToRgba(hex, alpha){
    const h = hex.replace('#','');
    const bigint = parseInt(h, 16);
    const r = (bigint >> 16) & 255;
    const g = (bigint >> 8) & 255;
    const b = bigint & 255;
    return `rgba(${r},${g},${b},${alpha})`;
  }

  function applyScenario(key){
    state.scenario = scenarios[key] || scenarios.critical;
    document.getElementById('receiverName').textContent = state.scenario.receiver;
    document.getElementById('confidenceValue').textContent = state.scenario.confidence;
    document.getElementById('horizonValue').textContent = state.scenario.horizon;
    document.getElementById('verifyAlert').className = 'verify-alert ' + (
      state.scenario.state === 'CRITICAL' ? 'critical' :
      state.scenario.state === 'PRESSURE' ? 'watch' : 'safe'
    );
    document.querySelector('.verify-alert-title').textContent = state.scenario.alertTitle;
    document.getElementById('verifyAlertText').textContent = state.scenario.alertText;
    document.getElementById('traceLine1').textContent = state.scenario.trace[0];
    document.getElementById('traceLine2').textContent = state.scenario.trace[1];
    document.getElementById('traceLine3').textContent = state.scenario.trace[2];
    const btn = document.getElementById('primaryDecision');
    btn.textContent = state.scenario.primaryText;
    btn.className = 'btn verify-primary ' + state.scenario.primaryClass;
  }

  function frame(){
    state.time += 0.02;
    drawRing();
    drawTimeline();
    drawMicroGraph();
    requestAnimationFrame(frame);
  }

  window.VerifyV2 = { setScenario: applyScenario };
  applyScenario('critical');
  frame();
})();
