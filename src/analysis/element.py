class Element:
    __slots__ = ['tag', 'node_i', 'node_j']
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
    __slots__ = ['integration_points', 'section_tag', 'transf_tag', 'mass_density']
    def __init__(self, tag, node_i, node_j, section_tag, transf_tag, integration_points, mass_density= 0.0):
        super().__init__(tag, node_i, node_j)
        self.integration_points = integration_points
        self.section_tag = section_tag
        self.transf_tag = transf_tag
        self.mass_density = mass_density 
        
    def get_opensees_command(self):
        f"element forceBeamColumn {self.tag} {self.node_i} {self.node_j} {self.transf_tag} \"Lobatto\" {self.section_tag} {self.integration_points} \"-mass\" {self.mass_density}"

    def to_dict(self):
        # 1. Obtenemos el dict básico del padre
        data = super().to_dict() 
        
        # 2. Modificamos el tipo y añadimos los campos específicos
        data["type"] = "ForceBeamColumn"
        data["section_tag"] = self.section_tag
        data["transf_tag"] = self.transf_tag
        data["mass_density"] = self.mass_density
        data["integration_points"] = self.integration_points
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
            mass_density=data["mass_density"],
            integration_points=data["integration_points"]

        )

class ForceBeamColumnHinge(Element):
    __slots__ = [
        'transf_tag', 'section_i_tag', 'lp_i', 'section_j_tag', 'lp_j', 'section_e_tag', 'mass_density'
    ]    

    @property
    def integration_points(self):
        # HingeRadau (y por extensión este elemento) garantiza 6 puntos de integración fijos.
        return 6

    def __init__(self, tag, node_i, node_j,
                 transf_tag, section_i_tag, lp_i,    
                 section_j_tag, lp_j, section_e_tag, mass_density = 0.0):
        
        super().__init__(tag, node_i, node_j)


        #Asiganación de atributos propios
        self.transf_tag = transf_tag
        self.section_i_tag = section_i_tag
        self.lp_i = lp_i
        self.section_j_tag = section_j_tag
        self.lp_j = lp_j
        self.section_e_tag = section_e_tag
        self.mass_density = mass_density 


    def to_dict(self):
        # 1. Obtenemos el dict básico del padre
        data = super().to_dict() 
        
        # 2. Modificamos el tipo y añadimos los campos específicos
        data["type"] = "ForceBeamColumnHinge"
        data["transf_tag"] = self.transf_tag
        data["section_i_tag"] = self.section_i_tag
        data["lp_i"] = self.lp_i
        data["section_j_tag"] = self.section_j_tag
        data["lp_j"] = self.lp_j
        data["section_e_tag"] = self.section_e_tag
        data["mass_density"] = self.mass_density
        return data        

    @classmethod
    def from_dict(cls, data):
        # 3. Reconstruimos el objeto desde el diccionario JSON
        return cls(
            tag=data["tag"],
            node_i=data["node_i"],
            node_j=data["node_j"],
            transf_tag=data["transf_tag"],
            section_i_tag=data["section_i_tag"],
            lp_i=data["lp_i"],
            section_j_tag=data["section_j_tag"],
            lp_j=data["lp_j"],
            section_e_tag=data["section_e_tag"],
            mass_density=data.get("mass_density", 0.0)
        )

