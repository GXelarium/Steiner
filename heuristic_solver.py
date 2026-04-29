# heuristic_solver.py
import networkx as nx
import time

def steiner_tree_mst_heuristic(graph_nx_orig: nx.Graph, terminals_heur):
    start_time_heur = time.time()

    if not terminals_heur or len(terminals_heur) < 2:
        return 0, [], time.time() - start_time_heur

    # Validar que los terminales estén en el grafo
    valid_terminals = [t for t in terminals_heur if graph_nx_orig.has_node(t)]
    if len(valid_terminals) < len(terminals_heur):
        pass
    if len(valid_terminals) < 2:
        return 0, [], time.time() - start_time_heur
    
    terminals_to_use = valid_terminals

    H = nx.Graph()
    paths_in_G = {}
    for i in range(len(terminals_to_use)):
        for j in range(i + 1, len(terminals_to_use)):
            t1, t2 = terminals_to_use[i], terminals_to_use[j]
            try:
                length = nx.shortest_path_length(graph_nx_orig, source=t1, target=t2, weight='weight')
                path = nx.shortest_path(graph_nx_orig, source=t1, target=t2, weight='weight')
                H.add_edge(t1, t2, weight=length)
                paths_in_G[(min(t1,t2), max(t1,t2))] = path
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                return None, [], time.time() - start_time_heur
    
    if H.number_of_nodes() == 0 or (H.number_of_edges() == 0 and len(terminals_to_use) > 1) :
        if len(terminals_to_use) == 1: return 0, [], time.time() - start_time_heur
        return None, [], time.time() - start_time_heur

    mst_H = nx.minimum_spanning_tree(H, weight='weight')
    steiner_graph_edges_set = set()
    for u_h, v_h, _ in mst_H.edges(data=True):
        path_key = (min(u_h,v_h), max(u_h,v_h))
        if path_key not in paths_in_G: continue
        path_uv = paths_in_G[path_key]
        for i_path in range(len(path_uv) - 1):
            node1, node2 = path_uv[i_path], path_uv[i_path+1]
            if graph_nx_orig.has_edge(node1, node2) and 'weight' in graph_nx_orig[node1][node2]:
                original_weight = graph_nx_orig[node1][node2]['weight']
                edge_tuple = tuple(sorted((node1, node2))) + (original_weight,)
                steiner_graph_edges_set.add(edge_tuple)

    S_union = nx.Graph()
    for u_s, v_s, w_s in steiner_graph_edges_set:
        S_union.add_edge(u_s, v_s, weight=w_s)

    if not S_union.nodes:
        return (0, [], time.time() - start_time_heur) if len(terminals_to_use) <=1 else (None, [], time.time() - start_time_heur)

    final_tree_candidate = nx.minimum_spanning_tree(S_union, weight='weight')
    
    # Bucle de poda mejorado
    current_tree_nodes = set(final_tree_candidate.nodes())
    terminals_set = set(terminals_to_use)
    
    while True:
        hojas_a_podar = [
            node for node, degree in final_tree_candidate.degree()
            if degree == 1 and node in current_tree_nodes and node not in terminals_set
        ]
        if not hojas_a_podar: break
        for hoja in hojas_a_podar:
            if final_tree_candidate.has_node(hoja): 
                final_tree_candidate.remove_node(hoja)
                current_tree_nodes.remove(hoja) # Actualizar el conjunto de nodos


    aristas_finales = []
    costo_final = 0
    for u, v, data in final_tree_candidate.edges(data=True):
        aristas_finales.append((u, v, data['weight']))
        costo_final += data['weight']
    
    duration = time.time() - start_time_heur
    return costo_final, aristas_finales, duration