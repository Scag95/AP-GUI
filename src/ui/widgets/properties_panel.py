from matplotlib.container import Container
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QDockWidget, QStackedWidget, QLabel, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from src.ui.widgets.properties_forms import NodeForms, ElementForm

class PropertiesPanel(QDockWidget):
    dataChanged = pyqtSignal()
    def __init__(self,parent=None):
        super().__init__("Panel de Propiedades", parent)
        self.setWindowTitle("Panel de Propiedades")
        self.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea | Qt.DockWidgetArea.LeftDockWidgetArea)

        #Widget contenedor
        container = QWidget()
        layout = QVBoxLayout(container)

        self.stack = QStackedWidget()

        self.lbl_placeholder = QLabel("Selecione un elemento")
        self.lbl_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stack.addWidget(self.lbl_placeholder) 

        #1. Formulario nodos
        self.node_form = NodeForms()
        self.node_form.dataChanged.connect(self.dataChanged.emit)
        self.stack.addWidget(self.node_form)
        layout.addWidget(self.stack)
        self.setWidget(container)

        #2. Formulario Elementos
        self.element_form = ElementForm()
        self.element_form.dataChanged.connect(self.dataChanged.emit)
        self.stack.addWidget(self.element_form)

    def show_node(self, node):
        self.node_form.load_node(node)
        self.stack.setCurrentWidget(self.node_form)

    def show_element(self, element):
        self.element_form.load_element(element)
        self.stack.setCurrentWidget(self.element_form)

    def clear_selection(self):
        #vuelve al mensaje por defecto
        self.stack.setCurrentWidget(self.lbl_placeholder)