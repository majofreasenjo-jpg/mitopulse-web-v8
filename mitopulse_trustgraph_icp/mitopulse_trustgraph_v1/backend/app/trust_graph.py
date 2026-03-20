from __future__ import annotations

import json
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Tuple

from .db import q, exec_


def node_id(user_id: str, device_id: str, epoch: int) -> str:
    return f"{user_id}:{device_id}:e{epoch}"


@dataclass
class Edge:
    src: str
    dst: str
    edge_type: str
    weight: float


def update_graph(conn, tenant_id: str, event_row: dict) -> None:
    """Heurísticas simples de grafo, suficientes para demo."""
    now = int(time.time())
    src = node_id(event_row["user_id"], event_row["device_id"], event_row["epoch"])

    edges: List[Edge] = []

    # 1) Edge de riesgo: si coercion -> conectar al nodo 'RISK' del tenant
    if int(event_row["coercion"]) == 1 or int(event_row["risk"]) >= 80:
        risk_anchor = f"{tenant_id}:RISK"
        edges.append(Edge(src, risk_anchor, "risk", min(1.0, event_row["risk"] / 100.0)))

    # 2) Convivencia (cohab): mismo context_fp dentro de 30min, distinto user
    if event_row.get("context_fp"):
        rows = q(
            conn,
            """SELECT user_id, device_id, epoch, ts FROM identity_events
               WHERE tenant_id=? AND context_fp=? AND ABS(ts-?)<=1800
               ORDER BY ts DESC LIMIT 25""",
            (tenant_id, event_row["context_fp"], event_row["ts"]),
        )
        for r in rows:
            if r["user_id"] != event_row["user_id"]:
                dst = node_id(r["user_id"], r["device_id"], r["epoch"])
                edges.append(Edge(src, dst, "cohab", 0.35))

    # Persist edges
    for e in edges:
        exec_(
            conn,
            "INSERT INTO graph_edges(tenant_id, src_node, dst_node, edge_type, weight, created_at) VALUES(?,?,?,?,?,?)",
            (tenant_id, e.src, e.dst, e.edge_type, e.weight, now),
        )

    # 3) Clusters muy simples (para dashboard)
    build_clusters(conn, tenant_id)


def build_clusters(conn, tenant_id: str) -> None:
    now = int(time.time())
    # cluster work: todos los nodos recientes por tenant
    recent = q(
        conn,
        """SELECT DISTINCT user_id, device_id, epoch FROM identity_events
           WHERE tenant_id=? AND ts >= ?""",
        (tenant_id, now - 86400 * 7),
    )
    members = [node_id(r["user_id"], r["device_id"], r["epoch"]) for r in recent]
    if not members:
        return

    # attack cluster: si hay >=3 coercion en 10min
    coerc = q(
        conn,
        """SELECT COUNT(*) as c FROM identity_events
           WHERE tenant_id=? AND coercion=1 AND ts>=?""",
        (tenant_id, now - 600),
    )[0]["c"]
    attack_score = min(1.0, coerc / 5.0)

    # overwrite latest clusters snapshot
    exec_(conn, "DELETE FROM clusters WHERE tenant_id=?", (tenant_id,))
    exec_(
        conn,
        "INSERT INTO clusters(tenant_id, cluster_type, label, score, members_json, created_at) VALUES(?,?,?,?,?,?)",
        (tenant_id, "work", f"tenant:{tenant_id}", 1.0, json.dumps(members), now),
    )
    if coerc >= 3:
        exec_(
            conn,
            "INSERT INTO clusters(tenant_id, cluster_type, label, score, members_json, created_at) VALUES(?,?,?,?,?,?)",
            (tenant_id, "attack", "coercion-burst", attack_score, json.dumps(members), now),
        )
