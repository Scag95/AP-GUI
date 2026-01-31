from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction
from src.ui.dialogs.element_loads_dialog import ElementLoadsDialog
from src.ui.dialogs.nodal_loads_dialog import NodalLoadsDialog
from src.ui.dialogs.restraints_dialog import RestraintsDialog

class AssignMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__("Asignar",parent)

        # 1. Restricciones en los nodos
        self.action_restraints = QAction("Restricciones", self)
        self.action_restraints.triggered.connect(self.open_restraints)
        self.addAction(self.action_restraints)

        #2. Cargas en los nodos
        self.action_nodal_loads = QAction("Cargas en los nodos", self)
        self.action_nodal_loads.triggered.connect(self.open_nodal_loads)
        self.addAction(self.action_nodal_loads)

        #3. Cargas en los elementos
        self.action_element_loads = QAction("Cargas en los elementos",self)
        self.action_element_loads.triggered.connect(self.open_element_loads)
        self.addAction(self.action_element_loads)

    def open_element_loads(self):
        dialog = ElementLoadsDialog(self.parent())
        dialog.exec()

    def open_nodal_loads(self):
        dialog = NodalLoadsDialog(self.parent())
        dialog.exec()

    def open_restraints(self):
        dlg = RestraintsDialog(self)
        dlg.exec() 
