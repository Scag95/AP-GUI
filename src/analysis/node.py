class Node:
    def __init__(self, tag, x, y):
        self.tag = tag
        self.x = x
        self.y = y
    
    def get_opensees_command(self):
        # Sintaxis OpenSees: node $tag $x $y
        return f"node {self.tag} {self.x} {self.y}"
            
    def __repr__(self):
        return f"Node(tag={self.tag}, x={self.x}, y={self.y})"