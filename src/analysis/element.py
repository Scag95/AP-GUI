class Element:
    def __init__(self, tag, node_i, node_j):
        self.tag = tag
        self.node_i = node_i # ID del nodo inicial
        self.node_j = node_j # ID del nodo final

class ForceBeamColumn(Element):
    def __init__(self, tag, node_i, node_j, section_tag, transf_tag):
        super().__init__(tag, node_i, node_j)
        self.num_int_points = 5
        self.section_tag = section_tag
        self.transf_tag = transf_tag
        
    def get_opensees_command(self):

        return f"element forceBeamColumn {self.tag} {self.node_i} {self.node_j} {self.transf_tag} \"Lobatto\" {self.section_tag} {self.num_int_points}"