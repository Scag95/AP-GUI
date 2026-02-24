import openseespy.opensees as ops
import math
from src.analysis.manager import ProjectManager

class LoadPushoverGenerator:
    """
    Clase responsable de calcular distribuciones de fuerzas laterales
    para análisis estáticos no lineales (Pushover), incluyendo análisis modal.
    """

    def __init__(self, builder):
        self.builder = builder
        self.manager = ProjectManager.instance()

    def run_modal_analysis(self, n_modes):
        """
        Ejecuta el análisis modal, obtiene periodos y vectores de forma,
        y calcula las fuerzas inerciales (F_i = M_i * Phi_i) normalizadas.
        """

        #Cargamos los nodos del proyecto.
        nodes = self.manager.get_all_nodes()
        floor_masses = self.manager.get_floor_masses()

        if self.builder.debug_file: self.builder.debug_file.write("\n# --- Analysis Modal ---\n")
        lambdas = ops.eigen(n_modes)
        self.builder.log_command('eigen', n_modes)

        periods = []
        count = 0
        for lam in lambdas:
            omega = math.sqrt(lam)
            T = 2*math.pi / omega
            periods.append(T)
            count += 1
            print(f"[Modal] Modo {count} T = {T:.4f}s")


        #1. Agrumaos los nodos por planta.
        floors = {}
        tolerance = 0.01

        for node in nodes:
            if node.fixity[0] == 1: continue
            
            found_floor_key = None
            for y_key in floors.keys():
                if abs(node.y - y_key) < tolerance:
                    found_floor_key = y_key
                    break
                
            if found_floor_key is not None:
                floors[found_floor_key].append(node)
            else:
                floors[node.y] = [node]


        #2. Ordenamos los piso y seleccionamos un nodo Master
        sorted_floors = sorted(floors.keys())
        modal_data = []     #Lista de tuplas (node_tag, phi_x, phi_y, y_coord)
        for y in sorted_floors:
            floor_nodes = floors[y]
            #Seleccionamos el nodo con menos X (Izquierda)
            master_node = min(floor_nodes, key = lambda n: n.x)

            #Obtener vector propio(Mode 1)
            phi_x = ops.nodeEigenvector(master_node.tag, 1,1)
            phi_y = ops.nodeEigenvector(master_node.tag, 1,2)
            
            modal_data.append({
                'tag':master_node.tag,
                'y': y,
                'phi_x': phi_x,
                'phi_y': phi_y
            })

            print(f"[Modal] Floor Y = {y:.2f} -> Master node {master_node.tag}, disp = {phi_x:.4f}")

        if modal_data:

            for item in modal_data:
                item['mass'] = floor_masses.get(item['y'])
                #Calculamos la fuerzas de cada piso
                item['f_i'] = item['mass'] * item['phi_x']
            
            #Tomamos la fuerza de la ultima planta
            roof_f = modal_data[-1]['f_i']
            if abs(roof_f) <  1e-9: print("División por 0. Revisar run_modal_analisys")


            #Calculamos el vector de fuerzas normalizado
            for item in modal_data:
                item['f_norm'] = item['f_i']/roof_f
                print(f"Phi_x: {item['phi_x']:.4f}, Masa: {item['mass']:.2f}, Fi: {item['f_norm']:.2f}")

        return periods, modal_data
