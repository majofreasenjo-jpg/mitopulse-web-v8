from pathlib import Path
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from engine.modular_runner import run_live_profile, run_historical, list_profiles_meta, list_historical_meta, list_demo_killers, run_demo_killer
from ingestion.client_data_loader import save_uploaded_file
from api.live_service import list_live_configs, run_live_config
from core.fraud_detection_engine import FraudDetectionEngine
from core.systemic_collapse_predictor import SystemicCollapsePredictor
from core.fraud_evolution_engine import FraudEvolutionEngine
from core.guardian_swarm import GuardianSwarm
from core.relational_dark_matter import RelationalDarkMatter
from core.relational_wave_engine import RelationalWaveEngine
from core.rfdc import RelationalFieldDynamicsCore

BASE_DIR = Path(__file__).resolve().parents[1]
app = FastAPI(title="MitoPulse Final Modular Prototype v13")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "profiles": list_profiles_meta(),
            "historical": list_historical_meta(),
            "demos": list_demo_killers(),
        },
    )

@app.get("/verify", response_class=HTMLResponse)
def verify_challenge(request: Request):
    return templates.TemplateResponse("verify.html", {"request": request})

@app.get('/api/options')
def options():
    return {
        'profiles': list_profiles_meta(),
        'historical': list_historical_meta(),
        'demos': list_demo_killers(),
    }

@app.get("/api/profile/{profile_name}")
def profile(profile_name: str):
    return run_live_profile(profile_name)

@app.get("/api/historical/{scenario_name}")
def historical(scenario_name: str):
    return run_historical(scenario_name)

@app.get("/api/demo/{demo_name}")
def demo(demo_name: str):
    return run_demo_killer(demo_name)

@app.post('/api/upload')
async def upload(file: UploadFile = File(...)):
    return await save_uploaded_file(BASE_DIR / 'uploads', file)

@app.get('/api/live/options')
def live_options():
    return {'connectors': list_live_configs()}

@app.post('/api/live/run/{config_name}')
def live_run(config_name: str):
    return run_live_config(config_name)

@app.get('/api/detection/run')
def detection_run():
    import pandas as pd
    from pathlib import Path

    candidate_dirs = [
        Path('live_output/yahoo_live_market'),
        Path('live_output/binance_live_crypto'),
        Path('data/bank_medium_realistic_v1'),
        Path('data/afp_systemic_realistic_v1'),
    ]
    target = next((p for p in candidate_dirs if p.exists()), None)
    if target is None:
        return {'error': 'no dataset found in live_output or mapped data folders'}

    events_fp = target / 'events.csv'
    signals_fp = target / 'signals.csv'
    if not events_fp.exists():
        return {'error': f'events.csv not found in {target}'}

    events = pd.read_csv(events_fp)
    signals = pd.read_csv(signals_fp) if signals_fp.exists() else pd.DataFrame(columns=['entity_id','signal_type','severity','source','timestamp'])

    engine = FraudDetectionEngine()
    results = engine.detect(events, signals)
    return {
        'dataset': str(target),
        'count': int(len(results)),
        'alerts': results.to_dict(orient='records')
    }

@app.get('/api/systemic/run')
def systemic_run():
    import pandas as pd
    from pathlib import Path

    candidate_dirs = [
        Path('live_output/yahoo_live_market'),
        Path('live_output/binance_live_crypto'),
        Path('data/afp_systemic_realistic_v1'),
        Path('data/bank_medium_realistic_v1'),
    ]
    target = next((p for p in candidate_dirs if p.exists()), None)
    if target is None:
        return {'error': 'no dataset found in live_output or mapped data folders'}

    events_fp = target / 'events.csv'
    signals_fp = target / 'signals.csv'
    if not events_fp.exists():
        return {'error': f'events.csv not found in {target}'}

    events = pd.read_csv(events_fp)
    signals = pd.read_csv(signals_fp) if signals_fp.exists() else pd.DataFrame(columns=['entity_id','signal_type','severity','source','timestamp'])

    engine = SystemicCollapsePredictor()
    metrics = engine.run(events, signals)
    return {
        'dataset': str(target),
        'metrics': metrics
    }

@app.get('/api/rfdc/run')
def rfdc_run():
    import pandas as pd
    from pathlib import Path

    candidate_dirs = [
        Path('live_output/yahoo_live_market'),
        Path('live_output/binance_live_crypto'),
        Path('data/afp_systemic_realistic_v1'),
        Path('data/bank_medium_realistic_v1'),
    ]
    target = next((p for p in candidate_dirs if p.exists()), None)
    if target is None:
        return {'error': 'no dataset found in live_output or mapped data folders'}

    events_fp = target / 'events.csv'
    signals_fp = target / 'signals.csv'
    if not events_fp.exists():
        return {'error': f'events.csv not found in {target}'}

    events = pd.read_csv(events_fp)
    signals = pd.read_csv(signals_fp) if signals_fp.exists() else pd.DataFrame(columns=['entity_id','signal_type','severity','source','timestamp'])

    engine = RelationalFieldDynamicsCore()
    result = engine.run(events, signals)
    result['dataset'] = str(target)
    return result

@app.get('/api/v18/run')
def v18_run():
    import pandas as pd
    from pathlib import Path

    candidate_dirs = [
        Path('live_output/yahoo_live_market'),
        Path('live_output/binance_live_crypto'),
        Path('data/afp_systemic_realistic_v1'),
        Path('data/bank_medium_realistic_v1'),
    ]
    target = next((p for p in candidate_dirs if p.exists()), None)
    if target is None:
        return {'error': 'no dataset found in live_output or mapped data folders'}

    events_fp = target / 'events.csv'
    if not events_fp.exists():
        return {'error': f'events.csv not found in {target}'}

    events = pd.read_csv(events_fp)

    # V18 Engines
    rdm = RelationalDarkMatter()
    mdi = rdm.compute_mdi(events)
    clusters = rdm.detect_hidden_clusters(events)

    rwe = RelationalWaveEngine()
    waves = rwe.propagate(events)

    fee = FraudEvolutionEngine()
    p1 = fee.generate_pattern()
    p2 = fee.mutate_pattern(fee.generate_pattern())

    gs = GuardianSwarm()
    alerts_to_validate = [
        {"id": "A1", "score": 0.8},
        {"id": "A2", "score": 0.3},
        {"id": "A3", "score": 0.9}
    ]
    validated_alerts = gs.validate(alerts_to_validate)

    return {
        'dataset': str(target),
        'relational_dark_matter': {
            'mdi': mdi,
            'hidden_clusters_count': len(clusters)
        },
        'relational_wave_engine': {
            'waves_detected': len(waves)
        },
        'fraud_evolution_engine': {
            'generated_pattern': p1,
            'mutated_pattern': p2
        },
        'guardian_swarm': {
            'validated_alerts': validated_alerts
        }
    }
