import pyqtgraph as pg
import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QKeySequence, QShortcut
from src.analysis.manager import ProjectManager

# Importamos los nuevos renderizadores
from src.utils.scale_manager import ScaleManager
from src.ui.visualizers.model_renderer import ModelRenderer
from src.ui.visualizers.load_renderer import LoadRenderer
from src.ui.visualizers.deformation_renderer import DeformationRenderer
from src.ui.visualizers.force_diagram_renderer import ForceDiagramRenderer

class StructureInteractor(QWidget):
    nodeSelected = pyqtSignal(object)
    selectionCleared = pyqtSignal()
    elementSelected = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)

        # 1. Configurar el lienzo gráfico
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.showGrid(x=False,y=False, alpha=0.3)
        self.plot_widget.setAspectLocked(True)
        self.layout.addWidget(self.plot_widget)
        
        # 2. Project Manager
        self.manager = ProjectManager.instance()
        
        # 3. Inicializar Renderizadores
        self.renderer_model = ModelRenderer()
        self.renderer_model.attach(self.plot_widget)
        
        self.renderer_load = LoadRenderer()
        self.renderer_deform = DeformationRenderer()
        self.renderer_forces = ForceDiagramRenderer()
        self.current_diagram_type = None
        
        # Conectar Señales (Una vez todo inicializado)
        self.manager.dataChanged.connect(self._on_data_changed)
        ScaleManager.instance().scale_changed.connect(lambda t,v: self.refresh_viz())
        
        # 4. Estado de Interacción
        self.last_clicked_point = None
        self.last_clicked_element = None  
        self.current_label = None 
        self.current_results = None 

        # View Options
        self.show_node_labels = False 
        self.show_element_labels = False
        self.show_loads_nodes = True
        self.show_loads_elements = True
        self.show_deformed = True
        self.show_diagrams = True
        # --- ATAJOS DE TECLADO ---
        # Cargas (Ctrl +/-)
        self.shortcut_inc = QShortcut(QKeySequence("Ctrl++"), self)
        self.shortcut_inc.activated.connect(self.increase_load_scale)
        self.shortcut_dec = QShortcut(QKeySequence("Ctrl+-"), self)
        self.shortcut_dec.activated.connect(self.decrease_load_scale)

        # Deformada (PgUp / PgDown)
        self.shortcut_inc_def = QShortcut(QKeySequence("PgUp"), self)
        self.shortcut_inc_def.activated.connect(self.increase_deform_scale)
        self.shortcut_dec_def = QShortcut(QKeySequence("PgDown"), self)
        self.shortcut_dec_def.activated.connect(self.decrease_deform_scale)

        # Conectar eventos de la escena
        self.renderer_model.scatter_nodes.sigClicked.connect(self._on_node_clicked_wrapper)
        self.plot_widget.scene().sigMouseClicked.connect(self._on_background_clicked)

    def _on_data_changed(self):
        # Recalcular escalas automáticamente al cambiar geometría
        ScaleManager.instance().autocalculate_scales()
        self.refresh_viz()

    def set_overlay_widget(self, widget):
        self.overlay_widget = widget
        widget.setParent(self)
        widget.show()
        self.resizeEvent(None)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "overlay_widget") and self.overlay_widget:
            w = self.width()
            h_overlay = self.overlay_widget.height() 
            h_parent = self.height()
            self.overlay_widget.setGeometry(0, h_parent - h_overlay, w, h_overlay)

    def refresh_viz(self):
        """Redibuja todo usando los renderizadores."""
        self.last_clicked_point = None
        self.current_label = None 
        
        # Render Modelo
        self.renderer_model.draw_structure(
            self.plot_widget, 
            self.manager, 
            show_node_labels=self.show_node_labels,
            show_element_labels=self.show_element_labels,
            on_element_click=self._on_element_clicked_wrapper
        )
        
        
        # Render Cargas
        s_load = ScaleManager.instance().get_scale('load')
        self.renderer_load.draw_loads(self.plot_widget, self.manager, scale=s_load, 
                                      show_nodes=self.show_loads_nodes, 
                                      show_elements=self.show_loads_elements)
        
        # Render Deformada
        if self.current_results and self.show_deformed:
            s_def = ScaleManager.instance().get_scale('deformation')
            self.renderer_deform.draw_deformed(
                self.plot_widget, 
                self.manager, 
                self.current_results.get("displacements"),
                scale_factor=s_def
            )
        else:
            self.renderer_deform.clear(self.plot_widget)

        # Render fuerzas
        if self.current_results and self.current_diagram_type and self.show_diagrams:
            forces = self.current_results.get("element_forces",{})
            self.renderer_forces.draw_diagrams(
                self.plot_widget,
                self.manager,
                forces,
                type=self.current_diagram_type
            )
        else:
            self.renderer_forces.clear(self.plot_widget)


        print("[DEBUG] Viz updated (Renderers).")

    def set_visibility(self, item_type, visible):
        """ Controla visibilidad granular: 'deformed', 'diagrams' """
        if item_type == 'deformed': self.show_deformed = visible
        elif item_type == 'diagrams': self.show_diagrams = visible
        elif item_type == 'loads': # Master toggle
             self.show_loads_nodes = visible
             self.show_loads_elements = visible
        self.refresh_viz()

    def set_load_visibility(self, load_type, visible):
        if load_type == 'nodes': self.show_loads_nodes = visible
        elif load_type == 'elements': self.show_loads_elements = visible
        self.refresh_viz()

    def show_deformation(self, results, scale_factor=None):
        self.current_results = results
        displacements = results.get("displacements",{})
        
        if scale_factor is None:
            scale_factor = ScaleManager.instance().get_scale('deformation')
            
        self.renderer_deform.draw_deformed(self.plot_widget, self.manager, displacements, scale_factor)
        self.refresh_viz()

    def clear_results(self):
        self.current_results = None
        self.renderer_deform.clear(self.plot_widget)
        self.renderer_forces.celar(self.plot_widget)

    # --- MÉTODOS DE ESCALA ---
    def increase_load_scale(self):
        sm = ScaleManager.instance()
        val = sm.get_scale('load') * 1.2
        sm.set_scale('load', val)

    def decrease_load_scale(self):
        sm = ScaleManager.instance()
        val = sm.get_scale('load') / 1.2
        sm.set_scale('load', val)

    def increase_deform_scale(self):
        sm = ScaleManager.instance()
        val = sm.get_scale('deformation') * 1.2
        sm.set_scale('deformation', val)
        print(f"[DEBUG] Escala Deformada: {val:.2f}")

    def decrease_deform_scale(self):
        sm = ScaleManager.instance()
        val = sm.get_scale('deformation') / 1.2
        sm.set_scale('deformation', val)
        print(f"[DEBUG] Escala Deformada: {val:.2f}")

    # --- TOGGLES DE ETIQUETAS ---
    def toggle_node_labels(self, visible):
        self.show_node_labels = visible
        self.refresh_viz()

    def toggle_element_labels(self, visible):
        self.show_element_labels = visible
        self.refresh_viz()

    # --- INTERACCIÓN (Selección) ---
    def _on_node_clicked_wrapper(self, plot_item, points):
        self._deselect_all()
        if points:
            p = points[0]
            node_tag = p.data()
            node = self.manager.get_node(node_tag)
            if node:
                p.setBrush('r')
                self.last_clicked_point = p
                self.nodeSelected.emit(node)
                print(f"Node {node.tag} selected")
                
                text_item = pg.TextItem(text=f"ID: {node.tag}", color='k', anchor=(0,0))
                text_item.setPos(node.x, node.y)
                self.plot_widget.addItem(text_item)
                self.current_label = text_item

    def _on_element_clicked_wrapper(self, curve):
        #1. Limpiar selección previa
        self._deselect_all()

        #2. Resaltar nuevo elemento
        curve.setPen(color='r', width=4)
        self.last_clicked_element = curve
        
        #Obtener el objeto real y emitir
        ele_tag = getattr(curve.parentItem(), 'ele_tag', None)
        
        if ele_tag:
            element = self.manager.get_element(ele_tag)
            if element:
                self.elementSelected.emit(element)
                print(f"Element {ele_tag} selected")
                

    def _deselect_all(self):
        #1. Deseleccionar nodo 
        if self.last_clicked_point:
            self.last_clicked_point.resetBrush()
            self.last_clicked_point = None

        #2. Deseleccionar elementos
        if self.last_clicked_element:
            self.last_clicked_element.setPen(self.renderer_model.pen_element)
            self.last_clicked_element = None

        #3. Limpiar etiquetas flotantes
        if self.current_label:
            self.plot_widget.removeItem(self.current_label)
            self.current_label = None

        self.selectionCleared.emit()

    def _on_background_clicked(self, event):
        pos = event.scenePos()
        items = self.plot_widget.scene().items(pos)
        hit_node = any(isinstance(x, pg.ScatterPlotItem) for x in items)
        if not hit_node:
            self._deselect_all()

    def show_force_diagrams(self,diagram_type):
        self.current_diagram_type = diagram_type
        self.refresh_viz()
    
