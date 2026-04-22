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

    def analyze(self, results: Dict[str, Any]) -> List[FloorFailureState]:
        """
        Punto de entrada. Evalua iterativamente cada planta registrada en 'results'
        buscando formación de mecanismos
        """

        failed_floors: List[FloorFailureState] = []

        for y, data in results["floors"].items():
            disps = data["disp"]
            shears = data["shear"]
            H = data.get("H", 0.0)

            # Filtro : Necesitamos suficiente historia de pasos en la ronda 

            if len(disps) < 100:
                continue

            #1. Extraemos las magnitudes netas a través de nuestros helpers
            if y not in self.cached_k_ini:
                self.cached_k_ini[y] = self._calculate_initial_stiffness(disps, shears)
                
            k_ini = self.cached_k_ini[y]
            k_tan = self._calculate_tangent_stiffness(disps, shears)
            current_drift = disps[-1]

            # --- MONITOR DE SIGNOS VITALES ---
            step_actual = len(disps)
            if step_actual % 50 == 0 or step_actual > 10000:
                ratio = (k_tan / k_ini) * 100 if k_ini > 0 else 0
                print(f"[Monitor] Planta Y={y} | Paso: {step_actual} | Deriva: {current_drift:.5f} m | K_tan: {ratio:.2f}% de la inicial")
            # ----------------------------------------

            #2. Evaluacióndel Mecanismo (Basta con que la rigidez tangente sea menor a la tolerancia elástica)
            is_flat = k_tan < (self.sensitivity * k_ini)

            #3. Evaculación de la deriva.
            is_excessive_drift = False 

            if self.max_drift is not None and H > 0:
                drift_ratio = abs(current_drift)/H
                is_excessive_drift = drift_ratio > self.max_drift

            #4. Empaquetar y reportar si se activó el fallo
            if is_flat or is_excessive_drift:
                #Construimos un string dinámico con el motivo exacto del fallo
                causes = []
                drift_pct = (abs(current_drift) / H) * 100 if H > 0 else 0
                if is_flat:
                    ratio = (k_tan / k_ini) * 100 if k_ini > 0 else 0
                    causes.append(f"Rigidez ({ratio:.1f}%) | Deriva ({drift_pct:.2f}%)")
                if is_excessive_drift:
                    causes.append(f"Deriva Excesiva ({drift_pct:.2f}%)")
                failure_state = FloorFailureState(
                    y_level = y,
                    cause = " | ".join(causes),
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

        d_last = disps[-5:]
        v_last = shears[-5:]

        dq_tan = d_last[-1] - d_last[0]
        dv_tan = v_last[-1] - v_last[0]

        try:
            return dv_tan/dq_tan
        except ZeroDivisionError:
            return 1.0e9 #Vertcial / Plana por infinito

    
