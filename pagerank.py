import json
file = 'linkto.json'
fp = open(file, 'r')
inlink_map = json.load(fp)

file = 'outlink.json'
fp = open(file, 'r')
outlink_counts = json.load(fp)

def pagerank(inlink_map, outlink_counts, damping=0.85, epsilon=1.0e-4):
    all_nodes = set(inlink_map.keys())
    for node, outlink_count in outlink_counts.items():
        if outlink_count == 0:
            outlink_counts[node] = len(all_nodes)
            for l_node in all_nodes: inlink_map[l_node].add(node)

    initial_value = 0.15
    ranks = {}
    for node in inlink_map.keys(): ranks[node] = initial_value

    new_ranks = {}
    delta = 1.0
    n_iterations = 0
    # you can use iterations or delta to converge
    while n_iterations < 2:
    #while delta > epsilon:
        new_ranks = {}
        for node, inlinks in inlink_map.items():
            try:
                new_ranks[node] = (1 - damping) + (damping * sum(ranks[inlink] / outlink_counts[inlink] for inlink in inlinks))
            except:
                new_ranks[node] = 1 - damping
        delta = sum(abs(new_ranks[node] - ranks[node]) for node in new_ranks.keys())
        ranks, new_ranks = new_ranks, ranks
        n_iterations += 1 #iterations converge
    return ranks
    
pagerank(inlink_map, outlink_counts)
