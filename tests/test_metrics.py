from mitopulse_benchmark.engine.metrics import lead_time

def test_lead_time():
    assert lead_time(100, 120) == 20
