import openseespy.opensees as ops
import os
import math
from src.analysis.manager import ProjectManager
from src.analysis.element import ForceBeamColumn

class PushoverSolver:
    def __init__(self, builder):
        self.builder = builder
        self.manager = ProjectManager.instance()

    def _get_element_force(self, ele_tag):
        """Helper para obtener el cortante en Top (última sección) de manera dinámica."""
        element = self.manager.get_element(ele_tag)
        if not element: return 0.0
        
        # Obtener último punto (Top)
        n_points = getattr(element, 'integration_points')
        
        # Leer fuerza en la sección n_points
        forces = ops.eleResponse(ele_tag, 'section', n_points, 'force')
        if forces and len(forces) >= 3:
            return forces[2] # Cortante local (Vy?)
        return 0.0

    def run_modal_analysis(self, n_modes):
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
    
    def _get_colums_by_floor(self):
        columns_by_floor = {}
        floor_data = self.manager.get_floor_data()

        for y, data in floor_data.items():
            if data["columns"]:
                # Aquí asignamos la lista al diccionario bajo la clave 'y'
                columns_by_floor[y] = [col.tag for col in data["columns"]]     
                    
        return columns_by_floor

    def _setup_pushover_recorders(self, output_dir="pushover_data"):
        """
        Configura los recorders para guardar fuerzas y deformaciones 
        de todas las secciones de todos los elementos durante el Pushover.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        print(f"[OpenSees] Configurando Recorders en: {os.path.abspath(output_dir)}")
        
        # Limpiar recorders previos para evitar duplicados
        ops.remove('recorders')
        
        for ele in self.manager.get_all_elements():
            # Solo nos interesan elementos viga-columna con secciones
            if isinstance(ele, ForceBeamColumn):
                # Recorder de Fuerzas (P, M, V) en todas las secciones
                ops.recorder('Element', '-file', f'{output_dir}/ele_{ele.tag}_force.out', 
                             '-time', '-ele', ele.tag, 'section', 'force')
                
                # Recorder de Deformaciones (eps, kappa) en todas las secciones
                ops.recorder('Element', '-file', f'{output_dir}/ele_{ele.tag}_deform.out', 
                             '-time', '-ele', ele.tag, 'section', 'deformation')

    def detect_failed_floors(self, results):
        """
        Analiza las curvas V-D de cada piso para detectar mecanismos.
        Criterio: Pendiente tangente < 1% Rigidez Inicial + Deriva > 0.5%
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


    def run_pushover(self, control_node_tag, max_disp, load_pattern_type, n_steps = 100, pattern_tag = 2,
                     initial_shears_override=None, fixed_load_vector=None, setup_recorders=True):
        """
        Ejecuta un análisis Pushover (Displacement Control).
        Retonra una tupa (lista_desplazamiento, lista_cortanes).
        """
        self.builder.debug_file = open("model_debug.py", "a")
        
        if self.builder.debug_file: self.builder.debug_file.write(f"\n# --- PUSHOVER ANALYSIS (Node {control_node_tag}, Dmax = {max_disp}, Distribución {load_pattern_type})---\n")

        #4. Definir patrónde carga lateral (Pushover)
        ts_tag_push = pattern_tag
        pattern_tag_push = pattern_tag
        
        # Crear TimeSeries lineal única para este patrón
        self.builder.log_command('timeSeries', 'Linear', ts_tag_push)
        self.builder.log_command('pattern', 'Plain', pattern_tag_push, ts_tag_push)

            
        if fixed_load_vector:
            # Usar vector pre-calculado (consistente para Adaptive)
            for node_tag, f_val in fixed_load_vector.items():
                self.builder.log_command('load', node_tag, f_val, 0.0, 0.0)
                print(f"[DEBUG Pushover] Load Node {node_tag} FX = {f_val} (Fixed)")
        else:
            # Calcular en el momento (Standard)
            periods, modal_data = self.run_modal_analysis(1)
            
            if load_pattern_type == "Modal":
                for item in modal_data:
                    f_val = item['f_norm']
                    node_tag = item['tag']
                    self.builder.log_command('load', node_tag, f_val, 0.0, 0.0)
                    print(f"[DEBUG Pushover] Load Node {node_tag} FX = {f_val}")
            else:
                for item in modal_data:
                    node_tag = item['tag']
                    self.builder.log_command('load', node_tag, 1.0, 0.0, 0.0)

        #5. Identificar columnas por piso (Pre-Proceso) 
        floor_cols_map = self._get_colums_by_floor()
        sorted_floor_y = sorted(floor_cols_map.keys())

        #6. Configurar Análisis Pushover
        incr_disp = max_disp/n_steps

        # Estructura de resultados
        results = {
            "roof_disp": [],
            "base_shear": [],
            "steps": [],
            "floors": {}
        }

        #Inicializar istas de cada piso

        for y in sorted_floor_y:
            results["floors"][y] = {"disp":[], "shear": []}

        print(f"[Pushover] Analizando cortantes en pisos: {list(floor_cols_map.keys())}")


        #6. Configurar Análisis Pushover
        incr_disp = max_disp/n_steps
        
        # --- SETUP RECORDERS FOR MOMENT-CURVATURE ---
        if setup_recorders:
            self._setup_pushover_recorders()

        self.builder.log_command('integrator', 'DisplacementControl', control_node_tag,1,incr_disp)
        self.builder.log_command('test','NormDispIncr', 1e-06, 100)
        self.builder.log_command('algorithm', 'KrylovNewton')
        self.builder.log_command('analysis', 'Static')
        
        # Detectar bases globales (reacción total)
        nodes = self.manager.get_all_nodes()
        base_nodes = [n.tag for n in nodes if n.fixity[0] == 1]


        initial_story_shears = {}
        
        if initial_shears_override:
             initial_story_shears = initial_shears_override
        else:
            print("[Pushover] Capturando estado inicial (Gravedad)...")
            ops.reactions()
            for y in sorted_floor_y:
                shear_gravity = 0.0
                cols = floor_cols_map[y]
                for ele_tag in cols:
                    # USAMOS HELPER DINÁMICO
                    shear_gravity += self._get_element_force(ele_tag)
                    
                initial_story_shears[y] = shear_gravity
                   
        for i in range(1, n_steps + 1):
            ok = ops.analyze(1)
            #ok = self.builder.log_command('analyze', 1)
            
            if ok != 0:
                print(f"[Pushover] Convergencia perdida en paso {i}")
                break
        
            #A) Resultados globales
            current_roof_disp = ops.nodeDisp(control_node_tag, 1)

            ops.reactions()
            current_base_shear = 0.0
            for b_node in base_nodes:
                reacs = ops.nodeReaction(b_node)
                current_base_shear += reacs[0]

            #Guardamos global
            results["roof_disp"].append(current_roof_disp)
            results["base_shear"].append(-current_base_shear)
            results["steps"].append(i)

            for y in sorted_floor_y:
                shear_total = 0.0
                cols = floor_cols_map[y]
                for ele_tag in cols:
                     # USAMOS HELPER DINÁMICO
                    shear_total += self._get_element_force(ele_tag)

                shear_net = (shear_total - initial_story_shears[y])
                
                # Deriva Relativa
                ref_col_tag = cols[0]
                col_obj = self.manager.get_element(ref_col_tag)
                u_top = ops.nodeDisp(col_obj.node_j, 1) # Assumes node_j is top
                u_bot = ops.nodeDisp(col_obj.node_i, 1)
                drift = u_top - u_bot
                
                # Obtener altura real (H)
                node_j = self.manager.get_node(col_obj.node_j)
                node_i = self.manager.get_node(col_obj.node_i)
                h_floor = abs(node_j.y - node_i.y)
        
                results["floors"][y]["disp"].append(drift)
                results["floors"][y]["shear"].append(shear_net)
                results["floors"][y]["H"] = h_floor
                
        return results
    
    def _merge_results(self, consolidated, new_res,cycle_idx):
        """Helper para unir los resultados"""
        consolidated["roof_disp"].extend(new_res["roof_disp"])
        consolidated["base_shear"].extend(new_res["base_shear"]) 

        count = len(new_res["roof_disp"])
        consolidated["cycle_id"].extend([cycle_idx] * count)
        
        last_step = consolidated["steps"][-1] if consolidated["steps"] else 0
        new_steps = [s + last_step for s in new_res["steps"]]
        consolidated["steps"].extend(new_steps)

        for y, data in new_res["floors"].items():
            if y not in consolidated["floors"]:
                consolidated["floors"][y] = {"disp":[], "shear":[], "H": data.get("H")}

            consolidated["floors"][y]["disp"].extend(data["disp"])
            consolidated["floors"][y]["shear"].extend(data["shear"])
    
    def run_adaptative_pushover(self,control_node_tag, max_disp, load_pattern_type):
        MAX_ROUNDS = 5
        base_steps = 100


        #Desplazamiento por ronda

        disp_per_round = max_disp/1
        consolidated = {
            "roof_disp":[],
            "base_shear":[],
            "steps":[],
            "cycle_id":[], 
            "steps":[],
            "cycle_id":[], 
            "floors":{}
        }

        current_pattern = 200 #ID seguro para patterns incrementales
        
        # Historial de pisos ya congelado para no repetor freeze
        frozen_floors = set()

        print(f"[Adaptive] Iniciando Pushover Adaptativo ({MAX_ROUNDS} Rondas, Dmax={max_disp})")
        
        # 0. Capturar Gravedad Base una única vez
        gravity_base_shears = {}
        try:
             floor_cols_map = self._get_colums_by_floor()
             processed_ys = sorted(floor_cols_map.keys())
             ops.reactions() 
             for y in processed_ys:
                shear = 0.0
                for tag in floor_cols_map[y]:
                     # USAMOS HELPER DINÁMICO
                    shear += self._get_element_force(tag)
                gravity_base_shears[y] = shear
        except:
             pass 

        # 0.b Pre-calcular Vector de Cargas (Fixed shape)
        initial_load_vector = {}
        print("[Adaptive] Calculando forma modal inicial...")
        # Ejecutamos modal una vez para obtener distribución
        periods, modal_data = self.run_modal_analysis(1)
        
        for item in modal_data:
            node_tag = item['tag']
            if load_pattern_type == "Modal":
                initial_load_vector[node_tag] = item['f_norm']
            else:
                initial_load_vector[node_tag] = 1.0
        
        # PRE-SETUP RECORDERS (Una vez para todo el análisis)
        self._setup_pushover_recorders()

        for i in range(MAX_ROUNDS):
            print(f"\n[Adaptative] --- ronda {i+1}")

            if i > 0:
                self.builder.log_command('loadConst', '-time', 0.0)

            #Correr pushover incrementeal
            # Pasamos gravity_base_shears y fixed_load_vector
            results = self.run_pushover(control_node_tag, disp_per_round, load_pattern_type, 
                                      n_steps=base_steps, 
                                      pattern_tag=current_pattern,
                                      initial_shears_override=gravity_base_shears,
                                      fixed_load_vector=initial_load_vector,
                                      setup_recorders=False)

            #unir resultados
            self._merge_results(consolidated, results, i)

            new_failures = self.detect_failed_floors(results)
            has_new_freeze = False
            for y_fail in new_failures:
                if y_fail not in frozen_floors:
                    #Encontrar piso inferior
                    sorted_ys = sorted(results["floors"].keys())
                    idx = sorted_ys.index(y_fail)

                    if idx > 0:
                        y_prev = sorted_ys[idx-1] 
                        self.builder.freeze_floor(y_fail, y_prev)
                        frozen_floors.add(y_fail)
                        has_new_freeze = True 
                    else: 
                        print(f"[adaptive] Ignorando fallo en piso base Y = {y_fail}")
            if any(y == sorted(results["floors"].keys())[-1] for y in new_failures):
                print("[Adaptive] La última planta ha fallado. Deteniendo análisis para evitar singularidad.")
                break
            #preaprar sigunete ronda
            current_pattern += 1

        print("[Adaptive] Análisis Finalizado.")
        return consolidated
