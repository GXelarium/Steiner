# main_executor.py
import matplotlib # Importar matplotlib primero
matplotlib.use('TkAgg') # Establecer el backend ANTES de importar pyplot
import matplotlib.pyplot as plt
import time
import networkx as nx
import random

# Importar funciones de los otros archivos
from config_input import get_graph_parameters
from graph_generator import generate_random_steiner_graph
from ip_solver import steiner_tree_ip
# No se importa dp_solver ya que fue eliminado
from heuristic_solver import steiner_tree_mst_heuristic

def run_steiner_main():
    # --- Solicitar Parámetros al Usuario ---
    NUM_NODES_TARGET, M_BARABASI, MIN_EDGE_WEIGHT, MAX_EDGE_WEIGHT, NUM_TERMINALS_REQUESTED = get_graph_parameters()
    
    print("\n--- Iniciando Comparación de Algoritmos para Árbol de Steiner ---")
    print(f"Parámetros del Grafo: Nodos Objetivo={NUM_NODES_TARGET}, m={M_BARABASI}, Terminales Solicitados={NUM_TERMINALS_REQUESTED}")
    
    # --- Generar el Grafo Aleatorio ---
    print("Generando grafo aleatorio...")
    actual_num_nodes, edges_list, terminals_list, G_nx = generate_random_steiner_graph(
        NUM_NODES_TARGET, M_BARABASI, MIN_EDGE_WEIGHT, MAX_EDGE_WEIGHT, NUM_TERMINALS_REQUESTED
    )

    if actual_num_nodes == 0 or not G_nx or (NUM_TERMINALS_REQUESTED > 0 and not terminals_list):
        print("\nError crítico: El grafo generado es inválido o no tiene suficientes terminales.")
        print("Finalizando ejecución.")
        return

    print(f"Grafo generado con {actual_num_nodes} nodos y {len(edges_list)} aristas.")
    print(f"Terminales ({len(terminals_list)}): {sorted(terminals_list) if terminals_list else 'Ninguno'}")

    # Visualizar el grafo generado inicialmente
    if G_nx.number_of_nodes() > 0:
        plt.figure(figsize=(10,7) if actual_num_nodes <= 50 else (14,10))
        node_size_dynamic = max(20, int(3500 / actual_num_nodes)) if actual_num_nodes > 0 else 50
        font_size_dynamic = max(6, int(12 - actual_num_nodes / 10)) if actual_num_nodes > 0 else 8

        pos_init = nx.spring_layout(G_nx, seed=random.randint(0,10000), k=0.9/((actual_num_nodes/20)**0.5) if actual_num_nodes > 0 else 0.9)
        nx.draw(G_nx, pos_init, with_labels=True, node_color='skyblue', 
                node_size=node_size_dynamic, 
                font_size=font_size_dynamic, width=0.8)
        if terminals_list:
            nx.draw_networkx_nodes(G_nx, pos_init, nodelist=terminals_list, node_color='red', node_size=node_size_dynamic)
        
        try:
            edge_labels_init = nx.get_edge_attributes(G_nx, 'weight')
            nx.draw_networkx_edge_labels(G_nx, pos_init, edge_labels=edge_labels_init, 
                                         font_size=max(5, font_size_dynamic-2))
        except Exception:
            pass 
        plt.title(f"Grafo Aleatorio Generado (N={actual_num_nodes}, K={len(terminals_list)}) (Terminales en Rojo)", fontsize=14)
        plt.show()
    else:
        print("No se puede visualizar un grafo vacío.")

    # --- Ejecutar Algoritmos ---
    costo_ip, aristas_ip, t_ip = (None, None, 0.0)
    costo_heur, aristas_heur, t_heur = (None, None, 0.0)

    if len(terminals_list) < 2 and NUM_TERMINALS_REQUESTED > 0 :
        print("\nSe necesitan al menos 2 terminales para resolver el problema de Steiner.")
        print("El costo es 0 para menos de 2 terminales. No se ejecutarán los algoritmos de Steiner.")
        costo_ip, aristas_ip, t_ip = 0, [], 0
        costo_heur, aristas_heur, t_heur = 0, [], 0
    elif NUM_TERMINALS_REQUESTED == 0:
        print("\nNo se solicitaron terminales. El costo del árbol de Steiner es 0.")
        costo_ip, aristas_ip, t_ip = 0, [], 0
        costo_heur, aristas_heur, t_heur = 0, [], 0
    else:
        print("\nResolviendo con Programación Entera (MCF)...")
        costo_ip, aristas_ip, t_ip = steiner_tree_ip(actual_num_nodes, edges_list, terminals_list)
        if costo_ip is not None:
            print(f"Costo IP: {costo_ip:.2f}, Aristas en ST: {len(aristas_ip) if aristas_ip else 0}, Tiempo: {t_ip:.4f}s")
        else:
            print(f"IP no encontró solución. Tiempo: {t_ip:.4f}s")

        print("\nResolviendo con Heurística MST...")
        # Crear una copia del grafo G_nx para la heurística, ya que podría ser modificada
        # o simplemente para asegurar que no hay efectos secundarios.
        if G_nx.number_of_nodes() > 0 : # Solo si G_nx es un grafo válido
            G_nx_copy_for_heuristic = G_nx.copy()
            costo_heur, aristas_heur, t_heur = steiner_tree_mst_heuristic(G_nx_copy_for_heuristic, terminals_list)
            if costo_heur is not None:
                print(f"Costo Heurístico: {costo_heur:.2f}, Aristas en ST: {len(aristas_heur) if aristas_heur else 0}, Tiempo: {t_heur:.4f}s")
            else:
                print(f"Heurística no encontró solución. Tiempo: {t_heur:.4f}s")
        else:
            print("Heurística MST no se puede ejecutar en un grafo vacío.")
            costo_heur, aristas_heur, t_heur = None, None, 0.0


    print("\n--- Resumen de Tiempos ---")
    print(f"Programación Entera: {t_ip:.4f} segundos")
    print(f"Heurística MST:      {t_heur:.4f} segundos")

    # --- Visualización en Malla 1x2 ---
    if G_nx.number_of_nodes() == 0 or (NUM_TERMINALS_REQUESTED > 0 and not terminals_list):
        print("\nNo se pueden generar gráficas de solución para un grafo inválido o sin terminales suficientes.")
        return
    
    if not (costo_ip is None and costo_heur is None):
        fig, axes = plt.subplots(1, 2, figsize=(18, 8)) 
        fig.suptitle(f"Comparación de Soluciones - Árbol de Steiner (N={actual_num_nodes}, K={len(terminals_list)})", fontsize=16)
        
        final_pos_layout = nx.spring_layout(G_nx, seed=random.randint(0,10000), k=0.9/((actual_num_nodes/20)**0.5) if actual_num_nodes > 0 else 0.9)
        
        node_size_viz = max(20, int(2500 / actual_num_nodes)) if actual_num_nodes > 0 else 30
        font_size_viz = max(6, int(10 - actual_num_nodes / 12)) if actual_num_nodes > 0 else 7
        edge_label_font_size_viz = max(5, font_size_viz - 2)

        # Subplot 1: Programación Entera
        ax_ip = axes[0]
        title_ip = f"Programación Entera\nCosto: {'{:.2f}'.format(costo_ip) if costo_ip is not None else 'N/A'} - T: {t_ip:.2f}s"
        ax_ip.set_title(title_ip, fontsize=12)
        if costo_ip is not None and aristas_ip is not None:
            ST_ip = nx.Graph()
            ST_ip.add_weighted_edges_from(aristas_ip)
            nx.draw(G_nx, final_pos_layout, ax=ax_ip, with_labels=False, node_color='whitesmoke', node_size=node_size_viz, style='dotted', width=0.5, alpha=0.7)
            nx.draw(ST_ip, final_pos_layout, ax=ax_ip, with_labels=True, node_color='lightgreen', node_size=int(node_size_viz*1.5), width=2.0, edge_color='green', font_size=font_size_viz)
            if terminals_list: nx.draw_networkx_nodes(G_nx, final_pos_layout, ax=ax_ip, nodelist=terminals_list, node_color='red', node_size=int(node_size_viz*1.5))
            try:
                edge_labels_sol_ip = {(u,v):d['weight'] for u,v,d in ST_ip.edges(data=True)}
                nx.draw_networkx_edge_labels(ST_ip, final_pos_layout, ax=ax_ip, edge_labels=edge_labels_sol_ip, font_size=edge_label_font_size_viz, font_color='darkgreen')
            except Exception: pass
        else:
            ax_ip.text(0.5, 0.5, "IP: Sin solución / Error", ha='center', va='center', transform=ax_ip.transAxes)
        ax_ip.axis('off')

        # Subplot 2: Heurística MST
        ax_heur = axes[1]
        title_heur = f"Heurística MST\nCosto: {'{:.2f}'.format(costo_heur) if costo_heur is not None else 'N/A'} - T: {t_heur:.2f}s"
        ax_heur.set_title(title_heur, fontsize=12)
        if costo_heur is not None and aristas_heur is not None:
            ST_heur = nx.Graph()
            ST_heur.add_weighted_edges_from(aristas_heur)
            nx.draw(G_nx, final_pos_layout, ax=ax_heur, with_labels=False, node_color='whitesmoke', node_size=node_size_viz, style='dotted', width=0.5, alpha=0.7)
            nx.draw(ST_heur, final_pos_layout, ax=ax_heur, with_labels=True, node_color='lightblue', node_size=int(node_size_viz*1.5), width=2.0, edge_color='blue', font_size=font_size_viz)
            if terminals_list: nx.draw_networkx_nodes(G_nx, final_pos_layout, ax=ax_heur, nodelist=terminals_list, node_color='red', node_size=int(node_size_viz*1.5))
            try:
                edge_labels_sol_heur = {(u,v):d['weight'] for u,v,d in ST_heur.edges(data=True)}
                nx.draw_networkx_edge_labels(ST_heur, final_pos_layout, ax=ax_heur, edge_labels=edge_labels_sol_heur, font_size=edge_label_font_size_viz, font_color='darkblue')
            except Exception: pass
        else:
            ax_heur.text(0.5, 0.5, "Heurística: Sin solución / Error", ha='center', va='center', transform=ax_heur.transAxes)
        ax_heur.axis('off')

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.show()
    elif NUM_TERMINALS_REQUESTED > 0 and len(terminals_list) >=2 : 
        print("\nNo se pudieron obtener soluciones para graficar o no hubo resultados válidos.")


if __name__ == '__main__':
    run_steiner_main()