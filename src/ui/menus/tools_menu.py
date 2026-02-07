from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction
from src.ui.dialogs.self_weight_dialog import SelfWeightDialog

class ToolsMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__("Herramientas", parent)
        self.main_window = parent

        #Submenú: Cargas
        self.loads_menu = QMenu("Generación de Cargas", self)
        self.addMenu(self.loads_menu)

        #Acción Peso propio
        self.action_self_weight = QAction("Generar Peso Propio")
        self.action_self_weight.setStatusTip("Calcula y aplica cargas distribuidas en la sección y material")

        self.action_self_weight.triggered.connect(self.open_self_weight_dialog)
        self.loads_menu.addAction(self.action_self_weight)

    def open_self_weight_dialog(self):
        dialog = SelfWeightDialog(self.main_window)
        dialog.exec()

