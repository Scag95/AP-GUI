import openseespy.opensees as ops
from src.analysis.manager import ProjectManager

class GravitySolver:
    def __init__(self, builder):
        self.builder = builder
        self.manager = ProjectManager.instance()

    def run(self):
        """Ejecuta un análisis de gravedad básico."""
        if self.builder.debug_file: 
            self.builder.debug_file.write("\n# --- Gravity Analysis ---\n")
        
        self.builder.log_command('system', 'UmfPack')
        self.builder.log_command('numberer', 'RCM')
        self.builder.log_command('constraints', 'Plain')
        self.builder.log_command('integrator', 'LoadControl', 0.1)
        self.builder.log_command('algorithm', 'Newton')
        self.builder.log_command('analysis', 'Static')
        
        ok = self.builder.log_command('analyze', 10)
        
        if ok == 0:
            print("[OpenSees] Análisis de Gravedad completado con EXITO")
            self.builder.log_command('loadConst', '-time', 0.0)
            return True
        else:
            print(f"[OpenSees] FALLÓ el análisis de Gravedad.")
            return False

    def get_results(self):
        results = {
            "displacements":{},
            "reactions":{},
            "element_forces":{}
        }
        # 1. Desplazamientos y reacciones en nodos.
        ops.reactions()
        for node in self.manager.get_all_nodes():
            disp = ops.nodeDisp(node.tag)
            reac = ops.nodeReaction(node.tag)
            results["displacements"][node.tag] = disp
            results["reactions"][node.tag] = reac

        # 2. Fuerza en los elementos.
        for ele in self.manager.get_all_elements():
            try:
                sections_data = []
                num_int_pts = 5

                for i in range(1, num_int_pts+1):
                    sec_forces = ops.eleResponse(ele.tag, 'section', i, 'force')
                    # Validation needed in case aggregation adds more components
                    # But usually first 3 match logical P, M, V
                    sections_data.append({
                        "i": i,
                        "P": sec_forces[0],
                        "M": sec_forces[1], # M usually 2nd
                        "V": sec_forces[2]  # V usually 3rd
                    })

                results["element_forces"][ele.tag] = sections_data
            except Exception as e:
                print(f"[Error] fuerzas elemento {ele.tag}: {e}")
        
        return results
