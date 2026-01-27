from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import Qt 
from src.ui.menus.file_menu import FileMenu
from src.ui.menus.define_menu import DefineMenu
from src.ui.menus.assign_menu import AssignMenu
from src.ui.widgets.structure_interactor import StructureInteractor
from src.ui.widgets.properties_panel import PropertiesPanel
from src.analysis.manager import ProjectManager

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

        self.assign_menu = AssignMenu(self)
        bar.addMenu(self.assign_menu) 

        self.viz_widget = StructureInteractor()
        self.setCentralWidget(self.viz_widget)

        #Panel de propiedades
        self.props_panel = PropertiesPanel(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea,self.props_panel)

        #Conexiones Interactor -> Panel
        self.viz_widget.nodeSelected.connect(self.props_panel.show_node)
        self.viz_widget.selectionCleared.connect(self.props_panel.clear_selection)

        # Conexiones Panel -> Manager (Refrescar gráfico)
        self.props_panel.dataChanged.connect(self.refresh_project)


    def refresh_project(self):
        ProjectManager.instance().dataChanged.emit()

        
        



    


