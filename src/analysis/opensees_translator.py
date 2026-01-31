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

    def build_model(self):
        """Construye el modelo completo en OpenSees."""
        print("[OpenSees] Iniciando construcción del modelo...")
        
            #1 Inicialización
        ops.wipe()
        ops.model('basic', '-ndm', 2, '-ndf', 3)  # 2D, 3 Grados de libertad por nodo (Dx, Dy, Rz)
        
        # 2. Definir Geometría (Nodos y Restricciones)
        self._build_nodes()
        
        # 3. Definir Materiales
        self._build_materials()
        
        # 4. Definir Secciones
        self._build_sections()
        
        # 5. Definir Transformaciones Geométricas
        # Por defecto usamos Linear con tag=1 (Suficiente para análisis de primer orden)
        ops.geomTransf('Linear', 1)
        
        # 6. Definir Elementos
        self._build_elements()
        
        # 7. Definir Patrones de Carga
        self._build_patterns()
        
        print("[OpenSees] Modelo construido exitosamente.")

    def _build_nodes(self):
        print(f"[DEBUG] --- Construcción de Nodos ---")
        for node in self.manager.get_all_nodes():
            print(f"[DEBUG] Create Node {node.tag}: ({node.x}, {node.y}) Fix: {node.fixity}")
            ops.node(node.tag, node.x, node.y)
            
            # Aplicar restricciones (Fixity)
            if any(f != 0 for f in node.fixity):
                ops.fix(node.tag, *node.fixity)

    def _build_materials(self):
        for mat in self.manager.get_all_materials():
            if isinstance(mat, Concrete01):
                # Concrete01: tag, fpc, epsc0, fpcu, epsu
                ops.uniaxialMaterial('Concrete01', mat.tag, mat.fpc, mat.epsc0, mat.fpcu, mat.epsu)
            elif isinstance(mat, Steel01):
                # Steel01: tag, Fy, E0, b
                ops.uniaxialMaterial('Steel01', mat.tag, mat.Fy, mat.E0, mat.b)

    def _build_sections(self):
        for sec in self.manager.get_all_sections():
            if isinstance(sec, FiberSection):
                # Inicia la definición de la sección Fiber (NO usar 'sections', es 'section')
                ops.section('Fiber', sec.tag)
                
                # Definir Parches (Patches)
                # Definir Parches (Patches)
                for p in sec.patches:
                    print(f"[DEBUG] Sec {sec.tag} Patch: Mat={p.material_tag} yI={p.yI} zI={p.zI} yJ={p.yJ} zJ={p.zJ}")
                    ops.patch('rect', p.material_tag, p.nIy, p.nIz, p.yI, p.zI, p.yJ, p.zJ)
                
                # Definir Capas (Layers)
                for l in sec.layers:
                    ops.layer('straight', l.material_tag, l.num_bars, l.area_bar, 
                              l.yStart, l.zStart, l.yEnd, l.zEnd)

    def _build_elements(self):
        transf_tag = 1 # Usamos la transformación definida en build_model
        
        for ele in self.manager.get_all_elements():
            if isinstance(ele, ForceBeamColumn):
                integ_tag = ele.tag 
                num_int_pts = 5
                
                # Definimos integración Lobatto asociada a la sección del elemento
                ops.beamIntegration('Lobatto', integ_tag, ele.section_tag, num_int_pts)
                
                # element forceBeamColumn $eleTag $iNode $jNode $transfTag $integrationTag <-mass $massDens>
                args = [ele.tag, ele.node_i, ele.node_j, transf_tag, integ_tag]
                
                if ele.mass_density > 0:
                    args.append('-mass')
                    args.append(ele.mass_density)
                
                ops.element('forceBeamColumn', *args)

    def _build_patterns(self):
        # Crear un TimeSeries lineal para cargas estáticas
        ts_tag = 1
        pattern_tag = 1
        ops.timeSeries('Linear', ts_tag)
        ops.pattern('Plain', pattern_tag, ts_tag)
        
        # Iterar todas las cargas
        print(f"[DEBUG] --- Construcción de Cargas ---")
        for load in self.manager.get_all_loads():
            if isinstance(load, NodalLoad):
                print(f"[DEBUG] Load Node {load.node_tag}: Fx={load.fx}, Fy={load.fy}, Mz={load.mz}")
                ops.load(load.node_tag, load.fx, load.fy, load.mz)
                
            elif isinstance(load, ElementLoad):
                print(f"[DEBUG] EleLoad {load.element_tag}: wy={load.wy}")
                ops.eleLoad('-ele', load.element_tag, '-type', '-beamUniform', load.wy, load.wx)

    def run_gravity_analysis(self):
        """Ejecuta un análisis de gravedad básico."""
        ops.system('BandGeneral')
        ops.numberer('Plain')
        ops.constraints('Plain')
        ops.integrator('LoadControl', 1.0)
        ops.algorithm('Linear')
        ops.analysis('Static')
        
        ok = ops.analyze(1)
        
        if ok == 0:
            print("[OpenSees] Análisis de Gravedad completado con EXITO")
            return True
        else:
            print(f"[OpenSees] FALLÓ el análisis de Gravedad.")
            return False

    def get_analysis_results(self):
        results = {
            "displacements":{},
            "reactions":{}
        }

        ops.reactions()
        for node in self.manager.get_all_nodes():
            #1. Desplazamientos [dx, dy, rz]
            disp = ops.nodeDisp(node.tag)
            results["displacements"][node.tag] = disp

            reac = ops.nodeReaction(node.tag)
            results["reactions"][node.tag] = reac

        return results

    def dump_model_to_file(self, filename="model_dump.out"):
        """Vuelca el estado actual de OpenSees a un archivo de texto."""
        # ops.printModel cotillea todo a la salida estándar o archivo.
        # En la versión de Python, ops.printModel('-file', filename) suele funcionar.
        ops.printModel('-file', filename)
        print(f"[OpenSees] Modelo volcado en: {filename}")