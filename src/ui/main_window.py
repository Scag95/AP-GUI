from PyQt6.QtWidgets import QMainWindow, QDockWidget
from PyQt6.QtCore import Qt 
from src.ui.menus.file_menu import FileMenu
from src.ui.menus.define_menu import DefineMenu
from src.ui.menus.assign_menu import AssignMenu
from src.ui.menus.analyze_menu import AnalyzeMenu
from src.ui.widgets.structure_interactor import StructureInteractor
from src.ui.widgets.properties_panel import PropertiesPanel
from src.analysis.manager import ProjectManager
from src.ui.widgets.command_line import CommandLineWidget
from src.analysis.command_processor import CommandProcessor

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
        
        self.analyze_menu = AnalyzeMenu(self)
        bar.addMenu(self.analyze_menu) 

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

        # Conectar cambios de unidades -> Refrescar gráfico
        from src.utils.units import UnitManager
        UnitManager.instance().unitsChanged.connect(self.refresh_project)

        # --- SISTEMA DE COMANDOS ---
        self.cmd_processor = CommandProcessor()
        self.console_widget = CommandLineWidget() 
        self.viz_widget.set_overlay_widget(self.console_widget)
        
        # Conectar señal
        self.console_widget.commandEntered.connect(self.execute_command)
        self.console_widget.log_message("Sistema listo. Prueba: 'tag nodes on'", "blue")

    def refresh_project(self):
        ProjectManager.instance().dataChanged.emit()

    def execute_command(self, cmd):
        # 1. Procesar lógica
        msg, action = self.cmd_processor.process_command(cmd)
        
        # 2. Mostrar respuesta
        if msg:
            color = "red" if "error" in msg.lower() else "black"
            self.console_widget.log_message(msg, color)
        # 3. Ejecutar acción visual (si la hay)
        if action:
            act_type = action.get("action")
            value = action.get("value")
            if act_type == "toggle_node_labels":
                self.viz_widget.toggle_node_labels(value)
            elif act_type == "toggle_element_labels":
                self.viz_widget.toggle_element_labels(value)
            elif act_type == "set_visibility":
                self.viz_widget.set_visibility(action.get("type"), value)
            elif act_type == "set_diagram_type":
                self.viz_widget.show_force_diagrams(value) # Ya existe este método, lo reusamos
                self.viz_widget.set_visibility("diagrams", True)
            elif act_type == "set_load_visibility":
                self.viz_widget.set_load_visibility(action.get("type"), value)
        



    


