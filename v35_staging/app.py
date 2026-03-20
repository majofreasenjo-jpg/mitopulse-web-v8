
import json
from core.rfdc_core import compute
from core.vortex_engine import detect
from core.collapse_radar import probability

with open('datasets/sample_market.json') as f:
    data = json.load(f)

nodes = compute(data)
vortex = detect(nodes)
scr = probability(nodes)

print("=== MITOPULSE v35 ===")
print("Nodes:", nodes)
print("Vortex:", vortex)
print("Collapse Probability:", scr)
