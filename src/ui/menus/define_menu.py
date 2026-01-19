from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction
from src.ui.dialogs.material_dialog import MaterialDialog


class DefineMenu(QMenu):
    def __init__(self,parent=None):
        super().__init__("Definir",parent)
        self.setup_actions()

    def setup_actions(self):
        #Materiales
        self.action_materials = QAction("Materiales",self)
        self.action_materials.triggered.connect(self.open_material_dialog)
        self.addAction(self.action_materials)

        #Secciones
        self.action_sections = QAction("Secciones",self)
        self.addAction(self.action_sections)
    def open_material_dialog(self):
        dlg = MaterialDialog(self)
        dlg.exec()

