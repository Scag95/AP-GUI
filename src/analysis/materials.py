
class Material:
    def __init__(self, tag, name):
        self.tag = tag
        self.name = name


class Concrete01(Material):
    def __init__(self,tag,name,fpc,epsc0,fpcu,epsu):
        super().__init__(tag,name)

        self.fpc = fpc          #Resistencia a la compresión   
        self.epsc0 = epsc0      #Deformación unitaria
        self.fpcu = fpcu        #Resistencia al aplastamiento
        self.epsU = epsu        #Deformación última


    def get_opensees_args(self):
        return["Concrete01",self.tag, self.fpc,self.epsc0,self.fpcu,self.epsU]

class Steel01(Material):
    def __init__(self,tag,name,Fy,E0,b):
        super().__init__(tag,name)
        
        self.Fy = Fy
        self.E0 = E0
        self.b = b


    def get_opensees_args(self):
        return["Steel01",self.tag,self.Fy,self.E0,self.b]
    