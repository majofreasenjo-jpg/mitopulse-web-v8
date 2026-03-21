
from mitopulse_impact.engine.impact import roi

def test_roi():
    assert roi(200,100) == 1.0
