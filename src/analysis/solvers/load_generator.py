import openseespy.opensees as ops
import math
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from src.analysis.manager import ProjectManager

@dataclass
class LoadPatternResult:
    """Encapsula el resultado de la generación del patrón de cargas"""
    force_vector: Dict[int, float]  #Diccionario {node_tag: force_x}
    periods: List[float]            #Periodos findamentales (si existen)


class LoadPushoverGenerator:
    """
    Fábrica responsable de cálcular distribuciones de fuerzas laterales (vectores)
    para análisis estático n lineales (Pushover).
    """

    def __init__(self, builder):
        self.builder = builder
        self.manager = ProjectManager.instance()

    def generate_pattern(self, pattern_type: str, n_modes : int = 1) -> LoadPatternResult:
        """
        Punto de entrada unificado. Devuelve el vector de fuerzas estáticas
        basado en la estratecia seleccionada (Modal o Uniforme).
        """

        master_nodes = self._identify_master_nodes()

        if pattern_type == "Modal":
            return self._generate_modal_pattern(master_nodes, n_modes)
        elif pattern_type == "Uniforme":
            return self._generate_uniform_pattern(master_nodes)
        else:
            raise ValueError(f"Patron de cargan no soportado: {pattern_type}")

    def _identify_master_nodes(self) -> Dict[float, int]:
        """
        Consulta al ProjectManager los nodos por planta y extrae el nodo de control (menor X) de cada una.
        Retorna: {y_coord: master_node_tag}
        """
        master_nodes = {}
        floor_data = self.manager.get_floor_data()

        for y, data in floor_data.items():
            floor_nodes = data.get("nodes", [])
            if floor_nodes:
                master_node = min(floor_nodes, key=lambda n: n.x)
                master_nodes[y] = master_node.tag

        return master_nodes


    def _generate_modal_pattern(self, master_nodes: Dict[float, int], n_modes: int) -> LoadPatternResult:
        """
        Ejecuta el análisis modal en OpenSees, extrae los vectores propios de la forma modal 1, 
        y normaliza las fuerzas inerciales (F_i = M_i * Phi_i) respecto al techo.
        """
        floor_masses = self.manager.get_floor_masses()

        if self.builder.debug_file:
            self.builder.debug_file.write("\n# --- Anañysis Modal --- \n")

        lambdas = ops.eigen(n_modes)
        self.builder.log_command('eigen', n_modes)

        periods = []
        if lambdas:
            for count, lam in enumerate(lambdas, 1):
                omega = math.sqrt(lam)
                T = 2 * math.pi / omega
                periods.append(T)
                print(f"[Modal] Modo {count} T = {T:.4f}s")

        force_vector = {}
        modal_data = []

        for y, master_tag in master_nodes.items():
            phi_x = ops.nodeEigenvector(master_tag, 1,1)
            mass = floor_masses.get(y,0.0)
            f_i = mass * phi_x

            modal_data.append({'tag':master_tag, 'y':y, 'phi_x': phi_x, 'mass':mass, 'f_i':f_i})
            print(f"[Modal] Floor Y = {y:.2f} -> Master node {master_tag}, disp = {phi_x:.4f}")

        if modal_data:
            roof_f = modal_data[-1]['f_i']
            if abs(roof_f) < 1e-9:
                print("División por 0. Revisar run_modal_analaysis")
                roof_f = 1.0

            for item in modal_data:
                f_norm = item['f_i'] / roof_f
                force_vector [item['tag']] = f_norm
                print(f"Phi_x : {item['phi_x']:.4f}, Masa {item['mass']:.2f}, Fi: {f_norm:.2f}")
        return LoadPatternResult(force_vector= force_vector, periods= periods)

    def _generate_uniform_pattern(self, master_nodes: Dict[float, int]) -> LoadPatternResult:
        """
        Genera un patrón de fuerzas constante asignando una magnitud de 1.0
        exclusivamente a los nodos maestros del diafragma.
        """

        force_vector = {}

        for y, master_tag in master_nodes.items():
            force_vector[master_tag] = 1.0
            print(f"[Uniforme] Floor Y = {y:.2f} -> Master node {master_tag}, Fi = 1.0")

        return LoadPatternResult(force_vector= force_vector, periods=[])
