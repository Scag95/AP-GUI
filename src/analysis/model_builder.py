import openseespy.opensees as ops
from src.analysis.manager import ProjectManager
from src.analysis.materials import Concrete01, Steel01, Elastic, Hysteretic, HystereticSM
from src.analysis.sections import FiberSection
from src.analysis.element import ForceBeamColumn, ForceBeamColumnHinge
from src.analysis.loads import NodalLoad, ElementLoad

class ModelBuilder:
    def __init__(self):
        self.manager = ProjectManager.instance()
        self.debug_file = None

    def log_command(self, command, *args):
        """
        Helper method to:
        1. Write the command to model_debug.py (if open)
        2. Execute the command via openseespy
        """
        # 1. Log to file
        if self.debug_file:
            str_args = []
            for arg in args:
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
        self.log_command('wipe')
        self.log_command('model', 'basic', '-ndm', 2, '-ndf', 3)  # 2D, 3 DoF
        
        # 2. Definir Geometría (Nodos y Restricciones)
        self._build_nodes()
        
        # 3. Definir Materiales
        self._build_materials()
        
        # 4. Definir Secciones
        self._build_sections()
        
        # 5. Definir Transformaciones Geométricas
        if self.debug_file: self.debug_file.write("\n# --- Transformations ---\n")
        self.log_command('geomTransf', 'PDelta', 1)
        
        # 6. Definir Elementos
        self._build_elements()
        
        # 7. Definir Patrones de Carga
        self._build_patterns()
        
        print("[OpenSees] Modelo construido exitosamente.")

    def _build_nodes(self):
        print(f"[DEBUG] --- Construcción de Nodos ---")
        if self.debug_file: self.debug_file.write("\n# --- Nodes ---\n")
        
        for node in self.manager.get_all_nodes():
            self.log_command('node', node.tag, node.x, node.y)
            
            # Aplicar masas nodales si están definidas
            if node.mass is not None:
                self.log_command('mass', node.tag, *node.mass)

            # Aplicar restricciones (Fixity)
            if any(f != 0 for f in node.fixity):
                self.log_command('fix', node.tag, *node.fixity)

    def _build_materials(self):
        if self.debug_file: self.debug_file.write("\n# --- Materials ---\n")

        # Material Rígido para futuras Congelaciones (Cruces de San Andrés)
        if self.debug_file: self.debug_file.write("# Material Elastico Rígido para Congelaciones adaptativas\n")
        self.log_command('uniaxialMaterial', 'Elastic', 99999, 1.0e12)

        for mat in self.manager.get_all_materials():
            args = list(mat.get_opensees_args())
            
            base_tag = mat.tag
            has_minmax = getattr(mat, 'minmax', None) is not None
            
            if has_minmax:
                base_tag = mat.tag + 100000
                args[1] = base_tag
                
            self.log_command('uniaxialMaterial', *args)
            
            if has_minmax:
                min_val = mat.minmax.get("min", -0.05)
                max_val = mat.minmax.get("max", 0.05)
                self.log_command('uniaxialMaterial', 'MinMax', mat.tag, base_tag, '-min', min_val, '-max', max_val)

    def _build_sections(self):
        if self.debug_file: self.debug_file.write("\n# --- Sections ---\n")
        
        for sec in self.manager.get_all_sections():
            if isinstance(sec, FiberSection):
                # Estategia AGGREGATOR
                fiber_tag_internal = sec.tag + 10000
                shear_mat_tag = sec.tag + 20000

                self.log_command('section', 'Fiber', fiber_tag_internal)
                
                total_area = 0.0

                # Definir Parches (Patches)
                for p in sec.patches:
                    self.log_command('patch', 'rect', p.material_tag, p.nIy, p.nIz, p.yI, p.zI, p.yJ, p.zJ)
                    width = abs(p.zJ - p.zI)
                    height = abs(p.yJ - p.yI)
                    total_area += width * height

                # Definir Capas (Layers)
                for l in sec.layers:
                    self.log_command('layer', 'straight', l.material_tag, l.num_bars, l.area_bar, 
                                      l.yStart, l.zStart, l.yEnd, l.zEnd)

                G_concrete = 1.0e10
                shear_area = total_area * (5.0/6.0)
                GA = G_concrete * shear_area
                if GA <= 0: GA = 1.0e10

                self.log_command('uniaxialMaterial', 'Elastic', shear_mat_tag, GA)

                # Aggregator
                if self.debug_file: self.debug_file.write(f"# Section Aggregator {sec.tag} wrapping {fiber_tag_internal}\n")
                self.log_command('section', 'Aggregator', sec.tag, shear_mat_tag, 'Vy', '-section', fiber_tag_internal)

        # 2. Las AggregatorSection explícitas (después de las bases para respetar dependencias)
        from src.analysis.sections import AggregatorSection
        for sec in self.manager.get_all_sections():
            if isinstance(sec, AggregatorSection):
                cmds = sec.get_opensees_commands()
                for cmd in cmds:
                    self.log_command('section', *cmd)

    def _build_elements(self):
        if self.debug_file: self.debug_file.write("\n# --- Elements ---\n")
        transf_tag = 1 # Usamos la transformación definida en build_model
        
        created_integrations = {}
        next_integ_id = 1
        
        for ele in self.manager.get_all_elements():
            if isinstance(ele, ForceBeamColumn):
                # Usamos TUPLA para diferenciar (Sección 1 con 5 ptos) vs (Sección 1 con 7 ptos)
                integ_key = (ele.section_tag, ele.integration_points)
                
                if integ_key in created_integrations:
                    integ_tag = created_integrations[integ_key]
                else:
                    integ_tag = next_integ_id
                    next_integ_id += 1
                    
                    # Creamos la integración
                    # beamIntegration 'Lobatto' tag sectionTag numIntPoints
                    self.log_command('beamIntegration', 'Lobatto', integ_tag, ele.section_tag, ele.integration_points)
                    created_integrations[integ_key] = integ_tag
                
                # CREAMOS EL ELEMENTO USANDO SOLO EL TAG DE INTEGRACIÓN
                args = [ele.tag, ele.node_i, ele.node_j, transf_tag, integ_tag]
                
                if ele.mass_density > 0:
                    args.append('-mass')
                    args.append(ele.mass_density)
                args.extend(['-iter', 10, 1e-12])
                
                self.log_command('element', 'forceBeamColumn', *args)

            elif isinstance(ele, ForceBeamColumnHinge):
                # Para HingeRadau en OpenSeesPy, debes definir la integración antes:
                # beamIntegration 'HingeRadau' tag secI lpI secJ lpJ secE
                integ_tag = next_integ_id
                next_integ_id += 1
                
                self.log_command('beamIntegration', 'HingeRadau', integ_tag,
                                 ele.section_i_tag, ele.lp_i, 
                                 ele.section_j_tag, ele.lp_j, 
                                 ele.section_e_tag)

                args = [
                    ele.tag, ele.node_i, ele.node_j, ele.transf_tag, integ_tag
                ]

                if ele.mass_density > 0:
                    args.append('-mass')
                    args.append(ele.mass_density)
                args.extend(['-iter', 10, 1e-12])

                self.log_command('element', 'forceBeamColumn', *args)

    def _build_patterns(self):
        if self.debug_file: self.debug_file.write("\n# --- Patterns ---\n")
        
        for pattern in self.manager.get_all_patterns():
            # Creamos una TimeSeries para este patrón. Por simplicidad usamos Linear.
            # Usamos el propio tag del patrón como tag de la TimeSeries para evitar colisiones
            ts_tag = pattern.tag
            self.log_command('timeSeries', 'Linear', ts_tag)
            
            # Inicializamos el patrón Plain inyectándole su factor dinámico
            self.log_command('pattern', 'Plain', pattern.tag, ts_tag, '-fact', pattern.factor)
            
            # Anidamos sus cargas correspondientes
            for load in pattern.loads:
                if isinstance(load, NodalLoad):
                    self.log_command('load', load.node_tag, load.fx, load.fy, load.mz)
                elif isinstance(load, ElementLoad):
                    self.log_command('eleLoad', '-ele', load.element_tag, '-type', '-beamUniform', load.wy, load.wx)
                


    def freeze_floor(self, deformed_state: list, method="spring"):
        """
        Freeze logic SRP: Recibe el estado deformado desde el Solver.
        Inyecta restricciones en el modelo (Opensees) temporalmente.
        """

        if not deformed_state:
            return

        print(f"[Adaptative] Congelando piso ({len(deformed_state)} nodos). Método: {method}")

        created_nodes = []

        if method == "spring":

            # --- FLAG DE PRUEBA: True = nodo fantasma en coordenadas ORIGINALES del nodo real (sin warning)
            #                     False = nodo fantasma en coordenadas DEFORMADAS (comportamiento anterior)
            USE_ORIGINAL_COORDS = True

            # Creamos el material Uniforme 
            try:
                self.log_command('uniaxialMaterial', 'Elastic', 999999, 1.0e10)
            except:
                pass

            for i, node_data in enumerate(deformed_state):
                real_tag = node_data["real_node_tag"]

                ghost_tag = 2000000 + (real_tag * 10)
                spring_ele_tag = 3000000 + (real_tag * 10)

                # Decidir coordenadas del fantasma según el flag
                if USE_ORIGINAL_COORDS:
                    node_obj = self.manager.get_node(real_tag)
                    ghost_x, ghost_y = node_obj.x, node_obj.y
                else:
                    ghost_x, ghost_y = node_data["def_x"], node_data["def_y"]

                #1. Crear el nodo fantasma en la posición elegida
                self.log_command('node', ghost_tag, ghost_x, ghost_y)

                #2. Fijar el nodo fantasma
                self.log_command('fix', ghost_tag, 1, 1, 1)

                #3. Conectar el nodo real con el fantasma usando zeroLength solo en la dirección x
                self.log_command('element', 'zeroLength', spring_ele_tag, ghost_tag, real_tag, '-mat', 999999, '-dir', 1)

                #4. Guardamos el anclaje creado
                created_nodes.append(ghost_tag)

        elif method == "fix":
            # Creamos una "caja fuerte" (Pattern estático y permanente) para estas anclas
            # Usamos un ID derivado del nodo para que no choque si congelamos varias plantas
            safe_pattern_tag = 8000 + int(deformed_state[0]["real_node_tag"])
            self.log_command('pattern', 'Plain', safe_pattern_tag, 1)
            
            for node_data in deformed_state:
                real_tag = node_data["real_node_tag"]
                # 1. Leemos dónde está el nodo en este instante milimétrico
                current_disp_x = ops.nodeDisp(real_tag, 1)
                # 2. Le clavamos una tuerca irrompible exactamente en ese punto
                self.log_command('sp', real_tag, 1, current_disp_x)


        return created_nodes 

            

