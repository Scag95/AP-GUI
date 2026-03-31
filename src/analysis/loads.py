from abc import ABC, abstractmethod
class Load(ABC):
    __slots__ = ['tag']
    def __init__(self, tag):
        self.tag = tag

    @abstractmethod
    def to_dict(self):
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls,data):
        pass

class NodalLoad(Load):
    __slots__ = ['node_tag', 'fx', 'fy', 'mz']
    def __init__(self, tag, node_tag, fx=0.0 ,fy=0.0, mz=0.0):
        super().__init__(tag)
        self.node_tag = node_tag
        self.fx = fx
        self.fy = fy
        self.mz = mz
    def to_dict(self):
        return{
            "type": "NodalLoad",
            "tag": self.tag,
            "node_tag": self.node_tag,
            "fx": self.fx,
            "fy": self.fy,
            "mz": self.mz
        }
    @classmethod
    def from_dict(cls, data):
        return cls(
            tag=data["tag"],
            node_tag=data["node_tag"],
            fx=data.get("fx", 0.0),
            fy=data.get("fy", 0.0),
            mz=data.get("mz", 0.0)
        )
class ElementLoad(Load):
    __slots__ = ['element_tag', 'wx', 'wy']
    def __init__(self, tag, element_tag, wx =0.0, wy = 0.0):
        super().__init__(tag)
        self.element_tag = element_tag
        self.wx = wx
        self.wy = wy
        
    def to_dict(self):
        return{
            "type": "ElementLoad",
            "tag": self.tag,
            "element_tag": self.element_tag,
            "wx": self.wx,
            "wy": self.wy
        }
    @classmethod
    def from_dict(cls, data):
        return cls(
            tag=data["tag"],
            element_tag=data["element_tag"],
            wx=data.get("wx", 0.0),
            wy=data.get("wy", 0.0)
        )   

class LoadPattern:
    __slots__ = ['tag', 'name', 'factor', 'loads']

    def __init__(self, tag: int, name:str, factor: float = 1.0):
        self.tag = tag
        self.name = name
        self.factor = factor
        self.loads = []  #Lista que guardatrá objetor generícos Load (NodalLoad o ElementLoad)

    def add_load(self, load_obj: Load):
        """ Añade un fuernza a este LoadPattern """
        self.loads.append(load_obj)

    def remove_load(self, load_tag: int):
        """ Elimina una fuerza de este LoadPattern """
        self.loads = [L for L in self.loads if L.tag != load_tag]

    def to_dict(self):
        return {
            "type": "LoadPattern",
            "tag": self.tag,
            "name": self.name,
            "factor": self.factor,
            "loads": [L.to_dict() for L in self.loads]
        }

    @classmethod
    def from_dict(cls, data):
        #1. Crear el patrón base vacío
        pattern = cls(
            tag = data["tag"],
            name = data.get("name", f"Pattern_{data['tag']}"),
            factor=data.get("factor", 1.0)
        )

        #2. Rellenar las fuerzas que tenía aninadas
        for l_data in data.get("loads", []):
            tipo = l_data.get("type")
            if tipo == "NodalLoad":
                pattern.add_load(NodalLoad.from_dict(l_data))
            elif tipo == "ElementLoad":
                pattern.add_load(ElementLoad.from_dict(l_data))

        return pattern

        