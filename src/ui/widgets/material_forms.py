from PyQt6.QtWidgets import QWidget, QFormLayout, QDoubleSpinBox, QSpinBox, QCheckBox, QVBoxLayout, QTabWidget
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
        self.spin_fpc.setRange(-1e10, 1e10) 
        self.spin_fpc.set_value_base(25*1e6) # 25 MPa
        layout.addRow("Resistencia a la compresión [fpc]",self.spin_fpc)

        #Campo epsc0
        self.spin_epsc0 = QDoubleSpinBox()
        self.spin_epsc0.setDecimals(4)
        self.spin_epsc0.setRange(-1e10, 1e10) 
        self.spin_epsc0.setSingleStep(0.0001)
        self.spin_epsc0.setValue(0.0020)
        layout.addRow("Deformación Unitaria [epsc0]",self.spin_epsc0)

        #Campo fpcU
        self.spin_fpcU = UnitSpinBox(UnitType.STRESS)
        self.spin_fpcU.setDecimals(0)
        self.spin_fpcU.setRange(-1e10, 1e10)
        self.spin_fpcU.set_value_base(25*1e6) # 25 MPa

        layout.addRow("Resistencia al aplastamiento [fpcU]",self.spin_fpcU)

        #Campo epscU
        self.spin_epscU = QDoubleSpinBox()
        self.spin_epscU.setDecimals(4)
        self.spin_epscU.setRange(-1e10, 1e10) 
        self.spin_epscU.setSingleStep(0.0001)
        self.spin_epscU.setValue(0.0035)
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
        self.spin_b.setDecimals(6)
        self.spin_b.setSingleStep(0.000001)
        self.spin_b.setValue(0.000001)
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
        self.spin_a2.setValue(1.0)
        opt_layout.addRow("Parámetro endur. [a2]:", self.spin_a2)

        self.spin_a3 = QDoubleSpinBox()
        self.spin_a3.setDecimals(3)
        self.spin_a3.setValue(0.0)
        opt_layout.addRow("Parámetro endur. [a3]:", self.spin_a3)

        self.spin_a4 = QDoubleSpinBox()
        self.spin_a4.setDecimals(3)
        self.spin_a4.setValue(1.0)
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
        a2 = getattr(material, 'a2', 1.0)
        a3 = getattr(material, 'a3', 0.0)
        a4 = getattr(material, 'a4', 1.0)
        
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


