
class GuardianSwarm:

    def validate(self, alerts):
        validated = []
        for a in alerts:
            if a.get("score",0) > 0.5:
                a["validated"] = True
                validated.append(a)
        return validated
