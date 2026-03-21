
from mitopulse_trust.engine.trust_score import compute_trust

def test_trust():
    assert compute_trust(0.9,0.9) > 0.8
