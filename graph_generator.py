# graph_generator.py
import random
import networkx as nx

def generate_random_steiner_graph(num_nodes_target, m_barabasi_param, min_weight, max_weight, num_terminals_requested):
    if num_nodes_target <= 0:
        return 0, [], [], nx.Graph()

    G = nx.Graph()

    if num_nodes_target == 1:
        G.add_node(0)
    else:
        actual_m = max(1, min(m_barabasi_param, num_nodes_target - 1))
        try:
            G = nx.barabasi_albert_graph(num_nodes_target, actual_m, seed=None)
        except nx.NetworkXError as e:
            if num_nodes_target > 1:
                G = nx.barabasi_albert_graph(num_nodes_target, 1, seed=None)
            else:
                 G.add_node(0)

    random_edges_list = []
    for u, v in G.edges():
        weight = random.randint(min_weight, max_weight)
        G.edges[u,v]['weight'] = weight
        random_edges_list.append((u, v, weight))
    
    current_nodes = list(G.nodes())
    actual_num_nodes = G.number_of_nodes()

    final_num_terminals = num_terminals_requested
    if num_terminals_requested > actual_num_nodes:
        if actual_num_nodes > 0:
            final_num_terminals = actual_num_nodes
        else:
            final_num_terminals = 0
            
    terminals_list = []
    if actual_num_nodes > 0 and final_num_terminals > 0:
        try:
            terminals_list = random.sample(current_nodes, final_num_terminals)
        except ValueError: # Si final_num_terminals > len(current_nodes), que no debería pasar por el ajuste
            terminals_list = current_nodes 
            
    elif actual_num_nodes == 0 and final_num_terminals > 0:
        pass 
        
    return actual_num_nodes, random_edges_list, terminals_list, G