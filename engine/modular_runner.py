from __future__ import annotations
from pathlib import Path
import json
import yaml
from engine.graph_builder import build_graph
from ingestion.client_data_loader import load_client_folder, dataset_profile
from engine.core_engines import (
    relational_identity_score, cross_pulse_pairs, danger_signal_score, trust_propagation_score,
    relational_gravity, shadow_coordination, morphogenesis_signature, system_indices,
    pre_contact_risk, decision_from_risk, entropy_analysis, criticality_score
)

BASE_DIR = Path(__file__).resolve().parents[1]

LAYER_COLORS = {
    'identity': '#3B82F6',
    'interaction': '#2563EB',
    'propagation': '#38BDF8',
    'collective': '#22C55E',
    'physics': '#8B5CF6',
    'dynamics': '#F97316',
    'learning': '#EAB308',
    'defense': '#EF4444',
    'simulation': '#94A3B8',
    'future': '#FFFFFF',
}

GRAPH_COLORS = {
    'stable': '#22C55E',
    'anomaly': '#EAB308',
    'high_risk': '#EF4444',
    'hidden': '#8B5CF6',
    'guardian': '#38BDF8',
    'neutral': '#CBD5E1',
    'device': '#3B82F6',
}

RUNTIME_MAP = {
    'real_time_ms': ['Relational Identity', 'Pulse', 'Cross-Pulse', 'Danger Signals', 'Neural Response Layer', 'Pre-Contact Risk', 'Decision Engine'],
    'fast_seconds': ['Relational Wave Engine', 'Trust Propagation', 'Relational Gravity', 'Shadow Coordination Detection', 'Mass Distortion Index'],
    'deep_seconds': ['Relational Dark Matter Detection', 'Entropy Analysis', 'Criticality Engine', 'Climate Dynamics Engine', 'Vortex Formation Engine', 'NHI', 'TPI', 'SCR'],
    'simulation_batch': ['Ecosystem Simulation Engine', 'Financial Storm Simulator', 'Fraud Evolution Engine', 'Fraud Evolution Arena', 'Historical Scenario Lab']
}

MATH_CORE = {
    'Pulse': 'P_i(t) = Σ ω_k e_ik(t)',
    'CrossPulse': 'CP_ij(t) = Corr(P_i(t), P_j(t))',
    'DangerSignals': 'DS_i(t) = |P_i(t) - P̂_i(t)|',
    'RelationalWave': 'RW_i(t) = Σ_j I_ij e^(-d_ij/λ) DS_j(t)',
    'RelationalGravity': 'RG_i = Σ_j (M_j · T_j)/(d_ij^2 + ε)',
    'DarkMatterResidual': 'DMR_i = ObsInfluence_i - ExpInfluence_i',
    'MDI': 'MDI_i = (ObsInfluence_i - ExpInfluence_i)/(σ_G + ε)',
    'Entropy': 'H(t) = -Σ p_i log p_i',
    'NHI': 'NHI = w1 T̄ - w2 R̄ - w3 H - w4 Fragility',
    'TPI': 'TPI = u1 DS̄ + u2 SCS̄ + u3 MDĪ + u4 ContagionRate',
    'SCR': 'SCR = g(NHI, TPI, H, Crit, Pressure, VFE)',
    'Decision': 'RiskScore = κ1 PCR + κ2 TPI + κ3 SCR + κ4 LocalSignal',
}

DEMO_KILLERS = {
    'invisible_storm': {
        'title': 'The Invisible Storm',
        'subtitle': 'Pequeñas anomalías evolucionan en una tormenta relacional antes del colapso.',
        'focus': ['Relational Wave Engine', 'Contagion Dynamics Engine', 'Climate Dynamics Engine', 'Financial Storm Simulator'],
        'acts': [
            'Mercado aparentemente estable',
            'Señales débiles y aumento de MDI',
            'Formación de onda relacional y presión sistémica',
            'Simulación de cascada y contención adaptativa',
        ],
        'kpis': {'NHI': 61, 'TPI': 42, 'SCR': 82},
    },
    'invisible_network': {
        'title': 'The Invisible Network',
        'subtitle': 'Una red coordinada aparece donde no existen enlaces visibles.',
        'focus': ['Relational Gravity', 'Relational Dark Matter Detection', 'Mass Distortion Index', 'Shadow Coordination Detection'],
        'acts': [
            'Grafo aparentemente normal',
            'Sincronías débiles entre cuentas',
            'Distorsión gravitacional y enlaces inferidos',
            'Cluster oculto revelado y contenido',
        ],
        'kpis': {'NHI': 74, 'TPI': 31, 'SCR': 14},
    },
    'coming_collapse': {
        'title': 'The Coming Collapse',
        'subtitle': 'Anticipación de tipping points y crisis sistémica antes de que el mercado la vea.',
        'focus': ['Entropy Analysis', 'Climate Dynamics Engine', 'Vortex Formation Engine', 'Criticality Engine', 'Financial Storm Simulator'],
        'acts': [
            'Sistema estable',
            'Acumulación de presión invisible',
            'Formación de vórtice y criticalidad',
            'Simulación del colapso y acción defensiva',
        ],
        'kpis': {'NHI': 52, 'TPI': 51, 'SCR': 91},
    }
}