class ElasticForm(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout(self)

        # Densidad
        self.spin_rho = UnitSpinBox(UnitType.DENSITY)
        self.spin_rho.setDecimals(0)
        self.spin_rho.setRange(0, 1e6)
        self.spin_rho.set_value_base(7850) # Por defecto como acero
        layout.addRow("Densidad [rho]:", self.spin_rho)

        # Módulo de elasticidad E
        self.spin_E = UnitSpinBox(UnitType.STRESS)
        self.spin_E.setDecimals(0)
        self.spin_E.setRange(0, 1e12)
        self.spin_E.set_value_base(200*1e9) # 200 GPa
        layout.addRow("Módulo Elástico [E]:", self.spin_E)

    def set_data(self, material):
        if not material: return
        self.spin_rho.set_value_base(material.rho)
        self.spin_E.set_value_base(material.E)

    def get_data(self):
        return {
            "rho": self.spin_rho.get_value_base(),
            "E": self.spin_E.get_value_base()
        }

class HystereticForm(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # Densidad
        form_rho = QFormLayout()
        self.spin_rho = UnitSpinBox(UnitType.DENSITY)
        self.spin_rho.setDecimals(1)
        self.spin_rho.setRange(0, 1e6)
        form_rho.addRow("Densidad [rho]:", self.spin_rho)
        layout.addLayout(form_rho)

        # Tabs para envolventes y evitar interfaz kilométrica
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.tab_pos = QWidget()
        self.tab_neg = QWidget()
        self.tab_hys = QWidget()

        self.tabs.addTab(self.tab_pos, "Env. Positiva (+)")
        self.tabs.addTab(self.tab_neg, "Env. Negativa (-)")
        self.tabs.addTab(self.tab_hys, "Histéresis")

        # Configurar Tab Positiva
        pos_layout = QFormLayout(self.tab_pos)
        self.spin_s1p = UnitSpinBox(UnitType.STRESS)
        self.spin_e1p = QDoubleSpinBox(); self.spin_e1p.setDecimals(6); self.spin_e1p.setRange(0, 10.0); self.spin_e1p.setSingleStep(0.001)
        self.spin_s2p = UnitSpinBox(UnitType.STRESS)
        self.spin_e2p = QDoubleSpinBox(); self.spin_e2p.setDecimals(6); self.spin_e2p.setRange(0, 10.0); self.spin_e2p.setSingleStep(0.001)
        self.spin_s3p = UnitSpinBox(UnitType.STRESS)
        self.spin_e3p = QDoubleSpinBox(); self.spin_e3p.setDecimals(6); self.spin_e3p.setRange(0, 10.0); self.spin_e3p.setSingleStep(0.001)
        
        for spin in [self.spin_s1p, self.spin_s2p, self.spin_s3p]:
            spin.setRange(-1e15, 1e15)
            
        pos_layout.addRow("Esfuerzo 1 [s1p]:", self.spin_s1p)
        pos_layout.addRow("Deformación 1 [e1p]:", self.spin_e1p)
        pos_layout.addRow("Esfuerzo 2 [s2p]:", self.spin_s2p)
        pos_layout.addRow("Deformación 2 [e2p]:", self.spin_e2p)
        pos_layout.addRow("Esfuerzo 3 [s3p]:", self.spin_s3p)
        pos_layout.addRow("Deformación 3 [e3p]:", self.spin_e3p)

        # Configurar Tab Negativa
        neg_layout = QFormLayout(self.tab_neg)
        self.spin_s1n = UnitSpinBox(UnitType.STRESS)
        self.spin_e1n = QDoubleSpinBox(); self.spin_e1n.setDecimals(6); self.spin_e1n.setRange(-10.0, 0); self.spin_e1n.setSingleStep(0.001)
        self.spin_s2n = UnitSpinBox(UnitType.STRESS)
        self.spin_e2n = QDoubleSpinBox(); self.spin_e2n.setDecimals(6); self.spin_e2n.setRange(-10.0, 0); self.spin_e2n.setSingleStep(0.001)
        self.spin_s3n = UnitSpinBox(UnitType.STRESS)
        self.spin_e3n = QDoubleSpinBox(); self.spin_e3n.setDecimals(6); self.spin_e3n.setRange(-10.0, 0); self.spin_e3n.setSingleStep(0.001)
        
        for spin in [self.spin_s1n, self.spin_s2n, self.spin_s3n]:
            spin.setRange(-1e15, 1e15)

        neg_layout.addRow("Esfuerzo 1 [s1n]:", self.spin_s1n)
        neg_layout.addRow("Deformación 1 [e1n]:", self.spin_e1n)
        neg_layout.addRow("Esfuerzo 2 [s2n]:", self.spin_s2n)
        neg_layout.addRow("Deformación 2 [e2n]:", self.spin_e2n)
        neg_layout.addRow("Esfuerzo 3 [s3n]:", self.spin_s3n)
        neg_layout.addRow("Deformación 3 [e3n]:", self.spin_e3n)

        # Configurar Tab Histéresis
        hys_layout = QFormLayout(self.tab_hys)
        self.spin_pinch_x = QDoubleSpinBox(); self.spin_pinch_x.setRange(0, 1.0); self.spin_pinch_x.setDecimals(3); self.spin_pinch_x.setSingleStep(0.1)
        self.spin_pinch_y = QDoubleSpinBox(); self.spin_pinch_y.setRange(0, 1.0); self.spin_pinch_y.setDecimals(3); self.spin_pinch_y.setSingleStep(0.1)
        self.spin_damage1 = QDoubleSpinBox(); self.spin_damage1.setRange(0, 1.0); self.spin_damage1.setDecimals(3); self.spin_damage1.setSingleStep(0.1)
        self.spin_damage2 = QDoubleSpinBox(); self.spin_damage2.setRange(0, 1.0); self.spin_damage2.setDecimals(3); self.spin_damage2.setSingleStep(0.1)
        
        self.chk_beta = QCheckBox("Definir degradación de descarga (beta)")
        self.spin_beta = QDoubleSpinBox(); self.spin_beta.setRange(0, 1.0); self.spin_beta.setDecimals(3); self.spin_beta.setSingleStep(0.1)
        self.spin_beta.setEnabled(False)
        self.chk_beta.toggled.connect(self.spin_beta.setEnabled)

        hys_layout.addRow("Pinch X (e):", self.spin_pinch_x)
        hys_layout.addRow("Pinch Y (F):", self.spin_pinch_y)
        hys_layout.addRow("Daño 1 (ductilidad):", self.spin_damage1)
        hys_layout.addRow("Daño 2 (energía):", self.spin_damage2)
        hys_layout.addRow(self.chk_beta)
        hys_layout.addRow("Valor Beta:", self.spin_beta)

    def set_data(self, material):
        if not material: return
        self.spin_rho.set_value_base(material.rho)
        self.spin_s1p.set_value_base(material.s1p); self.spin_e1p.setValue(material.e1p)
        self.spin_s2p.set_value_base(material.s2p); self.spin_e2p.setValue(material.e2p)
        self.spin_s3p.set_value_base(material.s3p); self.spin_e3p.setValue(material.e3p)

        self.spin_s1n.set_value_base(material.s1n); self.spin_e1n.setValue(material.e1n)
        self.spin_s2n.set_value_base(material.s2n); self.spin_e2n.setValue(material.e2n)
        self.spin_s3n.set_value_base(material.s3n); self.spin_e3n.setValue(material.e3n)

        self.spin_pinch_x.setValue(material.pinch_x)
        self.spin_pinch_y.setValue(material.pinch_y)
        self.spin_damage1.setValue(material.damage1)
        self.spin_damage2.setValue(material.damage2)

        if material.beta is not None:
            self.chk_beta.setChecked(True)
            self.spin_beta.setValue(material.beta)
        else:
            self.chk_beta.setChecked(False)

    def get_data(self):
        return {
            "rho": self.spin_rho.get_value_base(),
            "s1p": self.spin_s1p.get_value_base(), "e1p": self.spin_e1p.value(),
            "s2p": self.spin_s2p.get_value_base(), "e2p": self.spin_e2p.value(),
            "s3p": self.spin_s3p.get_value_base(), "e3p": self.spin_e3p.value(),
            "s1n": self.spin_s1n.get_value_base(), "e1n": self.spin_e1n.value(),
            "s2n": self.spin_s2n.get_value_base(), "e2n": self.spin_e2n.value(),
            "s3n": self.spin_s3n.get_value_base(), "e3n": self.spin_e3n.value(),
            "pinch_x": self.spin_pinch_x.value(),
            "pinch_y": self.spin_pinch_y.value(),
            "damage1": self.spin_damage1.value(),
            "damage2": self.spin_damage2.value(),
            "beta": self.spin_beta.value() if self.chk_beta.isChecked() else None
        }

class HystereticSMForm(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # Densidad
        form_rho = QFormLayout()
        self.spin_rho = UnitSpinBox(UnitType.DENSITY)
        self.spin_rho.setDecimals(1)
        self.spin_rho.setRange(0, 1e6)
        form_rho.addRow("Densidad [rho]:", self.spin_rho)
        layout.addLayout(form_rho)

        # Tabs para envolventes y evitar interfaz kilométrica
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.tab_pos = QWidget()
        self.tab_neg = QWidget()
        self.tab_hys = QWidget()

        self.tabs.addTab(self.tab_pos, "Env. Positiva (+)")
        self.tabs.addTab(self.tab_neg, "Env. Negativa (-)")
        self.tabs.addTab(self.tab_hys, "Histéresis")

        # Configurar Tab Positiva (4 puntos)
        pos_layout = QFormLayout(self.tab_pos)
        self.spin_s1p = UnitSpinBox(UnitType.STRESS)
        self.spin_e1p = QDoubleSpinBox(); self.spin_e1p.setDecimals(6); self.spin_e1p.setRange(0, 10.0); self.spin_e1p.setSingleStep(0.001)
        self.spin_s2p = UnitSpinBox(UnitType.STRESS)
        self.spin_e2p = QDoubleSpinBox(); self.spin_e2p.setDecimals(6); self.spin_e2p.setRange(0, 10.0); self.spin_e2p.setSingleStep(0.001)
        self.spin_s3p = UnitSpinBox(UnitType.STRESS)
        self.spin_e3p = QDoubleSpinBox(); self.spin_e3p.setDecimals(6); self.spin_e3p.setRange(0, 10.0); self.spin_e3p.setSingleStep(0.001)
        self.spin_s4p = UnitSpinBox(UnitType.STRESS)
        self.spin_e4p = QDoubleSpinBox(); self.spin_e4p.setDecimals(6); self.spin_e4p.setRange(0, 10.0); self.spin_e4p.setSingleStep(0.001)
        
        for spin in [self.spin_s1p, self.spin_s2p, self.spin_s3p, self.spin_s4p]:
            spin.setRange(-1e15, 1e15)
            
        pos_layout.addRow("Esfuerzo 1 [s1p]:", self.spin_s1p)
        pos_layout.addRow("Deformación 1 [e1p]:", self.spin_e1p)
        pos_layout.addRow("Esfuerzo 2 [s2p]:", self.spin_s2p)
        pos_layout.addRow("Deformación 2 [e2p]:", self.spin_e2p)
        pos_layout.addRow("Esfuerzo 3 [s3p]:", self.spin_s3p)
        pos_layout.addRow("Deformación 3 [e3p]:", self.spin_e3p)
        pos_layout.addRow("Esfuerzo 4 [s4p]:", self.spin_s4p)
        pos_layout.addRow("Deformación 4 [e4p]:", self.spin_e4p)

        # Configurar Tab Negativa (4 puntos)
        neg_layout = QFormLayout(self.tab_neg)
        self.spin_s1n = UnitSpinBox(UnitType.STRESS)
        self.spin_e1n = QDoubleSpinBox(); self.spin_e1n.setDecimals(6); self.spin_e1n.setRange(-10.0, 0); self.spin_e1n.setSingleStep(0.001)
        self.spin_s2n = UnitSpinBox(UnitType.STRESS)
        self.spin_e2n = QDoubleSpinBox(); self.spin_e2n.setDecimals(6); self.spin_e2n.setRange(-10.0, 0); self.spin_e2n.setSingleStep(0.001)
        self.spin_s3n = UnitSpinBox(UnitType.STRESS)
        self.spin_e3n = QDoubleSpinBox(); self.spin_e3n.setDecimals(6); self.spin_e3n.setRange(-10.0, 0); self.spin_e3n.setSingleStep(0.001)
        self.spin_s4n = UnitSpinBox(UnitType.STRESS)
        self.spin_e4n = QDoubleSpinBox(); self.spin_e4n.setDecimals(6); self.spin_e4n.setRange(-10.0, 0); self.spin_e4n.setSingleStep(0.001)
        
        for spin in [self.spin_s1n, self.spin_s2n, self.spin_s3n, self.spin_s4n]:
            spin.setRange(-1e15, 1e15)

        neg_layout.addRow("Esfuerzo 1 [s1n]:", self.spin_s1n)
        neg_layout.addRow("Deformación 1 [e1n]:", self.spin_e1n)
        neg_layout.addRow("Esfuerzo 2 [s2n]:", self.spin_s2n)
        neg_layout.addRow("Deformación 2 [e2n]:", self.spin_e2n)
        neg_layout.addRow("Esfuerzo 3 [s3n]:", self.spin_s3n)
        neg_layout.addRow("Deformación 3 [e3n]:", self.spin_e3n)
        neg_layout.addRow("Esfuerzo 4 [s4n]:", self.spin_s4n)
        neg_layout.addRow("Deformación 4 [e4n]:", self.spin_e4n)

        # Configurar Tab Histéresis
        hys_layout = QFormLayout(self.tab_hys)
        self.spin_pinch_x = QDoubleSpinBox(); self.spin_pinch_x.setRange(0, 1.0); self.spin_pinch_x.setDecimals(3); self.spin_pinch_x.setSingleStep(0.1)
        self.spin_pinch_y = QDoubleSpinBox(); self.spin_pinch_y.setRange(0, 1.0); self.spin_pinch_y.setDecimals(3); self.spin_pinch_y.setSingleStep(0.1)
        self.spin_damage1 = QDoubleSpinBox(); self.spin_damage1.setRange(0, 1.0); self.spin_damage1.setDecimals(3); self.spin_damage1.setSingleStep(0.1)
        self.spin_damage2 = QDoubleSpinBox(); self.spin_damage2.setRange(0, 1.0); self.spin_damage2.setDecimals(3); self.spin_damage2.setSingleStep(0.1)
        
        self.chk_beta = QCheckBox("Definir degradación de descarga (beta)")
        self.spin_beta = QDoubleSpinBox(); self.spin_beta.setRange(0, 1.0); self.spin_beta.setDecimals(3); self.spin_beta.setSingleStep(0.1)
        self.spin_beta.setEnabled(False)
        self.chk_beta.toggled.connect(self.spin_beta.setEnabled)

        hys_layout.addRow("Pinch X (e):", self.spin_pinch_x)
        hys_layout.addRow("Pinch Y (F):", self.spin_pinch_y)
        hys_layout.addRow("Daño 1 (ductilidad):", self.spin_damage1)
        hys_layout.addRow("Daño 2 (energía):", self.spin_damage2)
        hys_layout.addRow(self.chk_beta)
        hys_layout.addRow("Valor Beta:", self.spin_beta)

    def set_data(self, material):
        if not material: return
        self.spin_rho.set_value_base(material.rho)
        self.spin_s1p.set_value_base(material.s1p); self.spin_e1p.setValue(material.e1p)
        self.spin_s2p.set_value_base(material.s2p); self.spin_e2p.setValue(material.e2p)
        self.spin_s3p.set_value_base(material.s3p); self.spin_e3p.setValue(material.e3p)
        self.spin_s4p.set_value_base(material.s4p); self.spin_e4p.setValue(material.e4p)

        self.spin_s1n.set_value_base(material.s1n); self.spin_e1n.setValue(material.e1n)
        self.spin_s2n.set_value_base(material.s2n); self.spin_e2n.setValue(material.e2n)
        self.spin_s3n.set_value_base(material.s3n); self.spin_e3n.setValue(material.e3n)
        self.spin_s4n.set_value_base(material.s4n); self.spin_e4n.setValue(material.e4n)

        self.spin_pinch_x.setValue(material.pinch_x)
        self.spin_pinch_y.setValue(material.pinch_y)
        self.spin_damage1.setValue(material.damage1)
        self.spin_damage2.setValue(material.damage2)

        if material.beta is not None:
            self.chk_beta.setChecked(True)
            self.spin_beta.setValue(material.beta)
        else:
            self.chk_beta.setChecked(False)

    def get_data(self):
        return {
            "rho": self.spin_rho.get_value_base(),
            "s1p": self.spin_s1p.get_value_base(), "e1p": self.spin_e1p.value(),
            "s2p": self.spin_s2p.get_value_base(), "e2p": self.spin_e2p.value(),
            "s3p": self.spin_s3p.get_value_base(), "e3p": self.spin_e3p.value(),
            "s4p": self.spin_s4p.get_value_base(), "e4p": self.spin_e4p.value(),
            "s1n": self.spin_s1n.get_value_base(), "e1n": self.spin_e1n.value(),
            "s2n": self.spin_s2n.get_value_base(), "e2n": self.spin_e2n.value(),
            "s3n": self.spin_s3n.get_value_base(), "e3n": self.spin_e3n.value(),
            "s4n": self.spin_s4n.get_value_base(), "e4n": self.spin_e4n.value(),
            "pinch_x": self.spin_pinch_x.value(),
            "pinch_y": self.spin_pinch_y.value(),
            "damage1": self.spin_damage1.value(),
            "damage2": self.spin_damage2.value(),
            "beta": self.spin_beta.value() if self.chk_beta.isChecked() else None
        }
