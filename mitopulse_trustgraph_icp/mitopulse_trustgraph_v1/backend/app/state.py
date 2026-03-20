from __future__ import annotations

import time
import math
from typing import Tuple

from .db import q, exec_


def update_identity_state(conn, tenant_id: str, user_id: str, device_id: str, epoch: int, index_value: float, dynamic_id: str, ts: int) -> Tuple[float, float, float]:
    """Rolling baseline mean/std with gentle re-onboarding after dormancy."""
    now = int(time.time())

    state = q(
        conn,
        "SELECT * FROM identity_state WHERE tenant_id=? AND user_id=? AND device_id=? AND epoch=?",
        (tenant_id, user_id, device_id, epoch),
    )
    if not state:
        mean = index_value
        std = 0.05
        band = 0.15
        exec_(
            conn,
            """INSERT INTO identity_state(tenant_id,user_id,device_id,epoch,baseline_mean,baseline_std,stability_band,last_dynamic_id,last_ts,dormant_since)
               VALUES(?,?,?,?,?,?,?,?,?,NULL)""",
            (tenant_id, user_id, device_id, epoch, mean, std, band, dynamic_id, ts),
        )
        return mean, std, band

    s = state[0]
    last_ts = s.get("last_ts")
    dormant_since = s.get("dormant_since")

    # hibernation detection
    if last_ts is not None and ts - int(last_ts) > 86400 * 14:
        # mark dormant
        if dormant_since is None:
            exec_(
                conn,
                "UPDATE identity_state SET dormant_since=? WHERE tenant_id=? AND user_id=? AND device_id=? AND epoch=?",
                (now, tenant_id, user_id, device_id, epoch),
            )

    mean = float(s.get("baseline_mean") or index_value)
    std = float(s.get("baseline_std") or 0.05)

    # if waking from dormancy, use slow alpha
    alpha = 0.05
    if dormant_since is not None:
        alpha = 0.02
        # clear dormancy after 7 days of fresh activity
        if ts - int(last_ts or ts) <= 86400 * 7:
            exec_(
                conn,
                "UPDATE identity_state SET dormant_since=NULL WHERE tenant_id=? AND user_id=? AND device_id=? AND epoch=?",
                (tenant_id, user_id, device_id, epoch),
            )

    # EWMA mean/std
    new_mean = (1 - alpha) * mean + alpha * index_value
    # EW variance
    var = std * std
    new_var = (1 - alpha) * var + alpha * (index_value - new_mean) ** 2
    new_std = max(0.02, math.sqrt(new_var))

    band = max(0.10, min(0.35, 2.0 * new_std))

    exec_(
        conn,
        """UPDATE identity_state
           SET baseline_mean=?, baseline_std=?, stability_band=?, last_dynamic_id=?, last_ts=?
           WHERE tenant_id=? AND user_id=? AND device_id=? AND epoch=?""",
        (new_mean, new_std, band, dynamic_id, ts, tenant_id, user_id, device_id, epoch),
    )
    return new_mean, new_std, band
