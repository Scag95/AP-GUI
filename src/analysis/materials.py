
class Material:
    __slots__ = ['tag', 'name', 'rho']
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
    __slots__ = ['fpc', 'epsc0', 'fpcu', 'epsu', 'minmax']
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
    __slots__ = ['Fy', 'E0', 'b', 'a1', 'a2', 'a3', 'a4', 'minmax']
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
    __slots__ = ['E']
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
            name = data.get("name", "ElasticMaterial"),
            E = data["E"],
            rho = data.get("rho", 0.0)
        )

class Hysteretic(Material):
    __slots__ = [
        's1p', 'e1p', 's2p', 'e2p', 's3p', 'e3p',   # Envolvente positiva
        's1n', 'e1n', 's2n', 'e2n', 's3n', 'e3n',   # Envolvente negativa
        'pinch_x', 'pinch_y', 'damage1', 'damage2',  # Histéresis
        'beta'                                         # Opcional
    ]

    def __init__(self, tag, name,
                 s1p, e1p, s2p, e2p, s3p, e3p,
                 s1n, e1n, s2n, e2n, s3n, e3n,
                 pinch_x=0.0, pinch_y=0.0, damage1=0.0, damage2=0.0,
                 beta=None, rho=0.0):

        super().__init__(tag, name, rho)
        #Rama positiva
        self.s1p, self.e1p = s1p, e1p
        self.s2p, self.e2p = s2p, e2p
        self.s3p, self.e3p = s3p, e3p
        # Rama negativa
        self.s1n, self.e1n = s1n, e1n
        self.s2n, self.e2n = s2n, e2n
        self.s3n, self.e3n = s3n, e3n
        # Histéresis
        self.pinch_x  = pinch_x
        self.pinch_y  = pinch_y
        self.damage1  = damage1
        self.damage2  = damage2
        self.beta     = beta  # None = no se pasa a OpenSees

    def get_opensees_args(self):
        args = [
            "Hysteretic", self.tag,
            self.s1p, self.e1p, self.s2p, self.e2p, self.s3p, self.e3p,
            self.s1n, self.e1n, self.s2n, self.e2n, self.s3n, self.e3n,
            self.pinch_x, self.pinch_y, self.damage1, self.damage2
        ]
        if self.beta is not None:
            args.append(self.beta)
        return args

    def to_dict(self):
        data = super().to_dict()
        data["type"]     = "Hysteretic"
        data["s1p"]      = self.s1p;  data["e1p"] = self.e1p
        data["s2p"]      = self.s2p;  data["e2p"] = self.e2p
        data["s3p"]      = self.s3p;  data["e3p"] = self.e3p
        data["s1n"]      = self.s1n;  data["e1n"] = self.e1n
        data["s2n"]      = self.s2n;  data["e2n"] = self.e2n
        data["s3n"]      = self.s3n;  data["e3n"] = self.e3n
        data["pinch_x"]  = self.pinch_x
        data["pinch_y"]  = self.pinch_y
        data["damage1"]  = self.damage1
        data["damage2"]  = self.damage2
        data["beta"]     = self.beta   # puede ser None → JSON null
        return data

    @classmethod
    def from_dict(cls, data):
        return cls(
            tag=data["tag"],          name=data["name"],
            s1p=data["s1p"],          e1p=data["e1p"],
            s2p=data["s2p"],          e2p=data["e2p"],
            s3p=data["s3p"],          e3p=data["e3p"],
            s1n=data["s1n"],          e1n=data["e1n"],
            s2n=data["s2n"],          e2n=data["e2n"],
            s3n=data["s3n"],          e3n=data["e3n"],
            pinch_x=data.get("pinch_x",  0.0),
            pinch_y=data.get("pinch_y",  0.0),
            damage1=data.get("damage1",  0.0),
            damage2=data.get("damage2",  0.0),
            beta=data.get("beta",        None),
            rho=data.get("rho",          0.0)
        )

class HystereticSM(Material):
    __slots__ = [
        's1p', 'e1p', 's2p', 'e2p', 's3p', 'e3p', 's4p', 'e4p',   # Envolvente positiva (4 puntos)
        's1n', 'e1n', 's2n', 'e2n', 's3n', 'e3n', 's4n', 'e4n',   # Envolvente negativa (4 puntos)
        'pinch_x', 'pinch_y', 'damage1', 'damage2', 'beta'
    ]

    def __init__(self, tag, name,
                 s1p, e1p, s2p, e2p, s3p, e3p, s4p, e4p,
                 s1n, e1n, s2n, e2n, s3n, e3n, s4n, e4n,
                 pinch_x=1.0, pinch_y=1.0, damage1=0.0, damage2=0.0,
                 beta=0.5, rho=0.0):
        super().__init__(tag, name, rho)
        self.s1p, self.e1p = s1p, e1p
        self.s2p, self.e2p = s2p, e2p
        self.s3p, self.e3p = s3p, e3p
        self.s4p, self.e4p = s4p, e4p
        self.s1n, self.e1n = s1n, e1n
        self.s2n, self.e2n = s2n, e2n
        self.s3n, self.e3n = s3n, e3n
        self.s4n, self.e4n = s4n, e4n
        self.pinch_x  = pinch_x
        self.pinch_y  = pinch_y
        self.damage1  = damage1
        self.damage2  = damage2
        self.beta     = beta

    def get_opensees_args(self):
        return [
            "HystereticSM", self.tag,
            self.s1p, self.e1p, self.s2p, self.e2p,
            self.s3p, self.e3p, self.s4p, self.e4p,
            self.s1n, self.e1n, self.s2n, self.e2n,
            self.s3n, self.e3n, self.s4n, self.e4n,
            self.pinch_x, self.pinch_y,
            self.damage1, self.damage2, self.beta
        ]

    def to_dict(self):
        data = super().to_dict()
        data["type"]     = "HystereticSM"
        data["s1p"]      = self.s1p;  data["e1p"] = self.e1p
        data["s2p"]      = self.s2p;  data["e2p"] = self.e2p
        data["s3p"]      = self.s3p;  data["e3p"] = self.e3p
        data["s4p"]      = self.s4p;  data["e4p"] = self.e4p
        data["s1n"]      = self.s1n;  data["e1n"] = self.e1n
        data["s2n"]      = self.s2n;  data["e2n"] = self.e2n
        data["s3n"]      = self.s3n;  data["e3n"] = self.e3n
        data["s4n"]      = self.s4n;  data["e4n"] = self.e4n
        data["pinch_x"]  = self.pinch_x
        data["pinch_y"]  = self.pinch_y
        data["damage1"]  = self.damage1
        data["damage2"]  = self.damage2
        data["beta"]     = self.beta
        return data

    @classmethod
    def from_dict(cls, data):
        return cls(
            tag=data["tag"],  name=data["name"],
            s1p=data["s1p"],  e1p=data["e1p"],
            s2p=data["s2p"],  e2p=data["e2p"],
            s3p=data["s3p"],  e3p=data["e3p"],
            s4p=data["s4p"],  e4p=data["e4p"],
            s1n=data["s1n"],  e1n=data["e1n"],
            s2n=data["s2n"],  e2n=data["e2n"],
            s3n=data["s3n"],  e3n=data["e3n"],
            s4n=data["s4n"],  e4n=data["e4n"],
            pinch_x=data.get("pinch_x",  1.0),
            pinch_y=data.get("pinch_y",  1.0),
            damage1=data.get("damage1",  0.0),
            damage2=data.get("damage2",  0.0),
            beta=data.get("beta",        0.5),
            rho=data.get("rho",          0.0)
        )
