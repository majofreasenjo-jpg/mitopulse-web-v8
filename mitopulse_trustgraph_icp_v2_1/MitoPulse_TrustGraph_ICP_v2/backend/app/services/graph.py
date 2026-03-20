
from __future__ import annotations
from typing import Dict, Any, List, Tuple
import time, json, math
from ..db.db import q, fetchall, fetchone

def node_id(user_id: str, device_id: str, epoch: int) -> str:
    return f"{user_id}:{device_id}:{epoch}"

def add_edge(conn, a: str, b: str, edge_type: str, weight: float, meta: Dict[str,Any]):
    now = int(time.time())
    q(conn, "INSERT INTO trust_edges(a_node,b_node,edge_type,weight,meta_json,created_at) VALUES(?,?,?,?,?,?)",
      (a,b,edge_type,weight,json.dumps(meta,ensure_ascii=False),now))
    conn.commit()

def infer_continuity(conn, old_node: str, new_node: str, score: float, reason: str):
    # add continuity edge with weight
    add_edge(conn, old_node, new_node, "continuity", score, {"reason": reason})

def infer_cohab(conn, nodes: List[str], score: float, context: str):
    # simple pairwise links
    for i in range(len(nodes)):
        for j in range(i+1,len(nodes)):
            add_edge(conn, nodes[i], nodes[j], "cohab", score, {"context": context})

def infer_risk_cluster(conn, nodes: List[str], score: float, trigger: str):
    for i in range(len(nodes)):
        for j in range(i+1,len(nodes)):
            add_edge(conn, nodes[i], nodes[j], "risk", score, {"trigger": trigger})

def simple_clusters(conn):
    # create demo clusters based on tenant membership and recent "coercion" bursts
    # returns dict cluster_type -> list of node_ids
    # recent 1h events
    rows = fetchall(conn, "SELECT user_id,device_id,epoch,coercion,created_at,tenant_id FROM identity_events WHERE created_at > ?", (int(time.time())-3600,))
    nodes = [node_id(r["user_id"], r["device_id"], int(r["epoch"])) for r in rows]
    risk_nodes = [node_id(r["user_id"], r["device_id"], int(r["epoch"])) for r in rows if int(r["coercion"])==1]
    by_tenant={}
    for r in rows:
        by_tenant.setdefault(r["tenant_id"], []).append(node_id(r["user_id"], r["device_id"], int(r["epoch"])))
    return {"work": {k:list(dict.fromkeys(v)) for k,v in by_tenant.items()},
            "attack": list(dict.fromkeys(risk_nodes))}
