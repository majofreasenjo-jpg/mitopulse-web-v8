
def compute(nodes):
    return [{"id":n["id"],"score":n.get("value",0)*1.5} for n in nodes]
