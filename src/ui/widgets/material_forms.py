from PyQt6.QtWidgets import QWidget, QFormLayout, QDoubleSpinBox

class ConcreteForm(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout(self)

        #Campo fpc
        self.spin_fpc = QDoubleSpinBox()
        self.spin_fpc.setDecimals(0)
        self.spin_fpc.setRange(0,100) #Rango de 0 a 100 MPa
        self.spin_fpc.setSuffix( "MPa")
        self.spin_fpc.setValue(25)
        layout.addRow("Resistencia a la compresión [fpc]",self.spin_fpc)

        #Campo epsc0
        self.spin_epsc0 = QDoubleSpinBox()
        self.spin_epsc0.setDecimals(4)
        self.spin_epsc0.setSingleStep(0.0001)
        self.spin_epsc0.setValue(0.0021)
        layout.addRow("Deformación Unitaria [epsc0]",self.spin_epsc0)

        #Campo fpcU
        self.spin_fpcU = QDoubleSpinBox()
        self.spin_fpcU.setDecimals(0)
        self.spin_fpcU.setRange(0,100) #Rango de 0 a 100 MPa
        self.spin_fpcU.setSuffix( "MPa")
        self.spin_fpcU.setValue(25)
        layout.addRow("Resistencia al aplastamiento [fpcU]",self.spin_fpcU)

        #Campo epscU
        self.spin_epscU = QDoubleSpinBox()
        self.spin_epscU.setDecimals(4)
        self.spin_epscU.setSingleStep(0.0001)
        self.spin_epscU.setValue(0.003)
        layout.addRow("Deformación última [epscU]",self.spin_epscU)

    def get_data(self):
        #Devuelve los valores del formulario
        return{
            "fpc":self.spin_fpc.value(),
            "epsc0":self.spin_epsc0.value(),
            "fpcu":self.spin_fpcU.value(),
            "epsu":self.spin_epscU.value()
        }

class SteelForm(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout(self)

        #Campo Fy
        self.spin_Fy = QDoubleSpinBox()
        self.spin_Fy.setDecimals(0)
        self.spin_Fy.setRange(0,1000) #Rango de 0 a 1000 MPa
        self.spin_Fy.setSuffix( "MPa")
        self.spin_Fy.setValue(500)
        layout.addRow("Esfuerzo de fluencia [Fy]",self.spin_Fy)

        #Campo E0
        self.spin_E0 = QDoubleSpinBox()
        self.spin_E0.setDecimals(0)
        self.spin_E0.setRange(0,1000000) #Rango de 0 a 1000 MPa
        self.spin_E0.setSuffix( "MPa")
        self.spin_E0.setValue(200000) #Rango de 0 a 1000 MPa
        layout.addRow("Módulo de elasticidad [E0]",self.spin_E0)

        #Campo b
        self.spin_b = QDoubleSpinBox()
        self.spin_b.setDecimals(3)
        self.spin_b.setSingleStep(0.001)
        self.spin_b.setValue(0.01)
        layout.addRow("Ratio de endurecimiento [b]",self.spin_b)

    def get_data(self):
        #Devuelve los valores del formulario
        return{
            "Fy":self.spin_Fy.value(),
            "E0":self.spin_E0.value(),
            "b":self.spin_b.value(),
        }
