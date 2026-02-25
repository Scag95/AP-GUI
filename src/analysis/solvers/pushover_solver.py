import openseespy.opensees as ops
import os
import math
from src.analysis.manager import ProjectManager
from src.analysis.element import ForceBeamColumn
from src.analysis.solvers.failure_detector import FailureDetector
from src.analysis.solvers.load_generator import LoadPushoverGenerator


class PushoverSolver:
    def __init__(self, builder):
        self.builder = builder
        self.manager = ProjectManager.instance()
        self._element_top_section_cache = {}
        self.failure_detector = FailureDetector()
        self.load_pushover = LoadPushoverGenerator(self.builder)
        
  
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

    def run_pushover(self, control_node_tag, max_disp, load_pattern_type, n_steps = 100, pattern_tag = 2,
                     initial_shears_override=None, fixed_load_vector=None, setup_recorders=True):
        """
        Ejecuta un análisis Pushover (Displacement Control).
        Retonra una tupa (lista_desplazamiento, lista_cortanes).
        """
        self.builder.debug_file = open("model_debug.py", "a")
        
        if self.builder.debug_file: self.builder.debug_file.write(f"\n# --- PUSHOVER ANALYSIS (Node {control_node_tag}, Dmax = {max_disp}, Distribución {load_pattern_type})---\n")

        #4. Definir patrón de carga lateral (Pushover)
        ts_tag_push = pattern_tag
        pattern_tag_push = pattern_tag
        
        # Crear TimeSeries lineal única para este patrón
        self.builder.log_command('timeSeries', 'Linear', ts_tag_push)
        self.builder.log_command('pattern', 'Plain', pattern_tag_push, ts_tag_push)
  
        if fixed_load_vector:
            # Usar vector pre-calculado (consistente para Adaptive)
            for node_tag, f_val in fixed_load_vector.items():
                self.builder.log_command('load', node_tag, f_val, 0.0, 0.0)
                print(f"[DEBUG Pushover] Load Node {node_tag} FX = {f_val}")
        else:
            # Calcular en el momento (Standard)
            periods, modal_data = self.load_pushover.run_modal_analysis(1)
            
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

        # Estructura de resultados
        results = {
            "roof_disp": [],
            "base_shear": [],
            "steps": [],
            "node_displacements": [], # Añadido para animación (Video)
            "floors": {}
        }
        
        # Pre-caché estático de nodos para la iteración cinemática rápida
        all_node_tags = [n.tag for n in self.manager.get_all_nodes()]

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

        floor_meta = {}
        for y in sorted_floor_y:
            cols = floor_cols_map[y]
            if not cols:
                continue

            ref_col_tag = cols[0]
            col_obj = self.manager.get_element(ref_col_tag)
            node_i = self.manager.get_node(col_obj.node_i)
            node_j = self.manager.get_node(col_obj.node_j)
            h_floor = abs(node_j.y - node_i.y)

            #Caché de section_idx para cada columna del piso

            col_section_map = {}
            for ele_tag in cols:
                element = self.manager.get_element(ele_tag)
                n_points = int(getattr(element, 'integration_points', 0) or 0)

                section_idx = n_points if node_j.y >= node_i.y else 1
                col_section_map[ele_tag] = section_idx
            
            floor_meta[y] = {
                "cols": cols,
                "node_bot_tag": col_obj.node_i,
                "node_top_tag": col_obj.node_j,
                "h_floor": h_floor,
                "cols_section_map": col_section_map
            }

        initial_story_shears = {}
        
        if initial_shears_override:
             initial_story_shears = initial_shears_override
        else:
            print("[Pushover] Capturando estado inicial (Gravedad)...")
            ops.reactions()
            for y in sorted_floor_y:
                shear_gravity = 0.0
                
                for ele_tag, sec_idx in floor_meta[y]["cols_section_map"].items():
                    forces = ops.eleResponse(ele_tag, 'section', sec_idx, 'force')
                    if forces and len(forces) >= 3:
                        shear_gravity += float(forces[2])
                    
                initial_story_shears[y] = shear_gravity
                   
        # --- CAPTURAR ESTADO 0 (T=0, GRAVEDAD) PARA LA ANIMACIÓN ---
        results["roof_disp"].append(ops.nodeDisp(control_node_tag, 1))
        
        ops.reactions()
        initial_base_shear = 0.0
        for b_node in base_nodes:
             reacs = ops.nodeReaction(b_node)
             initial_base_shear += reacs[0]
        results["base_shear"].append(-initial_base_shear) # Suele ser 0 en X
        results["steps"].append(0)
        
        step0_disp = {}
        for n_tag in all_node_tags:
            step0_disp[n_tag] = [
                ops.nodeDisp(n_tag, 1), # dx
                ops.nodeDisp(n_tag, 2), # dy
                ops.nodeDisp(n_tag, 3)  # rz
            ]
        results["node_displacements"].append(step0_disp)
        
        # Inicializar derivas de piso en el paso 0
        for y in sorted_floor_y:
            meta = floor_meta[y]
            u_top = ops.nodeDisp(meta["node_top_tag"], 1)
            u_bot = ops.nodeDisp(meta["node_bot_tag"], 1)
            drift0 = u_top - u_bot
            results["floors"][y]["disp"].append(drift0)
            results["floors"][y]["shear"].append(0.0) # Shear net es 0 en el t=0
            results["floors"][y]["H"] = meta["h_floor"]

        # --- BUCLE DE PUSHOVER ---
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
            
            # B) Captura Cinemática (Foto del paso)
            step_disp = {}
            for n_tag in all_node_tags:
                step_disp[n_tag] = [
                    ops.nodeDisp(n_tag, 1), # dx
                    ops.nodeDisp(n_tag, 2), # dy
                    ops.nodeDisp(n_tag, 3)  # rz
                ]
            results["node_displacements"].append(step_disp)

            for y in sorted_floor_y:
                meta = floor_meta[y]
                shear_total = 0.0
                
                # 1. Fuerza local usando caché de seccion
                for ele_tag, sec_idx in meta["cols_section_map"].items():
                    forces = ops.eleResponse(ele_tag, 'section', sec_idx, 'force')
                    if forces and len(forces) >= 3:
                        shear_total += float(forces[2])

                shear_net = (shear_total - initial_story_shears[y])
                
                # 2. Deriva Relativa directa con Tags de la caché
                u_top = ops.nodeDisp(meta["node_top_tag"], 1)
                u_bot = ops.nodeDisp(meta["node_bot_tag"], 1)
                drift = u_top - u_bot
        
                results["floors"][y]["disp"].append(drift)
                results["floors"][y]["shear"].append(shear_net)
                results["floors"][y]["H"] = meta["h_floor"]
                
        return results
    
    def _merge_results(self, consolidated, new_res,cycle_idx):
        """Helper para unir los resultados"""
        consolidated["roof_disp"].extend(new_res["roof_disp"])
        consolidated["base_shear"].extend(new_res["base_shear"]) 
        consolidated.setdefault("node_displacements", []).extend(new_res.get("node_displacements", [])) # Video extension

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
        periods, modal_data = self.load_pushover.run_modal_analysis(1)
        
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

            new_failures = self.failure_detector.analyze(results)
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
