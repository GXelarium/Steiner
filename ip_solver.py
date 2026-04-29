# ip_solver.py
import pulp
import time # Usar time directamente

def steiner_tree_ip(num_nodes_ip, edges_ip, terminals_ip):
    start_time_ip = time.time()
    prob = pulp.LpProblem("SteinerTree_MCF", pulp.LpMinimize)

    edge_vars = {} 
    edge_map_for_flow = {} 

    for u, v, w in edges_ip:
        u_key, v_key = min(u, v), max(u, v)
        if (u_key, v_key) not in edge_vars:
            edge_vars[(u_key, v_key)] = pulp.LpVariable(f"x_{u_key}_{v_key}", 0, 1, pulp.LpBinary)
        edge_map_for_flow[(u,v)] = (u_key, v_key)
        edge_map_for_flow[(v,u)] = (u_key, v_key)

    objective_terms = []
    temp_added_to_obj = set()
    for u, v, w in edges_ip:
        u_key, v_key = min(u,v), max(u,v)
        if (u_key, v_key) not in temp_added_to_obj:
            objective_terms.append(w * edge_vars[(u_key, v_key)])
            temp_added_to_obj.add((u_key, v_key))
    
    if objective_terms:
        prob += pulp.lpSum(objective_terms), "Total_Steiner_Weight"
    else:
        prob += 0, "Total_Steiner_Weight"

    if terminals_ip and len(terminals_ip) >= 2:
        root_terminal = terminals_ip[0]
        commodities = terminals_ip[1:]

        # Crear un diccionario para adjacencias solo con nodos que realmente existen
        adj = {i: [] for i in range(num_nodes_ip)}
        existing_nodes_in_edges = set()
        for u, v, _ in edges_ip:
            adj[u].append(v)
            adj[v].append(u)
            existing_nodes_in_edges.add(u)
            existing_nodes_in_edges.add(v)

        # Solo definir variables de flujo para nodos que existen en el grafo y aristas
        flow_vars_dict = {}
        for comm_idx, _ in enumerate(commodities):
            for u_node in range(num_nodes_ip):
                for v_node in range(num_nodes_ip):
                    # Solo crear variable si la arista u-v (o v-u) existe
                    u_key_flow, v_key_flow = min(u_node, v_node), max(u_node, v_node)
                    if (u_key_flow, v_key_flow) in edge_vars:
                         flow_vars_dict[(comm_idx, u_node, v_node)] = pulp.LpVariable(f"flow_{comm_idx}_{u_node}_{v_node}", lowBound=0)


        for comm_idx, dest_terminal in enumerate(commodities):
            for u_orig, v_orig, _ in edges_ip:
                edge_key = edge_map_for_flow[(u_orig, v_orig)]
                if edge_key in edge_vars:
                    if (comm_idx, u_orig, v_orig) in flow_vars_dict:
                        prob += flow_vars_dict[(comm_idx, u_orig, v_orig)] <= edge_vars[edge_key], f"cap_{comm_idx}_{u_orig}_{v_orig}"
                    if (comm_idx, v_orig, u_orig) in flow_vars_dict:
                        prob += flow_vars_dict[(comm_idx, v_orig, u_orig)] <= edge_vars[edge_key], f"cap_{comm_idx}_{v_orig}_{u_orig}"

            for n in range(num_nodes_ip):
                # Solo considerar nodos que están en el grafo (tienen aristas o son terminales)
                # o, más simple, si un nodo no tiene vecinos en adj, las sumas serán 0.
                outflow = pulp.lpSum(flow_vars_dict.get((comm_idx, n, neighbor), 0) for neighbor in adj.get(n, []))
                inflow = pulp.lpSum(flow_vars_dict.get((comm_idx, neighbor, n), 0) for neighbor in adj.get(n, []))
                
                supply = 0
                if n == root_terminal: supply = 1
                elif n == dest_terminal: supply = -1
                prob += outflow - inflow == supply, f"flow_balance_{comm_idx}_{n}"
    
    try:
        prob.solve(pulp.PULP_CBC_CMD(msg=0))
    except Exception as e:
        print(f"Error al resolver con PuLP (MCF): {e}")
        return None, [], time.time() - start_time_ip

    duration = time.time() - start_time_ip

    if pulp.LpStatus[prob.status] == "Optimal":
        costo_total = pulp.value(prob.objective) if prob.objective is not None else 0
        aristas_seleccionadas = []
        if edge_vars:
            for u_orig, v_orig, w_orig in edges_ip:
                u_key, v_key = min(u_orig, v_orig), max(u_orig, v_orig)
                if (u_key,v_key) in edge_vars and edge_vars[(u_key, v_key)].varValue is not None and edge_vars[(u_key, v_key)].varValue > 0.9:
                    aristas_seleccionadas.append((u_orig, v_orig, w_orig))
        elif not terminals_ip or len(terminals_ip) < 2:
            costo_total = 0
        return costo_total, aristas_seleccionadas, duration
    else:
        # print(f"IP (MCF): No se encontró solución óptima. Estado: {pulp.LpStatus[prob.status]}")
        return None, [], duration