
(() => {
  const chart = document.getElementById('realityChart');
  const prop = document.getElementById('propMap');
  if(!chart || !prop) return;
  const ctx = chart.getContext('2d');
  const pctx = prop.getContext('2d');

  const state = {
    data: null,
    playing: true,
    hist: [],
    t: 0
  };

  async function refresh(){
    const r = await fetch('/api/live/crypto/binance');
    const j = await r.json();
    state.data = j;
    state.hist = j.klines || [];
    updateDom(j);
  }

  function updateDom(j){
    document.getElementById('rmSymbol').textContent = j.ticker.symbol;
    document.getElementById('rmPrice').textContent = Number(j.ticker.last_price).toFixed(2);
    document.getElementById('rmChange').textContent = Number(j.ticker.price_change_percent).toFixed(2) + '%';
    document.getElementById('rmVolume').textContent = Math.round(j.ticker.quote_volume).toLocaleString();

    document.getElementById('bTriggered').textContent = j.baseline.triggered ? 'YES' : 'NO';
    document.getElementById('bSeverity').textContent = j.baseline.severity;
    document.getElementById('bReason').textContent = j.baseline.reason;

    document.getElementById('mTriggered').textContent = j.ml.triggered ? 'YES' : 'NO';
    document.getElementById('mSeverity').textContent = j.ml.severity + ' / z=' + j.ml.zscore;
    document.getElementById('mReason').textContent = j.ml.reason;

    document.getElementById('pTriggered').textContent = j.protocol.protocol_triggered ? 'YES' : 'NO';
    document.getElementById('pSeverity').textContent = j.protocol.risk_state;
    document.getElementById('pReason').textContent = 'policy=' + (j.protocol.policy_name || 'none');

    document.getElementById('leadAdv').textContent = j.benchmark.lead_advantage_units;
    document.getElementById('policyName').textContent = j.protocol.policy_name || 'none';
    document.getElementById('validationLine').textContent = j.protocol.validated ? ('validated / quorum=' + j.protocol.quorum_score) : ('not validated / quorum=' + j.protocol.quorum_score);

    document.getElementById('protoExplain').textContent = JSON.stringify(j.protocol.full_result, null, 2);
  }

  function drawChart(){
    ctx.clearRect(0,0,chart.width,chart.height);
    const g = ctx.createLinearGradient(0,0,chart.width,chart.height);
    g.addColorStop(0,'#081022');
    g.addColorStop(1,'#040916');
    ctx.fillStyle = g;
    ctx.fillRect(0,0,chart.width,chart.height);

    const data = state.hist;
    if(!data || !data.length) return;
    const pad = 34;
    const w = chart.width - pad*2;
    const h = chart.height - pad*2;

    const closes = data.map(d => d.close);
    const minV = Math.min(...closes);
    const maxV = Math.max(...closes);
    const span = (maxV-minV) || 1;

    ctx.strokeStyle = 'rgba(255,255,255,0.08)';
    ctx.beginPath();
    ctx.moveTo(pad, pad+h);
    ctx.lineTo(pad+w, pad+h);
    ctx.stroke();

    ctx.beginPath();
    data.forEach((d, i) => {
      const x = pad + (i/(data.length-1))*w;
      const y = pad + h - ((d.close-minV)/span)*h;
      if(i === 0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
    });
    ctx.strokeStyle = '#7bdcff';
    ctx.lineWidth = 2.2;
    ctx.stroke();

    // protocol threshold overlay
    if(state.data){
      const stateName = state.data.protocol.risk_state;
      let col = '#4cc9f0';
      if(stateName === 'PRESSURE') col = '#ffd166';
      if(['INSTABILITY','CRITICAL','COLLAPSE'].includes(stateName)) col = '#ff6b6b';
      ctx.fillStyle = 'rgba(255,255,255,0.85)';
      ctx.font = 'bold 18px Arial';
      ctx.fillText('Reality Mode — BTCUSDT / Baseline vs ML vs Protocol', 18, 28);
      ctx.fillStyle = col;
      ctx.fillText('Protocol State: ' + stateName, 18, 54);

      const li = data.length-1;
      const lx = pad + (li/(data.length-1))*w;
      const ly = pad + h - ((data[li].close-minV)/span)*h;
      ctx.beginPath();
      ctx.arc(lx, ly, 6, 0, Math.PI*2);
      ctx.fillStyle = col;
      ctx.fill();

      // baseline marker
      if(state.data.baseline.triggered){
        ctx.fillStyle = '#ffd166';
        ctx.fillRect(chart.width-210, 18, 12, 12);
        ctx.fillStyle = '#eef4ff';
        ctx.fillText('Baseline Alert', chart.width-188, 30);
      }
      if(state.data.ml.triggered){
        ctx.fillStyle = '#b78cff';
        ctx.fillRect(chart.width-210, 42, 12, 12);
        ctx.fillStyle = '#eef4ff';
        ctx.fillText('ML Alert', chart.width-188, 54);
      }
      if(state.data.protocol.protocol_triggered){
        ctx.fillStyle = col;
        ctx.fillRect(chart.width-210, 66, 12, 12);
        ctx.fillStyle = '#eef4ff';
        ctx.fillText('Protocol Trigger', chart.width-188, 78);
      }
    }
  }

  function drawPropMap(){
    pctx.clearRect(0,0,prop.width,prop.height);
    pctx.fillStyle = '#091121';
    pctx.fillRect(0,0,prop.width,prop.height);

    const nodes = [
      {x:80,y:120,label:'BTC',risk: state.data ? state.data.protocol.scr : 35},
      {x:220,y:70,label:'ETH',risk: state.data ? Math.min(95, state.data.protocol.scr*0.82) : 28},
      {x:220,y:170,label:'SOL',risk: state.data ? Math.min(95, state.data.protocol.scr*0.74) : 26},
      {x:390,y:60,label:'ALT-A',risk: state.data ? Math.min(95, state.data.protocol.scr*0.66) : 20},
      {x:390,y:120,label:'ALT-B',risk: state.data ? Math.min(95, state.data.protocol.scr*0.58) : 18},
      {x:390,y:180,label:'ALT-C',risk: state.data ? Math.min(95, state.data.protocol.scr*0.52) : 16},
      {x:540,y:120,label:'MARKET FIELD',risk: state.data ? Math.min(95, state.data.protocol.scr*0.48) : 12}
    ];
    const links = [[0,1],[0,2],[1,3],[1,4],[2,5],[3,6],[4,6],[5,6]];
    links.forEach(([a,b], idx) => {
      const na = nodes[a], nb = nodes[b];
      pctx.beginPath();
      pctx.moveTo(na.x,na.y);
      pctx.lineTo(nb.x,nb.y);
      pctx.strokeStyle = 'rgba(108,142,220,0.28)';
      pctx.stroke();

      const t = ((state.t*0.25)+idx*0.15)%1;
      const x = na.x + (nb.x-na.x)*t;
      const y = na.y + (nb.y-na.y)*t;
      pctx.beginPath();
      pctx.arc(x,y,2.5,0,Math.PI*2);
      pctx.fillStyle = '#eef4ff';
      pctx.fill();
    });

    nodes.forEach(n=>{
      const col = n.risk >= 75 ? '#ff6b6b' : n.risk >= 40 ? '#ffd166' : '#4cc9f0';
      pctx.beginPath();
      pctx.arc(n.x,n.y,12 + n.risk/20,0,Math.PI*2);
      pctx.fillStyle = col;
      pctx.fill();
      pctx.fillStyle = '#eef4ff';
      pctx.font = '12px Arial';
      pctx.textAlign = 'center';
      pctx.fillText(n.label, n.x, n.y+28);
    });
  }

  function loop(){
    if(state.playing) state.t += 1;
    drawChart();
    drawPropMap();
    requestAnimationFrame(loop);
  }

  window.RM = {
    refresh,
    togglePlay(){ state.playing = !state.playing; }
  };
  refresh();
  loop();
})();
