class Node:
    def __init__(self, tag, x, y, fixity=None):
        self.tag = tag
        self.x = x
        self.y = y
        self.fixity = fixity if fixity is not None else [0,0,0]
    
    def get_opensees_command(self):
        # Sintaxis OpenSees: node $tag $x $y
        return f"node {self.tag} {self.x} {self.y}"
            
    def __repr__(self):
        return f"Node(tag={self.tag}, x={self.x}, y={self.y}, fixity={self.fixity})"

    def to_dict(self):
        # Devuelve un diccionario con la claves 'tag', 'x', 'y'
        return{
            "tag": self.tag,
            "x": self.x,
            "y": self.y,
            "fixity": self.fixity
        }
    
    @classmethod
    def from_dict(cls, data):
        # Extrae los datos del diccionario y retorna una nueva instancia
        fixity = data.get("fixity", [0,0,0])
        return cls(data["tag"], data["x"], data["y"], fixity)