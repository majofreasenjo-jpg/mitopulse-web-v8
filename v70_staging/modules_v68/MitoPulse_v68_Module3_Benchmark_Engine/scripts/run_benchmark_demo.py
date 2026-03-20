from mitopulse_benchmark.engine.metrics import lead_time, precision, false_rates, loss_prevented
from mitopulse_benchmark.engine.sai import compute_sai
from mitopulse_benchmark.engine.report import build_report

def main():
    mito_ts = 100
    baseline_ts = 120

    tp, fp, fn, total = 80, 20, 10, 100

    events = [
        {"amount": 10000, "probability": 0.8},
        {"amount": 5000, "probability": 0.6}
    ]

    lt = lead_time(mito_ts, baseline_ts)
    prec = precision(tp, fp)
    fr = false_rates(fp, fn, total)
    loss = loss_prevented(events)

    sai = compute_sai(lt, prec, loss)

    report = build_report({
        "lead_time": lt,
        "precision": prec,
        "fpr": fr["fpr"],
        "fnr": fr["fnr"],
        "loss_prevented": loss,
        "sai": sai
    })

    print(report)

if __name__ == "__main__":
    main()
