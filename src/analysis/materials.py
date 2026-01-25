
class Material:
    def __init__(self, tag, name):
        self.tag = tag
        self.name = name
    
    def to_dict(self):
        return{
            "tag": self.tag,
            "name": self.name
        }
    @classmethod
    def from_dict(cls,data):
        return cls(data["tag"], data["name"])


class Concrete01(Material):
    def __init__(self,tag,name,fpc,epsc0,fpcu,epsu):
        super().__init__(tag,name)

        self.fpc = fpc          #Resistencia a la compresión   
        self.epsc0 = epsc0      #Deformación unitaria
        self.fpcu = fpcu        #Resistencia al aplastamiento
        self.epsu = epsu        #Deformación última

    def get_opensees_args(self):
        return["Concrete01",self.tag, self.fpc,self.epsc0,self.fpcu,self.epsu]

    def to_dict(self):
        data=super().to_dict()

        data["type"] = "Concrete01"
        data["fpc"] = self.fpc
        data["epsc0"] = self.epsc0
        data["fpcu"] = self.fpcu
        data["epsu"] = self.epsu
        return data

    @classmethod
    def from_dict(cls,data):
        return cls(
            tag = data["tag"],
            name = data["name"],
            fpc = data["fpc"],
            epsc0 = data["epsc0"],
            fpcu = data["fpcu"],
            epsu = data["epsu"]
        )

class Steel01(Material):
    def __init__(self,tag,name,Fy,E0,b):
        super().__init__(tag,name)
        
        self.Fy = Fy
        self.E0 = E0
        self.b = b


    def get_opensees_args(self):
        return["Steel01",self.tag,self.Fy,self.E0,self.b]
    
    def to_dict(self):
        data=super().to_dict()

        data["type"] = "Steel01"
        data["Fy"] = self.Fy
        data["E0"] = self.E0
        data["b"] = self.b
        return data

    @classmethod
    def from_dict(cls,data):
        return cls(
            tag = data["tag"],
            name = data["name"],
            Fy = data["Fy"],
            E0 = data["E0"],
            b = data["b"]
        )