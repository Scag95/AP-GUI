from PyQt6.QtWidgets import QMainWindow
from src.ui.menus.file_menu import FileMenu
from src.ui.menus.define_menu import DefineMenu



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        #Configuración basica    
        self.setWindowTitle("AP-GUI")
        self.resize(1200,800) #Tamaño de la ventana

        bar = self.menuBar()

        self.file_menu = FileMenu(self)
        bar.addMenu(self.file_menu)

        self.define_menu =DefineMenu(self)
        bar.addMenu(self.define_menu)




    


