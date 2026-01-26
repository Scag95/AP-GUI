class Element:
    def __init__(self, tag, node_i, node_j):
        self.tag = tag
        self.node_i = node_i # ID del nodo inicial
        self.node_j = node_j # ID del nodo final

    def to_dict(self):
        return{
            "type": "Element", # Etiqueta para saber qué es
            "tag": self.tag,
            "node_i": self.node_i,
            "node_j": self.node_j  
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["tag"], data["node_i"], data["node_j"])

class ForceBeamColumn(Element):
    def __init__(self, tag, node_i, node_j, section_tag, transf_tag, mass_density=0.0):
        super().__init__(tag, node_i, node_j)
        self.num_int_points = 5
        self.section_tag = section_tag
        self.transf_tag = transf_tag
        self.mass_density = mass_density 
        
    def get_opensees_command(self):

        cmd = f"element forceBeamColumn {self.tag} {self.node_i} {self.node_j} {self.transf_tag} \"Lobatto\" {self.section_tag} {self.num_int_points}"
        if self.mass_density > 0:
            cmd += f"-mass {self.mass_density}"
        return cmd

    def to_dict(self):
        # 1. Obtenemos el dict básico del padre
        data = super().to_dict() 
        
        # 2. Modificamos el tipo y añadimos los campos específicos
        data["type"] = "ForceBeamColumn"
        data["section_tag"] = self.section_tag
        data["transf_tag"] = self.transf_tag
        data["mass_density"] = self.mass_density
        return data

    @classmethod
    def from_dict(cls, data):
        # Aquí creamos directamente el ForceBeamColumn con TODOS sus datos
        return cls(
            tag=data["tag"],
            node_i=data["node_i"],
            node_j=data["node_j"],
            section_tag=data["section_tag"],
            transf_tag=data["transf_tag"],
            mass_density=data.get("mass_density",0.0)
        )
