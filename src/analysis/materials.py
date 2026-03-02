
class Material:
    def __init__(self, tag, name, rho=0.0):
        self.tag = tag
        self.name = name
        self.rho = rho
    
    def to_dict(self):
        return{
            "tag": self.tag,
            "name": self.name,
            "rho": self.rho
        }
    @classmethod
    def from_dict(cls,data):
        return cls(data["tag"], data["name"])


class Concrete01(Material):
    def __init__(self,tag,name,fpc,epsc0,fpcu,epsu, rho=2500.0, minmax = None):
        super().__init__(tag,name,rho)

        self.fpc = fpc          #Resistencia a la compresión   
        self.epsc0 = epsc0      #Deformación unitaria
        self.fpcu = fpcu        #Resistencia al aplastamiento
        self.epsu = epsu        #Deformación última
        self.rho = rho          #Densidad 
        self.minmax = minmax 


    def get_opensees_args(self):
        return["Concrete01",self.tag, self.fpc,self.epsc0,self.fpcu,self.epsu]

    def to_dict(self):
        data=super().to_dict()

        data["type"] = "Concrete01"
        data["fpc"] = self.fpc
        data["epsc0"] = self.epsc0
        data["fpcu"] = self.fpcu
        data["epsu"] = self.epsu
        data["rho"] = self.rho
        data["minmax"] = self.minmax 
        return data

    @classmethod
    def from_dict(cls,data):
        return cls(
            tag = data["tag"],
            name = data["name"],
            fpc = data["fpc"],
            epsc0 = data["epsc0"],
            fpcu = data["fpcu"],
            epsu = data["epsu"],
            rho = data.get("rho",2500.0),
            minmax = data.get("minmax", None)
        )

class Steel01(Material):
    def __init__(self,tag,name,Fy,E0,b, rho=7850.0,a1=0.0, a2=0.0, a3=0.0, a4=0.0, minmax=None):
        super().__init__(tag,name, rho)
        
        self.Fy = Fy
        self.E0 = E0
        self.b = b
        self.rho = rho
        self.a1 = a1
        self.a2 = a2
        self.a3 = a3
        self.a4 = a4
        self.minmax = minmax


    def get_opensees_args(self):
        return ["Steel01", self.tag, self.Fy, self.E0, self.b, self.a1, self.a2, self.a3, self.a4]
    
    def to_dict(self):
        data=super().to_dict()

        data["type"] = "Steel01"
        data["Fy"] = self.Fy
        data["E0"] = self.E0
        data["b"] = self.b
        data["rho"] = self.rho
        data["a1"] = self.a1
        data["a2"] = self.a2
        data["a3"] = self.a3
        data["a4"] = self.a4
        data["minmax"] = self.minmax
        return data

    @classmethod
    def from_dict(cls,data):
        return cls(
            tag = data["tag"],
            name = data["name"],
            Fy = data["Fy"],
            E0 = data["E0"],
            b = data["b"],
            rho = data.get("rho",7850.0),
            a1 = data.get("a1", 0.0),
            a2 = data.get("a2", 0.0),
            a3 = data.get("a3", 0.0),
            a4 = data.get("a4", 0.0),
            minmax = data.get("minmax", None)
        )

class Elastic(Material):
    def __init__(self, tag, name, E, rho=0.0):
        super().__init__(tag, name, rho)
        self.E = E

    @classmethod
    def create_internal(cls,tag,E):
        return cls(tag, "InternalElastic", E, 0.0)
        
    def get_opensees_args(self):
        return["Elastic",self.tag, self.E]

    def to_dict(self):
        data=super().to_dict()

        data["type"] = "Elastic"
        data["E"] = self.E
        return data

    @classmethod
    def from_dict(cls,data):
        return cls(
            tag = data["tag"],
            E = data["E"]
        )
