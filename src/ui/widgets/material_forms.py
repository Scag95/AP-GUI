from PyQt6.QtWidgets import QWidget, QFormLayout, QDoubleSpinBox, QSpinBox, QCheckBox
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
        self.spin_fpcU.set_value_base(5*1e6) # 5 MPa

        layout.addRow("Resistencia al aplastamiento [fpcU]",self.spin_fpcU)

        #Campo epscU
        self.spin_epscU = QDoubleSpinBox()
        self.spin_epscU.setDecimals(4)
        self.spin_epscU.setSingleStep(0.0001)
        self.spin_epscU.setValue(0.003)
        layout.addRow("Deformación última [epscU]",self.spin_epscU)

        # --- Propiedades Opcionales ---
        self.chk_optional = QCheckBox("Mostrar Propiedades Opcionales")
        layout.addRow(self.chk_optional)

        self.widget_optional = QWidget()
        opt_layout = QFormLayout(self.widget_optional)
        self.widget_optional.setVisible(False)

        # Checkbox MinMax
        self.chk_minmax = QCheckBox("Habilitar Envolvente de Rotura (MinMax)")
        opt_layout.addRow(self.chk_minmax)

        self.spin_min_strain = QDoubleSpinBox()
        self.spin_min_strain.setDecimals(4)
        self.spin_min_strain.setRange(-1.0, 1.0)
        self.spin_min_strain.setSingleStep(0.001)
        self.spin_min_strain.setValue(-0.05) # Compresión

        self.spin_max_strain = QDoubleSpinBox()
        self.spin_max_strain.setDecimals(4)
        self.spin_max_strain.setRange(-1.0, 1.0)
        self.spin_max_strain.setSingleStep(0.001)
        self.spin_max_strain.setValue(0.05) # Tracción
        
        opt_layout.addRow("Deformación Mínima (Compresión):", self.spin_min_strain)
        opt_layout.addRow("Deformación Máxima (Tracción):", self.spin_max_strain)

        layout.addRow(self.widget_optional)

        # Estado inicial
        self.spin_min_strain.setEnabled(False)
        self.spin_max_strain.setEnabled(False)

        # Conexiones
        self.chk_optional.toggled.connect(self.widget_optional.setVisible)
        self.chk_minmax.toggled.connect(self.spin_min_strain.setEnabled)
        self.chk_minmax.toggled.connect(self.spin_max_strain.setEnabled)


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

        # --- Propiedades Opcionales ---
        self.chk_optional = QCheckBox("Mostrar Propiedades Opcionales")
        layout.addRow(self.chk_optional)

        self.widget_optional = QWidget()
        opt_layout = QFormLayout(self.widget_optional)
        self.widget_optional.setVisible(False)

        # a1, a2, a3, a4
        self.spin_a1 = QDoubleSpinBox()
        self.spin_a1.setDecimals(3)
        self.spin_a1.setValue(0.0)
        opt_layout.addRow("Parámetro endur. [a1]:", self.spin_a1)

        self.spin_a2 = QDoubleSpinBox()
        self.spin_a2.setDecimals(3)
        self.spin_a2.setValue(0.0)
        opt_layout.addRow("Parámetro endur. [a2]:", self.spin_a2)

        self.spin_a3 = QDoubleSpinBox()
        self.spin_a3.setDecimals(3)
        self.spin_a3.setValue(0.0)
        opt_layout.addRow("Parámetro endur. [a3]:", self.spin_a3)

        self.spin_a4 = QDoubleSpinBox()
        self.spin_a4.setDecimals(3)
        self.spin_a4.setValue(0.0)
        opt_layout.addRow("Parámetro endur. [a4]:", self.spin_a4)

        # Checkbox MinMax
        self.chk_minmax = QCheckBox("Habilitar Envolvente de Rotura (MinMax)")
        opt_layout.addRow(self.chk_minmax)

        self.spin_min_strain = QDoubleSpinBox()
        self.spin_min_strain.setDecimals(4)
        self.spin_min_strain.setRange(-1.0, 1.0)
        self.spin_min_strain.setSingleStep(0.001)
        self.spin_min_strain.setValue(-0.05) 

        self.spin_max_strain = QDoubleSpinBox()
        self.spin_max_strain.setDecimals(4)
        self.spin_max_strain.setRange(-1.0, 1.0)
        self.spin_max_strain.setSingleStep(0.001)
        self.spin_max_strain.setValue(0.05) 
        
        opt_layout.addRow("Def. Mínima (Compresión):", self.spin_min_strain)
        opt_layout.addRow("Def. Máxima (Tracción):", self.spin_max_strain)

        layout.addRow(self.widget_optional)

        # Estado inicial
        self.spin_min_strain.setEnabled(False)
        self.spin_max_strain.setEnabled(False)

        # Conexiones
        self.chk_optional.toggled.connect(self.widget_optional.setVisible)
        self.chk_minmax.toggled.connect(self.spin_min_strain.setEnabled)
        self.chk_minmax.toggled.connect(self.spin_max_strain.setEnabled)

    def set_data(self, material):
        if not material: return
        self.spin_rho_s.set_value_base(material.rho)
        self.spin_Fy.set_value_base(material.Fy)
        self.spin_E0.set_value_base(material.E0)
        self.spin_b.setValue(material.b)

        a1 = getattr(material, 'a1', 0.0)
        a2 = getattr(material, 'a2', 0.0)
        a3 = getattr(material, 'a3', 0.0)
        a4 = getattr(material, 'a4', 0.0)
        
        self.spin_a1.setValue(a1)
        self.spin_a2.setValue(a2)
        self.spin_a3.setValue(a3)
        self.spin_a4.setValue(a4)
        
        has_minmax = getattr(material, 'minmax', None) is not None
        has_a = any(v != 0.0 for v in [a1, a2, a3, a4])
        
        if has_minmax or has_a:
            self.chk_optional.setChecked(True)
        else:
            self.chk_optional.setChecked(False)
            
        if has_minmax:
            self.chk_minmax.setChecked(True)
            self.spin_min_strain.setValue(material.minmax.get("min", -0.05))
            self.spin_max_strain.setValue(material.minmax.get("max", 0.05))
        else:
            self.chk_minmax.setChecked(False)

    def get_data(self):
        #Devuelve los valores del formulario
        data = {
            "rho": self.spin_rho_s.get_value_base(),
            "Fy": self.spin_Fy.get_value_base(),
            "E0": self.spin_E0.get_value_base(),
            "b": self.spin_b.value(),
            "a1": 0.0,
            "a2": 0.0,
            "a3": 0.0,
            "a4": 0.0,
            "minmax": None
        }
        
        if self.chk_optional.isChecked():
            data["a1"] = self.spin_a1.value()
            data["a2"] = self.spin_a2.value()
            data["a3"] = self.spin_a3.value()
            data["a4"] = self.spin_a4.value()
            
            if self.chk_minmax.isChecked():
                data["minmax"] = {
                    "min": self.spin_min_strain.value(),
                    "max": self.spin_max_strain.value()
                }
                
        return data
