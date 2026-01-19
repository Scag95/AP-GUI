from PyQt6.QtWidgets import QMenu, QApplication
from PyQt6.QtGui import QAction


class FileMenu(QMenu):
    def __init__(self,parent=None):
        super().__init__("Archivo",parent)
        self.setup_actions()

    def setup_actions(self):
        #Salir
        self.actions_exit =QAction("Salir",self)
        
        self.actions_exit.triggered.connect(QApplication.instance().quit)
        
        self.addAction(self.actions_exit)

        
