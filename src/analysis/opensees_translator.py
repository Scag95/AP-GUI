import openseespy.opensees as ops
import math
from src.analysis.manager import ProjectManager
from src.analysis.materials import Concrete01, Steel01
from src.analysis.sections import FiberSection
from src.analysis.element import ForceBeamColumn
from src.analysis.loads import NodalLoad, ElementLoad

class OpenSeesTranslator:
    """
    Clase encargada de traducir el modelo de objetos de AP-GUI
    a comandos de OpenSees (openseespy).
    """
    def __init__(self):
        self.manager = ProjectManager.instance()
        self.debug_file = None

    def _log_and_run(self, command, *args):
        """
        Helper method to:
        1. Write the command to model_debug.py (if open)
        2. Execute the command via openseespy
        """
        # 1. Log to file
        if self.debug_file:
            # Format arguments: strings get quoted, numbers don't
            str_args = []
            for arg in args:
                # Use repr() to quote strings (e.g. 'Linear' -> "'Linear'")
                # and leave numbers as is (e.g. 1 -> 1)
                str_args.append(repr(arg))
            
            line = f"{command}({', '.join(str_args)})"
            self.debug_file.write(line + "\n")
            self.debug_file.flush()

        # 2. Execute
        func = getattr(ops, command)
        return func(*args)

    def build_model(self):
        """Construye el modelo completo en OpenSees."""
        print("[OpenSees] Iniciando construcción del modelo...")
        
        # Create/Overwrite debug file
        self.debug_file = open("model_debug.py", "w")
        self.debug_file.write("# Auto-generated debug script from AP-GUI\n")
        self.debug_file.write("from openseespy.opensees import *\n\n")

        # 1 Inicialización
        self._log_and_run('wipe')
        self._log_and_run('model', 'basic', '-ndm', 2, '-ndf', 3)  # 2D, 3 DoF
        
        # 2. Definir Geometría (Nodos y Restricciones)
        self._build_nodes()
        
        # 3. Definir Materiales
        self._build_materials()
        
        # 4. Definir Secciones
        self._build_sections()
        
        # 5. Definir Transformaciones Geométricas
        # Por defecto usamos Linear con tag=1
        if self.debug_file: self.debug_file.write("\n# --- Transformations ---\n")
        self._log_and_run('geomTransf', 'PDelta', 1)
        
        # 6. Definir Elementos
        self._build_elements()
        
        # 7. Definir Patrones de Carga
        self._build_patterns()
        
        print("[OpenSees] Modelo construido exitosamente.")

    def _build_nodes(self):
        print(f"[DEBUG] --- Construcción de Nodos ---")
        if self.debug_file: self.debug_file.write("\n# --- Nodes ---\n")
        
        for node in self.manager.get_all_nodes():
            print(f"[DEBUG] Create Node {node.tag}: ({node.x}, {node.y}) Fix: {node.fixity}")
            self._log_and_run('node', node.tag, node.x, node.y)
            
            # Aplicar restricciones (Fixity)
            if any(f != 0 for f in node.fixity):
                self._log_and_run('fix', node.tag, *node.fixity)

    def _build_materials(self):
        if self.debug_file: self.debug_file.write("\n# --- Materials ---\n")

        for mat in self.manager.get_all_materials():
            if isinstance(mat, Concrete01):
                # Concrete01: tag, fpc, epsc0, fpcu, epsu
                self._log_and_run('uniaxialMaterial', 'Concrete01', mat.tag, mat.fpc, mat.epsc0, mat.fpcu, mat.epsu)
            elif isinstance(mat, Steel01):
                # Steel01: tag, Fy, E0, b
                self._log_and_run('uniaxialMaterial', 'Steel01', mat.tag, mat.Fy, mat.E0, mat.b)

    def _build_sections(self):
        if self.debug_file: self.debug_file.write("\n# --- Sections ---\n")
        

        for sec in self.manager.get_all_sections():
            if isinstance(sec, FiberSection):
                #Estategia AGGREGATOR:
                # 1. Creamos la sección Fiber real en un tag auxiliar
                # 2. Creamos un materials Elastic para cortante (G*Av)
                # 3. Creamos el Aggregator en el tag ORIGINAL usando los anteriores

                fiber_tag_internal = sec.tag + 10000
                shear_mat_tag = sec.tag + 20000

                # Inicia la definición de la sección Fiber
                self._log_and_run('section', 'Fiber', fiber_tag_internal)
                
                total_area = 0.0


                # Definir Parches (Patches)
                for p in sec.patches:
                    # ops.patch('rect', matTag, numSubdivY, numSubdivZ, yI, zI, yJ, zJ)
                    print(f"[DEBUG] Sec {sec.tag} Patch: Mat={p.material_tag} yI={p.yI} zI={p.zI} yJ={p.yJ} zJ={p.zJ}")
                    self._log_and_run('patch', 'rect', p.material_tag, p.nIy, p.nIz, p.yI, p.zI, p.yJ, p.zJ)
                
                    #Sumar área para cálculo de cortantes
                    width = abs(p.zJ - p.zI)
                    height = abs(p.yJ - p.yI)
                    total_area += width * height



                # Definir Capas (Layers)
                for l in sec.layers:
                    # ops.layer('straight', matTag, numBars, areaBar, yStart, zStart, yEnd, zEnd)
                    self._log_and_run('layer', 'straight', l.material_tag, l.num_bars, l.area_bar, 
                                      l.yStart, l.zStart, l.yEnd, l.zEnd)

                G_concrete = 1.0e10
                shear_area = total_area * (5.0/6.0)
                GA = G_concrete * shear_area

                #Evitar GA=0 si no hay parches
                if GA <=0: GA = 1.0e10

                self._log_and_run('uniaxialMaterial', 'Elastic', shear_mat_tag, GA)

                #3. Crear Aggregator (Tag Original) ->[Fiber + Vy]
                # section Aggregator $secTag $matTag $dof -'section' $sectionTag
               
               

               #[DEBUG]
                if self.debug_file: self.debug_file.write(f"# Section Aggregator {sec.tag} wrapping {fiber_tag_internal}\n")
                self._log_and_run('section', 'Aggregator', sec.tag, shear_mat_tag, 'Vy', '-section', fiber_tag_internal)

    def _build_elements(self):
        if self.debug_file: self.debug_file.write("\n# --- Elements ---\n")
        transf_tag = 1 # Usamos la transformación definida en build_model
        
        # Diccionario para evitar duplicar beamIntegration: {section_tag: integration_tag}
        created_integrations = {}
        
        for ele in self.manager.get_all_elements():
            if isinstance(ele, ForceBeamColumn):
                # La integración depende de la sección. Si ya creamos una para esta sección, la reutilizamos.
                if ele.section_tag in created_integrations:
                    integ_tag = created_integrations[ele.section_tag]
                else:
                    # Crear nueva integración usando el ID de la sección (asumiendo 1 a 1)
                    integ_tag = ele.section_tag 
                    num_int_pts = 5
                    self._log_and_run('beamIntegration', 'Lobatto', integ_tag, ele.section_tag, num_int_pts)
                    created_integrations[ele.section_tag] = integ_tag
                
                # element forceBeamColumn $eleTag $iNode $jNode $transfTag $integrationTag <-mass $massDens> <-iter $maxIters $tol>
                args = [ele.tag, ele.node_i, ele.node_j, transf_tag, integ_tag]
                
                if ele.mass_density > 0:
                    args.append('-mass')
                    args.append(ele.mass_density)

                # Añadir iteraciones para precisión en fuerzas internas
                args.extend(['-iter', 10, 1e-12])
                
                self._log_and_run('element', 'forceBeamColumn', *args)

    def _build_patterns(self):
        if self.debug_file: self.debug_file.write("\n# --- Patterns ---\n")
        
        # Crear un TimeSeries lineal para cargas estáticas
        ts_tag = 1
        pattern_tag = 1
        self._log_and_run('timeSeries', 'Linear', ts_tag)
        self._log_and_run('pattern', 'Plain', pattern_tag, ts_tag)
        
        print(f"[DEBUG] --- Construcción de Cargas ---")
        for load in self.manager.get_all_loads():
            if isinstance(load, NodalLoad):
                print(f"[DEBUG] Load Node {load.node_tag}: Fx={load.fx}, Fy={load.fy}, Mz={load.mz}")
                self._log_and_run('load', load.node_tag, load.fx, load.fy, load.mz)
                
            elif isinstance(load, ElementLoad):
                print(f"[DEBUG] EleLoad {load.element_tag}: wy={load.wy}")
                self._log_and_run('eleLoad', '-ele', load.element_tag, '-type', '-beamUniform', load.wy, load.wx)

    def run_gravity_analysis(self):
        """Ejecuta un análisis de gravedad básico."""
        if self.debug_file: self.debug_file.write("\n# --- Analysis ---\n")
        
        self._log_and_run('system', 'UmfPack')
        self._log_and_run('numberer', 'RCM')
        self._log_and_run('constraints', 'Plain')
        self._log_and_run('integrator', 'LoadControl', 0.1)
        self._log_and_run('algorithm', 'Newton')
        self._log_and_run('analysis', 'Static')
        
        ok = self._log_and_run('analyze', 10)
        
        if ok == 0:
            print("[OpenSees] Análisis de Gravedad completado con EXITO")
            self._log_and_run('loadConst', '-time', 0.0)
            return True
        else:
            print(f"[OpenSees] FALLÓ el análisis de Gravedad.")
            return False

    def get_analysis_results(self):
        results = {
            "displacements":{},
            "reactions":{},
            "element_forces":{}
        }
        #1. Desplazamientos y reacciones en nodos.
        ops.reactions()
        for node in self.manager.get_all_nodes():
            #1. Desplazamientos [dx, dy, rz]
            disp = ops.nodeDisp(node.tag)
            results["displacements"][node.tag] = disp

            reac = ops.nodeReaction(node.tag)
            results["reactions"][node.tag] = reac

        #2. Fuerza en los elementos.
        for ele in self.manager.get_all_elements():
            try:
                sections_data = []
                num_int_pts = 5

                for i in range(1, num_int_pts+1):
                    sec_forces = ops.eleResponse(ele.tag, 'section', i, 'force')
                    sections_data.append({
                        "i": i,
                        "P": sec_forces[0],
                        "M": sec_forces[1],
                        "V": sec_forces[2]
                    })

                results["element_forces"][ele.tag] = sections_data
                
            except Exception as e:
                print(f"[Error] fuerzas elemento {ele.tag}: {e}")

        return results

    def dump_model_to_file(self, filename="model_dump.out"):
        """Vuelca el estado actual de OpenSees a un archivo de texto."""
        ops.printModel('-file', filename)
        print(f"[OpenSees] Modelo volcado en: {filename}")

    def run_modal_analysis(self, n_modes):
        #Cargamos los nodos del proyecto.
        nodes = self.manager.get_all_nodes()
        if self.debug_file: self.debug_file.write("\n# --- Analysis Modal ---\n")
        lambdas = ops.eigen(n_modes)
        self._log_and_run('eigen', n_modes)

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

        #2. Ordenamos lo spiso y seleccionamos un nodo Master
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
            roof_phi = modal_data[-1]['phi_x']

            if abs(roof_phi) < 1e-9: roof_phi = 1.0

            for item in modal_data:
                item['phi_norm'] = item['phi_x']/roof_phi
                print(f" -> norm Phi: {item['phi_norm']:.4f}")

        return periods, modal_data

    def _get_colums_by_floor(self):
        columns_by_floor = {}
        tolerance = 0.05

        elements = self.manager.get_all_elements()

        for ele in elements:
            #Obtener nodos
            ni = self.manager.get_node(ele.node_i)
            nj = self.manager.get_node(ele.node_j)

            if not ni or not nj: continue


            dy = abs(nj.y - ni.y)
            dx = abs(nj.x - ni.x)

            if dy > tolerance and dx < tolerance: # Es vertical
                # Identificar 'techo' de este elemento (el Y mayor)
                y_ceil = max(ni.y, nj.y)
                
                # Agrupar por esa altura
                found_key = None
                for key in columns_by_floor.keys():
                    if abs(key - y_ceil) < tolerance:
                        found_key = key
                        break
                
                if found_key is not None:
                    columns_by_floor[found_key].append(ele.tag)
                else:
                    columns_by_floor[y_ceil] = [ele.tag]
                    
        return columns_by_floor

    def run_pushover_analysis(self, control_node_tag, max_disp, load_pattern_type, n_steps = 100):
        """
        Ejecuta un análisis Pushover (Displacement Control).
        Retonra una tupa (lista_desplazamiento, lista_cortanes).
        """

        # Limpieza preventiva por si es re-ejecución
        try:
            ops.remove('loadPattern', 2)  # pattern tag 2
            ops.remove('timeSeries', 2)   # timeSeries tag 2
        except:
            pass # Si no existen, no pasa nada
        
        self.debug_file = open("model_debug.py", "a")
        if self.debug_file: self.debug_file.write(f"\n# --- PUSHOVER ANALYSIS (Node {control_node_tag}, Dmax = {max_disp}, Distribución {load_pattern_type})---\n")

        #4. Definir patrónde carga lateral (Pushover)
        ts_tag_push = 2
        pattern_tag_push = 2
        

        
        self._log_and_run('pattern', 'Plain', pattern_tag_push, 1)

            
        periods, modal_data = self.run_modal_analysis(1)
        if load_pattern_type == "Modal":

            for item in modal_data:
                f_val = item['phi_norm']
                node_tag = item['tag']
                self._log_and_run('load', node_tag, f_val, 0.0, 0.0)
                print(f"[DEBUG Pushover] Load Node {node_tag} FX = {f_val}")
        else:
            for item in modal_data:
                node_tag = item['tag']
                self._log_and_run('load', node_tag, 1.0, 0.0, 0.0)



        #5. Identificar columnas por piso (Pre-Proceso) 
        floor_cols_map = self._get_colums_by_floor()
        sorted_floor_y = sorted(floor_cols_map.keys())

        #Estructura de resultados
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

        self._log_and_run('integrator', 'DisplacementControl', control_node_tag,1,incr_disp)
        self._log_and_run('test','NormDispIncr', 1e-06, 100)
        self._log_and_run('algorithm', 'KrylovNewton')
        self._log_and_run('analysis', 'Static')
        

        # Detectar bases globales (reacción total)
        nodes = self.manager.get_all_nodes()
        base_nodes = [n.tag for n in nodes if n.fixity[0] == 1]

        initial_story_shears = {}
        print("[Pushover] Capturando estado inicial (Gravedad)...")
        ops.reactions()

        for y in sorted_floor_y:
            shear_gravity = 0.0
            cols = floor_cols_map[y]
            for ele_tag in cols:
                forces = ops.eleResponse(ele_tag, 'section', 5, 'force')
                print(f"{forces[2]} : elemento {ele_tag}")
                shear_gravity += forces[2]
                
            initial_story_shears[y] = shear_gravity
                   
        for i in range(1, n_steps + 1):
            ok = ops.analyze(1)
            #ok = self._log_and_run('analyze', 1)
            
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
                    forces = ops.eleResponse(ele_tag, 'section', 5, 'force')
                    shear_total += forces[2]

                shear_net = (shear_total - initial_story_shears[y])
                ref_col_tag = cols[0]
                col_obj = self.manager.get_element(ref_col_tag)
                
                # Nodos superior e inferior del piso
                tag_top = col_obj.node_j
                tag_bot = col_obj.node_i
                # Calcular Deriva Relativa (Drift) = U_top - U_bot
                u_top = ops.nodeDisp(tag_top, 1)
                u_bot = ops.nodeDisp(tag_bot, 1)
                drift = u_top - u_bot
        
                results["floors"][y]["disp"].append(drift)
                
                # Cortante: Suma de fuerzas en extremo J (Vj)
                # Nota: OpenSees Vj suele ser negativo de la fuerza aplicada, verifica el signo si es necesario.
                results["floors"][y]["shear"].append(shear_net)
                
                # --- DEBUG TEMPORAL ---
                if i <= 5 and y == 3.0: 
                    print(f"[DEBUG STEP {i}] Piso Y={y}: Drift={drift:.6f}, V_net={shear_net:.4f} (V_tot={shear_total:.4f}, V_inic={initial_story_shears[y]:.4f})")
                    # Ver fuerzas individuales
                    for ele_tag in cols:
                        f = ops.eleResponse(ele_tag, 'force')
                        print(f"   -> Ele {ele_tag}: V_top_raw={f[4]:.4f}")


            if i % 10 == 0:
                print(f"[Pushover] Step {i}: D={current_roof_disp:.4f}, Vb={-current_base_shear:.2f}")

        return results


        