def load_profile(profile_name: str) -> dict:
    path = BASE_DIR / 'profiles' / f'{profile_name}.yaml'
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def list_profiles_meta() -> list[dict]:
    out = []
    for path in sorted((BASE_DIR / 'profiles').glob('*.yaml')):
        cfg = yaml.safe_load(path.read_text(encoding='utf-8'))
        out.append({'name': path.stem, 'industry': cfg.get('industry'), 'size': cfg.get('size'), 'mode': cfg.get('mode'), 'scenario': cfg.get('scenario')})
    return out


def list_historical_meta() -> list[dict]:
    out = []
    for path in sorted((BASE_DIR / 'historical').glob('*.json')):
        j = json.loads(path.read_text(encoding='utf-8'))
        out.append({'name': path.stem, 'title': j.get('title', path.stem)})
    return out


def list_demo_killers() -> list[dict]:
    return [{'name': k, **v} for k, v in DEMO_KILLERS.items()]


def load_historical_scenario(name: str) -> dict:
    path = BASE_DIR / 'historical' / f'{name}.json'
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def top_node_scores(G, events_df, limit: int = 14):
    rows = []
    for node, attrs in list(G.nodes(data=True))[:60]:
        if attrs.get('node_type') != 'customer':
            continue
        ri = relational_identity_score(G, node)
        ds = danger_signal_score(G, node)
        tp = trust_propagation_score(G, node)
        rg = relational_gravity(G, node)
        mdi = round(max(0.0, (rg * (1 + ds) - tp) / 2.5), 3)
        rows.append({'node': node, 'relational_identity': ri, 'danger': ds, 'trust_risk': tp, 'gravity': rg, 'MDI': mdi})
    rows.sort(key=lambda x: (x['danger'], x['gravity'], x['MDI']), reverse=True)
    return rows[:limit]


def graph_payload(G, top_nodes, shadow_pairs):
    risk_map = {r['node']: r for r in top_nodes}
    nodes = []
    for i, (node, attrs) in enumerate(list(G.nodes(data=True))[:220]):
        r = risk_map.get(node, {})
        danger = float(r.get('danger', 0.0))
        if attrs.get('node_type') == 'device':
            color = GRAPH_COLORS['device']
            category = 'device'
        elif danger >= 0.72:
            color = GRAPH_COLORS['high_risk']
            category = 'high_risk'
        elif danger >= 0.35:
            color = GRAPH_COLORS['anomaly']
            category = 'anomaly'
        else:
            color = GRAPH_COLORS['stable'] if attrs.get('node_type') == 'customer' else GRAPH_COLORS['neutral']
            category = attrs.get('node_type', 'neutral')
        nodes.append({
            'id': str(node),
            'label': str(node),
            'type': attrs.get('node_type', 'unknown'),
            'category': category,
            'color': color,
            'size': 10 + int(18 * min(1.0, float(r.get('gravity', 0.0)) / 3.0)),
            'danger': danger,
            'gravity': float(r.get('gravity', 0.0)),
            'mdi': float(r.get('MDI', 0.0)),
        })
    visible_ids = {n['id'] for n in nodes}
    edges = []
    for u, v, attrs in list(G.edges(data=True))[:360]:
        if str(u) in visible_ids and str(v) in visible_ids:
            edges.append({
                'source': str(u), 'target': str(v), 'label': attrs.get('edge_type', 'link'),
                'weight': float(attrs.get('weight', 0.2)), 'color': '#64748B', 'dashed': False
            })
    hidden_nodes = []
    for idx, sp in enumerate(shadow_pairs[:8]):
        hidden_id = f'HIDDEN_{idx+1}'
        hidden_nodes.append({'id': hidden_id, 'label': hidden_id, 'type': 'hidden', 'category': 'hidden', 'color': GRAPH_COLORS['hidden'], 'size': 16, 'danger': sp['score'], 'gravity': sp['score'] * 2, 'mdi': sp['pattern']})
        if sp['a'] in visible_ids:
            edges.append({'source': hidden_id, 'target': sp['a'], 'label': 'inferred', 'weight': 1.0, 'color': GRAPH_COLORS['hidden'], 'dashed': True})
        if sp['b'] in visible_ids:
            edges.append({'source': hidden_id, 'target': sp['b'], 'label': 'inferred', 'weight': 1.0, 'color': GRAPH_COLORS['hidden'], 'dashed': True})
    nodes.extend(hidden_nodes)
    return {'nodes': nodes, 'edges': edges, 'legend': GRAPH_COLORS}


