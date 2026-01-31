import pyqtgraph as pg
import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QKeySequence, QShortcut
from src.analysis.manager import ProjectManager

# Importamos los nuevos renderizadores
from src.ui.visualizers.model_renderer import ModelRenderer
from src.ui.visualizers.load_renderer import LoadRenderer
from src.ui.visualizers.deformation_renderer import DeformationRenderer

class StructureInteractor(QWidget):
    nodeSelected = pyqtSignal(object)
    selectionCleared = pyqtSignal()

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
        self.manager.dataChanged.connect(self.refresh_viz)
        
        # 3. Inicializar Renderizadores
        self.renderer_model = ModelRenderer()
        self.renderer_model.attach(self.plot_widget)
        
        self.renderer_load = LoadRenderer()
        self.renderer_deform = DeformationRenderer()
        
        # 4. Estado de Interacción
        self.last_clicked_point = None
        self.current_label = None
        self.current_results = None 

        # View Options
        self.show_node_labels = False 
        self.show_element_labels = False
        self.load_scale = 0.05 
        self.deform_scale = 1000.0

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
            show_labels=(self.show_node_labels or self.show_element_labels)
        )
        
        # Render Cargas
        self.renderer_load.draw_loads(self.plot_widget, self.manager, scale=self.load_scale)
        
        # Render Deformada
        if self.current_results:
            self.renderer_deform.draw_deformed(
                self.plot_widget, 
                self.manager, 
                self.current_results.get("displacements"),
                scale_factor=self.deform_scale
            )

        print("[DEBUG] Viz updated (Renderers).")

    # --- API PÚBLICA ---
    def show_deformation(self, displacements, scale_factor=5000.0):
        self.current_results = {"displacements": displacements}
        self.renderer_deform.draw_deformed(self.plot_widget, self.manager, displacements, scale_factor)

    def clear_results(self):
        self.current_results = None
        self.renderer_deform.clear(self.plot_widget)

    # --- MÉTODOS DE ESCALA ---
    def increase_load_scale(self):
        self.load_scale *= 1.2
        self.refresh_viz()

    def decrease_load_scale(self):
        self.load_scale /= 1.2
        self.refresh_viz()

    def increase_deform_scale(self):
        self.deform_scale *= 1.5
        print(f"[DEBUG] Escala Deformada: {self.deform_scale:.2f}")
        self.refresh_viz()

    def decrease_deform_scale(self):
        self.deform_scale /= 1.5
        print(f"[DEBUG] Escala Deformada: {self.deform_scale:.2f}")
        self.refresh_viz()

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

    def _deselect_all(self):
        if self.last_clicked_point:
            self.last_clicked_point.resetBrush()
            self.last_clicked_point = None
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