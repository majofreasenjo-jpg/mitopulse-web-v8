from pathlib import Path
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from engine.modular_runner import run_live_profile, run_historical, list_profiles_meta, list_historical_meta, list_demo_killers, run_demo_killer
from ingestion.client_data_loader import save_uploaded_file
from api.live_service import list_live_configs, run_live_config
from core.fraud_detection_engine import FraudDetectionEngine
from core.systemic_collapse_predictor import SystemicCollapsePredictor
from core.rfdc import RelationalFieldDynamicsCore
from core.rfdc_visualizer import build_graph_payload, build_demo_story

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


@app.get('/api/rfdc/graph')
def rfdc_graph():
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
    graph = build_graph_payload(events, result)
    graph['dataset'] = str(target)
    return graph

@app.get('/api/demo/run/{demo_id}')
def demo_run(demo_id: str):
    import pandas as pd
    from pathlib import Path

    candidate_dirs = [
        Path('data/bank_medium_realistic_v1'),
        Path('data/afp_systemic_realistic_v1'),
        Path('live_output/yahoo_live_market'),
        Path('live_output/binance_live_crypto'),
    ]
    target = next((p for p in candidate_dirs if p.exists()), None)
    if target is None:
        return {'error': 'no dataset found for demo execution'}

    events_fp = target / 'events.csv'
    signals_fp = target / 'signals.csv'
    if not events_fp.exists():
        return {'error': f'events.csv not found in {target}'}

    events = pd.read_csv(events_fp)
    signals = pd.read_csv(signals_fp) if signals_fp.exists() else pd.DataFrame(columns=['entity_id','signal_type','severity','source','timestamp'])

    engine = RelationalFieldDynamicsCore()
    result = engine.run(events, signals)
    story = build_demo_story(demo_id, result)
    graph = build_graph_payload(events, result)
    return {
        'demo_id': demo_id,
        'dataset': str(target),
        'story': story,
        'graph': graph,
        'result': result
    }


@app.get('/api/simulation/playback')
def simulation_playback():
    import pandas as pd
    from pathlib import Path
    from core.simulation_playback import SimulationPlayback

    candidate_dirs = [
        Path('live_output/yahoo_live_market'),
        Path('live_output/binance_live_crypto'),
        Path('data/bank_medium_realistic_v1'),
        Path('data/afp_systemic_realistic_v1'),
    ]
    target = next((p for p in candidate_dirs if p.exists()), None)
    if target is None:
        return {'error': 'no dataset found for playback'}

    events_fp = target / 'events.csv'
    if not events_fp.exists():
        return {'error': f'events.csv not found in {target}'}

    events = pd.read_csv(events_fp)
    engine = SimulationPlayback()
    steps = engine.run_steps(events)
    return {"dataset": str(target), "steps": steps}
