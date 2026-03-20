class GuardianSwarm:
    def validate(self, alerts):
        validated = []
        for a in alerts:
            score = float(a.get("score", 0) or 0)
            if score >= 50:
                a["guardian_validated"] = True
                validated.append(a)
        return validated
