class Node:
    __slots__ = ['tag', 'x', 'y', 'fixity', 'mass']
    def __init__(self, tag, x, y, fixity=None, mass=None):
        self.tag = tag
        self.x = x
        self.y = y
        self.fixity = fixity if fixity is not None else [0,0,0]
        self.mass = mass # Lista [mx, my, mrz] o None si no tiene masa
    
    def get_opensees_command(self):
        # Sintaxis OpenSees: node $tag $x $y
        return f"node {self.tag} {self.x} {self.y}"
            
    def __repr__(self):
        return f"Node(tag={self.tag}, x={self.x}, y={self.y}, fixity={self.fixity}, mass={self.mass})"

    def to_dict(self):
        # Devuelve un diccionario con la claves 'tag', 'x', 'y'
        data = {
            "tag": self.tag,
            "x": self.x,
            "y": self.y,
            "fixity": self.fixity
        }
        if self.mass is not None:
            data["mass"] = self.mass
        
        return data
    
    @classmethod
    def from_dict(cls, data):
        # Extrae los datos del diccionario y retorna una nueva instancia
        fixity = data.get("fixity", [0,0,0])
        mass = data.get("mass", None)
        return cls(data["tag"], data["x"], data["y"], fixity, mass)

