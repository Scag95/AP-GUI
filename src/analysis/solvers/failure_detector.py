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
    def __init__(self, sensitivity: float = 0.001, max_drift: Optional[float] = None):
        #sensitivity: Factor multiplicador para considerar "plana" la rigidez tangente frente a la inicial.ProcessLookupError
        self.sensitivity = sensitivity
        self.max_drift = max_drift
        self.cached_k_ini = {} # Memoria de rigidez elástica global original
        self.reported_floors: set = set() # Pisos ya impresos en el monitor

    def analyze(self, results: Dict[str, Any]) -> List[FloorFailureState]:
        """
        Punto de entrada. Evalua iterativamente cada planta registrada en 'results'
        buscando formación de mecanismos
        """

        failed_floors: List[FloorFailureState] = []
        floor_states = []

        for y, data in results["floors"].items():
            disps = data["disp"]
            shears = data["shear"]
            H = data.get("H", 0.0)

            if len(disps) < 100:
                continue

            if y not in self.cached_k_ini:
                self.cached_k_ini[y] = self._calculate_initial_stiffness(disps, shears)

            k_ini = self.cached_k_ini[y]
            k_tan = self._calculate_tangent_stiffness(disps, shears)
            current_drift = disps[-1]
            step = len(disps)
            drift_ratio = abs(current_drift) / H if H > 0 else 0

            is_flat = k_tan < (self.sensitivity * k_ini)
            is_excessive_drift = self.max_drift is not None and H > 0 and drift_ratio > self.max_drift
            is_failed = is_flat or is_excessive_drift

            floor_states.append({
                "y": y, "step": step, "drift": current_drift,
                "drift_pct": drift_ratio * 100, "k_ini": k_ini,
                "k_tan": k_tan, "failed": is_failed
            })

            if is_failed:
                causes = []
                if is_flat:
                    ratio = (k_tan / k_ini) * 100 if k_ini > 0 else 0
                    causes.append(f"Rigidez ({ratio:.1f}%)")
                if is_excessive_drift:
                    causes.append(f"Deriva Excesiva ({drift_ratio * 100:.2f}%)")
                failed_floors.append(FloorFailureState(
                    y_level=y, cause=" | ".join(causes),
                    k_ini=k_ini, k_tan=k_tan, current_drift=current_drift
                ))

        new_failures = {s["y"] for s in floor_states if s["failed"] and s["y"] not in self.reported_floors}
        if new_failures:
            self.reported_floors |= new_failures
            for s in sorted(floor_states, key=lambda x: x["y"]):
                label = "[Fallo]" if s["failed"] else "[OK]   "
                ratio = (s["k_tan"] / s["k_ini"]) * 100 if s["k_ini"] > 0 else 0
                print(f"{label} Planta Y={s['y']:5.2f} m | Paso: {s['step']:5d} | "
                      f"Deriva: {s['drift']:.5f} m ({s['drift_pct']:.2f}%) | "
                      f"K_tan/K_ini: {ratio:6.2f}%")

        return failed_floors

    def _calculate_initial_stiffness(self, disps: List[float], shears: List[float]) -> float:
        """ 
        Calcula la Rigidez Inicial (K_ini) usando los primeros pasoso de la ronda 
        para evitar ruido numérico en el paso 0. Devuelve la magnitud absoluta.
        """

        dq_ini = disps[20] - disps[0]
        dv_ini = shears[20] - shears[0]

        if abs(dq_ini) > 1e-9:
            return abs(dv_ini /dq_ini)
        return 1.0e9 #Asumir rigidez infinita si no hay desplazamiento válido


    def _calculate_tangent_stiffness(self, disps: List[float], shears: List[float]) -> float:
        """
        Calcula la rigidez Tangente actual (K_tan) analizando la pendiente
        lineal simple de los últimos 5 puntyos para la estabilidad numérica.
        """

        d_last = disps[-2:]
        v_last = shears[-2:]

        dq_tan = d_last[-1] - d_last[0]
        dv_tan = v_last[-1] - v_last[0]

        try:
            return dv_tan/dq_tan
        except ZeroDivisionError:
            return 1.0e9 #Vertcial / Plana por infinito

    
