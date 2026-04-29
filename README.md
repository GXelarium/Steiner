# Comparación de Algoritmos para el Problema del Árbol de Steiner

Este proyecto fue desarrollado como trabajo final para la materia de **Optimización 2**. El objetivo principal es comparar el rendimiento (costo computacional y tiempo de ejecución) entre un método exacto y un método heurístico para resolver el **Problema del Árbol de Steiner en Grafos**.

## Descripción del Proyecto

El programa genera grafos aleatorios utilizando el modelo de Barabási-Albert y selecciona un subconjunto de nodos como "terminales". Luego, intenta conectar todos estos nodos terminales minimizando el costo total de las aristas utilizando dos enfoques distintos:

1. **Programación Entera (Exacto):** Utiliza una formulación de Flujo Multi-Producto (Multi-Commodity Flow) implementada con la librería `PuLP`. Garantiza encontrar la solución óptima, pero su tiempo de ejecución crece exponencialmente con el tamaño del grafo.
2. **Heurística KMB (Aproximado):** Implementa el algoritmo de Kou, Markowsky y Berman (1981) utilizando `NetworkX`. Combina cálculos de caminos más cortos (Shortest Path) y Árboles de Expansión Mínima (MST) para encontrar una solución de buena calidad en una fracción del tiempo que requiere el modelo exacto.

Al finalizar, el programa despliega una interfaz gráfica utilizando `matplotlib` para visualizar el grafo original y comparar visualmente los resultados de ambos algoritmos.

##  Cómo funciona el Algoritmo Heurístico (KMB)

El archivo `heuristic_solver.py` implementa los siguientes pasos:
1. Calcula la distancia del camino más corto entre todos los pares de nodos terminales.
2. Construye un grafo completo temporal con los terminales, donde los pesos son estas distancias mínimas.
3. Encuentra el Árbol de Expansión Mínima (MST) de este grafo temporal.
4. Reconstruye un subgrafo en la red original mapeando las aristas del MST a sus caminos originales.
5. Calcula un nuevo MST sobre este subgrafo para asegurar que no haya ciclos.
6. Poda recursivamente los nodos hoja que no son terminales para obtener el Árbol de Steiner final.

##  Requisitos

Para configurar el entorno y poder ejecutar los scripts, instala las dependencias con el siguiente comando:

```bash
pip install -r requirements.txt
```
## Ejecución
Para ejecutar el programa  sigue el siguiente comando:
```
python main.py
```

