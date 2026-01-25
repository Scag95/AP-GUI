from PyQt6.QtWidgets import QMenu, QApplication, QFileDialog
from PyQt6.QtGui import QAction
from src.analysis.manager import ProjectManager



class FileMenu(QMenu):
    def __init__(self,parent=None):
        super().__init__("Archivo",parent)
        self.setup_actions()
    

    def setup_actions(self):

        
        #Cargar projecto
        self.actions_load_project = QAction("Cargar Projecto",self)
        self.actions_load_project.triggered.connect(self.open_load_dialog)
        self.addAction(self.actions_load_project)
        
        #Guardar projecto
        self.actions_save_project = QAction("Guardar Proyecto", self)
        self.actions_save_project.triggered.connect(self.open_save_dialog)
        self.addAction(self.actions_save_project)
    
        #Salir
        self.actions_exit =QAction("Salir",self)
        self.actions_exit.triggered.connect(QApplication.instance().quit)
        self.addAction(self.actions_exit)

        
    def open_save_dialog(self):
        manager = ProjectManager.instance()
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Projecto",
            "",
            "Archivos Json (*.json);;Todos los archivos (*)"
        )

        if filename:
            manager.save_project(filename)

    def open_load_dialog(self):
        manager = ProjectManager.instance()
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Cargar Proyecto",
            "",
            "Archivos JSON (*.json);;Todos los archivos (*)"
        )
        if filename:
            manager.load_project(filename)