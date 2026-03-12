from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class FloorFailureState:
    """Estructura de datos que encapsul toda la información sobre el fallo de una planta."""
    y_level: float
    cause: str
    k_ini: float
    k_tan: float
    current_drift: float

class FailureDetector:
    """Clase responsable de analizar secuencias de resultados de un Pushover para detectar la pérdida de capacidad estructural"""
    def __init__(self, sensitivity: float = 0.001):
        #sensitivity: FActor multiplicador para considerar "plana" la rigidez tangente frente a la inicial.ProcessLookupError
        self.sensitivity = sensitivity

    def analyze(self, results: Dict[str, Any]) -> List[FloorFailureState]:
        """
        Punto de entrada. Evalua iterativamente cada planta registrada en 'results'
        buscando formación de mecanismos
        """

        failed_floors: List[FloorFailureState] = []

        for y, data in results["floors"].items():
            disps = data["disp"]
            shears = data["shear"]

            # Filtro : Necesitamos suficiente historia de pasos en la ronda 

            if len(disps) < 100:
                continue

            #1. Extraemos las magnitudes netas a través de nuestros helpers
            k_ini = self._calculate_initial_stiffness(disps, shears)
            k_tan = self._calculate_tangent_stiffness(disps, shears)
            current_drift = disps[-1]

            #2. Evaluacióndel Mecanismo (Curva Plana)
            is_flat = (k_tan < 0) or (abs(k_tan) < (self.sensitivity * k_ini))

            #3. Empaquetar y reportar si se activó el fallo
            if is_flat:
                failure_state = FloorFailureState(
                    y_level = y,
                    cause = "Mecanismo Plano (K_tan = 0)",
                    k_ini = k_ini,
                    k_tan = k_tan,
                    current_drift = current_drift
                )
                failed_floors.append(failure_state)

        return failed_floors

    def _calculate_initial_stiffness(self, disps: List[float], shears: List[float]) -> float:
        """ 
        Calcula la Rigidez Inicial (K_ini) usando los primeros pasoso de la ronda 
        para evitar ruido numérico en el paso 0. Devuelve la magnitud absoluta.
        """

        dq_ini = disps[40] - disps[0]
        dv_ini = shears[40] - shears[0]

        if abs(dq_ini) > 1e-9:
            return abs(dv_ini /dq_ini)
        return 1.0e9 #Asumir rigidez infinita si no hay desplazamiento válido


    def _calculate_tangent_stiffness(self, disps: List[float], shears: List[float]) -> float:
        """
        Calcula la rigidez Tangente actual (K_tan) analizando la pendiente
        lineal simple de los últimos 5 puntyos para la estabilidad numérica.
        """

        d_last = disps[-40:]
        v_last = shears[-40:]

        dq_tan = d_last[-1] - d_last[0]
        dv_tan = v_last[-1] - v_last[0]

        try:
            return dv_tan/dq_tan
        except ZeroDivisionError:
            return 0.0 #Vertcial / Plana por infinito

    
