class FailureDectector:
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
            
            if len(disps) < 5: continue
            
            # 1. Calcular Rigidez Inicial (K_ini)
            # Promedio de los primeros 3 pasos (o pasos iniciales)
            dq = disps[2] - disps[0]
            if abs(dq) > 1e-9:
                k_ini = (shears[2] - shears[0]) / dq
            else:
                k_ini = 1.0e9 # Muy rígido
            
            # 2. Analizar últimos pasos (Pendiente Tangente)
            # Usamos regresión lineal simple de los últimos 3 puntos
            d_last = disps[-3:]
            v_last = shears[-3:]
            current_drift = d_last[-1]
            
            # Pendiente local (K_tan)
            try:
                k_tan = (v_last[-1] - v_last[0]) / (d_last[-1] - d_last[0])
            except ZeroDivisionError:
                k_tan = 0.0 # Vertical
            
            # 3. Evaluar Criterios
            # A) Deriva Relativa Significativa (> 0.5%)
            drift_ratio = abs(current_drift) / h_floor
            is_significant_drift = drift_ratio > 0.005 # 0.5%
            
            # B) Pendiente plana (o negativa) -> Mecanismo
            # Si K_tan cae por debajo del 1% de K_ini
            sensitivity = 0.001 
            is_flat = k_tan < (sensitivity * k_ini)
            
            # C) Safety Net (Deriva excesiva > 5%)
            is_huge_drift = drift_ratio > 0.08

            if (is_significant_drift and is_flat) or is_huge_drift:
                print(f"[Adaptive] Piso Y={y:.2f} DETECTADO FALLO (Drift Ratio={drift_ratio*100:.2f}%, K_tan/K_ini={k_tan/k_ini:.4f})")
                failed_floors.append(y)
                
        return failed_floors
