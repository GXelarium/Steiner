# config_input.py

def get_graph_parameters():
    """Solicita al usuario los parámetros para la generación del grafo."""
    print("--- Configuración de Parámetros del Grafo ---")
    
    while True:
        try:
            num_nodes = int(input("Número deseado de nodos (e.g., 10, 20, 50): "))
            if num_nodes <= 0:
                print("El número de nodos debe ser positivo.")
                continue
            break
        except ValueError:
            print("Entrada inválida. Por favor, ingresa un número entero.")

    m_barabasi = 1 # Valor por defecto si num_nodes es pequeño
    if num_nodes > 1:
        while True:
            try:
                m_barabasi = int(input(f"Parámetro 'm' para Barabasi-Albert (1 <= m < {num_nodes}, e.g., 2): "))
                if 1 <= m_barabasi < num_nodes:
                    break
                else:
                    print(f"m debe estar entre 1 y {num_nodes - 1}.")
            except ValueError:
                print("Entrada inválida. Por favor, ingresa un número entero.")
    
    while True:
        try:
            min_weight = int(input("Peso mínimo para las aristas (e.g., 1): "))
            if min_weight < 0:
                print("El peso mínimo no puede ser negativo.")
                continue
            break
        except ValueError:
            print("Entrada inválida. Por favor, ingresa un número entero.")

    while True:
        try:
            max_weight = int(input(f"Peso máximo para las aristas (>= {min_weight}, e.g., 20): "))
            if max_weight < min_weight:
                print(f"El peso máximo debe ser mayor o igual que el mínimo ({min_weight}).")
                continue
            break
        except ValueError:
            print("Entrada inválida. Por favor, ingresa un número entero.")

    max_possible_terminals = num_nodes
    num_terminals = 0
    if max_possible_terminals > 0:
        while True:
            try:
                num_terminals = int(input(f"Número deseado de terminales (0 <= k <= {max_possible_terminals}, e.g., 4): "))
                if 0 <= num_terminals <= max_possible_terminals:
                    break
                else:
                    print(f"El número de terminales debe estar entre 0 y {max_possible_terminals}.")
            except ValueError:
                print("Entrada inválida. Por favor, ingresa un número entero.")
    else:
        print("No se pueden solicitar terminales para un grafo sin nodos.")


    print("------------------------------------------------")
    return num_nodes, m_barabasi, min_weight, max_weight, num_terminals