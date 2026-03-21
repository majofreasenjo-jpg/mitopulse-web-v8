
from mitopulse_impact.engine.impact import loss_prevented, roi, efficiency_gain
from mitopulse_impact.engine.report import build_executive_report

def main():
    events = [
        {"amount": 100000, "probability": 0.8},
        {"amount": 50000, "probability": 0.6}
    ]

    saved = loss_prevented(events)
    roi_val = roi(saved, 20000)
    eff = efficiency_gain(200000, 50000)

    report = build_executive_report(saved, roi_val, eff)

    print(report)

if __name__ == "__main__":
    main()
