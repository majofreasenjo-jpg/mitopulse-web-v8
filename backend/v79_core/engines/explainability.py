from __future__ import annotations

class ExplainabilityEngine:
    def summarize(self, state, drivers):
        mapping = {
            "coherent": "El sistema conserva identidad, homeostasis y continuidad operacional.",
            "stressed": "Aumenta la presión activa; todavía hay margen, pero la deriva ya es medible.",
            "compensating": "El sistema absorbe perturbaciones, pero gasta reservas adaptativas.",
            "degraded-but-viable": "La coherencia cae y la homeostasis se vuelve costosa, aunque persiste la viabilidad.",
            "near-fracture": "La acumulación de tensión y propagación sitúa al sistema cerca de ruptura sistémica.",
            "reconstituting": "El sistema entra en fase de reconstitución tras degradación severa."
        }
        base = mapping.get(state, "Estado sistémico no definido.")
        if drivers:
            return base + " Drivers principales: " + ", ".join(drivers[:3]) + "."
        return base
