from src.analysis.materials import Material

#---------Clases Auxiliares -------  
class RectPatch:
    __slots__ = ['material_tag', 'yI', 'zI', 'yJ', 'zJ', 'nIy', 'nIz']
    def __init__(self, material_tag,yI,zI,yJ,zJ,nIy,nIz):
        self.material_tag = material_tag
        self.yI = yI
        self.zI = zI
        self.yJ = yJ
        self.zJ = zJ
        self.nIy = nIy
        self.nIz = nIz

    def to_dict(self):
        return{
            "type": "RectPatch", # Etiqueta para saber qué es
            "material_tag": self.material_tag,
            "yI": self.yI,
            "zI": self.zI,
            "yJ": self.yJ,
            "zJ": self.zJ,
            "nIy": self.nIy,
            "nIz": self.nIz
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["material_tag"], data["yI"], data["zI"],
         data["yJ"], data["zJ"], data["nIy"], data["nIz"])


class LayerStraight:
    __slots__ = ['material_tag', 'num_bars', 'area_bar', 'yStart', 'zStart', 'yEnd', 'zEnd']
    def __init__(self, material_tag, num_bars, area_bar, yStart, zStart, yEnd, zEnd):
        self.material_tag = material_tag
        self.num_bars = num_bars
        self.area_bar = area_bar
        # Coordenadas de inicio y fin de la línea de barras
        self.yStart = yStart
        self.zStart = zStart
        self.yEnd = yEnd
        self.zEnd = zEnd

    def to_dict(self):
        return{
            "type": "LayerStraight", # Etiqueta para saber qué es
            "material_tag": self.material_tag,
            "num_bars": self.num_bars,
            "area_bar": self.area_bar,
            "yStart": self.yStart,
            "zStart": self.zStart,
            "yEnd": self.yEnd,
            "zEnd": self.zEnd
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["material_tag"], 
            data["num_bars"], 
            data["area_bar"],
            data["yStart"], 
            data["zStart"], 
            data["yEnd"], 
            data["zEnd"]
        )



#---------Clases Princpales -------        
class Section:
    __slots__ = ['tag', 'name']
    def __init__(self,tag,name):
        self.tag = tag
        self.name = name

    def to_dict(self):
        return{
            "tag":self.tag,
            "name":self.name
        }

class FiberSection(Section):
    __slots__ = ['patches', 'layers']
    def __init__(self,tag,name):
        super().__init__(tag,name)
        self.patches = []
        self.layers = []

    def add_rect_patch(self,patch: RectPatch):
        self.patches.append(patch)
    
    def add_layer_straight(self,layer: LayerStraight):
        self.layers.append(layer)
    
    def get_opensees_commands(self):
            cmds = [f"section ('Fiber' {self.tag} {{"]
            
            for p in self.patches:
                # Sintaxis: patch rect $matTag $numSubdivY $numSubdivZ $yI $zI $yJ $zJ
                cmd = f"  patch rect {p.material_tag} {p.nIy} {p.nIz} {p.yI} {p.zI} {p.yJ} {p.zJ}"
                cmds.append(cmd)
                
            for l in self.layers:
                # Sintaxis: layer straight $matTag $numBars $areaBar $yStart $zStart $yEnd $zEnd
                cmd = f"  layer straight {l.material_tag} {l.num_bars} {l.area_bar} {l.yStart} {l.zStart} {l.yEnd} {l.zEnd}"
                cmds.append(cmd)
                
            cmds.append("}")
            return cmds

    def to_dict(self):
        data = super().to_dict()
        data["type"] = "FiberSection"
        data["patches"] = [p.to_dict() for p in self.patches]
        data["layers"] = [l.to_dict() for l in self.layers]
        return data
    
    @classmethod
    def from_dict(cls, data):
        new_sec = cls(data["tag"],data["name"])

        for p_data in data.get("patches",[]):
            patch = RectPatch.from_dict(p_data)
            new_sec.add_rect_patch(patch)

        for l_data in data.get("layers",[]):
            layer = LayerStraight.from_dict(l_data)
            new_sec.add_layer_straight(layer)
        
        return new_sec

    def get_mass_per_length(self,material_manager):
        total_mass = 0.0

        for p in self.patches:
            mat = material_manager.get_material(p.material_tag)
            if mat:
                area = abs(p.yJ - p.yI) * abs(p.zJ-p.zI)
                total_mass += area * mat.rho

        return total_mass

class AggregatorSection(Section):
    __slots__ = ['base_section_tag', 'materials']
    
    def __init__(self, tag, name, base_section_tag=None):
        super().__init__(tag, name)
        # ID de la sección base opcional
        self.base_section_tag = base_section_tag
        # Lista de diccionarios: [{"mat_tag": 2, "dof": "Vy"}, ...]
        self.materials = []

    def add_material(self, mat_tag: int, dof: str):
        self.materials.append({"mat_tag": mat_tag, "dof": dof})

    def get_opensees_commands(self):
        # Devolvemos una lista de tuplas de argumentos listos para desempaquetar con *args
        # Sintaxis OpenSees: section('Aggregator', secTag, matTag1, dof1, ...)
        args = ['Aggregator', self.tag]
        
        for m in self.materials:
            args.append(m['mat_tag'])
            args.append(m['dof'])
            
        if self.base_section_tag is not None and self.base_section_tag > 0:
            args.extend(['-section', self.base_section_tag])
            
        return [tuple(args)]  # Lista de una tupla (una sola llamada a section())

    def to_dict(self):
        data = super().to_dict()
        data["type"] = "AggregatorSection"
        data["base_section_tag"] = self.base_section_tag
        data["materials"] = self.materials
        return data

    @classmethod
    def from_dict(cls, data):
        new_sec = cls(
            tag=data["tag"],
            name=data["name"],
            base_section_tag=data.get("base_section_tag")
        )
        new_sec.materials = data.get("materials", [])
        return new_sec

    def get_mass_per_length(self, material_manager):
        # La masa de esta sección compuesta depende puramente de su núcleo original
        if self.base_section_tag:
            from src.analysis.manager import ProjectManager
            base_sec = ProjectManager.instance().get_section(self.base_section_tag)
            if base_sec and hasattr(base_sec, 'get_mass_per_length'):
                return base_sec.get_mass_per_length(material_manager)
        return 0.0
