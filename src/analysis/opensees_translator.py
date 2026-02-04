import openseespy.opensees as ops
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
        self._log_and_run('geomTransf', 'Linear', 1)
        
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
        self._log_and_run('algorithm', 'Linear')
        self._log_and_run('analysis', 'Static')
        
        ok = self._log_and_run('analyze', 10)
        
        if ok == 0:
            print("[OpenSees] Análisis de Gravedad completado con EXITO")
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

    def run_pushover_analysis(self, control_node_tag, max_disp, n_steps = 100):
        """
        Ejecuta un análisis Pushover (Displacement Control).
        Retonra una tupa (lista_desplazamiento, lista_cortanes).
        """
        if self.debug_file: self.debug_file.write(f"\n# --- PUSHOVER ANALYSIS (Node {control_node_tag}, Dmax = {max_disp})---\n")

        #1. Construir el modelo (Geometría, materiale, secciones, elementos)
        #Nota: Asumimos que build_model ya se llamó

        self.build_model()

        # 2. Análisis de Gravedad (Pre-Pushover)
        # Recalculamos gravedad asegurando que sea estática
        print("[Pushover] Aplicando Gravedad...")
        
        # Configuración de Gravedad
        self._log_and_run('system', 'BandGeneral')
        self._log_and_run('numberer', 'RCM')
        self._log_and_run('constraints', 'Plain')
        self._log_and_run('test', 'NormDispIncr', 1.0e-8, 6)
        self._log_and_run('algorithm', 'Newton')
        self._log_and_run('integrator', 'LoadControl', 0.1)
        self._log_and_run('analysis', 'Static')
        
        # Aplicar gravedad en 10 pasos
        ok = self._log_and_run('analyze', 10)
        if ok != 0:
            print("[Error] Gravedad falló en Pushover.")
            return None, None
            
        print("[Pushover] Gravedad OK. Iniciando Empuje Lateral...")

        #3. Mantener cargas constantesy resetear tiempo
        self._log_and_run('loadConst', '-time', 0.0)

        #4. Definir patrónde carga lateral (Pushover)
        ts_tag_push = 2
        pattern_tag_push = 2

        self._log_and_run('timeSeries', 'Linear', ts_tag_push)
        self._log_and_run('pattern', 'Plain', pattern_tag_push, ts_tag_push)

        self._log_and_run('load', control_node_tag, 1.0,0.0,0.0)

        #5. Configurar Análisis Pushover
        incr_disp = max_disp/n_steps

        self._log_and_run('integrator', 'DisplacementControl', control_node_tag,1,incr_disp)

        data_x = []
        data_y = []

        current_disp = 0.0

        nodes = self.manager.get_all_nodes()
        base_nodes = [n.tag for n in nodes if n.fixity[0] == 1]

        print(f"[Pushover] Nodos basales detectados para Cortante:{base_nodes}")

        for i in range(n_steps):
            ok = self._log_and_run('analyze',1)

            if ok !=0:
                print(f"[Pushover] Falló convergencia en paso{i}")
                break
        
            #A) Capturamos resultados
            disp = ops.nodeDisp(control_node_tag,1)

            #B) Cortante Basal (Reacciones)
            ops.reactions()
            base_shear = 0.0
            for b_node in base_nodes:
                reacs = ops.nodeReaction(b_node)
                base_shear += reacs[0]

            data_x.append(disp)
            data_y.append(-base_shear)

            if i % 10 == 0:
                print(f"[Pushover] Step {i}/{n_steps}: Disp= {disp:.4f}, Vb={-base_shear:.2f}")

        return data_x, data_y


        
