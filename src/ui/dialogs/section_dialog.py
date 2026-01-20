from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QListWidget, QPushButton, QWidget, QLabel,
                             QComboBox,QStackedWidget,QListWidgetItem, QFormLayout,
                             QDoubleSpinBox, QSpinBox, QComboBox, QGroupBox)
from PyQt6.QtCore import Qt

from src.analysis.manager import ProjectManager
from src.analysis.materials import Concrete01, Steel01

class SectionDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle("Definir Secciones")
        self.resize(800,600)

        #Centrar ventana al centro de la pantalla
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        layout = QFormLayout(self)


        #Base
        self.spin_b = QSpinBox()
        self.spin_b.setRange(0,10000)
        self.spin_b.setSuffix(" mm")
        self.spin_b.setValue(300)
        layout.addRow("base de la sección",self.spin_b)
        #Altura
        self.spin_h = QSpinBox()
        self.spin_h.setRange(0,10000)
        self.spin_h.setSuffix(" mm")
        self.spin_h.setValue(300)
        layout.addRow("altura de la sección",self.spin_h)

        self.combo_concrete = QComboBox()
        self.combo_steel = QComboBox()
        
        # Llenar los combos
        self.populate_materials()
        
        layout.addRow("Material Concreto:", self.combo_concrete)
        layout.addRow("Material Acero:", self.combo_steel)



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

