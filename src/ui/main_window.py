from PyQt6.QtWidgets import QMainWindow, QDockWidget, QMdiArea, QMdiSubWindow
from PyQt6.QtCore import Qt 
from PyQt6.QtGui import QAction
from src.ui.menus.file_menu import FileMenu
from src.ui.menus.define_menu import DefineMenu
from src.ui.menus.assign_menu import AssignMenu
from src.ui.menus.analyze_menu import AnalyzeMenu
from src.ui.widgets.structure_interactor import StructureInteractor
from src.ui.widgets.properties_panel import PropertiesPanel
from src.analysis.manager import ProjectManager
from src.ui.widgets.command_line import CommandLineWidget
from src.analysis.command_processor import CommandProcessor
from src.ui.menus.tools_menu import ToolsMenu
from src.ui.widgets.animation_toolbar import AnimationToolbar
from src.ui.widgets.scales_panel import ScalesPanel

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

        self.tools_menu = ToolsMenu(self)
        bar.addMenu(self.tools_menu) 
        
        self.analyze_menu = AnalyzeMenu(self)
        bar.addMenu(self.analyze_menu) 
        
        self.view_menu = bar.addMenu("Ver")
        
        self.act_new_view = QAction("Nueva Vista 3D", self)
        self.act_new_view.triggered.connect(lambda: self.add_new_viewport())
        self.view_menu.addAction(self.act_new_view)
        self.view_menu.addSeparator()

        # --- ANIMATION TOOLBAR ---
        self.anim_toolbar = AnimationToolbar(self)
        self.addToolBar(self.anim_toolbar)
        self.anim_toolbar.hide() # Oculta por defecto hasta que haya un resultado de Pushover

        self.mdi_area = QMdiArea()
        self.setCentralWidget(self.mdi_area)

        #Panel de propiedades
        self.props_panel = PropertiesPanel(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea,self.props_panel)
        
        # Acción en el menú "Ver" para ocultar/mostrar panel de propiedades
        view_props_action = self.props_panel.toggleViewAction()
        view_props_action.setText("Panel de Propiedades")
        self.view_menu.addAction(view_props_action)

        # Primer Viewport Inicial
        self.add_new_viewport("Vista General")

        # Conexiones Panel -> Manager (Refrescar gráfico)
        self.props_panel.dataChanged.connect(self.refresh_project)

        # Conectar cambios de unidades -> Refrescar gráfico
        from src.utils.units import UnitManager
        UnitManager.instance().unitsChanged.connect(self.refresh_project)

        # --- SISTEMA DE COMANDOS ---
        self.cmd_processor = CommandProcessor()
        self.console_widget = CommandLineWidget() 
        
        self.console_dock = QDockWidget(self)
        self.console_dock.setWidget(self.console_widget)
        self.console_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)
        # Quitar la barra de título (botones de cerrar/maximizar) asignando un widget vacío
        from PyQt6.QtWidgets import QWidget
        self.console_dock.setTitleBarWidget(QWidget())
        
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.console_dock)
        
        # Acción en el menú "Ver"
        view_console_action = self.console_dock.toggleViewAction()
        view_console_action.setText("Consola de Comandos")
        self.view_menu.addAction(view_console_action)

        # --- SCALES PANEL ---
        self.scales_panel = ScalesPanel(self)
        self.scales_dock = QDockWidget("Panel de Escalas", self)
        self.scales_dock.setWidget(self.scales_panel)
        self.scales_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.scales_dock)
        
        # Acción en el menú "Ver"
        view_scales_action = self.scales_dock.toggleViewAction()
        view_scales_action.setText("Panel de Escalas")
        self.view_menu.addAction(view_scales_action)
        self.scales_dock.hide() # Oculto por defecto
        
        # Conectar señal de consola
        self.console_widget.commandEntered.connect(self.execute_command)
        self.console_widget.log_message("Sistema listo. Prueba: 'tag nodes on'", "blue")

    def refresh_project(self):
        ProjectManager.instance().dataChanged.emit()

    @property
    def _viewports(self):
        return [sub.widget() for sub in self.mdi_area.subWindowList() if isinstance(sub.widget(), StructureInteractor)]

    @property
    def viz_widget(self):
        """Devuelve el interactor activo para retrocompatibilidad con los menus"""
        active_sub = self.mdi_area.activeSubWindow()
        if active_sub and isinstance(active_sub.widget(), StructureInteractor):
            return active_sub.widget()
        vps = self._viewports
        return vps[-1] if vps else None

    def add_new_viewport(self, title=None):
        vps_count = len(self._viewports)
        if not title:
            title = f"Vista 3D - {vps_count + 1}"
        interactor = StructureInteractor()
        sub_window = QMdiSubWindow()
        sub_window.setWidget(interactor)
        sub_window.setWindowTitle(title)
        
        # Conexiones Interactor -> Panel
        interactor.nodeSelected.connect(self.props_panel.show_node)
        interactor.elementSelected.connect(self.props_panel.show_element)
        interactor.selectionCleared.connect(self.props_panel.clear_selection)
        
        self.mdi_area.addSubWindow(sub_window)
        sub_window.show()
        
        # Si ya hay un result de gravedad guardado, pasarlo
        if ProjectManager.instance().gravity_results:
             interactor.show_deformation(ProjectManager.instance().gravity_results)
             
        self.mdi_area.tileSubWindows()
        return interactor

    def broadcast_results(self, results):
        """Envía resultados a todas las ventanas abiertas y lanza panel de escalas"""
        self.scales_dock.show()
        self.scales_dock.raise_()
        for viz in self._viewports:
            viz.show_deformation(results)

    def toggle_animation_toolbar(self, show=True):
        if show:
            if self.anim_toolbar.load_pushover_results():
                self.anim_toolbar.show()
                for viz in self._viewports:
                    viz.set_visibility("deformed", True)
            else:
                print("[UI] No hay resultados de Pushover para animar.")
        else:
            self.anim_toolbar.hide()
            for viz in self._viewports:
                viz.renderer_deform.clear(viz.plot_widget)

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
            viz = self.viz_widget
            if not viz: return
            if act_type == "toggle_node_labels":
                viz.toggle_node_labels(value)
            elif act_type == "toggle_element_labels":
                viz.toggle_element_labels(value)
            elif act_type == "set_visibility":
                viz.set_visibility(action.get("type"), value)
            elif act_type == "set_diagram_type":
                viz.show_force_diagrams(value) 
                viz.set_visibility("diagrams", True)
            elif act_type == "set_load_visibility":
                viz.set_load_visibility(action.get("type"), value)
        



    


