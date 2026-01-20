from src.analysis.materials import Material

#---------Clases Auxiliares -------  
class RectPatch:
    def __init__(self, material_tag,yI,zI,yJ,zJ,nIy=10,nIz=10):
        self.material_tag = material_tag
        self.yI = yI
        self.zI = zI
        self.yJ = yJ
        self.zJ = zJ
        self.nIy = nIy
        self.nIz = nIz

class LayerStraight:
    def __init__(self, material_tag, num_bars, area_bar, yStart, zStart, yEnd, zEnd):
        self.material_tag = material_tag
        self.num_bars = num_bars
        self.area_bar = area_bar
        # Coordenadas de inicio y fin de la línea de barras
        self.yStart = yStart
        self.zStart = zStart
        self.yEnd = yEnd
        self.zEnd = zEnd

#---------Clases Princpales -------        
class Section:
    def __init__(self,tag,name):
        self.tag = tag
        self.name = name

class FiberSection(Section):
    def __init__(self,tag,name):
        super().__init__(tag,name)
        self.patches = []
        self.layers = []

    def add_rect_patch(self,patch: RectPatch):
        self.patches.append(patch)
    
    def add_layer_straight(self,layer: LayerStraight):
        self.layers.append(layer)
    
def get_opensees_commands(self):
        cmds = [f"section Fiber {self.tag} {{"]
        
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
