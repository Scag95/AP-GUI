class FailureDetector:
    """
    Clase responsable exclusivamente de analizar las curvas de respuesta (Pushover)
    para detectar la formación de mecanismos (fallo) en los diferentes pisos.
    """

    def __init__(self, sensitivity=0.001, drift_limit=0.005,safety_limit=0.08):
        # sensitivity: Porcentaje de la rigidez inicial para considerar "plana" la curva (Mecanismo)
        # drift_limit: Deriva relativa mínima para considerar que un mecanismo es significativo
        # safety_limit: Límite absoluto de deriva para detener por deformación excesiva (colapso)

        self.sensitivity = sensitivity
        self.drift_limit = drift_limit
        self.safety_limit = safety_limit


    def analyze(self, results):
        """
        Analiza el diccionario de resultados de un Pushover y devuelve los niveles 'y' que han fallado.
        Reemplaza a PushoverSolver.detect_failed_floors()
        """
        failed_floors = []

        for y, data in results["floors"].items():
            disps = data["disp"] # Drift absoluto (m)
            shears = data["shear"]
            h_floor = data.get("H") # Altura del piso (default 3m)
            
            # Filtro 1: Necesitamos suficiente historia para no captar ruido numérico del reinicio (Ej: Paso 4)
            if len(disps) < 20: 
                continue
            
            # 1. Calcular Rigidez Inicial (K_ini) del inicio de la ronda (suavizado)
            dq_ini = disps[5] - disps[0]
            dv_ini = shears[5] - shears[0]
            if abs(dq_ini) > 1e-9:
                k_ini = dv_ini / dq_ini
            else:
                k_ini = 1.0e9 # Muy rígido
            
            # 2. Analizar últimos pasos (Pendiente Tangente)
            # Usamos regresión lineal simple de los últimos 5 puntos para más estabilidad
            d_last = disps[-5:]
            v_last = shears[-5:]
            current_drift = d_last[-1]
            
            # Pendiente local (K_tan)
            dq_tan = d_last[-1] - d_last[0]
            dv_tan = v_last[-1] - v_last[0]
            try:
                k_tan = dv_tan / dq_tan
            except ZeroDivisionError:
                k_tan = 0.0 # Vertical
            
            # 3. Evaluar Criterios
            # A) Deriva Relativa Significativa (> 0.5% real para evitar micro-asentamientos)
            drift_ratio = abs(current_drift) / h_floor
            is_significant_drift = drift_ratio > self.drift_limit
            
            # B) Mecanismo Estructural: Pendiente puramente plana (usando absolutos)
            is_flat = abs(k_tan) < (self.sensitivity * abs(k_ini))
            
            # B.2) Softening crítico: Pérdida marcada de resistencia (tangente muy negativa respecto al empuje original)
            is_softening = k_tan < 0 and abs(k_tan) > (0.05 * abs(k_ini)) and is_significant_drift
            
            # C) Safety Net (Deriva excesiva de colapso)
            is_huge_drift = drift_ratio > self.safety_limit

            if (is_significant_drift and is_flat) or is_softening or is_huge_drift:
                cause = "Mecanismo Plano" if is_flat else ("Caída Resistencia" if is_softening else "Colapso Displ")
                print(f"[Adaptive] Piso Y={y:.2f} DETECTADO FALLO [{cause}] (Drift={drift_ratio*100:.2f}%, K_tan/K_ini={k_tan/k_ini:.4f})")
                failed_floors.append(y)
                
        return failed_floors
