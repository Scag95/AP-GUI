import openseespy.opensees as ops
from src.analysis.manager import ProjectManager
from src.analysis.materials import Concrete01, Steel01, Elastic
from src.analysis.sections import FiberSection
from src.analysis.element import ForceBeamColumn
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
        self.log_command('geomTransf', 'Linear', 1)
        
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
            
            # Aplicar restricciones (Fixity)
            if any(f != 0 for f in node.fixity):
                self.log_command('fix', node.tag, *node.fixity)

    def _build_materials(self):
        if self.debug_file: self.debug_file.write("\n# --- Materials ---\n")

        for mat in self.manager.get_all_materials():
            if isinstance(mat, Concrete01):
                self.log_command('uniaxialMaterial', 'Concrete01', mat.tag, mat.fpc, mat.epsc0, mat.fpcu, mat.epsu)
            elif isinstance(mat, Steel01):
                self.log_command('uniaxialMaterial', 'Steel01', mat.tag, mat.Fy, mat.E0, mat.b)
            elif isinstance(mat, Elastic): # New elastic material
                 self.log_command('uniaxialMaterial', 'Elastic', mat.tag, mat.E)

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

    def _build_patterns(self):
        if self.debug_file: self.debug_file.write("\n# --- Patterns ---\n")
        
        ts_tag = 1
        pattern_tag = 1
        self.log_command('timeSeries', 'Linear', ts_tag)
        self.log_command('pattern', 'Plain', pattern_tag, ts_tag)
        
        for load in self.manager.get_all_loads():
            if isinstance(load, NodalLoad):
                self.log_command('load', load.node_tag, load.fx, load.fy, load.mz)
            elif isinstance(load, ElementLoad):
                self.log_command('eleLoad', '-ele', load.element_tag, '-type', '-beamUniform', load.wy, load.wx)
                
    def create_rigid_material_internal(self):
        """Helper to create internal rigid material without polluting Manager."""
        try:
            self.log_command('uniaxialMaterial', 'Elastic', 99999, 1.0e12) 
        except:
            pass

    def freeze_floor(self, y_roof, y_floor_below):
        """Cross-Bracing freeze logic."""
        self.create_rigid_material_internal()
        
        tol = 0.1
        nodes_top = [n for n in self.manager.get_all_nodes() if abs(n.y - y_roof) < tol]
        nodes_bot = [n for n in self.manager.get_all_nodes() if abs(n.y - y_floor_below) < tol]
        
        if not nodes_top or not nodes_bot: return
        
        nodes_top.sort(key=lambda n: n.x)
        nodes_bot.sort(key=lambda n: n.x)
        
        num_bays = min(len(nodes_top), len(nodes_bot)) - 1
        freeze_base_tag = 900000 + int(y_roof * 100)
        
        print(f"[Adaptive] Congelando piso Y={y_roof}")
        
        for i in range(num_bays):
            n_bl = nodes_bot[i]
            n_br = nodes_bot[i+1]
            n_tl = nodes_top[i]
            n_tr = nodes_top[i+1]
            
            tag1 = freeze_base_tag + (i*2)
            tag2 = freeze_base_tag + (i*2) + 1
            
            self.log_command('element', 'Truss', tag1, n_bl.tag, n_tr.tag, 1000.0, 99999)
            self.log_command('element', 'Truss', tag2, n_br.tag, n_tl.tag, 1000.0, 99999)


