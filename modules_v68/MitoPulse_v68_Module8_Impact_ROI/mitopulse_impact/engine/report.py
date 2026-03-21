
def build_executive_report(saved, roi, efficiency):
    return {
        "saved_usd": round(saved,2),
        "roi": round(roi,4),
        "efficiency_gain": round(efficiency,4),
        "summary": f"MitoPulse evitó ${round(saved,2)} con ROI {round(roi,2)}"
    }
