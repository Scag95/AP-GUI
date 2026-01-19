from PyQt6.QtWidgets import QApplication, QMainWindow,QLabel,QVBoxLayout,QWidget
from PyQt6.QtGui import QAction 

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        #Configuración basica    
        self.setWindowTitle("AP-GUI")
        self.resize(1200,800) #Tamaño de la ventana

        # Llamamos a las funciones del MainWindow
        self._setup_ui()
        self._create_menu()


    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
    
    def _create_menu(self):
    #Definición de barra de tareas
        menu = self.menuBar()
        file_menu = menu.addMenu("&Archivo")
        define_menu = menu.addMenu("Definir")
        # Definición de Botones dentro del menú
        button_materials = QAction("Materiales",self)
        button_sections = QAction("Secciones",self)
        define_menu.addAction(button_materials)
        define_menu.addAction(button_sections)



    


