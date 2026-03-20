
from __future__ import annotations
from typing import Dict, Any
import time, json, math
from .engine import compute_stability
from ..db.db import fetchone, q

def robust_update_mean_std(prev_mean: float, prev_std: float, x: float, alpha: float=0.12):
    # EWMA + EWMVar (simple, stable)
    mean = (1-alpha)*prev_mean + alpha*x
    var = (1-alpha)*(prev_std**2) + alpha*(x-mean)**2
    std = math.sqrt(max(var, 1e-6))
    return mean, std

def update_state(conn, tenant_id: str, user_id: str, device_id: str, epoch: int, ts: int, idx: float, hr: float) -> Dict[str, Any]:
    row = fetchone(conn, "SELECT * FROM identity_state WHERE user_id=? AND device_id=? AND epoch=?", (user_id, device_id, epoch))
    now = int(time.time())
    if row is None:
        mean_idx, std_idx = idx, 0.05
        mean_hr, std_hr = hr, 5.0
        stability_band = 0.75
        hibernating = 0
        q(conn, "INSERT INTO identity_state(user_id,device_id,epoch,last_ts,mean_idx,std_idx,mean_hr,std_hr,stability_band,hibernating,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
          (user_id, device_id, epoch, ts, mean_idx, std_idx, mean_hr, std_hr, stability_band, hibernating, now))
    else:
        # hibernation: if gap > 14d, freeze and mark as hibernating; first event after resets gradually
        gap = max(0, ts - int(row["last_ts"]))
        hibernating = int(row["hibernating"])
        mean_idx = float(row["mean_idx"]); std_idx=float(row["std_idx"])
        mean_hr  = float(row["mean_hr"]);  std_hr=float(row["std_hr"])
        if gap > 14*24*3600:
            hibernating = 1
            # thaw slowly for first 7 days
            alpha = 0.05
        else:
            alpha = 0.12
        mean_idx, std_idx = robust_update_mean_std(mean_idx, std_idx, idx, alpha=alpha)
        mean_hr,  std_hr  = robust_update_mean_std(mean_hr, std_hr, hr, alpha=alpha)
        if hibernating and gap < 7*24*3600:
            hibernating = 0  # thawed
        z_idx = (idx-mean_idx)/max(std_idx,1e-3)
        z_hr  = (hr-mean_hr)/max(std_hr,1e-3)
        stability = compute_stability(z_hr, z_idx)
        # stability_band is rolling average of stability
        stability_band = (1-0.15)*float(row["stability_band"]) + 0.15*stability
        q(conn, "UPDATE identity_state SET last_ts=?, mean_idx=?, std_idx=?, mean_hr=?, std_hr=?, stability_band=?, hibernating=?, updated_at=? WHERE user_id=? AND device_id=? AND epoch=?",
          (ts, mean_idx, std_idx, mean_hr, std_hr, stability_band, hibernating, now, user_id, device_id, epoch))
    conn.commit()
    out = fetchone(conn, "SELECT * FROM identity_state WHERE user_id=? AND device_id=? AND epoch=?", (user_id, device_id, epoch))
    return out or {}
