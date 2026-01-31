from PyQt6.QtWidgets import QWidget, QFormLayout, QDoubleSpinBox, QSpinBox
from src.ui.widgets.unit_spinbox import UnitSpinBox 
from src.utils.units import UnitType

class ConcreteForm(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout(self)

        #Densidad
        self.spin_rho_c = UnitSpinBox(UnitType.DENSITY)
        self.spin_rho_c.setDecimals(0)
        self.spin_rho_c.setRange(0, 1e6)
        self.spin_rho_c.set_value_base(2500)
        layout.addRow("Densidad [rho]",self.spin_rho_c)

        #Campo fpc
        self.spin_fpc = UnitSpinBox(UnitType.STRESS)
        self.spin_fpc.setDecimals(0)
        self.spin_fpc.setRange(0, 1e10) 
        self.spin_fpc.set_value_base(25*1e6) # 25 MPa = 25,000,000 Pa
        layout.addRow("Resistencia a la compresión [fpc]",self.spin_fpc)

        #Campo epsc0
        self.spin_epsc0 = QDoubleSpinBox()
        self.spin_epsc0.setDecimals(4)
        self.spin_epsc0.setSingleStep(0.0001)
        self.spin_epsc0.setValue(0.0021)
        layout.addRow("Deformación Unitaria [epsc0]",self.spin_epsc0)

        #Campo fpcU
        self.spin_fpcU = UnitSpinBox(UnitType.STRESS)
        self.spin_fpcU.setDecimals(0)
        self.spin_fpcU.setRange(0, 1e10)
        self.spin_fpcU.set_value_base(25*1e6) # 25 MPa

        layout.addRow("Resistencia al aplastamiento [fpcU]",self.spin_fpcU)

        #Campo epscU
        self.spin_epscU = QDoubleSpinBox()
        self.spin_epscU.setDecimals(4)
        self.spin_epscU.setSingleStep(0.0001)
        self.spin_epscU.setValue(0.003)
        layout.addRow("Deformación última [epscU]",self.spin_epscU)

    def set_data(self, material):
        if not material: return
        self.spin_rho_c.set_value_base(material.rho)
        self.spin_fpc.set_value_base(material.fpc)
        self.spin_epsc0.setValue(material.epsc0)
        self.spin_fpcU.set_value_base(material.fpcu)
        self.spin_epscU.setValue(material.epsu)
        
    def get_data(self):
        #Devuelve los valores del formulario
        return{
            "rho": self.spin_rho_c.get_value_base(),
            "fpc": self.spin_fpc.get_value_base(),
            "epsc0": self.spin_epsc0.value(),
            "fpcu": self.spin_fpcU.get_value_base(),
            "epsu": self.spin_epscU.value()
        }
    



class SteelForm(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout(self)

        #Densidad
        self.spin_rho_s = UnitSpinBox(UnitType.DENSITY)
        self.spin_rho_s.setDecimals(0)
        self.spin_rho_s.setRange(0, 1e6)
        self.spin_rho_s.set_value_base(7850)
        layout.addRow("Densidad [rho]",self.spin_rho_s)

        #Campo Fy
        self.spin_Fy = UnitSpinBox(UnitType.STRESS)
        self.spin_Fy.setDecimals(0)
        self.spin_Fy.setRange(0, 1e10) 
        self.spin_Fy.set_value_base(500*1e6) # 500 MPa = 500e6 Pa
        layout.addRow("Esfuerzo de fluencia [Fy]",self.spin_Fy)

        #Campo E0
        self.spin_E0 = UnitSpinBox(UnitType.STRESS)
        self.spin_E0.setDecimals(0)
        self.spin_E0.setRange(0, 1e12)
        self.spin_E0.set_value_base(200*1e9) # 200 GPa = 200,000 MPa = 200e9 Pa
        layout.addRow("Módulo de elasticidad [E0]",self.spin_E0)

        #Campo b
        self.spin_b = QDoubleSpinBox()
        self.spin_b.setDecimals(3)
        self.spin_b.setSingleStep(0.001)
        self.spin_b.setValue(0.01)
        layout.addRow("Ratio de endurecimiento [b]",self.spin_b)

    def set_data(self, material):
        if not material: return
        self.spin_rho_s.set_value_base(material.rho)
        self.spin_Fy.set_value_base(material.Fy)
        self.spin_E0.set_value_base(material.E0)
        self.spin_b.setValue(material.b)

    def get_data(self):
        #Devuelve los valores del formulario
        return{
            "rho": self.spin_rho_s.get_value_base(),
            "Fy": self.spin_Fy.get_value_base(),
            "E0": self.spin_E0.get_value_base(),
            "b": self.spin_b.value(),
        }
