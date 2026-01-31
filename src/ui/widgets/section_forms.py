
from PyQt6.QtWidgets import (QWidget, QFormLayout, QGroupBox, QComboBox,
                             QSpinBox, QLineEdit)
from src.analysis.manager import ProjectManager
from src.analysis.materials import Concrete01, Steel01
from src.ui.widgets.unit_spinbox import UnitSpinBox
from src.utils.units import UnitType
import math


class SectionForm(QWidget):
    def __init__(self):
        super().__init__()
        #Panel Derecho
        layout = QFormLayout(self)
        
        #Nombre de la Sección
        self.textbox_name = QLineEdit()
        self.textbox_name.setPlaceholderText("ej: Viga_300x500")
        layout.addRow("Nombre de la sección",self.textbox_name)
        
        #Base
        self.spin_b = UnitSpinBox(UnitType.SECTION_DIM)
        self.spin_b.setRange(0, 1e6) # Rango amplio visual (ej. 1,000,000 mm)
        self.spin_b.setDecimals(2)   # 2 decimales fijos
        self.spin_b.set_value_base(0.3) # 300 mm = 0.3 m
        layout.addRow("Base de la sección:", self.spin_b)

        #Altura
        self.spin_h = UnitSpinBox(UnitType.SECTION_DIM)
        self.spin_h.setRange(0,1e6)  # Rango amplio visual (ej. 1,000,000 mm)
        self.spin_b.setDecimals(2)   # 2 decimales fijos
        self.spin_h.set_value_base(0.3)    # 300 mm = 0.3 m
        layout.addRow("Altura de la sección:",self.spin_h)

        self.combo_concrete = QComboBox()
        self.combo_steel = QComboBox()
        
        # Llenar los combos
        self.populate_materials()
        
        layout.addRow("Material Concreto:", self.combo_concrete)
        layout.addRow("Material Acero:", self.combo_steel)

        # --- Recubrimiento ---
        self.spin_cover = UnitSpinBox(UnitType.SECTION_DIM)
        self.spin_cover.setRange(0, 1e6)
        self.spin_cover.setDecimals(2)
        self.spin_cover.set_value_base(0.040)
        layout.addRow("Recubrimiento:", self.spin_cover)

        # --- Refuerzo Superior ---
        # Usamos un GroupBox para que se vea ordenado
        group_top = QGroupBox("Refuerzo Superior")
        form_top = QFormLayout() 
        group_top.setLayout(form_top)
        
        self.spin_top_qty = QSpinBox()
        self.spin_top_qty.setRange(0, 50)
        self.spin_top_qty.setValue(3)
        form_top.addRow("Cantidad:", self.spin_top_qty)
        
        self.spin_top_diam = UnitSpinBox(UnitType.SECTION_DIM)
        self.spin_top_diam.setRange(0, 100)
        self.spin_top_diam.setDecimals(2)
        self.spin_top_diam.set_value_base(0.020)
        form_top.addRow("Diámetro:", self.spin_top_diam)
        
        layout.addRow(group_top)
        # --- Refuerzo Inferior ---
        group_bot = QGroupBox("Refuerzo Inferior")
        form_bot = QFormLayout()
        group_bot.setLayout(form_bot)
        
        self.spin_bot_qty = QSpinBox()
        self.spin_bot_qty.setRange(0, 50)
        self.spin_bot_qty.setValue(3)
        form_bot.addRow("Cantidad:", self.spin_bot_qty)
        
        self.spin_bot_diam = UnitSpinBox(UnitType.SECTION_DIM)
        self.spin_bot_diam.setRange(0, 100)
        self.spin_bot_diam.setDecimals(2)
        self.spin_bot_diam.set_value_base(0.020)
        form_bot.addRow("Diámetro:", self.spin_bot_diam)
        
        layout.addRow(group_bot)



    def populate_materials(self):
        self.combo_concrete.clear()
        self.combo_steel.clear()

        materials = ProjectManager.instance().get_all_materials()

        for mat in materials:
            display_text = f"{mat.tag} - {mat.name} ({mat.__class__.__name__})"

            if isinstance(mat, Concrete01):
                self.combo_concrete.addItem(display_text, mat.tag)

            elif isinstance(mat, Steel01):
                self.combo_steel.addItem(display_text, mat.tag)

    def get_data(self):
        #Devuelve los valores del formulario
        return{
            "name": self.textbox_name.text(),
            "b": self.spin_b.get_value_base(),
            "h": self.spin_h.get_value_base(),
            "concrete": self.combo_concrete.currentData(),
            "steel": self.combo_steel.currentData(),
            "cover": self.spin_cover.get_value_base(),
            "bot_qty": self.spin_bot_qty.value(),
            "bot_diam": self.spin_bot_diam.get_value_base(),
            "top_qty": self.spin_top_qty.value(),
            "top_diam": self.spin_top_diam.get_value_base()
        }

    def set_data(self, section):
        if not section: return

        #1. Nombre
        self.textbox_name.setText(section.name)
        
        #2. Geometría
        if section.patches and len(section.patches) > 0:
            core = section.patches[0]
            # h  = yJ - yI
            h = abs(core.yJ - core.yI)
            # b = zJ - zI
            b = abs(core.zJ - core.zI)

            self.spin_h.set_value_base(h)
            self.spin_b.set_value_base(b)

            idx = self.combo_concrete.findData(core.material_tag)
            if idx >= 0:
                self.combo_concrete.setCurrentIndex(idx)
                
        self.spin_top_qty.setValue(0)
        self.spin_bot_qty.setValue(0)

        found_steel_mat = False

        for layer in section.layers:
            if not found_steel_mat:
                idx = self.combo_steel.findData(layer.material_tag)
                if idx>=0:
                    self.combo_steel.setCurrentIndex(idx)
                    found_steel_mat = True

            diam = math.sqrt(4*layer.area_bar/math.pi)

            if layer.yStart > 0:
                self.spin_top_qty.setValue(layer.num_bars)
                self.spin_top_diam.set_value_base(diam)
                h_val = self.spin_h.get_value_base()
                cover = (h_val/2) - layer.yStart

                if cover >0:
                    self.spin_cover.set_value_base(cover)
            elif layer.yStart <0:
                self.spin_bot_qty.setValue(layer.num_bars)
                self.spin_bot_diam.set_value_base(diam)