def technical_metrics(events_df, shadow_pairs, top_nodes, system):
    mdi_avg = round(sum(n.get('MDI', 0.0) for n in top_nodes) / max(len(top_nodes), 1), 3)
    gravity_avg = round(sum(n.get('gravity', 0.0) for n in top_nodes) / max(len(top_nodes), 1), 3)
    shadow_avg = round(sum(x.get('score', 0.0) for x in shadow_pairs) / max(len(shadow_pairs), 1), 3)
    return {
        'MDI_avg': mdi_avg,
        'gravity_avg': gravity_avg,
        'shadow_avg': shadow_avg,
        'entropy': system['entropy'],
        'criticality': system['criticality'],
        'wave_amplitude': round(min(1.0, shadow_avg * 0.75 + gravity_avg * 0.08), 3),
        'contagion_rate': round(min(1.0, system['TPI'] / 100.0 + shadow_avg * 0.25), 3),
        'climate_pressure': round(min(100.0, system['TPI'] * 0.55 + system['SCR'] * 0.45), 2),
        'vortex_score': round(min(1.0, shadow_avg * 0.35 + system['criticality'] * 0.45 + mdi_avg * 0.15), 3),
    }


def run_live_profile(profile_name: str) -> dict:
    import time
    t0 = time.time()
    profile = load_profile(profile_name)
    ds_path = BASE_DIR / profile['dataset']
    t1 = time.time()
    customers, devices, events, signals = load_client_folder(str(ds_path))
    t2 = time.time()
    G = build_graph(customers, devices, events, signals)
    t3 = time.time()
    dp = dataset_profile(customers, devices, events, signals)
    t4 = time.time()

    cpairs = cross_pulse_pairs(events)
    t5 = time.time()
    shadow = shadow_coordination(events, G)
    t6 = time.time()
    top_nodes = top_node_scores(G, events)
    t7 = time.time()
    morph = morphogenesis_signature(events)
    t8 = time.time()
    system = system_indices(G, events, shadow, top_nodes)
    t9 = time.time()
    tech = technical_metrics(events, shadow, top_nodes, system)
    t10 = time.time()

    cluster_pattern = max([x['pattern'] for x in shadow], default=0.0)
    if top_nodes:
        top_nodes = [
            {**n, 'PCR': pre_contact_risk(n, system, cluster_pattern), 'decision': decision_from_risk(pre_contact_risk(n, system, cluster_pattern))}
            for n in top_nodes
        ]

    active_modules = [k for k, v in profile.get('modules', {}).items() if v]
    storyline = [
        'La red metaboliza datos y construye identidad relacional.',
        'Pulse y Cross-Pulse detectan sincronía y señales débiles.',
        'Neural Response prioriza eventos y activa ondas relacionales.',
        'Relational Gravity y MDI revelan distorsiones estructurales.',
        'Shadow Coordination y Dark Matter infieren redes invisibles.',
        'NHI, TPI y SCR resumen la salud y la presión del ecosistema.',
        'Pre-Contact Risk y Decision Engine emiten la acción preventiva.',
    ]

    return {
        'kind': 'profile',
        'debug_timings': {
            'load_yaml': round(t1 - t0, 3),
            'load_csv': round(t2 - t1, 3),
            'build_graph': round(t3 - t2, 3),
            'dataset_profile': round(t4 - t3, 3),
            'cross_pulse': round(t5 - t4, 3),
            'shadow': round(t6 - t5, 3),
            'top_nodes': round(t7 - t6, 3),
            'morph': round(t8 - t7, 3),
            'system_indices': round(t9 - t8, 3),
            'tech': round(t10 - t9, 3)
        },
        'profile': profile,
        'dataset_profile': dp,
        'graph_stats': {'nodes': G.number_of_nodes(), 'edges': G.number_of_edges()},
        'active_modules': active_modules,
        'top_nodes': top_nodes,
        'cross_pulse_pairs': cpairs,
        'shadow_pairs': shadow,
        'morphogenesis': morph,
        'system_indices': system,
        'technical_metrics': tech,
        'runtime_map': RUNTIME_MAP,
        'math_core': MATH_CORE,
        'storyline': storyline,
        'graph': graph_payload(G, top_nodes, shadow),
        'colors': {'layers': LAYER_COLORS, 'graph': GRAPH_COLORS},
    }


def run_historical(name: str) -> dict:
    scenario = load_historical_scenario(name)
    return {
        'kind': 'historical',
        'scenario': scenario,
        'active_modules': scenario.get('modules', []),
        'storyline': scenario.get('storyline', []),
        'windows': scenario.get('windows', []),
        'conclusion': scenario.get('conclusion', ''),
        'colors': {'layers': LAYER_COLORS, 'graph': GRAPH_COLORS},
    }


def run_demo_killer(demo_name: str) -> dict:
    if demo_name not in DEMO_KILLERS:
        return {'error': 'demo not found'}
    d = DEMO_KILLERS[demo_name]
    return {'kind': 'demo', 'name': demo_name, **d, 'colors': {'layers': LAYER_COLORS, 'graph': GRAPH_COLORS}}
