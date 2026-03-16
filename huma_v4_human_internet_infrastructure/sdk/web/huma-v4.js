export class HumaV4 {
  constructor({ baseUrl = "http://localhost:8000", tenantId = "startup_demo" } = {}) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
    this.tenantId = tenantId;
    this.sessionId = `sess_${Math.random().toString(36).slice(2)}`;
    this.events = [];
    this.sessionStartedAt = Date.now();
    this.lastEventTs = null;
    this.focusSwitchCount = 0;
    window.addEventListener("focus", () => this.focusSwitchCount++);
    window.addEventListener("blur", () => this.focusSwitchCount++);
    ["mousemove","touchmove","keydown","click","scroll"].forEach(name => window.addEventListener(name, () => this.captureEvent()));
  }
  captureEvent(){ const now = Date.now(); if (this.lastEventTs !== null) this.events.push(now - this.lastEventTs); this.lastEventTs = now; }
  entropy(values){ if (!values.length) return 0; const bins = {}; for (const v of values){ const b = Math.floor(v/25)*25; bins[b] = (bins[b]||0)+1; } const n = values.length; let h = 0; for (const c of Object.values(bins)){ const p = c/n; h -= p*Math.log2(p); } return Math.min(1, h/4); }
  mean(values){ return values.length ? values.reduce((a,b)=>a+b,0)/values.length : 0; }
  std(values){ if (!values.length) return 0; const m = this.mean(values); return Math.sqrt(values.reduce((a,b)=>a+((b-m)**2),0)/values.length); }
  buildSignals(){
    return {
      event_count: this.events.length,
      session_duration_ms: Date.now() - this.sessionStartedAt,
      tap_interval_mean: Math.round(this.mean(this.events)),
      tap_interval_std: Math.round(this.std(this.events)),
      pointer_entropy: Number(this.entropy(this.events).toFixed(3)),
      focus_switch_count: this.focusSwitchCount,
      typing_variance: Number((this.std(this.events)/100).toFixed(3)),
      screen_width: window.innerWidth,
      screen_height: window.innerHeight,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || "",
      language: navigator.language || ""
    };
  }
  async verify({ user_ref, device_hint, action = "login", context = {} }){
    const r = await fetch(`${this.baseUrl}/v4/verify-human`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        tenant_id: this.tenantId,
        user_ref,
        device_hint,
        action,
        session_id: this.sessionId,
        signals: this.buildSignals(),
        context
      })
    });
    return r.json();
  }
}
