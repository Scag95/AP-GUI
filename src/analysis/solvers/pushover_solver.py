import openseespy.opensees as ops
from src.analysis.manager import ProjectManager
from src.analysis.solvers.failure_detector import FailureDetector
from src.analysis.solvers.load_generator import LoadPushoverGenerator
from src.analysis.solvers.pushover_configurator import PushoverConfigurator

class PushoverSolver:
    """
    Organizador del Análisis Pushover.
    Coordina al Builder, Generador de cargas, Motor de configuración y Dectector de Fallos.
    """

    def __init__(self, builder):
        self.builder = builder
        self.manager = ProjectManager.instance()

        self.load_generator = LoadPushoverGenerator(self.builder)
        self.configurator = PushoverConfigurator(self.builder)
        self.failure_detector = FailureDetector()
        self.acntive_support_nodes = []


    def _initialize_results_structure(self):
        """ Helpers para preparar los diccionarios limpios antes de un run."""
        results = {
            "roof_disp": [],
            "base_shear": [],
            "steps": [],
            "node_displacements": [],
            "failed_floors": [],
            "floors": {}
        }

        floor_data = self.manager.get_floor_data()
        if floor_data:
            base_y = min(floor_data.keys())
            for y in sorted(floor_data.keys()):
                if y > base_y: # Ignorar la planta base (y=0)
                    results["floors"][y] = {"disp": [], "shear":[], "H": 0.0}


        return results
    
    def _initialize_supports(self):
        """Reinicia la lista de apoyos leyendo los anclajes originales"""

        self.active_support_nodes = []
        floor_data = self.manager.get_floor_data()
        if not floor_data: return
        
        base_y = min(floor_data.keys())
        for n in floor_data[base_y]["nodes"]:
            if n.fixity[0] == 1:
                self.active_support_nodes.append(n.tag)


    def _apply_load_pattern(self, load_pattern_type: str, pattern_tag: int, precalc_vector=None):
        """Helper para delegar la creación del patrón al generador."""
        #1. Definir Pattern en Opensees a través del configurador / builder
        self.builder.log_command('timeSeries', 'Linear', pattern_tag)
        self.builder.log_command('pattern', 'Plain', pattern_tag, pattern_tag)

        #2. Pedirle al generador que haga la matemática (solo si no tenemos vector precalculado)
        if precalc_vector is None:
            result_pattern = self.load_generator.generate_pattern(pattern_type=load_pattern_type)
            force_vector = result_pattern.force_vector
        else:
            force_vector = precalc_vector

        #3. Aplicar las cargas en OpenSees devueltas por el generador (o el vector forzado)
        for node_tag, force in force_vector.items():
            if abs(force) > 1e-9:
                self.builder.log_command('load', node_tag, force, 0.0, 0.0)

    def _capture_step_state(self, results_dict, step_idx, control_node_tag):
        """ Helper para extrae desplazamientos y reaccionnes del modelo actual en OpenSees."""

        #1. Globales
        results_dict["steps"].append(step_idx)
        results_dict["roof_disp"].append(ops.nodeDisp(control_node_tag,1))
        results_dict["base_shear"].append(self._get_base_shear())

        #2.
        results_dict["node_displacements"].append(self._get_all_node_displacements())

        #3. Estado de Meacanismos por planta
        self._capture_floor_data(results_dict)
        

    def _get_base_shear(self) -> float:
        """Suma las reacciones en X de todos los nodos anclados a tierra."""
        ops.reactions()

        total_shear = 0.0

        for b_node in self.active_support_nodes:
            reacs = ops.nodeReaction(b_node)

            if reacs:
                # Los apoyos fantasma devuelven tracción en el resorte con signo opuesto,
                # por lo que invertimos su reacción.
                if b_node >= 2000000:
                    total_shear -= reacs[0]
                else:
                    total_shear += reacs[0]

        return -total_shear 

    def _get_all_node_displacements(self) -> dict:
        """Captura (dx, dy, rz) de todos los nodos para la animación."""
        step_disp = {}
    
        for n in self.manager.get_all_nodes():
            step_disp[n.tag] = ops.nodeDisp(n.tag)

        return step_disp

    def _capture_floor_data(self, results_dict):
        """Calcula el drift y el contante de cada planta y lo guarda"""

        floor_data = self.manager.get_floor_data()
        if not floor_data: return

        base_y = min(floor_data.keys())

        for y, data in floor_data.items():
            if y <= base_y: continue # Ignorar la planta base

            cols = data.get("columns", [])
            if not cols: continue

            #1 calcular cortante de la planta (Sumando cortantes en las columnas)
            shear_total = 0.0
            for col in cols:
                #Obtenemos nodos de la columna para saber cual es la base y el top
                node_i = self.manager.get_node(col.node_i)
                node_j = self.manager.get_node(col.node_j)
                n_points = int(getattr(col, 'integration_points', 0) or 0)

                # El cortante suele eestar en la sección más baja o alta
                sec_idx = n_points if node_j.y >= node_i.y else 1
                forces = ops.eleResponse(col.tag, 'section', sec_idx, 'force')

                if forces and len(forces) >= 3:
                    shear_total += float(forces[2]) #El cortante se encuentra en esa posición

            #2. Clacular Deriva Relativa (U-top - U_bot) de la primera columna como representante

            ref_col = cols[0]
            node_top = self.manager.get_node(ref_col.node_j)
            node_bot = self.manager.get_node(ref_col.node_i)

            h_floor = abs(node_top.y - node_bot.y)
            u_top = ops.nodeDisp(node_top.tag, 1)
            u_bot = ops.nodeDisp(node_bot.tag, 1)
            drift = u_top - u_bot

            #3. Guardar en el dict
            results_dict["floors"][y]["disp"].append(drift)
            results_dict["floors"][y]["shear"].append(shear_total)
            results_dict["floors"][y]["H"] = h_floor

    def run_pushover(self, control_node_tag, max_disp, n_steps, load_pattern_type, failure_detector=None, frozen_floors=None, pattern_tag=200, precalc_vector=None):
        """
        Ejecución limpia de un Pushover Monotónico estándar.
        """

        if frozen_floors is None:
            frozen_floors = set()

        self._initialize_supports()
        results = self._initialize_results_structure()
        

        #1. Aplicar Cargas 
        self._apply_load_pattern(load_pattern_type, pattern_tag=pattern_tag, precalc_vector=precalc_vector)

        #2. Configurar motor matématico
        incr_disp = max_disp/n_steps
        self.configurator.setup_static_analysis(control_node_tag, incr_disp)

        #3. Bucle Estático Principal
        for i in range(1, n_steps+1):
            ok = self.configurator.run_static_step_with_fallback()
            if ok !=0:
                print(f"[Pushover] 🔴 Fin prematuro por falta de convergencia en paso {i}.")
                break

            self._capture_step_state(results, i, control_node_tag)

            #4. Evaluación paso a paso:

            if failure_detector:
                fallos_dectectados = failure_detector.analyze(results)
                nuevos_fallos = [f for f in fallos_dectectados if f.y_level not in frozen_floors]
                
                if nuevos_fallos:
                    print(f"[Pushover] ⚠️ Fallo estructural detectado en vivo (Y={nuevos_fallos[0].y_level}) en paso {i}. Rompiendo bucle.")
                    break

        return results


    def _merge_results(self, consolidated: dict, new_res: dict, cycle_idx: int):
        """Helper para unir los resultados de una ronda adaptativa a la historia global"""
        consolidated["roof_disp"].extend(new_res["roof_disp"])
        consolidated["base_shear"].extend(new_res["base_shear"])
        consolidated.setdefault("node_displacements",[]).extend(new_res.get("node_displacements",[]))

        count = len(new_res["roof_disp"])
        consolidated["cycle_id"].extend([cycle_idx] * count)

        last_step = consolidated["steps"][-1] if consolidated["steps"] else 0
        new_steps = [s + last_step for s in new_res["steps"]]
        consolidated["steps"].extend(new_steps)

        for y, data in new_res["floors"].items():
            if y not in consolidated["floors"]:
                consolidated["floors"][y] = {"disp": [], "shear": [], "H": data.get("H",0.0)}
                consolidated["floors"][y]["disp"].extend(data["disp"])
                consolidated["floors"][y]["shear"].extend(data["shear"])



    def _get_deformed_floor_state(self, y_level: float) -> list:
        """
        Extrae las coordenadas espaciales deformadas actuales de todos los nodos en una cota dada.
        Retorna: Lista de diccionarios con el tag real del nodo y sus nuevas coordenadas(X,Y).
        """

        floor_data = self.manager.get_floor_data()
        if y_level not in floor_data:
            return []

        deformed_nodes = []

        for node in floor_data[y_level]["nodes"]:
            #1. Leemos el desplazamiento deformado DOF 1 (X) y DOF (Y)
            u_x = ops.nodeDisp(node.tag, 1)
            u_y = ops.nodeDisp(node.tag, 2)

            #2. Calculamos la coordenada real actual sumando la posición original
            def_x = node.x + u_x
            def_y = node.y + u_y

            #3. Guardamos el diccionario para el "contrato"
            deformed_nodes.append({
                "real_node_tag": node.tag,
                "def_x": def_x,
                "def_y": def_y
            })        
        
        return deformed_nodes




    def run_adaptative_pushover(self, control_node_tag, max_disp, steps, load_pattern_type, sensitivity = None, freeze_method="spring"):
        """
        Análisis Pushover secuancial
        Corre Pushover iterativamente delegando la matemática; cuando un planta colapsa, la congela y reinicia.
        """
        MAX_ROUND = len(self.manager.get_floor_data())
        disp_per_round = max_disp

        #1. Preparar el FailureDetector
        kwargs = {}
        if sensitivity is not None: kwargs['sensitivity'] = sensitivity/100.0
        self.failure_detector = FailureDetector(**kwargs)
        self._initialize_supports()

        #2. Diccionario consolidado 
        consolidated = {
            "roof_disp": [], "base_shear": [], "steps": [],
            "cycle_id": [], "node_displacements": [], "floors": {}, "failed_floors": []
        }

        frozen_floors = set()
        print(f"[Adaptative] Iniciando Pushover Adaptativo ({MAX_ROUND} posibles fallos, Dmax={max_disp})")

        # Novedad: Precalcular y congelar la distribución de carga original
        print(f"[Adaptive] Precalculando patrón modal original ({load_pattern_type}) intacto.")
        result_pattern = self.load_generator.generate_pattern(pattern_type=load_pattern_type)
        base_force_vector = result_pattern.force_vector

        # --- BUCLE DE RONDAS ADAPTATIVAS ---
        for round_idx in range(MAX_ROUND):
            print(f"\n[Adaptive] --- Ronda {round_idx + 1}")

            if round_idx > 0:
                self.builder.log_command('loadConst', '-time', 0.0)

            current_pattern_tag = 200 + round_idx
            # 3. Correr un Pushover Estándar (Delegar el Empuje)
            round_results = self.run_pushover(
                control_node_tag=control_node_tag, 
                max_disp=disp_per_round, 
                n_steps=steps, 
                load_pattern_type=load_pattern_type,
                failure_detector=self.failure_detector,
                frozen_floors=frozen_floors, pattern_tag=current_pattern_tag,
                precalc_vector=base_force_vector # Pasamos el vector inmutable
            )

            #4. Fusión de Datos
            self._merge_results(consolidated, round_results, round_idx)

            #5. Evaluar Fallos
            nuevos_fallos = [f.y_level for f in self.failure_detector.analyze(consolidated) if f.y_level not in frozen_floors]

            if not nuevos_fallos:
                print("[Adaptive] Ronda terminada sin nuevos mecanismos identificables u objetivo alcanzado.")
                break

            #6. Congelar la planta
            sorted_ys = sorted(self.manager.get_floor_data().keys())
            
            for y_fail in nuevos_fallos:
                idx = sorted_ys.index(y_fail)
                print(f"[Adaptive] ⚠️ Fallo detectado en cota Y={y_fail}. Aplicando Freeze='{freeze_method}'")

                # REFACTOR SRP: Extraermos el estacio espacial de los nodos
                deformed_state = self._get_deformed_floor_state(y_fail)


                # Recibimos los tags de los fantasmas recién anclados a la pared!
                new_ghosts = self.builder.freeze_floor(deformed_state, freeze_method)
                
                # Actualizamos nuestra memoria global de apoyos activos
                self.active_support_nodes.extend(new_ghosts)
                
                frozen_floors.add(y_fail)
                consolidated["failed_floors"].append(y_fail)

            # Check fatal: Si el fallo incluyó el techo supremo, la estructura es irreparable.
            if sorted_ys[-1] in nuevos_fallos:
                 print("[Adaptive] La última planta estructural ha fallado rotundo. Colapso Total.")
                 break

        print("[Adaptive] Análisis Finalizado Exitosamente.")

        return consolidated                