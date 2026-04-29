# ip_solver1.py
import pulp
import time # Usar time directamente

def steiner_tree_ip(num_nodes_ip, edges_ip, terminals_ip):
    """
    Resuelve el problema del Árbol de Steiner usando un modelo de Programación Entera (IP)
    con la formulación de Flujo Multi-Producto (MCF).

    Args:
        num_nodes_ip (int): Número total de nodos en el grafo.
        edges_ip (list): Lista de tuplas (u, v, w) que representan las aristas y sus pesos.
        terminals_ip (list): Lista de nodos terminales que deben ser conectados.

    Returns:
        tuple: Una tupla conteniendo (costo_total, aristas_seleccionadas, duracion).
               Retorna (None, [], duracion) si no se encuentra solución.
    """
    start_time_ip = time.time()
    
    # 1. Inicializar el problema de PuLP
    # Se define un problema de minimización llamado "SteinerTree_MCF".
    prob = pulp.LpProblem("SteinerTree_MCF", pulp.LpMinimize)

    # 2. Crear variables de decisión para las aristas
    # edge_vars: Diccionario para las variables binarias x_uv. Una por cada arista.
    # x_uv = 1 si la arista (u,v) se incluye en el árbol, 0 si no.
    # La clave (min(u,v), max(u,v)) asegura una única variable por arista no dirigida.
    edge_vars = {} 
    edge_map_for_flow = {} # Mapea aristas dirigidas (u,v) a su clave no dirigida (min,max)

    for u, v, w in edges_ip:
        u_key, v_key = min(u, v), max(u, v)
        if (u_key, v_key) not in edge_vars:
            edge_vars[(u_key, v_key)] = pulp.LpVariable(f"x_{u_key}_{v_key}", 0, 1, pulp.LpBinary)
        # Se guarda el mapeo para facilitar el acceso más tarde en las restricciones de flujo.
        edge_map_for_flow[(u,v)] = (u_key, v_key)
        edge_map_for_flow[(v,u)] = (u_key, v_key)

    # 3. Definir la función objetivo
    # Minimizar la suma ponderada de las aristas seleccionadas: sum(w_uv * x_uv)
    objective_terms = []
    temp_added_to_obj = set() # Para evitar añadir el costo de una misma arista dos veces
    for u, v, w in edges_ip:
        u_key, v_key = min(u,v), max(u,v)
        if (u_key, v_key) not in temp_added_to_obj:
            objective_terms.append(w * edge_vars[(u_key, v_key)])
            temp_added_to_obj.add((u_key, v_key))
    
    # Añadir la función objetivo al problema.
    if objective_terms:
        prob += pulp.lpSum(objective_terms), "Total_Steiner_Weight"
    else:
        prob += 0, "Total_Steiner_Weight" # Si no hay aristas, el costo es 0.

    # 4. Definir las restricciones de Flujo Multi-Producto (MCF)
    # Estas restricciones solo son necesarias si hay al menos 2 terminales.
    if terminals_ip and len(terminals_ip) >= 2:
        # Se elige el primer terminal como la "raíz" o fuente del flujo.
        root_terminal = terminals_ip[0]
        # Los demás terminales son los "destinos" o sumideros. Cada uno es un "producto" (commodity).
        commodities = terminals_ip[1:]

        # Crear una lista de adyacencia para construir las restricciones de flujo eficientemente.
        adj = {i: [] for i in range(num_nodes_ip)}
        for u, v, _ in edges_ip:
            adj[u].append(v)
            adj[v].append(u)

        # Crear variables de flujo: f^k_uv
        # flow_vars_dict[(k, u, v)] representa el flujo del producto k por la arista (u,v).
        flow_vars_dict = {}
        for comm_idx, _ in enumerate(commodities): # Para cada producto k
            for u_node in range(num_nodes_ip):
                for v_node in adj.get(u_node, []): # Para cada arista (u,v)
                    # Solo crear variables si la arista existe.
                    if (comm_idx, u_node, v_node) not in flow_vars_dict:
                         flow_vars_dict[(comm_idx, u_node, v_node)] = pulp.LpVariable(f"flow_{comm_idx}_{u_node}_{v_node}", lowBound=0)

        # Restricciones del modelo de flujo
        for comm_idx, dest_terminal in enumerate(commodities):
            # A. Restricción de capacidad: El flujo por una arista no puede exceder su capacidad,
            # que es 1 si la arista se selecciona (x_uv = 1) y 0 si no.
            # Esto enlaza las variables de flujo con las de decisión. f_uv <= x_uv
            for u_orig, v_orig, _ in edges_ip:
                edge_key = edge_map_for_flow[(u_orig, v_orig)]
                # Aplicar restricción para ambas direcciones del flujo en la arista.
                if (comm_idx, u_orig, v_orig) in flow_vars_dict:
                    prob += flow_vars_dict[(comm_idx, u_orig, v_orig)] <= edge_vars[edge_key], f"cap_{comm_idx}_{u_orig}_{v_orig}"
                if (comm_idx, v_orig, u_orig) in flow_vars_dict:
                    prob += flow_vars_dict[(comm_idx, v_orig, u_orig)] <= edge_vars[edge_key], f"cap_{comm_idx}_{v_orig}_{u_orig}"

            # B. Restricción de balance de flujo: Para cada nodo y cada producto.
            # Suma(flujos salientes) - Suma(flujos entrantes) = Suministro
            for n in range(num_nodes_ip):
                outflow = pulp.lpSum(flow_vars_dict.get((comm_idx, n, neighbor), 0) for neighbor in adj.get(n, []))
                inflow = pulp.lpSum(flow_vars_dict.get((comm_idx, neighbor, n), 0) for neighbor in adj.get(n, []))
                
                # Definir el suministro/demanda para cada nodo.
                supply = 0
                if n == root_terminal: supply = 1      # La raíz produce 1 unidad de flujo.
                elif n == dest_terminal: supply = -1   # El destino consume 1 unidad de flujo.
                
                prob += outflow - inflow == supply, f"flow_balance_{comm_idx}_{n}"
    
    # 5. Resolver el problema
    try:
        # Se llama al solver CBC (Coin-or Branch and Cut). msg=0 para suprimir mensajes del solver.
        prob.solve(pulp.PULP_CBC_CMD(msg=0))
    except Exception as e:
        print(f"Error al resolver con PuLP (MCF): {e}")
        return None, [], time.time() - start_time_ip

    duration = time.time() - start_time_ip

    # 6. Procesar y devolver los resultados
    # Comprobar si se encontró una solución óptima.
    if pulp.LpStatus[prob.status] == "Optimal":
        costo_total = pulp.value(prob.objective) if prob.objective is not None else 0
        
        # Recolectar las aristas que forman la solución (donde x_uv > 0.9, es decir, x_uv = 1).
        aristas_seleccionadas = []
        if edge_vars:
            # Usar un set para no duplicar aristas en la salida
            selected_keys = set()
            for u_orig, v_orig, w_orig in edges_ip:
                u_key, v_key = min(u_orig, v_orig), max(u_orig, v_orig)
                if (u_key, v_key) not in selected_keys:
                    if edge_vars[(u_key, v_key)].varValue is not None and edge_vars[(u_key, v_key)].varValue > 0.9:
                        aristas_seleccionadas.append((u_orig, v_orig, w_orig))
                        selected_keys.add((u_key, v_key))

        # Caso borde: si hay menos de 2 terminales, el costo es 0.
        elif not terminals_ip or len(terminals_ip) < 2:
            costo_total = 0
            
        return costo_total, aristas_seleccionadas, duration
    else:
        # Si el estado no es óptimo, se retorna un resultado vacío.
        return None, [], duration
    


