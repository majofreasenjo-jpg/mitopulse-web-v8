
def detect(nodes):
    return [n for n in nodes if n.get("score",0)>100]
