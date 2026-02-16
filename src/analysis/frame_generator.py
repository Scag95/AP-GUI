from src.analysis.node import Node
from src.analysis.element import ForceBeamColumn
from src.analysis.manager import ProjectManager

class FrameGenerator:
    def __init__(self):
        self.manager = ProjectManager.instance()

    def generate_2d_frame (self,stories, bays, story_height, bay_width,
                           beam_sec_tag,col_sec_tag, integration_points, add_base_beams = False, transf_tag=1):
        grid_nodes = {}
        #1. Guardamos los node en una matríz temporar para facilitar la conexíon
        # grid_node[i][j] guardará el objeto Node en la posición (i,j)
        # --- Generar Nodos --- 
        for i in range(bays + 1):
            for j  in range (stories + 1):
                x = round(i * bay_width, 6)
                y = round(j * story_height, 6)

                #Obtener Nuevo ID desde el manager
                tag = self.manager.get_next_node_tag()

                #Crear instancia de Node
                node = Node(tag,x,y)

                #Guardar en manager y en nuestra grilla temporal
                self.manager.add_node(node)
                grid_nodes[(i,j)] = node

        # Generar elementos (Columnas y vigas)
        # Columnas
        for i in range (bays + 1):
            for j in range(stories):
                node_bottom = grid_nodes[(i,j)]
                node_top = grid_nodes [(i,j+1)]
                ele_tag = self.manager.get_next_element_tag()
                col = ForceBeamColumn(ele_tag, node_bottom.tag, node_top.tag, col_sec_tag, transf_tag,integration_points, mass_density=0.0)
                
                # Asignar Densidad de Masa desde la Sección
                col_section = self.manager.get_section(col_sec_tag)
                if col_section:
                    col.mass_density = col_section.get_mass_per_length(self.manager)
                    
                self.manager.add_element(col)


        start_floor = 0 if add_base_beams else 1
        #Vigas
        for j in range(start_floor, stories + 1):
            for i in range(bays):
                node_left = grid_nodes[(i,j)]
                node_right = grid_nodes[(i+1,j)]
                
                ele_tag = self.manager.get_next_element_tag()

                beam = ForceBeamColumn(ele_tag, node_left.tag, node_right.tag, beam_sec_tag, transf_tag, integration_points, mass_density=0.0)

                # Asignar Densidad de Masa
                beam_section = self.manager.get_section(beam_sec_tag)
                if beam_section:
                    beam.mass_density = beam_section.get_mass_per_length(self.manager)

                self.manager.add_element(beam)

        print(f"Generando Portico: {bays} vanos x {stories} pisos ")


