
from PyQt6.QtWidgets import (QWidget, QFormLayout, QGroupBox, QComboBox,
                             QDoubleSpinBox, QSpinBox, QLineEdit)
from src.analysis.manager import ProjectManager
from src.analysis.materials import Concrete01, Steel01


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
        self.spin_b = QSpinBox()
        self.spin_b.setRange(0,10000)
        self.spin_b.setSuffix(" mm")
        self.spin_b.setValue(300)
        layout.addRow("Base de la sección:",self.spin_b)
        #Altura
        self.spin_h = QSpinBox()
        self.spin_h.setRange(0,10000)
        self.spin_h.setSuffix(" mm")
        self.spin_h.setValue(300)
        layout.addRow("Altura de la sección:",self.spin_h)

        self.combo_concrete = QComboBox()
        self.combo_steel = QComboBox()
        
        # Llenar los combos
        self.populate_materials()
        
        layout.addRow("Material Concreto:", self.combo_concrete)
        layout.addRow("Material Acero:", self.combo_steel)

        # --- Recubrimiento ---
        self.spin_cover = QSpinBox()
        self.spin_cover.setRange(0, 150)
        self.spin_cover.setSuffix(" mm")
        self.spin_cover.setValue(40)
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
        
        self.spin_top_diam = QSpinBox()
        self.spin_top_diam.setRange(0, 100)
        self.spin_top_diam.setSuffix(" mm")
        self.spin_top_diam.setValue(20)
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
        
        self.spin_bot_diam = QSpinBox()
        self.spin_bot_diam.setSuffix(" mm")
        self.spin_bot_diam.setValue(20)
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
            "b":self.spin_b.value(),
            "h":self.spin_h.value(),
            "concrete":self.combo_concrete.currentData(),
            "steel":self.combo_steel.currentData(),
            "cover":self.spin_cover.value(),
            "bot_qty":self.spin_bot_qty.value(),
            "bot_diam":self.spin_bot_diam.value(),
            "top_qty":self.spin_top_qty.value(),
            "top_diam":self.spin_top_diam.value()
        }