from PyQt6.QtWidgets import QMessageBox
from src.analysis.frame_generator import FrameGenerator
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction
from src.ui.dialogs.material_dialog import MaterialDialog
from src.ui.dialogs.section_dialog import SectionDialog

from src.ui.dialogs.geometry_dialog import GeometryDialog 


class DefineMenu(QMenu):
    def __init__(self,parent=None):
        super().__init__("Definir",parent)
        self.setup_actions()

    def setup_actions(self):
        #Materiales
        self.action_materials = QAction("Materiales",self)
        #Conectar el boton con material_dialog
        self.action_materials.triggered.connect(self.open_material_dialog)
        self.addAction(self.action_materials)

        #Secciones
        self.action_sections = QAction("Secciones",self)
        #Conectar el boton con section_dialog
        self.action_sections.triggered.connect(self.open_section_dialog)
        self.addAction(self.action_sections)

        #Geometría
        self.action_geometry = QAction("Geometría Libre (Nodos/Elementos)", self)
        self.action_geometry.triggered.connect(self.open_geometry_dialog)
        self.addAction(self.action_geometry)     


    def open_material_dialog(self):
        dlg = MaterialDialog(self)
        dlg.exec()

    def open_section_dialog(self):
        dlg = SectionDialog(self)
        dlg.exec()

    def open_geometry_dialog(self):
        dlg = GeometryDialog(self)
        dlg.exec()

    
