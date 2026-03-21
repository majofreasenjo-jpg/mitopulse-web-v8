
(() => {
  const canvas = document.getElementById('cinematicCanvas');
  if(!canvas) return;
  const ctx = canvas.getContext('2d');
  const steps = [
    {title:'Signal', sub:'Localized anomaly emerges', color:'#4cc9f0', x:180, y:380, r:30},
    {title:'Propagation', sub:'Relational wave expands', color:'#7bdcff', x:410, y:300, r:42},
    {title:'Pressure', sub:'System tension accumulates', color:'#ffd166', x:650, y:390, r:58},
    {title:'Validation', sub:'Quorum confirms threat', color:'#b98cff', x:900, y:300, r:66},
    {title:'Action', sub:'Policy triggers block / isolate', color:'#ff6b6b', x:1110, y:380, r:76},
  ];
  let t = 0;
  let playing = true;

  function bg(){
    const g = ctx.createLinearGradient(0,0,canvas.width,canvas.height);
    g.addColorStop(0, '#081022');
    g.addColorStop(1, '#040916');
    ctx.fillStyle = g;
    ctx.fillRect(0,0,canvas.width,canvas.height);
  }

  function drawLinks(){
    ctx.save();
    ctx.lineWidth = 3;
    for(let i=0;i<steps.length-1;i++){
      const a = steps[i], b = steps[i+1];
      ctx.beginPath();
      ctx.moveTo(a.x,a.y);
      ctx.lineTo(b.x,b.y);
      ctx.strokeStyle = 'rgba(110,140,220,0.22)';
      ctx.stroke();

      const p = Math.max(0, Math.min(1, (t - i*80)/80));
      if(p > 0){
        const px = a.x + (b.x-a.x)*p;
        const py = a.y + (b.y-a.y)*p;
        ctx.beginPath();
        ctx.moveTo(a.x,a.y);
        ctx.lineTo(px,py);
        ctx.strokeStyle = 'rgba(255,255,255,0.55)';
        ctx.stroke();
      }
    }
    ctx.restore();
  }

  function drawSteps(){
    steps.forEach((s, i) => {
      const active = t >= i*80;
      const pulse = active ? (Math.sin(t/10 + i)+1)/2 : 0;
      const radius = s.r + pulse*6;
      const ag = ctx.createRadialGradient(s.x,s.y,10,s.x,s.y,radius+26);
      ag.addColorStop(0, hexToRgba(s.color, 0.35));
      ag.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = ag;
      ctx.beginPath();
      ctx.arc(s.x,s.y,radius+26,0,Math.PI*2);
      ctx.fill();

      ctx.beginPath();
      ctx.arc(s.x,s.y,radius,0,Math.PI*2);
      ctx.fillStyle = active ? s.color : 'rgba(75,92,130,0.55)';
      ctx.fill();

      ctx.fillStyle = '#eef4ff';
      ctx.textAlign = 'center';
      ctx.font = 'bold 22px Arial';
      ctx.fillText(s.title, s.x, s.y - radius - 18);
      ctx.font = '15px Arial';
      ctx.fillStyle = 'rgba(220,232,255,0.86)';
      ctx.fillText(s.sub, s.x, s.y + radius + 24);
    });
  }

  function overlay(){
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 18px Arial';
    ctx.fillText('Cinematic Replay — Signal → Propagation → Pressure → Validation → Action', 22, 34);
  }

  function frame(){
    bg();
    drawLinks();
    drawSteps();
    overlay();
    if(playing) t += 1.2;
    requestAnimationFrame(frame);
  }

  function hexToRgba(hex, alpha){
    const h = hex.replace('#','');
    const bigint = parseInt(h, 16);
    const r = (bigint >> 16) & 255;
    const g = (bigint >> 8) & 255;
    const b = bigint & 255;
    return `rgba(${r},${g},${b},${alpha})`;
  }

  window.CR = {
    play(){ playing = true; },
    pause(){ playing = false; },
    reset(){ t = 0; }
  };
  frame();
})();
