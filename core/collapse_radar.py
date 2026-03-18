
def probability(nodes):
    avg = sum([n.get("score",0) for n in nodes])/len(nodes)
    return min(1, avg/150)
