from abc import ABC, abstractmethod
class Load(ABC):
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
